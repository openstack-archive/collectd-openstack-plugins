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
import inspect
import os
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
    base_path = os.path.dirname(os.path.abspath(script_path))
    while glob(os.path.join(base_path, '__init__.py*')):
        base_path = os.path.dirname(base_path)
    module_path = os.path.relpath(script_path, base_path)
    module_name = module_path.replace(os.path.sep, '.')
    return base_path, module_name


CONFIGURATION_TEMPLATE = """
    LoadPlugin "logfile"
    <Plugin "logfile">
        LogLevel "info"
        File STDOUT
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
    </Plugin>
"""

CODE_TEMPLATE = """
import os
import sys

os.chdir('{current_dir}')

sys.path.insert(0, '{module_path}')
from {module_name} import {function_name} as function

args = {args}
kwargs = {kwargs}

try:
    result = function(*args, **kwargs)
except Exception:
    sys.exit(1)
else:
    sys.exit(0)
"""


class CollectdRunner(object):

    runner_module_path, runner_module_name = get_module_info(__file__)

    configuration_template = CONFIGURATION_TEMPLATE

    args = tuple()
    kwargs = {}

    def __init__(self, function=None):
        self.configuration = self.configuration_template.format(
            runner_module_path=self.runner_module_path,
            runner_module_name=self.runner_module_name)
        self.function = function
        self.module_path, self.module_name = get_module_info(function)

    def run(self, *args, **kwargs):
        """Executes given function."""
        function = self.function
        code = CODE_TEMPLATE.format(
            current_dir=os.getcwd(),
            module_path=self.module_path,
            module_name=self.module_name,
            function_name=function.__name__,
            args=repr(args),
            kwargs=repr(kwargs))

        with create_temp_file(self.configuration) as configuration_path:
            with create_temp_file() as pid_path:
                process = subprocess.Popen(
                    ["collectd", '-f', '-P', pid_path,
                     "-C", configuration_path],
                    stdin=subprocess.PIPE,
                    # stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                process.communicate(input=code)
                return process.wait()

    __call__ = run

    @classmethod
    def run_in_collectd(cls, function):
        assert callable(function)
        if collectd:
            return function
        else:
            runner = cls(function=function)
            functools.update_wrapper(runner, function)
            return runner


run_in_collectd = CollectdRunner.run_in_collectd


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
