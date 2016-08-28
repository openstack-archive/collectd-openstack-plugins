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

import unittest

import collectd


class TestCollectd(unittest.TestCase):

    def test_info(self):
        collectd.info('Inside functional test!')

    def test_failure(self):
        collectd.warning('You were going to fail!')
        self.fail('Fail here.')

    def test_error(self):
        collectd.error('Some problem.')
        raise RuntimeError

    def test_skip(self):
        self.skipTest('Nevermind.')

    @unittest.expectedFailure
    def test_expected_failure(self):
        self.fail('You expected it.')

    @unittest.expectedFailure
    def test_unexpected_failure(self):
        collectd.info('It does not fail!')
