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

"""Plugin tests"""

from __future__ import unicode_literals

from collectd_ceilometer.meters.base import Meter
from collectd_ceilometer.tests.base import TestCase
import mock


class Values(object):
    """Stub class to replace collectd.Values"""
    def __init__(self, plugin=None, type=None):
        self.plugin = plugin
        self.type = type


class collectd_mock(object):
    """Model for the collectd class to be mocked"""
    def get_dataset(self, string):
        pass

collectd_class = 'collectd_ceilometer.tests.test_meters_base.collectd_mock'


class MetersTest(TestCase):
    """Test the meters/base.py class"""

    @mock.patch(collectd_class, spec=True)
    def setUp(self, collectd):
        self._collectd = collectd
        # need this as a parameter for sample_type()
        self.vl = Values(type="my_type")
        self.meter = Meter(self._collectd)

    def tearDown(self):
        pass

    def test_sample_type_gauge(self):
        # sample_type uses get_dataset()[0][1]
        self.meter._collectd.get_dataset.return_value = [('value', 'gauge', )]
        expected = "gauge"
        actual = self.meter.sample_type(self.vl)

        self.assertEqual(expected, actual)

    def test_sample_type_derive(self):
        # sample_type uses get_dataset()[0][1]
        self.meter._collectd.get_dataset.return_value = [('value', 'derive', )]
        expected = "delta"
        actual = self.meter.sample_type(self.vl)

        self._collectd.get_dataset.assert_called()
        self.assertEqual(expected, actual)

    def test_sample_type_absolute(self):
        # sample_type uses get_dataset()[0][1]
        self._collectd.get_dataset.return_value = [('value', 'absolute', )]
        expected = "cumulative"
        actual = self.meter.sample_type(self.vl)

        self._collectd.get_dataset.assert_called()
        self.assertEqual(expected, actual)

    def test_sample_type_counter(self):
        # sample_type uses get_dataset()[0][1]
        self._collectd.get_dataset.return_value = [('value', 'counter', )]
        expected = "cumulative"
        actual = self.meter.sample_type(self.vl)

        self.assertEqual(expected, actual)

    def test_sample_type_invalid(self):
        self._collectd.get_dataset.side_effect = Exception("Boom!")
        expected = "gauge"
        actual = self.meter.sample_type(self.vl)

        self.assertEqual(expected, actual)
