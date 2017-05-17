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

import abc
from unittest import TestCase

import mock
import six

from collectd_ceilometer.common import settings


def config_module(
        values, units=None, severities=None,
        module_name="collectd_ceilometer.ceilometer.plugin"):
    children = [config_value(key, value)
                for key, value in six.iteritems(values)]
    if units:
        children.append(config_units(units))
    elif severities:
        children.append(config_severities(severities))
    return config_node('MODULE', children=children, value=module_name)


def config_units(units):
    children = [config_value('UNIT', key, value)
                for key, value in six.iteritems(units)]
    return config_node('UNITS', children)


def config_severities(severities):
    children = [config_value('ALARM_SEVERITY', key, value)
                for key, value in six.iteritems(severities)]
    return config_node('ALARM_SEVERITIES', children)


def config_node(key, children, value=None):
    "Create a mocked collectd config node having given children and value"
    return mock.create_autospec(
        spec=MockCollectdConfig, spec_set=True, instance=True,
        children=tuple(children), key=key, values=(value,))


def config_value(key, *values):
    "Create a mocked collectd config node having given multiple values"
    return mock.create_autospec(
        spec=MockCollectdConfig, spec_set=True, instance=True,
        children=tuple(), key=key, values=values)


class MockCollectdConfig(object):

    @abc.abstractproperty
    def children(self):
        pass

    @abc.abstractproperty
    def key(self):
        pass

    @abc.abstractproperty
    def values(self):
        pass


class TestConfig(TestCase):
    """Test configuration reader"""

    @property
    def default_values(self):
        return dict(
            BATCH_SIZE=1,
            OS_AUTH_URL='https://test-auth.url.tld/test',
            CEILOMETER_URL_TYPE='internalURL',
            CEILOMETER_TIMEOUT=1000,
            OS_USERNAME='tester',
            OS_PASSWORD='testpasswd',
            OS_TENANT_NAME='service')

    @mock.patch.object(settings, 'LOGGER', autospec=True)
    def test_default_configuration(self, LOGGER):
        """Test valid configuration"""

        node = config_module(values=self.default_values)
        config = settings.Config._decorated()

        # read default configuration
        config.read(node)

        # compare the configuration values with the default values
        for key, value in six.iteritems(self.default_values):
            self.assertEqual(value, getattr(config, key))

        # test configuration change
        self.assertEqual(1, config.BATCH_SIZE)
        config.read(config_module(values=dict(BATCH_SIZE=10)))
        self.assertEqual(10, config.BATCH_SIZE)
        LOGGER.error.assert_not_called()

    def test_singleton(self):
        """Test config singleton class

        Verify that the TypeError exception is raised when the instance
        of the Config class is created by user.
        """

        with self.assertRaises(TypeError) as exc:
            # must rise a TypeError as the singleton class cannot
            # be created by the user and can be accessed only
            # by its instance() method
            settings.Config()  # flake8: noqa

        self.assertEqual(
            six.text_type(exc.exception),
            'Singleton must be accessed through instance() method')

    @mock.patch.object(settings, 'LOGGER', autospec=True)
    def test_invalid_value(self, LOGGER):
        """Test invalid value

        Test string instead of int
        """
        values = self.default_values
        values["BATCH_SIZE"] = "xyz"
        node = config_module(values=values)
        config = settings.Config._decorated()

        config.read(node)

        LOGGER.error.assert_called_once_with(
            'Invalid value "xyz" for configuration parameter "BATCH_SIZE"')
        self.assertEqual(1, config.BATCH_SIZE)

    @mock.patch.object(settings, 'LOGGER', autospec=True)
    def test_unknown_parameter(self, LOGGER):
        """Test unknown parameter

        Test configuration parameter which is not known (expected)
        """
        values = self.default_values
        values["UNKNOWN"] = "xyz"
        node = config_module(values=values)
        config = settings.Config._decorated()

        config.read(node)

        LOGGER.error.assert_called_with(
            'Unknown configuration parameter "%s"', 'UNKNOWN')
        self.assertFalse(hasattr(node, 'UNKNOWN'))

    @mock.patch.object(settings, 'LOGGER', autospec=True)
    def test_missing_value(self, LOGGER):
        """Test configuration node vithout value"""

        node = config_module(values=self.default_values)
        # remove values from some node
        for child in node.children:
            if child.key == 'OS_AUTH_URL':
                child.values = tuple()
                break
        config = settings.Config._decorated()

        config.read(node)

        LOGGER.error.assert_has_calls([
            mock.call('No configuration value found for "%s"', "OS_AUTH_URL"),
            mock.call('Configuration parameter %s not set.', "OS_AUTH_URL"),
            mock.call('Collectd plugin for Ceilometer will not work properly')])

    @mock.patch.object(settings, 'LOGGER', autospec=True)
    def test_user_units(self, LOGGER):
        """Test configuration with user defined units"""

        node = config_module(
            values=self.default_values,
            units={'age': 'years',
                   'star.distance': 'LY',
                   'star.temperature': 'K'})
        config = settings.Config._decorated()

        config.read(node)

        LOGGER.error.assert_not_called()
        self.assertEqual('years', config.unit('age', None))
        self.assertEqual('LY', config.unit('star', 'distance'))
        self.assertEqual('K', config.unit('star', 'temperature'))
        self.assertEqual('None', config.unit('monty', None))
        self.assertEqual('None', config.unit('monty', 'python'))

    @mock.patch.object(settings, 'LOGGER', autospec=True)
    def test_user_units_invalid(self, LOGGER):
        """Test invalid user defined units

        The unit node contains three values (two are expected)
        """

        node = config_module(values=self.default_values,
                             units=dict(age='years'))
        # make some unit entry invalid
        for child in node.children:
            if child.key == 'UNITS':
                child.children[0].values = (1, 2, 3)
                break
        config = settings.Config._decorated()

        config.read(node)

        self.assertEqual('None', config.unit('age', None))
        LOGGER.error.assert_called_with(
            'Invalid unit configuration: unit "1" "2" "3"')

    @mock.patch.object(settings, 'LOGGER', autospec=True)
    def test_user_units_invalid_invalid_node(self, LOGGER):
        """Test invalid node with units configuration"""

        node = config_module(values=self.default_values,
                             units=dict(age='years'))
        # make some unit entry invalid
        for child in node.children:
            if child.key == 'UNITS':
                child.children[0].key = 'NOT_UNITS'
                break
        config = settings.Config._decorated()

        config.read(node)

        LOGGER.error.assert_called_with(
            'Invalid unit configuration: %s',"NOT_UNITS")
        self.assertEqual('None', config.unit('age', None))

    @mock.patch.object(settings, 'LOGGER', autospec=True)
    def test_user_severities(self, LOGGER):
        """Test if a user enters a severity for a specific meter

        Set-up: Create a node with some user defined severities
                Configure the node
        Test: Read the configured node and compare the results
              of the method to the severities configured in the node
        Expected-behaviour: Valid mapping metric names are mapped correctly
                            to severities, and invalid values return None.
        """
        node = config_module(
            values=self.default_values,
            severities={'age': 'low',
                        'star.distance': 'moderate',
                        'star.temperature': 'critical',
                        'lemons': None})
        config = settings.Config._decorated()

        config.read(node)

        LOGGER.error.assert_not_called()
        self.assertEqual('low', config.alarm_severity('age'))
        self.assertEqual('moderate', config.alarm_severity('star.distance'))
        self.assertEqual('critical', config.alarm_severity('star.temperature'))
        self.assertEqual(None, config.alarm_severity('monty'))
        self.assertEqual(None, config.alarm_severity('python'))
        self.assertEqual(None, config.alarm_severity('lemons'))

    @mock.patch.object(settings, 'LOGGER', autospec=True)
    def test_user_severities_invalid(self, LOGGER):
        """Test invalid user defined severities

        Set-up: Configure the node with one defined severity
                Set a configuration to have 3 entries instead of the 2
                which are expected
        Test: Try to read the configuration node with incorrect configurations
              Compare the configuration to the response on the method
        Expected-behaviour: alarm_severity will return None
                            Log will be written that severities were
                            incorrectly configured
        """

        node = config_module(values=self.default_values,
                             severities=dict(age='low'))
        # make some alarm severity entry invalid
        for child in node.children:
            if child.key == 'ALARM_SEVERITIES':
                child.children[0].values = (1, 2, 3)
                break
        config = settings.Config._decorated()

        config.read(node)

        self.assertEqual(None, config.alarm_severity('age'))
        LOGGER.error.assert_called_with(
            'Invalid alarm severity configuration:            \
            severity "1" "2" "3"')

    @mock.patch.object(settings, 'LOGGER', autospec=True)
    def test_user_severities_invalid_node(self, LOGGER):
        """Test invalid node with severities configuration

        Set-up: Set up a configuration node with a severity defined
                Configure the node with an incorrect module title
        Test: Read the incorrect configuration node
        Expected-behaviour: Error will be recorded in the log
                            Severity configuration will return None
        """

        node = config_module(values=self.default_values,
                             severities=dict(age='moderate'))
        # make some alarm severity entry invalid
        for child in node.children:
            if child.key == 'ALARM_SEVERITIES':
                child.children[0].key = 'NOT_SEVERITIES'
                break
        config = settings.Config._decorated()

        config.read(node)

        LOGGER.error.assert_called_with(
            'Invalid alarm severity configuration: %s', "NOT_SEVERITIES")
        self.assertEqual(None, config.alarm_severity('age'))

    @mock.patch.object(settings, 'LOGGER', autospec=True)
    def test_read_alarm_severities(self, LOGGER):
        """Test reading in user defined alarm severities method

        Set-up: Set up a node configured with a severities dictionary defined
        Test: Read the node for the ALARM_SEVERITY configuration
        Expected-behaviour: Info log will be recorded
                            Severities are correctly configured
        """
        node = config_module(values=self.default_values,
                             severities=dict(age='low'))

        for n in node.children:
            if n.key.upper() == 'ALARM_SEVERITY':
                if len(n.values) == 2:
                    key, val = n.values
                    break
        config = settings.Config._decorated()

        config._read_node(node)

        self.assertEqual('low', config.alarm_severity('age'))
        LOGGER.info.assert_called_with(
            'Got user-defined severity "%s" for "%s" alarm', "low", "age")
