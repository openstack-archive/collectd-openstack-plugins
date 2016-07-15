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
import os
import unittest

from collectd_ceilometer.tests.collectd_service import CollectdService


LOG = logging.getLogger(__name__)


class TestCollectdPython(unittest.TestCase):

    _collectd = None

    @classmethod
    def setUpClass(cls):
        cls._initial_environ = dict(os.environ)

    def setUp(self):
        if not CollectdService.has_collectd():
            self.skipTest('Unable to execute collectd.')

    def test_run_collectd(self):
        collectd = self.run_collectd()
        self.assertReceiveMessage('init')
        collectd.send_message('ping 123')
        self.assertReceiveMessage('pong 123')
        collectd.send_message('quit')
        self.assertReceiveMessage('bye')

    def run_collectd(self, *args, **kwargs):
        self._collectd = collectd = CollectdService(*args, **kwargs)
        self.addCleanup(collectd.stop)
        collectd.start()
        return collectd

    def assertReceiveMessage(self, expected, *args, **kwargs):
        if args or kwargs:
            expected = expected.format(*args, **kwargs)
        actual = ' '.join(self._collectd.receive_message())
        self.assertEqual(expected, actual)
