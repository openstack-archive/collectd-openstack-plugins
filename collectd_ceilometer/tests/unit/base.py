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
"""Unittest tools"""

from __future__ import unicode_literals

from collectd_ceilometer.keystone_light import KeystoneException
from collections import OrderedDict
import logging
from mock import Mock
from mock import patch
import six
import unittest


class Value(object):
    """Value used for testing"""

    def __init__(self):
        self.host = 'localhost'
        self.plugin = None
        self.plugin_instance = None
        self.type = None
        self.type_instance = None
        self.time = 123456789
        self.values = []
        self.meta = None

    def add_value(self, value):
        """Add value"""
        self.values.append(value)


class TestConfig(object):
    """Test configuration"""

    default_values = OrderedDict([
        ('BATCH_SIZE', 1,),
        ('OS_AUTH_URL', 'https://test-auth.url.tld/test',),
        ('CEILOMETER_URL_TYPE', 'internalURL',),
        ('CEILOMETER_TIMEOUT', 1000,),
        ('OS_USERNAME', 'tester',),
        ('OS_PASSWORD', 'testpasswd',),
        ('OS_TENANT_NAME', 'service',),
    ])

    def __init__(self):
        self._values = self.default_values.copy()
        self._units = {}

    def update_value(self, key, value):
        """Update the configuration value

        @param key      configuration key
        @param value    configuration value
        """
        self._values.update({key: value})

    def add_unit(self, name, unit):
        """Add user defined unit

        @param name     name of the plugin
        @param unit     unit name
        """
        self._units.update({name: unit})

    @property
    def node(self):
        """Return the master node of current configuration

        Return the configuration node in format readable by config singleton.
        """
        nodes = [self._Node(key=key, values=[val])
                 for key, val in six.iteritems(self._values)]
        units = [self._Node(key='UNIT', values=[key, val])
                 for key, val in six.iteritems(self._units)]
        if units:
            nodes.append(self._Node(key='UNITS', children=units))
        return self._Node(key='MODULE', children=nodes)

    class _Node(object):
        """Test configuration node"""

        def __init__(self, children=None, key=None, values=None):
            """Create the node

            @param children     list of children nodes
            @param key          configuration key
            @param value        configuration value
            """

            if children is None:
                children = []
            if values is None:
                values = []

            self.children = children
            self.key = key
            self.values = values


class TestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        """Declare additional class attributes"""
        super(TestCase, self).__init__(*args, **kwargs)
        self._patchset = None
        self._mocked = {}

    def get_mock(self, module):
        """Get module mock"""
        return self._mocked.get(module)

    def setUp(self):
        """Mock collectd module"""

        super(TestCase, self).setUp()

        modules = ['collectd', 'libvirt', 'requests',
                   'collectd_ceilometer.keystone_light']

        self._mocked = {module: Mock() for module in modules}

        # requests
        requests = self.get_mock('requests')
        requests.exceptions.RequestException = Exception
        self._mocked.update({'requests.exceptions': requests.exceptions})

        keystone = self.get_mock('collectd_ceilometer.keystone_light')
        keystone.KeystoneException = KeystoneException
        self._mocked.update(
            {'collectd_ceilometer.keystone_light.KeystoneException':
             keystone.KeystoneException})

        self._patchset = patch.dict('sys.modules', self._mocked)
        self._patchset.start()

        self.config = TestConfig()

        logging.getLogger().handlers = []

    def tearDown(self):
        """Clean up"""
        self._patchset.stop()

    def assertNoError(self):
        """Assert no error has been logged"""
        collectd = self.get_mock('collectd')
        self.assertFalse(collectd.error.called, [collectd.error.call_args_list])

    def assertError(self, msg):
        """Assert an error has been logged"""

        collectd = self.get_mock('collectd')
        self.assertTrue(collectd.error.called,
                        'Error "%s" expected but not logged' % msg)
        self.assertIn(((msg,),), collectd.error.call_args_list)

    def assertErrors(self, errors):
        """Assert the list of logged errors"""

        collectd = self.get_mock('collectd')
        self.assertTrue(collectd.error.called, 'Errors expected but not logged')
        expected = [((i,),) for i in errors]
        self.assertEqual(expected, collectd.error.call_args_list)
