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

"""Test cases for collectd_ceilometer.meters.base module."""

from unittest import TestCase

import mock

from collectd_ceilometer.common.meters.base import Meter
from collectd_ceilometer.tests.mocking import patch_class


class Values(object):
    """Stub class to replace collectd.Values"""
    def __init__(self, plugin="my_plugin", _type="my_type"):
        self.plugin = plugin
        self.type = _type


class CollectdMock(object):
    """Model for the collectd class to be mocked"""
    def get_dataset(self, string):
        pass


patch_collectd = patch_class(CollectdMock)


class MetersTest(TestCase):
    """Test the meters/base.py class"""

    @patch_collectd
    def test_sample_type_gauge(self, collectd):
        # sample_type uses get_dataset()[0][1]
        collectd.get_dataset.return_value = [('value', 'gauge', )]
        meter = Meter(collectd)

        actual = meter.sample_type(Values())

        collectd.get_dataset.assert_called_once()
        self.assertEqual("gauge", actual)

    @patch_collectd
    def test_sample_type_derive(self, collectd):
        # sample_type uses get_dataset()[0][1]
        collectd.get_dataset.return_value = [('value', 'derive', )]
        meter = Meter(collectd)

        actual = meter.sample_type(Values())

        collectd.get_dataset.assert_called_once()
        self.assertEqual("delta", actual)

    @patch_collectd
    def test_sample_type_absolute(self, collectd):
        # sample_type uses get_dataset()[0][1]
        collectd.get_dataset.return_value = [('value', 'absolute', )]
        meter = Meter(collectd)

        actual = meter.sample_type(Values())

        collectd.get_dataset.assert_called_once()
        self.assertEqual("cumulative", actual)

    @patch_collectd
    def test_sample_type_counter(self, collectd):
        # sample_type uses get_dataset()[0][1]
        collectd.get_dataset.return_value = [('value', 'counter', )]
        meter = Meter(collectd)

        actual = meter.sample_type(Values())

        collectd.get_dataset.assert_called_once()
        self.assertEqual("cumulative", actual)

    @mock.patch('collectd_ceilometer.common.meters.base.LOGGER')
    @patch_collectd
    def test_sample_type_invalid(self, collectd, LOGGER):
        collectd.get_dataset.side_effect = Exception("Boom!")
        meter = Meter(collectd)

        actual = meter.sample_type(Values())

        collectd.get_dataset.assert_called_once()
        LOGGER.warning.assert_called_once()
        self.assertEqual("gauge", actual)
