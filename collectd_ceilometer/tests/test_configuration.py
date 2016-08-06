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


from collectd_ceilometer.attribute import RequiredAttributeError
from collectd_ceilometer.configuration import Configuration
from collectd_ceilometer.units import UNITS


class TestAttribute(unittest.TestCase):

    def test_init(self):
        configuration = Configuration()

        self.assertEqual({}, configuration.attributes)
        self.assertEqual(1, configuration.BATCH_SIZE)
        self.assertEqual('internalURL', configuration.CEILOMETER_URL_TYPE)
        self.assertEqual(1000, configuration.CEILOMETER_TIMEOUT)
        self.assertRaises(
            RequiredAttributeError, lambda: configuration.OS_AUTH_URL)
        self.assertRaises(
            RequiredAttributeError, lambda: configuration.OS_USERNAME)
        self.assertRaises(
            RequiredAttributeError, lambda: configuration.OS_PASSWORD)
        self.assertRaises(
            RequiredAttributeError, lambda: configuration.OS_TENANT_NAME)
        self.assertFalse(configuration.VERBOSE)
        self.assertEqual(UNITS, configuration.UNITS)
