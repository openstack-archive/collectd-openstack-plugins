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

import logging
import mock
import requests
import unittest

from collectd_openstack.common.keystone_light import KeystoneException
from collectd_openstack.common import sender as common_sender
from collectd_openstack.gnocchi import plugin
from collectd_openstack.gnocchi import sender as gnocchi_sender

from collectd_openstack.tests import match

Logger = logging.getLoggerClass()


def mock_collectd(**kwargs):
    "Returns collecd module with collecd logging hooks."
    return mock.patch(
        __name__ + '.' + MockedCollectd.__name__, specs=True,
        get_dataset=mock.MagicMock(side_effect=Exception), **kwargs)


class MockedCollectd(object):
    "Mocked collectd module specifications."

    def debug(self, record):
        "Hook for debug messages"

    def info(self, record):
        "Hook for info messages"

    def warning(self, record):
        "Hook for warning messages"

    def error(self, record):
        "Hook for error messages"

    def register_init(self, hook):
        "Register an hook for init."

    def register_config(self, hook):
        "Register an hook for config."

    def register_write(self, hook):
        "Register an hook for write."

    def register_shutdown(self, hook):
        "Register an hook for shutdown."

    def get_dataset(self, s):
        "Gets a dataset."


def mock_config(BATCH_SIZE=1, **kwargs):
    "Returns collecd module with collecd logging hooks."
    return mock.patch(
        __name__ + '.' + MockedConfig.__name__, specs=True,
        BATCH_SIZE=BATCH_SIZE, **kwargs)


class MockedConfig(object):
    "Mocked config class."

    BATCH_SIZE = 1


def mock_value(
        host='localhost', plugin='cpu', plugin_instance='0',
        _type='freq', type_instance=None, time=123456789, values=(1234,),
        **kwargs):
    """Create a mock value"""

    return mock.patch(
        __name__ + '.' + MockedValue.__name__, specs=True,
        host=host, plugin=plugin, plugin_instance=plugin_instance, type=_type,
        type_instance=type_instance, time=time, values=list(values), meta=None,
        **kwargs)


class MockedValue(object):
    """Value used for testing"""

    host = 'localhost'
    plugin = None
    plugin_instance = None
    type = None
    type_instance = None
    time = 123456789
    values = []
    meta = None


class TestPlugin(unittest.TestCase):
    """Test the collectd plugin"""

    @mock.patch.object(plugin, 'Plugin', autospec=True)
    @mock.patch.object(plugin, 'Config', autospec=True)
    @mock.patch.object(plugin, 'CollectdLogHandler', autospec=True)
    @mock.patch.object(plugin, 'ROOT_LOGGER', autospec=True)
    @mock_collectd()
    def test_callbacks(
            self, collectd, ROOT_LOGGER, CollectdLogHandler, Config, Plugin):
        """Verify that the callbacks are registered properly"""

        # When plugin function is called
        plugin.register_plugin(collectd=collectd)

        # Logger handler is set up
        ROOT_LOGGER.addHandler.assert_called_once_with(
            CollectdLogHandler.return_value)
        ROOT_LOGGER.setLevel.assert_called_once_with(logging.DEBUG)

        # It create a plugin
        Plugin.assert_called_once_with(
            collectd=collectd, config=Config.instance.return_value)

        # callbacks are registered to collectd
        instance = Plugin.return_value
        collectd.register_config.assert_called_once_with(instance.config)
        collectd.register_write.assert_called_once_with(instance.write)
        collectd.register_shutdown.assert_called_once_with(instance.shutdown)

    @mock.patch.object(gnocchi_sender.Sender, '_get_metric_id', autospec=True)
    @mock.patch.object(requests, 'post', spec=callable)
    @mock.patch.object(common_sender, 'ClientV3', autospec=True)
    @mock_collectd()
    @mock_config(BATCH_SIZE=2)
    @mock_value()
    def test_write(self, data, config, collectd, ClientV3, post, get_metric_id):
        """Test collectd data writing"""

        auth_client = ClientV3.return_value
        auth_client.get_service_endpoint.return_value = \
            'https://test-gnocchi.tld'

        post.return_value.status_code = common_sender.Sender.HTTP_CREATED
        post.return_value.text = 'Created'

        get_metric_id.return_value = 'my-metric-id'

        # init instance
        instance = plugin.Plugin(collectd=collectd, config=config)

        # write the first value
        instance.write(data)
        collectd.error.assert_not_called()

        # no value has been sent to ceilometer
        post.assert_not_called()

        # send the second value
        instance.write(data)
        collectd.error.assert_not_called()

        # authentication client has been created
        ClientV3.assert_called_once()

        # and values has been sent
        post.assert_called_once_with(
            'https://test-gnocchi.tld' +
            '/v1/metric/my-metric-id/measures',
            data=match.json([{
                "value": 1234,
                "timestamp": "1973-11-29T21:33:09",
                }, {
                "value": 1234,
                "timestamp": "1973-11-29T21:33:09",
                }]),
            headers={'Content-type': 'application/json',
                     'X-Auth-Token': auth_client.auth_token},
            timeout=1.0)

        # reset post method
        post.reset_mock()

        # write another values
        instance.write(data)
        collectd.error.assert_not_called()

        # nothing has been sent
        post.assert_not_called()

        # call shutdown
        instance.shutdown()

        # no errors
        collectd.error.assert_not_called()

        # previously written value has been sent
        post.assert_called_once_with(
            'https://test-gnocchi.tld' +
            '/v1/metric/my-metric-id/measures',
            data=match.json([{
                "value": 1234,
                "timestamp": "1973-11-29T21:33:09",
                }]),
            headers={
                'Content-type': 'application/json',
                'X-Auth-Token': auth_client.auth_token},
            timeout=1.0)

    @mock.patch.object(requests, 'post', spec=callable)
    @mock.patch.object(common_sender, 'ClientV3', autospec=True)
    @mock.patch.object(common_sender, 'LOGGER', autospec=True)
    @mock_collectd()
    @mock_config()
    @mock_value()
    def test_write_auth_failed(
            self, data, config, collectd, LOGGER, ClientV3, post):
        """Test authentication failure"""

        # tell the auth client to rise an exception
        ClientV3.side_effect = KeystoneException(
            "Missing name 'xxx' in received services",
            "exception",
            "services list")

        # init instance
        instance = plugin.Plugin(collectd=collectd, config=config)

        # write the value
        instance.write(data)

        LOGGER.error.assert_called_once_with(
            "Suspending error logs until successful auth")
        LOGGER.log.assert_called_once_with(
            logging.ERROR, "Authentication error: %s",
            "Missing name 'xxx' in received services\nReason: exception",
            exc_info=0)

        # no requests method has been called
        post.assert_not_called()

    @mock.patch.object(common_sender.Sender, '_perform_request', spec=callable)
    @mock.patch.object(common_sender, 'ClientV3', autospec=True)
    @mock_collectd()
    @mock_config()
    @mock_value()
    def test_request_error(
            self, data, config, collectd, ClientV3, perf_req):
        """Test error raised by underlying requests module"""

        # tell POST request to raise an exception
        perf_req.side_effect = requests.RequestException('Test POST exception')

        # ieit instance
        instance = plugin.Plugin(collectd=collectd, config=config)

        # write the value
        self.assertRaises(requests.RequestException, instance.write, data)

    @mock.patch.object(gnocchi_sender.Sender, '_get_metric_id', autospec=True)
    @mock.patch.object(requests, 'post', spec=callable)
    @mock.patch.object(common_sender, 'ClientV3', autospec=True)
    @mock_collectd()
    @mock_config()
    @mock_value()
    def test_reauthentication(self, data, config, collectd,
                              ClientV3, post, get_metric_id):
        """Test re-authentication"""
        # init instance
        instance = plugin.Plugin(collectd=collectd, config=config)

        # the sender used by the instance

        get_metric_id.return_value = 'my-metric-id'

        # response returned on success
        response_ok = requests.Response()
        response_ok.status_code = requests.codes["OK"]

        # response returned on failure
        response_unauthorized = requests.Response()
        response_unauthorized.status_code = requests.codes["UNAUTHORIZED"]

        post.return_value = response_ok

        client = ClientV3.return_value
        client.auth_token = 'Test auth token'

        # write the value
        instance.write(data)

        # verify the auth token
        post.assert_called_once_with(
            mock.ANY, data=mock.ANY,
            headers={u'Content-type': mock.ANY,
                     u'X-Auth-Token': 'Test auth token'},
            timeout=1.0)

        # POST response is unauthorized -> new token needs to be acquired
        post.side_effect = [response_unauthorized, response_ok]

        # set a new auth token
        client.auth_token = 'New test auth token'

        instance.write(data)

        # verify the auth token:
        call_list = post.call_args_list
        # POST called three times
        self.assertEqual(len(call_list), 3)

        # the second call contains the old token
        token = call_list[1][1]['headers']['X-Auth-Token']
        self.assertEqual(token, 'Test auth token')
        # the third call contains the new token
        token = call_list[2][1]['headers']['X-Auth-Token']
        self.assertEqual(token, 'New test auth token')

    @mock.patch.object(requests, 'post', spec=callable)
    @mock.patch.object(common_sender, 'ClientV3', autospec=True)
    @mock.patch.object(plugin, 'Writer', autospec=True)
    @mock.patch.object(plugin, 'LOGGER', autospec=True)
    @mock_collectd()
    @mock_config()
    @mock_value()
    def test_exception_value_error(self, data, config, collectd,
                                   LOGGER, Writer, ClientV3, post):
        """Test exception raised during write and shutdown"""

        writer = Writer.return_value
        writer.write.side_effect = ValueError('Test write error')

        # init instance
        instance = plugin.Plugin(collectd=collectd, config=config)

        self.assertRaises(ValueError, instance.write, data)

    @mock.patch.object(requests, 'post', spec=callable)
    @mock.patch.object(common_sender, 'ClientV3', autospec=True)
    @mock.patch.object(plugin, 'Writer', autospec=True)
    @mock.patch.object(plugin, 'LOGGER', autospec=True)
    @mock_collectd()
    @mock_config()
    @mock_value()
    def test_exception_runtime_error(self, data, config, collectd,
                                     LOGGER, Writer, ClientV3, post):
        """Test exception raised during write and shutdown"""

        writer = Writer.return_value
        writer.flush.side_effect = RuntimeError('Test shutdown error')

        # init instance
        instance = plugin.Plugin(collectd=collectd, config=config)

        self.assertRaises(RuntimeError, instance.shutdown)
