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

"""CollectdCeilometerPlugin tests"""

from __future__ import unicode_literals

import collections
import json

import mock
import requests

from collectd_ceilometer import collectd_ceilometer_plugin as plugin
from collectd_ceilometer import keystone_light
from collectd_ceilometer.tests import base


class PluginTest(base.TestCase):
    """Test the collectd plugin"""

    @mock.patch.object(keystone_light, 'ClientV2')
    def setUp(self, client_class):
        super(PluginTest, self).setUp()
        client_class.return_value\
            .get_service_endpoint.return_value = "https://test-ceilometer.tld"

        self.maxDiff = None

    def test_activate(self):
        """Verify that the callbacks are registered properly"""

        collectd = self.get_mock('collectd')
        plugin_instance = plugin.CollectdCeilometerPlugin.activate()
        collectd.register_init.assert_called_once_with(plugin_instance.init)
        collectd.register_config.assert_called_once_with(plugin_instance.config)
        collectd.register_write.assert_called_once_with(plugin_instance.write)
        collectd.register_shutdown.assert_called_once_with(
            plugin_instance.shutdown)

    @mock.patch.object(requests, 'post')
    def test_write(self, post):
        """Test collectd data writing"""
        from collectd_ceilometer.sender import HTTP_CREATED

        post.return_value.status_code = HTTP_CREATED
        post.return_value.text = 'Created'

        client_class \
            = self.get_mock('collectd_ceilometer.keystone_light').ClientV2
        auth_token = client_class.return_value.auth_token

        # set batch size to 2 and init instance
        self.config.update_value('BATCH_SIZE', 2)

        plugin_instance = plugin.CollectdCeilometerPlugin()
        plugin_instance.config(self.config.node)
        plugin_instance.init()

        # no authentication has been performed so far
        self.assertFalse(client_class.called)

        # create a value
        plugin_instance.write(base.Value.create())
        self.assertNoError()

        # no value has been sent to ceilometer
        post.assert_not_called()

        # send the second value
        plugin_instance.write(base.Value.create())
        self.assertNoError()

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
        plugin_instance.write(base.Value.create())
        self.assertNoError()
        # nothing has been sent
        self.assertFalse(requests.post.called)

        # call shutdown
        plugin_instance.shutdown()
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

        plugin_instance = plugin.CollectdCeilometerPlugin()
        plugin_instance.write(base.Value.create())

        # write the value
        self.assertError([
            'Exception during write: Test Client() exception'])

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
        plugin_instance = plugin.CollectdCeilometerPlugin()
        plugin_instance.config(self.config.node)
        plugin_instance.init()

        # write the value
        plugin_instance.write(base.Value.create())
        self.assertErrors([
            "Suspending error logs until successful auth",
            "Authentication error: Missing name 'xxx' in received services"
            "\nReason: exception"])

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
        plugin_instance = plugin.CollectdCeilometerPlugin()
        plugin_instance.config(self.config.node)
        plugin_instance.init()

        # write the value
        plugin_instance.write(base.Value.create())
        self.assertErrors(['Ceilometer request error: Test POST exception'])

    @mock.patch.object(requests, 'post')
    @mock.patch.object(keystone_light, 'ClientV2')
    def test_reauthentication(self, post, client_class):
        """Test re-authentication"""
        from collectd_ceilometer.sender import HTTP_UNAUTHORIZED

        client_class.return_value.auth_token = 'Test auth token'

        # init instance
        plugin_instance = plugin.CollectdCeilometerPlugin()
        plugin_instance.config(self.config.node)
        plugin_instance.init()

        # write the first value
        plugin_instance.write(base.Value.create())
        self.assertNoError()

        # verify the auth token
        post.assert_called_once_with(headers=['X-Auth-Token'])

        # subsequent call of POST method will fail due to the authentication
        post.return_value.status_code = HTTP_UNAUTHORIZED
        post.return_value.text = 'Unauthorized'
        # set a new auth token
        client_class.return_value.auth_token = 'New test auth token'

        plugin_instance.write(base.Value.create())
        self.assertNoError()

        # verify the auth token
        call_list = post.call_args_list

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
        plugin_instance = plugin.CollectdCeilometerPlugin()
        plugin_instance.config(self.config.node)
        plugin_instance.init()

        # the sender used by the instance
        sender = plugin_instance._writer._sender

        class DummyLock(
                collections.namedtuple(
                    'LockBase', ['sender', 'token', 'urlbase'])):
            """Lock simulation, which sets the auth token when locked"""

            def __enter__(self, *args, **kwargs):
                self.sender._auth_token = self.token
                self.sender._url_base = self.urlbase

            def __exit__(self, *args, **kwargs):
                pass

        # replace the sender's lock by the dummy lock
        sender._auth_lock = DummyLock(sender, 'TOKEN', 'URLBASE/%s')

        # write the value
        plugin_instance.write(base.Value.create())
        self.assertNoError()

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

        writer = mock.Mock()
        writer.flush.side_effect = Exception('Test shutdown error')
        writer.write.side_effect = Exception('Test write error')

        # init plugin instance
        plugin_instance = plugin.CollectdCeilometerPlugin()
        plugin_instance.config(self.config.node)
        plugin_instance.init()

        # pylint: disable=protected-access
        plugin_instance._writer = writer
        # pylint: enable=protected-access

        plugin_instance.write(base.Value.create())
        plugin_instance.shutdown()

        self.assertErrors([
            'Exception during write: Test write error',
            'Exception during shutdown: Test shutdown error'])
