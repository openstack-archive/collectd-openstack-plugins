# -*- coding: utf-8 -*-

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

import mock


def collectd(**kwargs):
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


def config(**kwargs):
    "Returns collecd module with collecd logging hooks."
    return mock.MagicMock(spec=MockedConfig, **kwargs)


class MockedConfig(object):
    "Mocked config class."

    BATCH_SIZE = 1


def value(
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
