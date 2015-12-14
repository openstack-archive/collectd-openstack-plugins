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

from collectd_ceilometer.tests.base import TestCase
from collectd_ceilometer.tests.base import Value
from collections import namedtuple
import json
import mock


class PluginTest(TestCase):
    """Test the collectd plugin"""

    def setUp(self):
        super(PluginTest, self).setUp()
        client_class \
            = self.get_mock('collectd_ceilometer.keystone_light').ClientV2
        client_class.return_value\
            .get_service_endpoint.return_value = "https://test-ceilometer.tld"

        # TODO(emma-l-foley): Import at top and mock here
        from collectd_ceilometer.plugin import instance
        from collectd_ceilometer.plugin import Plugin
        self.default_instance = instance
        self.plugin_instance = Plugin()
        self.maxDiff = None

    def test_callbacks(self):
        """Verify that the callbacks are registered properly"""

        collectd = self.get_mock('collectd')

        self.assertTrue(collectd.register_init.called)
        self.assertTrue(collectd.register_config.called)
        self.assertTrue(collectd.register_write.called)
        self.assertTrue(collectd.register_shutdown.called)

    def test_write(self):
        """Test collectd data writing"""
        from collectd_ceilometer.sender import HTTP_CREATED

        requests = self.get_mock('requests')
        requests.post.return_value.status_code = HTTP_CREATED
        requests.post.return_value.text = 'Created'

        client_class \
            = self.get_mock('collectd_ceilometer.keystone_light').ClientV2
        auth_token = client_class.return_value.auth_token

        # create a value
        data = self._create_value()

        # set batch size to 2 and init instance
        self.config.update_value('BATCH_SIZE', 2)
        self._init_instance()

        # no authentication has been performed so far
        self.assertFalse(client_class.called)

        # write first value
        self._write_value(data)

        # no value has been sent to ceilometer
        self.assertFalse(requests.post.called)

        # send the second value
        self._write_value(data)

        # authentication client has been created
        self.assertTrue(client_class.called)
        self.assertEqual(client_class.call_count, 1)
        # and values has been sent
        self.assertTrue(requests.post.called)
        self.assertEqual(requests.post.call_count, 1)

        expected_args = ('https://test-ceilometer.tld/v2/meters/cpu.freq',)
        expected_kwargs = {
            'data': [{
                "source": "collectd",
                "counter_name": "cpu.freq",
                "counter_unit": "jiffies",
                "counter_volume": 1234,
                "timestamp": "Thu Nov 29 21:33:09 1973",
                "resource_id": "localhost-0",
                "resource_metadata": None,
                "counter_type": "gauge"
            }, {
                "source": "collectd",
                "counter_name": "cpu.freq",
                "counter_unit": "jiffies",
                "counter_volume": 1234,
                "timestamp": "Thu Nov 29 21:33:09 1973",
                "resource_id": "localhost-0",
                "resource_metadata": None,
                "counter_type": "gauge"}],
            'headers': {
                'Content-type': u'application/json',
                'X-Auth-Token': auth_token},
            'timeout': 1.0}

        # we cannot compare JSON directly because the original data
        # dictionary is unordered
        called_kwargs = requests.post.call_args[1]
        called_kwargs['data'] = json.loads(called_kwargs['data'])

        # verify data sent to ceilometer
        self.assertEqual(requests.post.call_args[0], expected_args)
        self.assertEqual(called_kwargs, expected_kwargs)

        # reset post method
        requests.post.reset_mock()

        # write another values
        self._write_value(data)
        # nothing has been sent
        self.assertFalse(requests.post.called)

        # call shutdown
        self.plugin_instance.shutdown()
        self.assertNoError()
        # previously written value has been sent
        self.assertTrue(requests.post.called)
        # no more authentication required
        self.assertEqual(client_class.call_count, 1)

        expected_kwargs = {
            'data': [{
                "source": "collectd",
                "counter_name": "cpu.freq",
                "counter_unit": "jiffies",
                "counter_volume": 1234,
                "timestamp": "Thu Nov 29 21:33:09 1973",
                "resource_id": "localhost-0",
                "resource_metadata": None,
                "counter_type": "gauge"}],
            'headers': {
                'Content-type': u'application/json',
                'X-Auth-Token': auth_token},
            'timeout': 1.0}

        # we cannot compare JSON directly because the original data
        # dictionary is unordered
        called_kwargs = requests.post.call_args[1]
        called_kwargs['data'] = json.loads(called_kwargs['data'])

        # verify data sent to ceilometer
        self.assertEqual(requests.post.call_args[0], expected_args)
        self.assertEqual(called_kwargs, expected_kwargs)

    def test_write_auth_failed(self):
        """Test authentication failure"""

        # tell the auth client to rise an exception
        client_class \
            = self.get_mock('collectd_ceilometer.keystone_light').ClientV2
        client_class.side_effect = Exception('Test Client() exception')

        # init instance
        self._init_instance()

        # write the value
        errors = [
            'Exception during write: Test Client() exception']
        self._write_value(self._create_value(), errors)

        # no requests method has been called
        self.assertFalse(self.get_mock('requests').post.called,
                         "requests method has been called")

    def test_write_auth_failed2(self):
        """Test authentication failure2"""

        # tell the auth client to rise an exception
        keystone \
            = self.get_mock('collectd_ceilometer.keystone_light')

        client_class = keystone.ClientV2
        client_class.side_effect = keystone.KeystoneException(
            "Missing name 'xxx' in received services",
            "exception",
            "services list")

        # init instance
        self._init_instance()

        # write the value
        errors = [
            "Suspending error logs until successful auth",
            "Authentication error: Missing name 'xxx' in received services"
            "\nReason: exception"]
        self._write_value(self._create_value(), errors)

        # no requests method has been called
        self.assertFalse(self.get_mock('requests').post.called,
                         "requests method has been called")

    def test_request_error(self):
        """Test error raised by underlying requests module"""

        # we have to import the RequestException here as it has been mocked
        from requests.exceptions import RequestException

        # tell POST request to raise an exception
        requests = self.get_mock('requests')
        requests.post.side_effect = RequestException('Test POST exception')

        # init instance
        self._init_instance()

        # write the value
        self._write_value(
            self._create_value(),
            ['Ceilometer request error: Test POST exception'])

    def test_reauthentication(self):
        """Test re-authentication"""
        from collectd_ceilometer.sender import HTTP_UNAUTHORIZED

        requests = self.get_mock('requests')
        client_class \
            = self.get_mock('collectd_ceilometer.keystone_light').ClientV2
        client_class.return_value.auth_token = 'Test auth token'

        # init instance
        self._init_instance()

        # write the first value
        self._write_value(self._create_value())

        # verify the auth token
        call_list = requests.post.call_args_list
        self.assertEqual(len(call_list), 1)
        # 0 = first call > 1 = call kwargs > headers argument > auth token
        token = call_list[0][1]['headers']['X-Auth-Token']
        self.assertEqual(token, 'Test auth token')

        # subsequent call of POST method will fail due to the authentication
        requests.post.return_value.status_code = HTTP_UNAUTHORIZED
        requests.post.return_value.text = 'Unauthorized'
        # set a new auth token
        client_class.return_value.auth_token = 'New test auth token'

        self._write_value(self._create_value())

        # verify the auth token
        call_list = requests.post.call_args_list

        # POST called three times
        self.assertEqual(len(call_list), 3)
        # the second call contains the old token
        token = call_list[1][1]['headers']['X-Auth-Token']
        self.assertEqual(token, 'Test auth token')
        # the third call contains the new token
        token = call_list[2][1]['headers']['X-Auth-Token']
        self.assertEqual(token, 'New test auth token')

    def test_authentication_in_multiple_threads(self):
        """Test authentication in muliple threads

        This test simulates the authentication performed from different thread
        after the authentication lock has been acquired. The sender is not
        authenticated, the lock is acquired, the authentication token exists
        (i.e. it has been set by different thread) and it is used.
        """
        # pylint: disable=protected-access

        # init plugin instance
        self._init_instance()

        # the sender used by the instance
        sender = self.plugin_instance._writer._sender

        # create a dummy lock
        class DummyLock(namedtuple('LockBase', ['sender', 'token', 'urlbase'])):
            """Lock simulation, which sets the auth token when locked"""

            def __enter__(self, *args, **kwargs):
                self.sender._auth_token = self.token
                self.sender._url_base = self.urlbase

            def __exit__(self, *args, **kwargs):
                pass

        # replace the sender's lock by the dummy lock
        sender._auth_lock = DummyLock(sender, 'TOKEN', 'URLBASE/%s')

        # write the value
        self._write_value(self._create_value())

        # verify the results
        requests = self.get_mock('requests')
        client_class \
            = self.get_mock('collectd_ceilometer.keystone_light').ClientV2

        # client has not been called at all
        self.assertFalse(client_class.called)

        # verify the auth token
        call_list = requests.post.call_args_list
        self.assertEqual(len(call_list), 1)
        # 0 = first call > 1 = call kwargs > headers argument > auth token
        token = call_list[0][1]['headers']['X-Auth-Token']
        self.assertEqual(token, 'TOKEN')

    def test_exceptions(self):
        """Test exception raised during write and shutdown"""

        self._init_instance()

        writer = mock.Mock()
        writer.flush.side_effect = Exception('Test shutdown error')
        writer.write.side_effect = Exception('Test write error')

        # pylint: disable=protected-access
        self.plugin_instance._writer = writer
        # pylint: enable=protected-access

        self.plugin_instance.write(self._create_value())
        self.plugin_instance.shutdown()

        self.assertErrors([
            'Exception during write: Test write error',
            'Exception during shutdown: Test shutdown error'])

    @staticmethod
    def _create_value():
        """Create a value"""
        retval = Value()
        retval.plugin = 'cpu'
        retval.plugin_instance = '0'
        retval.type = 'freq'
        retval.add_value(1234)
        return retval

    def _init_instance(self):
        """Init current plugin instance"""
        self.plugin_instance.config(self.config.node)
        self.plugin_instance.init()

    def _write_value(self, value, errors=None):
        """Write a value and verify result"""
        self.plugin_instance.write(value)
        if errors is None:
            self.assertNoError()
        else:
            self.assertErrors(errors)
