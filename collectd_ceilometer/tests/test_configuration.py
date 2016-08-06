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

import abc
import unittest

import mock
import six

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
        self.assertEqual('qemu:///system', configuration.LIBVIRT_CONN_URI)

    def test_all_attributes(self):
        self.assertEqual(
            dict(BATCH_SIZE=Configuration.BATCH_SIZE,
                 CEILOMETER_URL_TYPE=Configuration.CEILOMETER_URL_TYPE,
                 CEILOMETER_TIMEOUT=Configuration.CEILOMETER_TIMEOUT,
                 OS_AUTH_URL=Configuration.OS_AUTH_URL,
                 OS_USERNAME=Configuration.OS_USERNAME,
                 OS_PASSWORD=Configuration.OS_PASSWORD,
                 OS_TENANT_NAME=Configuration.OS_TENANT_NAME,
                 VERBOSE=Configuration.VERBOSE,
                 UNITS=Configuration.UNITS,
                 LIBVIRT_CONN_URI=Configuration.LIBVIRT_CONN_URI),
            dict(Configuration.all_attributes()))

    def test_read_collectd_configuration(self):
        configuration = Configuration()
        collectd_congiguration = config_module(
            BATCH_SIZE='2',
            CEILOMETER_URL_TYPE='<some_url_type>',
            CEILOMETER_TIMEOUT=10,
            OS_AUTH_URL='<some_url>',
            OS_USERNAME='<some_user>',
            OS_PASSWORD='<some_password>',
            OS_TENANT_NAME='<some_tenant>',
            LIBVIRT_CONN_URI='<some_url>',
            VERBOSE='1')

        configuration.read_collectd_configuration(collectd_congiguration)

        self.maxDiff = 100000

        self.assertEqual(
            {Configuration.BATCH_SIZE: 2,
             Configuration.CEILOMETER_URL_TYPE: '<some_url_type>',
             Configuration.CEILOMETER_TIMEOUT: 10,
             Configuration.OS_AUTH_URL: '<some_url>',
             Configuration.OS_USERNAME: '<some_user>',
             Configuration.OS_PASSWORD: '<some_password>',
             Configuration.OS_TENANT_NAME: '<some_tenant>',
             Configuration.LIBVIRT_CONN_URI: '<some_url>',
             Configuration.VERBOSE: True,
             Configuration.UNITS: UNITS},
            configuration.attributes)
        self.assertEqual(2, configuration.BATCH_SIZE)
        self.assertEqual(10, configuration.CEILOMETER_TIMEOUT)
        self.assertEqual('<some_url>', configuration.OS_AUTH_URL)
        self.assertEqual('<some_user>', configuration.OS_USERNAME)
        self.assertEqual('<some_password>', configuration.OS_PASSWORD)
        self.assertEqual('<some_tenant>', configuration.OS_TENANT_NAME)
        self.assertTrue(configuration.VERBOSE)
        self.assertEqual(UNITS, configuration.UNITS)
        self.assertEqual('<some_url>', configuration.LIBVIRT_CONN_URI)

    def test_read_collectd_configuration_with_units(self):
        units = {'lenght': 'm', 'mass': 'g'}
        configuration = Configuration()
        collectd_congiguration = config_module(
            OS_AUTH_URL='<some_url>',
            OS_USERNAME='<some_user>',
            OS_PASSWORD='<some_password>',
            OS_TENANT_NAME='<some_tenant>',
            units=units)

        configuration.read_collectd_configuration(collectd_congiguration)

        self.maxDiff = 100000

        expected_units = dict(UNITS)
        expected_units.update(units)
        self.assertEqual(
            {Configuration.OS_AUTH_URL: '<some_url>',
             Configuration.OS_USERNAME: '<some_user>',
             Configuration.OS_PASSWORD: '<some_password>',
             Configuration.OS_TENANT_NAME: '<some_tenant>',
             Configuration.UNITS: expected_units},
            configuration.attributes)
        self.assertEqual('<some_url>', configuration.OS_AUTH_URL)
        self.assertEqual('<some_user>', configuration.OS_USERNAME)
        self.assertEqual('<some_password>', configuration.OS_PASSWORD)
        self.assertEqual('<some_tenant>', configuration.OS_TENANT_NAME)
        self.assertEqual(expected_units, configuration.UNITS)


class MockCollecdConfig(object):

    @abc.abstractproperty
    def parent(self):
        pass

    @abc.abstractproperty
    def children(self):
        pass

    @abc.abstractproperty
    def key(self):
        pass

    @abc.abstractproperty
    def value(self):
        pass


def config_module(
        module_name="collectd_ceilometer.plugin", units=None, **values):
    children = [
        config_value(key, value)
        for key, value in six.iteritems(values)]
    if units:
        children.append(config_units(**units))
    return config_node('MODULE', module_name, *children)


def config_units(**units):
    children = [
        config_value('UNIT', key, value)
        for key, value in six.iteritems(units)]
    return config_node('UNITS', None, *children)


def config_node(key, value, *children):
    node = mock.MagicMock(
        spec=MockCollecdConfig, parent=None, children=children, key=key,
        values=(value,))
    for child in children:
        child.parent = node
    return node


def config_value(key, *values):
    return mock.MagicMock(
        spec=MockCollecdConfig, parent=None, children=tuple(), key=key,
        values=values)
