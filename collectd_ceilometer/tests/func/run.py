# -*- coding: utf-8 -*-

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

from contextlib import contextmanager
import functools
from glob import glob
import importlib
import inspect
import json
import os
import sys
import subprocess
import tempfile

try:
    # when used inside collectd run a function
    import collectd

except ImportError:
    collectd = None


def get_module_info(obj):
    script_path = str(obj)
    if os.path.isfile(script_path):
        script_path = obj
    else:
        script_path = inspect.getfile(obj)
    script_path, _ = os.path.splitext(script_path)
    base_path = os.path.dirname(script_path)
    while glob(os.path.join(base_path, '__init__.py*')):
        base_path = os.path.dirname(base_path)
    module_path = os.path.relpath(script_path, base_path)
    module_name = module_path.replace(os.path.sep, '.')
    return base_path, module_name


CONFIGURATION_TEMPLATE = """
    LoadPlugin "logfile"
    <Plugin "logfile">
        LogLevel "info"
        File STDERR
        Timestamp true
    </Plugin>
   <LoadPlugin "python">
        Globals true
    </LoadPlugin>
    <Plugin python>
        ModulePath "{runner_module_path}"
        LogTraces true
        Interactive true
        Import "{runner_module_name}"
        <Module "{runner_module_name}">
            data_path "{data_path}"
        </Module>
    </Plugin>
"""


class CollectdRunner(object):

    runner_module_path, runner_module_name = get_module_info(__file__)

    configuration_template = CONFIGURATION_TEMPLATE

    args = tuple()
    kwargs = {}

    def __init__(self, function=None):
        self.function = function

    def __call__(self, *args, **kwargs):
        """Executes given function."""
        print "spawn collectd"

        function = self.function
        module_path, module_name = get_module_info(function)
        data = json.dumps({
            'module_path': module_path,
            'module_name': module_name,
            'function_name': function.__name__,
            'args': args,
            'kwargs': kwargs})

        with create_temp_file(data) as data_path:
            configuration = self.configuration_template.format(
                runner_module_path=self.runner_module_path,
                runner_module_name=self.runner_module_name,
                data_path=data_path)
            with create_temp_file(configuration) as configuration_path:
                with create_temp_file() as pid_path:
                    subprocess.check_call([
                        "collectd", '-f', '-P', pid_path,
                        "-C", configuration_path])

    def read_configuration(self, config):
        collectd.info("read_configuration: " + repr(config))
        values = {}
        for child in config.children:
            values[child.key.lower()] = child.values
        with open(values['data_path'][0]) as data_fd:
            data = json.load(data_fd)
        module_path = data.get('module_path')
        if module_path and module_path not in sys.path:
            sys.path.append(module_path)
        module = importlib.import_module(data['module_name'])
        function = getattr(module, data['function_name'])
        self.function = function
        self.args = data['args']
        self.kwargs = data['kwargs']

    def run(self):
        return self.function(*self.args, **self.kwargs)

    @classmethod
    def run_in_collectd(cls, function):
        assert callable(function)
        if collectd:
            return function
        else:
            runner = CollectdRunner(function=function)
            functools.update_wrapper(runner, function)
            return runner


@CollectdRunner.run_in_collectd
def main(argv):
    print 'inside collectd: ' + repr(collectd)


@contextmanager
def create_temp_file(text=None):
    fd, path = tempfile.mkstemp()
    try:
        try:
            if text:
                os.write(fd, text)
        finally:
            os.close(fd)

        yield path

    finally:
        os.remove(path)


if __name__ == '__main__':
    # when used as a script then run main entry point
    sys.exit(main(sys.argv))

else:
    try:
        # when used inside collectd run a function
        import collectd

        runner = CollectdRunner()
        collectd.register_config(runner.read_configuration)
        collectd.register_init(runner.run)

    except ImportError:
        pass  # when used as a library do nothing
