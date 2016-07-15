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


import logging
import fnmatch
import os
import unittest

from collectd_ceilometer.tests.collectd_service import CollectdService


LOG = logging.getLogger(__name__)


class FNMatch(object):

    def __init__(self, pattern):
        self._pattern = pattern

    def __eq__(self, obj):
        return fnmatch.fnmatchcase(obj, self._pattern)

    def __repr__(self, *args, **kwargs):
        return 'FNMatch({})'.format(repr(self._pattern))


class TestCollectdPython(unittest.TestCase):

    _collectd = None

    @classmethod
    def setUpClass(cls):
        cls._initial_environ = dict(os.environ)

    def setUp(self):
        if not CollectdService.has_collectd():
            self.skipTest('Unable to execute collectd.')

    def test_run_cpu_write(self):
        self.run_collectd(configuration='LoadPlugin "cpu"')
        self.assertReceiveMessage('init')
        self.assertReceiveMessage('read')

        # Expected write:
        #     collectd.Values(
        #         type='cpu',type_instance='user',plugin='cpu',
        #         plugin_instance='0',host='vagrant-ubuntu-trusty-64',
        #         time=1469180512.7518458,interval=10.0,values=[946])

        self.assertReceiveMessage(
            "write collectd.Values("
                "type='cpu',type_instance='user',plugin='cpu',"
                "plugin_instance='0',host='vagrant-ubuntu-trusty-64',"
                "time=*,interval=10.0,values=*)")

    def run_collectd(self, *args, **kwargs):
        self._collectd = collectd = CollectdService(*args, **kwargs)
        self.addCleanup(collectd.stop)
        collectd.start()
        return collectd

    def assertReceiveMessage(self, expected, *args, **kwargs):
        if args or kwargs:
            expected = expected.format(*args, **kwargs)

        actual = ' '.join(self._collectd.receive_message()).strip()
        self.assertEqual(FNMatch(expected), actual)
