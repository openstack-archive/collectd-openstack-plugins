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
"""Configuration tests"""

from __future__ import unicode_literals

from collectd_ceilometer.tests.base import TestCase
from collectd_ceilometer.settings import Config
import mock
import six

class TestConfig(TestCase):
    """Test configuration reader"""

    def setUp(self):
        """Initialization"""

        super(TestConfig, self).setUp()

        self.config_class = Config

    @mock.patch('collectd_ceilometer.settings.LOGGER')
    def test_default_configuration(self, mock_log):
        """Test valid configuration"""
        cfg = self.config_class._decorated()

        # read default configuration
        cfg.read(self.config.node)

        # compare the configuration values with the default values
        for key in self.config.default_values.keys():
            self.assertEqual(getattr(cfg, key),
                             self.config.default_values[key])

        # test configuration change
        self.assertEqual(cfg.BATCH_SIZE, 1)
        self.config.update_value('BATCH_SIZE', 10)
        cfg.read(self.config.node)
        self.assertEqual(cfg.BATCH_SIZE, 10)
        mock_log.error.assert_not_called()

    def test_singleton(self):
        """Test config singleton class

        Verify that the TypeError exception is raised when the instance
        of the Config class is created by user.
        """
        # pylint: disable=invalid-name,unused-variable

        Config = self.config_class

        with self.assertRaises(TypeError) as exc:
            # must rise a TypeError as the singleton class cannot
            # be created by the user and can be accessed only
            # by its instance() method
            new_cfg = Config()  # flake8: noqa

        self.assertEqual(
            six.text_type(exc.exception),
            'Singleton must be accessed through instance() method')

    @mock.patch('collectd_ceilometer.settings.LOGGER')
    def test_invalid_value(self, mock_log):
        """Test invalid value

        Test string instead of int
        """
        cfg = self.config_class._decorated()
        self.config.update_value('BATCH_SIZE', 'xyz')
        cfg.read(self.config.node)
        self.assertEqual(cfg.BATCH_SIZE, 1)
        mock_log.error.assert_called_with(
            'Invalid value "xyz" for configuration parameter "BATCH_SIZE"')

    @mock.patch('collectd_ceilometer.settings.LOGGER')
    def test_unknown_parameter(self, mock_log):
        """Test unknown parameter

        Test configuration parameter which is not known (expected)"""

        cfg = self.config_class._decorated()
        self.config.update_value('UNKNOWN', 'xyz')
        cfg.read(self.config.node)
        self.assertFalse(hasattr(cfg, 'UNKNOWN'))
        mock_log.error.assert_called_with('Unknown configuration parameter "%s"', 'UNKNOWN')

    @mock.patch('collectd_ceilometer.settings.LOGGER')
    def test_missing_value(self, mock_log):
        """Test configuration node vithout value"""

        cfg = self.config_class._decorated()

        # remove values from some node
        node = self.config.node
        first = node.children[1]
        self.assertEqual(first.key, 'OS_AUTH_URL')
        first.values = []

        cfg.read(node)

        mock_log.error.assert_any_call(
            'No configuration value found for "%s"', "OS_AUTH_URL")
        mock_log.error.assert_any_call(
            'Configuration parameter %s not set.', "OS_AUTH_URL")
        mock_log.error.assert_any_call(
            'Collectd plugin for Ceilometer will not work properly')

    @mock.patch('collectd_ceilometer.settings.LOGGER')
    def test_user_units(self, mock_log):
        """Test configuration with user defined units"""
        self.config.add_unit('age', 'years')
        self.config.add_unit('star.distance', 'LY')
        self.config.add_unit('star.temperature', 'K')

        cfg = self.config_class._decorated()
        cfg.read(self.config.node)
        mock_log.error.assert_not_called()

        self.assertEqual(cfg.unit('age', None), 'years')
        self.assertEqual(cfg.unit('star', 'distance'), 'LY')
        self.assertEqual(cfg.unit('star', 'temperature'), 'K')
        self.assertEqual(cfg.unit('monty', None), 'None')
        self.assertEqual(cfg.unit('monty', 'python'), 'None')

    @mock.patch('collectd_ceilometer.settings.LOGGER')
    def test_user_units_invalid(self, mock_log):
        """Test invalid user defined units

        The unit node contains three values (two are expected)
        """

        self.config.add_unit('age', 'years')

        node = self.config.node
        unit = node.children[-1].children[0]
        unit.values = [1, 2, 3]

        cfg = self.config_class._decorated()
        cfg.read(node)

        mock_log.error.assert_called_with(
            'Invalid unit configuration: unit "1" "2" "3"')
        self.assertEqual(cfg.unit('age', None), 'None')

    @mock.patch('collectd_ceilometer.settings.LOGGER')
    def test_user_units_invalid_invalid_node(self, mock_log):
        """Test invalid node with units configuration"""

        self.config.add_unit('age', 'years')

        node = self.config.node
        unit = node.children[-1].children[0]
        unit.key = 'NOT_UNITS'

        cfg = self.config_class._decorated()
        cfg.read(node)

        mock_log.error.assert_called_with(
            'Invalid unit configuration: %s',"NOT_UNITS")
        self.assertEqual(cfg.unit('age', None), 'None')
