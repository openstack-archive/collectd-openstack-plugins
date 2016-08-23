# -*- coding: utf-8 -*-

# Copyright 2010-2011 OpenStack Foundation
# Copyright (c) 2015 Intel Corporation.
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
"""Plugin tests

"""

from collections import namedtuple
import logging
import requests
import unittest

import mock

from collectd_ceilometer import keystone_light
from collectd_ceilometer import plugin
from collectd_ceilometer import sender

from collectd_ceilometer.tests import match


Logger = logging.getLoggerClass()


class TestPlugin(unittest.TestCase):
    """Test the collectd plugin"""

    @mock.patch.object(plugin, 'Plugin', autospec=True)
    @mock.patch.object(plugin, 'Config', autospec=True)
    @mock.patch.object(plugin, 'CollectdLogHandler', autospec=True)
    @mock.patch.object(plugin, 'ROOT_LOGGER', autospec=True)
    def test_callbacks(
            self, ROOT_LOGGER, CollectdLogHandler, Config, Plugin):
        """Verify that the callbacks are registered properly"""

        collectd = mocked_collectd()

        # When plugin function is called
        plugin.setup_plugin(collectd=collectd)

        # Logger handler is set up
        ROOT_LOGGER.addHandler.assert_called_once_with(
            CollectdLogHandler.return_value)
        ROOT_LOGGER.setLevel.assert_called_once_with(logging.NOTSET)

        # It create a plugin
        Plugin.assert_called_once_with(
            collectd=collectd, config=Config.instance.return_value)

        # callbacks are registered to collectd
        instance = Plugin.return_value
        collectd.register_init.assert_called_once_with(instance.init)
        collectd.register_config.assert_called_once_with(instance.config)
        collectd.register_write.assert_called_once_with(instance.write)
        collectd.register_shutdown.assert_called_once_with(instance.shutdown)

    @mock.patch.object(requests, 'post', spec=callable)
    @mock.patch.object(sender, 'keystoneClientV2', autospec=True)
    def test_write(self, ClientV2, post):
        """Test collectd data writing"""

        auth_client = ClientV2.return_value
        auth_client.get_service_endpoint.return_value =\
            'https://test-ceilometer.tld'

        post.return_value.status_code = sender.HTTP_CREATED
        post.return_value.text = 'Created'

        # init instance
        collectd = mocked_collectd()
        config = mocked_config(BATCH_SIZE=2)
        instance = plugin.Plugin(collectd=collectd, config=config)
        instance.init()

        # no authentication has been performed so far
        ClientV2.assert_not_called()

        # create a value
        data = mocked_value()

        # write first value
        instance.write(data)
        collectd.error.assert_not_called()

        # no value has been sent to ceilometer
        post.assert_not_called()

        # send the second value
        instance.write(data)
        collectd.error.assert_not_called()

        # authentication client has been created
        ClientV2.assert_called_once()

        # and values has been sent
        post.assert_called_once_with(
            'https://test-ceilometer.tld/v2/meters/cpu.freq',
            data=match.json([
                {"source": "collectd",
                 "counter_name": "cpu.freq",
                 "counter_unit": "jiffies",
                 "counter_volume": 1234,
                 "timestamp": "Thu Nov 29 21:33:09 1973",
                 "resource_id": "localhost-0",
                 "resource_metadata": None,
                 "counter_type": "gauge"},
                {"source": "collectd",
                 "counter_name": "cpu.freq",
                 "counter_unit": "jiffies",
                 "counter_volume": 1234,
                 "timestamp": "Thu Nov 29 21:33:09 1973",
                 "resource_id": "localhost-0",
                 "resource_metadata": None,
                 "counter_type": "gauge"}]),
            headers={'Content-type': 'application/json',
                     'X-Auth-Token': auth_client.auth_token},
            timeout=1.0)

        # reset post method
        post.reset_mock()

        # write another values
        instance.write(data)
        collectd.error.assert_not_called()

        # nothing has been sent
        post.assert_not_called()

        # call shutdown
        instance.shutdown()

        # no errors
        collectd.error.assert_not_called()

        # previously written value has been sent
        post.assert_called_once_with(
            'https://test-ceilometer.tld/v2/meters/cpu.freq',
            data=match.json([
                {"source": "collectd",
                 "counter_name": "cpu.freq",
                 "counter_unit": "jiffies",
                 "counter_volume": 1234,
                 "timestamp": "Thu Nov 29 21:33:09 1973",
                 "resource_id": "localhost-0",
                 "resource_metadata": None,
                 "counter_type": "gauge"}]),
            headers={
                'Content-type': 'application/json',
                'X-Auth-Token': auth_client.auth_token},
            timeout=1.0)

    @mock.patch.object(requests, 'post', spec=callable)
    @mock.patch.object(sender, 'keystoneClientV2', autospec=True)
    @mock.patch.object(plugin, 'LOGGER', autospec=True)
    def test_write_auth_failed(self, LOGGER, ClientV2, post):
        """Test authentication failure"""

        # tell the auth client to rise an exception
        ClientV2.side_effect = RuntimeError('Test Client() exception')

        # init instance
        collectd = mocked_collectd()
        config = mocked_config(BATCH_SIZE=1)
        instance = plugin.Plugin(collectd=collectd, config=config)
        instance.init()

        # write the value
        self.assertRaises(RuntimeError, lambda: instance.write(mocked_value()))

        # no requests method has been called
        post.assert_not_called()

    @mock.patch.object(requests, 'post', spec=callable)
    @mock.patch.object(sender, 'keystoneClientV2', autospec=True)
    @mock.patch.object(sender, 'LOGGER', autospec=True)
    def test_write_auth_failed2(self, LOGGER, ClientV2, post):
        """Test authentication failure2"""

        ClientV2.side_effect = keystone_light.KeystoneException(
            "Missing name 'xxx' in received services",
            "exception",
            "services list")

        # init instance
        collectd = mocked_collectd()
        config = mocked_config(BATCH_SIZE=1)
        instance = plugin.Plugin(collectd=collectd, config=config)
        instance.init()

        # write the value
        instance.write(mocked_value())

        LOGGER.error.assert_called_once_with(
            "Suspending error logs until successful auth")
        LOGGER.log.assert_called_once_with(
            logging.ERROR, "Authentication error: %s",
            "Missing name 'xxx' in received services\nReason: exception",
            exc_info=0)

        # no requests method has been called
        post.assert_not_called()

    @mock.patch.object(requests, 'post', spec=callable)
    @mock.patch.object(sender, 'keystoneClientV2', autospec=True)
    @mock.patch.object(sender, 'LOGGER', autospec=True)
    def test_request_error(self, LOGGER, ClientV2, post):
        """Test error raised by underlying requests module"""

        # tell POST request to raise an exception
        post.side_effect = requests.RequestException('Test POST exception')

        # init instance
        collectd = mocked_collectd()
        config = mocked_config(BATCH_SIZE=1)
        instance = plugin.Plugin(collectd=collectd, config=config)
        instance.init()

        # write the value
        instance.write(mocked_value())

        LOGGER.error.assert_called_once_with(
            'Ceilometer request error: %s', 'Test POST exception')

    # https://bugs.launchpad.net/collectd-ceilometer-plugin/+bug/1614772
    @unittest.expectedFailure
    @mock.patch.object(requests, 'post', spec=callable)
    @mock.patch.object(sender, 'keystoneClientV2', autospec=True)
    def test_reauthentication(self, ClientV2, post):
        """Test re-authentication"""

        # assure post rensponse is not mocked
        post.return_value = rensponse = requests.Response()

        client = ClientV2.return_value
        client.auth_token = 'Test auth token'

        # init instance
        collectd = mocked_collectd()
        config = mocked_config(BATCH_SIZE=1)
        instance = plugin.Plugin(collectd=collectd, config=config)
        instance.init()

        # write the value
        instance.write(mocked_value())

        # verify the auth token
        post.assert_called_once_with(
            mock.ANY, data=mock.ANY,
            headers={'Content-type': 'application/json',
                     'X-Auth-Token': 'Test auth token'},
            timeout=1.)

        # subsequent call of POST method will fail due to the authentication
        rensponse.status_code = sender.HTTP_UNAUTHORIZED

        # set a new auth token
        client.auth_token = 'New test auth token'
        post.reset_mock()

        # write the value
        instance.write(mocked_value())

        # verify the auth token
        post.assert_has_calls([
            mock.call(mock.ANY, data=mock.ANY,
                      headers={'Content-type': 'application/json',
                               'X-Auth-Token': 'Test auth token'},
                      timeout=1.),
            mock.call(mock.ANY, data=mock.ANY,
                      headers={'Content-type': 'application/json',
                               'X-Auth-Token': 'New test auth token'},
                      timeout=1.)])

    @mock.patch.object(requests, 'post', spec=callable)
    @mock.patch.object(sender, 'keystoneClientV2', autospec=True)
    @mock.patch.object(plugin, 'LOGGER', autospec=True)
    def test_authentication_in_multiple_threads(self, LOGGER, ClientV2, post):
        """Test authentication in muliple threads

        This test simulates the authentication performed from different thread
        after the authentication lock has been acquired. The sender is not
        authenticated, the lock is acquired, the authentication token exists
        (i.e. it has been set by different thread) and it is used.
        """
        # pylint: disable=protected-access

        # init instance
        collectd = mocked_collectd()
        config = mocked_config(BATCH_SIZE=1)
        instance = plugin.Plugin(collectd=collectd, config=config)
        instance.init()

        # the sender used by the instance
        sender = instance._writer._sender

        # create a dummy lock
        class DummyLock(namedtuple('LockBase', ['sender', 'token', 'urlbase'])):
            """Lock simulation, which sets the auth token when locked"""

            def __enter__(self, *args, **kwargs):
                # pylint: disable=protected-access
                self.sender._auth_token = self.token
                self.sender._url_base = self.urlbase

            def __exit__(self, *args, **kwargs):
                pass

        # replace the sender's lock by the dummy lock
        sender._auth_lock = DummyLock(sender, 'TOKEN', 'URLBASE/%s')

        # write the value
        instance.write(mocked_value())

        # No errors has been registered
        LOGGER.exception.assert_not_called()

        # client has not been called at all
        ClientV2.assert_not_called()

        # verify the auth token
        post.assert_called_once_with(
            'URLBASE/cpu.freq', data=mock.ANY,
            headers={
                'Content-type': 'application/json', 'X-Auth-Token': 'TOKEN'},
            timeout=1.0)

    @mock.patch.object(requests, 'post', spec=callable)
    @mock.patch.object(sender, 'keystoneClientV2', autospec=True)
    @mock.patch.object(plugin, 'Writer', autospec=True)
    @mock.patch.object(plugin, 'LOGGER', autospec=True)
    def test_exceptions(self, LOGGER, Writer, ClientV2, post):
        """Test exception raised during write and shutdown"""

        writer = Writer.return_value
        writer.write.side_effect = ValueError('Test write error')
        writer.flush.side_effect = RuntimeError('Test shutdown error')

        # init instance
        collectd = mocked_collectd()
        config = mocked_config(BATCH_SIZE=1)
        instance = plugin.Plugin(collectd=collectd, config=config)
        instance.init()

        self.assertRaises(ValueError, lambda: instance.write(mocked_value()))
        self.assertRaises(RuntimeError, instance.shutdown)

    @mock.patch.object(plugin, 'ROOT_LOGGER', new_callable=Logger, name='me')
    def test_log_debug_to_collectd(self, ROOT_LOGGER):
        """Verify that debug messages are sent to collectd."""

        collectd = mocked_collectd()
        plugin.setup_plugin(collectd=collectd)

        # When log messages are produced
        ROOT_LOGGER.debug('some %s', 'noise')

        # When plugin function is called
        collectd.debug.assert_called_once_with('some noise')

    @mock.patch.object(plugin, 'ROOT_LOGGER', new_callable=Logger, name='me')
    def test_log_infos_to_collectd(self, ROOT_LOGGER):
        """Verify that the callbacks are registered properly"""

        collectd = mocked_collectd()
        plugin.setup_plugin(collectd=collectd)

        # When log messages are produced
        ROOT_LOGGER.info('%d info', 1)

        # When plugin function is called
        collectd.info.assert_called_once_with('1 info')

    @mock.patch.object(plugin, 'ROOT_LOGGER', new_callable=Logger, name='me')
    def test_log_errors_to_collectd(self, ROOT_LOGGER):
        """Verify that the callbacks are registered properly"""

        collectd = mocked_collectd()
        plugin.setup_plugin(collectd=collectd)

        # When log messages are produced
        ROOT_LOGGER.error('some error')

        # When plugin function is called
        collectd.error.assert_called_once_with('some error')

    @mock.patch.object(plugin, 'ROOT_LOGGER', new_callable=Logger, name='me')
    def test_log_fatal_to_collectd(self, ROOT_LOGGER):
        """Verify that the callbacks are registered properly"""

        collectd = mocked_collectd()
        plugin.setup_plugin(collectd=collectd)

        # When log messages are produced
        ROOT_LOGGER.fatal('some error')

        # When plugin function is called
        collectd.error.assert_called_once_with('some error')

    @mock.patch.object(plugin, 'ROOT_LOGGER', new_callable=Logger, name='me')
    def test_log_exceptions_to_collectd(self, ROOT_LOGGER):
        """Verify that the callbacks are registered properly"""

        collectd = mocked_collectd()
        plugin.setup_plugin(collectd=collectd)

        # When exception is logged
        try:
            raise ValueError('some error')
        except ValueError:
            ROOT_LOGGER.exception('got exception')

        # When main function is called
        collectd.error.assert_called_once_with(
            match.wildcard('got exception\n'
                           'Traceback (most recent call last):\n'
                           '*'
                           'ValueError: some error'))


def mocked_collectd(**kwargs):
    "Returns collecd module with collecd logging hooks."
    return mock.MagicMock(spec=MockedCollectd, **kwargs)


class MockedCollectd(object):
    "Mocked collectd module specifications."

    def debug(self, record):
        "Hook for debug messages"

    def info(self, record):
        "Hook for info messages"

    def warning(self, record):
        "Hook for warning messages"

    def error(self, record):
        "Hook for error messages"

    def register_init(self, hook):
        "Register an hook for init."

    def register_config(self, hook):
        "Register an hook for config."

    def register_write(self, hook):
        "Register an hook for write."

    def register_shutdown(self, hook):
        "Register an hook for shutdown."


def mocked_config(**kwargs):
    "Returns collecd module with collecd logging hooks."
    return mock.MagicMock(spec=MockedConfig, **kwargs)


class MockedConfig(object):
    "Mocked config class."

    BATCH_SIZE = 1


def mocked_value(
        host='localhost', plugin='cpu', plugin_instance='0',
        _type='freq', type_instance=None, time=123456789, values=(1234,),
        **kwargs):
    """Create a mock value"""

    return mock.MagicMock(
        spec=MockedValue, host=host, plugin=plugin,
        plugin_instance=plugin_instance, type=_type,
        type_instance=type_instance, time=time, values=list(values), meta=None,
        **kwargs)


class MockedValue(object):
    """Value used for testing"""

    host = 'localhost'
    plugin = None
    plugin_instance = None
    type = None
    type_instance = None
    time = 123456789
    values = []
    meta = None
