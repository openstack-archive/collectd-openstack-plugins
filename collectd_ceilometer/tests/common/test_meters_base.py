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

from collectd_ceilometer.common.meters.base import Meter
from collectd_ceilometer.tests.base import TestCase
import mock


class Values(object):
    """Stub class to replace collectd.Values"""

    def __init__(self, plugin="my_plugin", type="my_type"):
        self.plugin = plugin
        self.type = type


class CollectdMock(object):
    """Model for the collectd class to be mocked"""

    def get_dataset(self, string):
        pass


collectd_class = \
    'collectd_ceilometer.tests.common.test_meters_base.CollectdMock'


class MetersTest(TestCase):
    """Test the meters/base.py class"""

    @mock.patch(collectd_class, spec=True)
    def setUp(self, collectd):
        super(MetersTest, self).setUp()
        self._collectd = collectd
        # need this as a parameter for sample_type()
        self.vl = Values()
        self.meter = Meter(self._collectd)

    def test_sample_type_gauge(self):
        # sample_type uses get_dataset()[0][1]
        self._collectd.get_dataset.return_value = [('value', 'gauge', )]

        actual = self.meter.sample_type(self.vl)

        self._collectd.get_dataset.assert_called_once()
        self.assertEqual("gauge", actual)

    def test_sample_type_derive(self):
        # sample_type uses get_dataset()[0][1]
        self._collectd.get_dataset.return_value = [('value', 'derive', )]

        actual = self.meter.sample_type(self.vl)

        self._collectd.get_dataset.assert_called_once()
        self.assertEqual("delta", actual)

    def test_sample_type_absolute(self):
        # sample_type uses get_dataset()[0][1]
        self._collectd.get_dataset.return_value = [('value', 'absolute', )]

        actual = self.meter.sample_type(self.vl)

        self._collectd.get_dataset.assert_called_once()
        self.assertEqual("cumulative", actual)

    def test_sample_type_counter(self):
        # sample_type uses get_dataset()[0][1]
        self._collectd.get_dataset.return_value = [('value', 'counter', )]

        actual = self.meter.sample_type(self.vl)

        self._collectd.get_dataset.assert_called_once()
        self.assertEqual("cumulative", actual)

    @mock.patch('collectd_ceilometer.common.meters.base.LOGGER')
    def test_sample_type_invalid(self, LOGGER):
        self._collectd.get_dataset.side_effect = Exception("Boom!")

        actual = self.meter.sample_type(self.vl)

        self._collectd.get_dataset.assert_called_once()
        LOGGER.warning.assert_called_once()
        self.assertEqual("gauge", actual)

    @mock.patch.object(Meter, 'alarm_severity', spec=callable)
    def test_low_alarm_severity(self, alarm_severity):
        """Test the 'low' severity setting.

        Set-up: set the return value for severity
                Call the alarm_severity method and its pre-requistites
        Test: Compare the configured severity to the result of alarm_severity()
        Expected behaviour: Result will be True
        """
        alarm_severity.return_value = 'low'

        meter_name = self.meter.meter_name(self.vl)
        result = alarm_severity(self.vl, meter_name)

        self.assertEqual('low', result)

    @mock.patch.object(Meter, 'alarm_severity', spec=callable)
    def test_moderate_alarm_severity(self, alarm_severity):
        """Test the 'moderate' severity setting.

        Set-up: set the return value for severity
                Call the alarm_severity method and its pre-requistites
        Test: Compare the configured severity to the result of alarm_severity()
        Expected behaviour: Result will be True
        """
        alarm_severity.return_value = 'moderate'

        meter_name = self.meter.meter_name(self.vl)
        result = alarm_severity(self.vl, meter_name)

        self.assertEqual('moderate', result)

    @mock.patch.object(Meter, 'alarm_severity', spec=callable)
    def test_critical_alarm_severity(self, alarm_severity):
        """Test the 'critical' severity setting.

        Set-up: set the return value for severity
                Call the alarm_severity method and its pre-requistites
        Test: Compare the configured severity to the result of alarm_severity()
        Expected behaviour: Result will be True.
        """
        alarm_severity.return_value = 'critical'

        meter_name = self.meter.meter_name(self.vl)
        result = self.meter.alarm_severity(self.vl, meter_name)

        self.assertEqual('critical', result)
