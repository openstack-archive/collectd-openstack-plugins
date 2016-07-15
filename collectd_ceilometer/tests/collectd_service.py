# -*- coding: utf-8 -*-

# Copyright 2010-2011 OpenStack Foundation
# Copyright (c) 2016 Intel Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


import logging
import os
import Queue
import select
import socket
import subprocess
import sys
import tempfile
import threading


LOG = logging.getLogger(__name__)


class CollectdServicePeer(object):

    _connection = None
    _started = False
    _thread = None
    _lock = None
    _lines = None

    def __init__(self):
        self._sockets = []
        self._processes = []
        self._temp_files = []
        self._lock = threading.Lock()

    def on_message(self, message, arguments):
        self.send_message(
                'error Invalid command: {} {}', message, arguments)

    def start(self, connection):
        with self._lock:
            if self._connection or self._thread:
                raise RuntimeError('Already stareted.')

            self._connection = connection
            self._sockets.append(connection)
            self._lines = iter(read_lines(self._connection))
            self._sockets.append(connection)
            self._thread = thread = threading.Thread(
                target=self._process_messages)
            thread.daemon = True
            thread.start()

    def stop(self):
        with self._lock:
            connection = self._connection
            if connection:
                try:
                    connection.send('quit\n')
                except socket.error:
                    LOG.debug(
                        'Do ignore socket error when stopping connection.',
                        exc_info=1)
                finally:
                    del self._connection

            sockets = self._sockets
            if sockets:
                self._sockets = []
                for sock in sockets:
                    try:
                        sock.close()
                    except socket.error:
                        LOG.debug(
                            'Do ignore socket failure when closing connection.',
                            exc_info=1)

            if self._processes:
                for process in self._processes:
                    process.kill()
            self._processes = []

            if self._temp_files:
                for temp_file in self._temp_files:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
            self._temp_files = []

            if self._lines:
                del self._lines

            thread = self._thread
            if thread:
                del self._thread
                thread.join(timeout=5.)

    def _process_messages(self):
        assert self._thread is threading.current_thread()
        try:
            for line in self._lines:
                try:
                    message, arguments = line.split(' ', 1)
                except ValueError:
                    message, arguments = line, ''

                if message == 'quit':
                    LOG.info('Service interrupted by peer.')
                    return

                elif message == 'ping':
                    self.send_message('pong {}', arguments)

                else:
                    try:
                        with self._lock:
                            self.on_message(message, arguments)
                    except Exception:
                        LOG.exception('Error processing message: %s', line)
                        raise
        finally:
            connection = self._connection
            if connection:
                try:
                    connection.close()
                except socket.error:
                    pass

    def _create_temp_file(self, write_data=None):
        stream, path = tempfile.mkstemp()
        try:
            self._temp_files.append(path)
            if write_data:
                os.write(stream, bytearray(write_data, 'UTF-8'))
        finally:
            os.close(stream)
        return path

    def send_message(self, message, *args, **kwargs):
        if args or kwargs:
            message = message.format(*args, **kwargs)
        self._connection.send(message.strip() + '\n')


class CollectdService(CollectdServicePeer):

    _environ = dict(os.environ)

    _COLLECTD_CONFIGURATION_TEMPLATE = """
    <LoadPlugin "python">
      Globals true
    </LoadPlugin>
    <Plugin python>
        ModulePath "{module_path}"
        LogTraces true
        Interactive false
        Import "collectd_ceilometer.tests.activate_collectd_plugin_service"
    </Plugin>
    {configuration}
    """

    _messages = None

    def __init__(self, configuration=None):
        super(CollectdService, self).__init__()
        self._configuration = self._COLLECTD_CONFIGURATION_TEMPLATE.format(
            module_path=self.get_module_dir(),
            configuration=configuration or '')

    def start(self, options=tuple()):
        self.stop()

        LOG.info('Starting collectd...')
        configuration_path = self._create_temp_file(
            write_data=self._configuration)
        options = ("-C", configuration_path) + options

        pid_path = self._create_temp_file()

        server = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        self._sockets.append(server)
        server.bind(('', 0))
        server.listen(1)
        environ = self._environ
        environ['PYTHONPATH'] = ':'.join([self.get_module_dir()]+ sys.path)
        environ['SERVER_PORT'] = str(server.getsockname()[1])

        command_line = ("collectd", '-f', '-P', pid_path) + options
        LOG.debug('Executing collectd: %s', command_line)
        self._processes.append(
            subprocess.Popen(command_line, env=environ))
        ready_to_read, _, _ = \
            select.select([server], [], [], 10.0)
        if server not in ready_to_read:
            raise RuntimeError('Collectd Python plugin not connected.')
        connection, _ = server.accept()
        self._messages = Queue.Queue()
        super(CollectdService, self).start(connection)

    def on_message(self, message, arguments):
        self._messages.put((message, arguments))

    def stop(self):
        super(CollectdService, self).stop()
        if self._messages:
            del self._messages

    _module_dir = None

    @classmethod
    def get_module_dir(cls):
        module_dir = cls._module_dir
        if module_dir is None:
            module_dir = os.path.abspath(
                os.path.dirname(__file__))
            parent_dir = os.path.dirname(module_dir)
            while os.path.exists(os.path.join(parent_dir, '__init__.py')):
                module_dir = parent_dir
                parent_dir = os.path.dirname(module_dir)
            cls._module_dir = module_dir

        return module_dir

    _has_collectd = None

    @classmethod
    def has_collectd(cls):
        has_collectd = cls._has_collectd
        if has_collectd is None:
            try:
                subprocess.check_output(['collectd', '-h'])
            except Exception:
                has_collectd = False
                LOG.debug('collectd not available.', exc_info=1)
            else:
                has_collectd = True
            cls._has_collectd = has_collectd

        return has_collectd

    def receive_message(self, timeout=5., *args, **kwargs):
        return self._messages.get(timeout=5., *args, **kwargs)

def read_lines(connection):
    buff = connection.recv(4096)
    buffering = True
    while buffering:
        if "\n" in buff:
            line, buff = buff.split("\n", 1)
            yield line
        else:
            try:
                more = connection.recv(4096)
            except socket.error:
                break
            if not more:
                buffering = False
            else:
                buff += more
    if buff:
        yield buff


class CollectdServicePlugin(CollectdServicePeer):

    def start(self):
        port = int(os.environ['SERVER_PORT'])
        connection = socket.create_connection(('localhost', port), 20)
        super(CollectdServicePlugin, self).start(connection)

    def config(self, config):
        self.send_message('config {}', config)

    def init(self):
        self.send_message('init')

    def read(self, data=None):
        if data:
            self.send_message('read {}', data)
        else:
            self.send_message('read')

    def write(self, data=None):
        self.send_message('write {}', data)


    @classmethod
    def activate(cls, *args, **kwargs):
        import collectd

        service = cls(*args, **kwargs)

        try:
            LOG.info('Start mock pluging service.')
            service.start()
            collectd.register_config(service.config)
            collectd.register_init(service.init)
            collectd.register_read(service.read)
            collectd.register_write(service.write)
        except Exception:
            LOG.exception('Unable to start mock plugin service.')
            service.stop()
            raise
        else:
            LOG.info('Plugin service started.')
            return service
