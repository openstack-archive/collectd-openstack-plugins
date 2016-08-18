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
"""Main modules tests

"""

from collections import namedtuple
import json
import logging
import unittest

import mock
import requests

from collectd_ceilometer import keystone_light
from collectd_ceilometer import main
from collectd_ceilometer import sender

from collectd_ceilometer.tests import mocked


class TestMain(unittest.TestCase):
    """Test main entry point"""

    def test_callbacks_are_registered(self):
        """Verify that the callbacks are registered properly"""

        collectd = mocked.collectd()

        # When main function is called
        main.main(collectd)

        self.assertTrue(collectd.register_init.called)
        self.assertTrue(collectd.register_config.called)
        self.assertTrue(collectd.register_write.called)
        self.assertTrue(collectd.register_shutdown.called)


class TestPlutin(unittest.TestCase):
    """Test the collectd plugin"""

    @mock.patch('requests.post', spec=callable)
    @mock.patch.object(sender, 'ClientV2', autospec=True)
    def test_write(self, ClientV2, post):
        """Test collectd data writing"""

        auth_client = ClientV2.return_value
        auth_client.get_service_endpoint.return_value =\
            'https://test-ceilometer.tld'

        post.return_value.status_code = sender.HTTP_CREATED
        post.return_value.text = 'Created'

        # init instance
        collectd = mocked.collectd()
        config = mocked.config(BATCH_SIZE=2)
        plugin = main.Plugin(collectd=collectd, config=config)
        plugin.init()

        # no authentication has been performed so far
        ClientV2.assert_not_called()

        # create a value
        data = mocked.value()

        # write first value
        plugin.write(data)
        collectd.error.assert_not_called()

        # no value has been sent to ceilometer
        post.assert_not_called()

        # send the second value
        plugin.write(data)
        collectd.error.assert_not_called()

        # authentication client has been created
        ClientV2.assert_called_once()

        # and values has been sent
        post.assert_called_once()

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
                'X-Auth-Token': auth_client.auth_token},
            'timeout': 1.0}

        # we cannot compare JSON directly because the original data
        # dictionary is unordered
        called_kwargs = post.call_args[1]
        called_kwargs['data'] = json.loads(called_kwargs['data'])

        # verify data sent to ceilometer
        self.assertEqual(expected_args, post.call_args[0])
        self.assertEqual(expected_kwargs, called_kwargs)

        # reset post method
        post.reset_mock()

        # write another values
        plugin.write(data)
        collectd.error.assert_not_called()

        # nothing has been sent
        self.assertFalse(post.called)

        # call shutdown
        plugin.shutdown()

        # no errors
        collectd.error.assert_not_called()

        # previously written value has been sent
        post.assert_called_once()

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
                'X-Auth-Token': auth_client.auth_token},
            'timeout': 1.0}

        # we cannot compare JSON directly because the original data
        # dictionary is unordered
        called_kwargs = post.call_args[1]
        called_kwargs['data'] = json.loads(called_kwargs['data'])

        # verify data sent to ceilometer
        self.assertEqual(post.call_args[0], expected_args)
        self.assertEqual(called_kwargs, expected_kwargs)

    @mock.patch('requests.post', spec=callable)
    @mock.patch.object(sender, 'ClientV2', autospec=True)
    @mock.patch.object(main, 'LOG', autospec=True)
    def test_write_auth_failed(self, LOG, ClientV2, post):
        """Test authentication failure"""

        # tell the auth client to rise an exception
        ClientV2.side_effect = RuntimeError('Test Client() exception')

        # init instance
        collectd = mocked.collectd()
        config = mocked.config(BATCH_SIZE=1)
        plugin = main.Plugin(collectd=collectd, config=config)
        plugin.init()

        # write the value
        plugin.write(mocked.value())

        LOG.exception.assert_called_once_with('Exception during write.')

        # no requests method has been called
        post.assert_not_called()

    @mock.patch('requests.post', spec=callable)
    @mock.patch.object(sender, 'ClientV2', autospec=True)
    @mock.patch.object(sender, 'LOGGER', autospec=True)
    def test_write_auth_failed2(self, LOG, ClientV2, post):
        """Test authentication failure2"""

        ClientV2.side_effect = keystone_light.KeystoneException(
            "Missing name 'xxx' in received services",
            "exception",
            "services list")

        # init instance
        collectd = mocked.collectd()
        config = mocked.config(BATCH_SIZE=1)
        plugin = main.Plugin(collectd=collectd, config=config)
        plugin.init()

        # write the value
        plugin.write(mocked.value())

        LOG.error.assert_called_once_with(
            "Suspending error logs until successful auth")
        LOG.log.assert_called_once_with(
            logging.ERROR, "Authentication error: %s",
            "Missing name 'xxx' in received services\nReason: exception",
            exc_info=0)

        # no requests method has been called
        post.assert_not_called()

    @mock.patch('requests.post', spec=callable)
    @mock.patch.object(sender, 'ClientV2', autospec=True)
    @mock.patch.object(sender, 'LOGGER', autospec=True)
    def test_request_error(self, LOG, ClientV2, post):
        """Test error raised by underlying requests module"""

        # tell POST request to raise an exception
        post.side_effect = requests.RequestException('Test POST exception')

        # init instance
        collectd = mocked.collectd()
        config = mocked.config(BATCH_SIZE=1)
        plugin = main.Plugin(collectd=collectd, config=config)
        plugin.init()

        # write the value
        plugin.write(mocked.value())

        LOG.error.assert_called_once_with(
            "Ceilometer request error: %s", "Test POST exception")

    @mock.patch('requests.post', spec=callable)
    @mock.patch.object(sender, 'ClientV2', autospec=True)
    def test_reauthentication(self, ClientV2, post):
        """Test re-authentication"""

        client = ClientV2.return_value
        client.auth_token = 'Test auth token'

        # init instance
        collectd = mocked.collectd()
        config = mocked.config(BATCH_SIZE=1)
        plugin = main.Plugin(collectd=collectd, config=config)
        plugin.init()

        # write the value
        plugin.write(mocked.value())

        # verify the auth token
        call_list = post.call_args_list
        self.assertEqual(len(call_list), 1)
        # 0 = first call > 1 = call kwargs > headers argument > auth token
        token = call_list[0][1]['headers']['X-Auth-Token']
        self.assertEqual(token, 'Test auth token')

        # subsequent call of POST method will fail due to the authentication
        post.return_value.status_code = sender.HTTP_UNAUTHORIZED
        post.return_value.text = 'Unauthorized'
        # set a new auth token
        client.auth_token = 'New test auth token'

        # write the value
        plugin.write(mocked.value())

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

    @mock.patch.object(sender, 'requests', autospec=True)
    @mock.patch.object(sender, 'ClientV2', autospec=True)
    @mock.patch.object(main, 'LOG', autospec=True)
    def test_authentication_in_multiple_threads(self, LOG, ClientV2, requests):
        """Test authentication in muliple threads

        This test simulates the authentication performed from different thread
        after the authentication lock has been acquired. The sender is not
        authenticated, the lock is acquired, the authentication token exists
        (i.e. it has been set by different thread) and it is used.
        """
        # pylint: disable=protected-access

        # init instance
        collectd = mocked.collectd()
        config = mocked.config(BATCH_SIZE=1)
        plugin = main.Plugin(collectd=collectd, config=config)
        plugin.init()

        # the sender used by the instance
        sender = plugin._writer._sender

        class DummyLock(namedtuple('LockBase', ['sender', 'token', 'urlbase'])):
            """Lock simulation, which sets the auth token when locked"""

            def __enter__(self, *args, **kwargs):
                # pylint: disable=protected-access
                self.sender._auth_token = self.token
                self.sender._url_base = self.urlbase

            def __exit__(self, *args, **kwargs):
                pass

        # replace the sender's lock by the dummy lock
        sender._auth_lock = DummyLock(sender, 'TOKEN', 'URLBASE/%s')

        # write the value
        plugin.write(mocked.value())

        # No errors has been registered
        LOG.exception.assert_not_called()

        # client has not been called at all
        ClientV2.assert_not_called()

        # verify the auth token
        requests.post.assert_called_once()

#         # 0 = first call > 1 = call kwargs > headers argument > auth token
#         token = post.call_args_list[0][1]['headers']['X-Auth-Token']
#         self.assertEqual(token, 'TOKEN')

    @mock.patch('requests.post', spec=callable)
    @mock.patch.object(sender, 'ClientV2', autospec=True)
    @mock.patch.object(main, 'Writer', autospec=True)
    @mock.patch.object(main, 'LOG', autospec=True)
    def test_exceptions(self, LOG, Writer, ClientV2, post):
        """Test exception raised during write and shutdown"""

        writer = Writer.return_value
        writer.flush.side_effect = Exception('Test shutdown error')
        writer.write.side_effect = Exception('Test write error')

        # init instance
        collectd = mocked.collectd()
        config = mocked.config(BATCH_SIZE=1)
        plugin = main.Plugin(collectd=collectd, config=config)
        plugin.init()

        plugin.write(mocked.value())
        plugin.shutdown()

        LOG.exception.assert_has_calls(
            [mock.call('Exception during write.'),
             mock.call('Exception during shutdown.')])
