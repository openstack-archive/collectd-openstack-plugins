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

"""Plugin tests."""

import logging
import mock
import requests
import unittest

from collectd_ceilometer.aodh import plugin
from collectd_ceilometer.aodh import sender
from collectd_ceilometer.common.keystone_light import KeystoneException
from collectd_ceilometer.common.meters import base

Logger = logging.getLoggerClass()


def mock_collectd(**kwargs):
    """Return collecd module with collecd logging hooks."""
    return mock.patch(
        __name__ + '.' + MockedCollectd.__name__, specs=True,
        get_dataset=mock.MagicMock(side_effect=Exception),
        get=mock.MagicMock(), **kwargs)


class MockedCollectd(object):
    """Mocked collectd module specifications."""

    def debug(self, record):
        """Hook for debug messages."""

    def info(self, record):
        """Hook for info messages."""

    def warning(self, record):
        """Hook for warning messages."""

    def error(self, record):
        """Hook for error messages."""

    def register_init(self, hook):
        """Register an hook for init."""

    def register_config(self, hook):
        """Register an hook for config."""

    def register_notification(self, hook):
        """Register an hook for notification."""

    def register_shutdown(self, hook):
        """Register an hook for shutdown."""

    def get_dataset(self, s):
        """Get a dataset."""

    def get(self):
        """Get notification severity."""


def mock_config(**kwargs):
    """Return collecd module with collecd logging hooks."""
    return mock.patch(
        __name__ + '.' + MockedConfig.__name__, specs=True,
        **kwargs)


class MockedConfig(object):
    """Mocked config class."""


def mock_value(
        host='localhost', plugin='cpu', plugin_instance='0',
        _type='freq', type_instance=None, time=123456789,
        values=(1234,), **kwargs):
    """Create a mock value."""
    return mock.patch(
        __name__ + '.' + MockedValue.__name__, specs=True,
        host=host, plugin=plugin, plugin_instance=plugin_instance, type=_type,
        type_instance=type_instance, time=time,
        values=list(values), meta=None, **kwargs)


class MockedValue(object):
    """Value used for testing."""

    host = 'localhost'
    plugin = None
    plugin_instance = None
    type = None
    type_instance = None
    time = 123456789
    values = []
    meta = None


class TestPlugin(unittest.TestCase):
    """Test the collectd plugin."""

    @mock.patch.object(plugin, 'Plugin', autospec=True)
    @mock.patch.object(plugin, 'Config', autospec=True)
    @mock.patch.object(plugin, 'CollectdLogHandler', autospec=True)
    @mock.patch.object(plugin, 'ROOT_LOGGER', autospec=True)
    @mock_collectd()
    def test_callbacks(
            self, collectd, ROOT_LOGGER, CollectdLogHandler, Config, Plugin):
        """Verify that the callbacks are registered properly."""
        # When plugin function is called
        plugin.register_plugin(collectd=collectd)

        # Logger handler is set up
        ROOT_LOGGER.addHandler.assert_called_once_with(
            CollectdLogHandler.return_value)
        ROOT_LOGGER.setLevel.assert_called_once_with(logging.NOTSET)

        # It creates a plugin
        Plugin.assert_called_once_with(
            collectd=collectd, config=Config.instance.return_value)

        # callbacks are registered to collectd
        instance = Plugin.return_value
        collectd.register_config.assert_called_once_with(instance.config)
        collectd.register_notification.assert_called_once_with(instance.notify)
        collectd.register_shutdown.assert_called_once_with(instance.shutdown)

    @mock.patch.object(sender.Sender, '_get_alarm_id', autospec=True)
    @mock.patch.object(requests, 'put', spec=callable)
    @mock.patch.object(sender, 'ClientV3', autospec=True)
    @mock_collectd()
    @mock_config()
    @mock_value()
    def test_notify(self, data, config, collectd, ClientV3, put,
                    _get_alarm_id):
        """Test collectd data notifying."""
        auth_client = ClientV3.return_value
        auth_client.get_service_endpoint.return_value = \
            'https://test-aodh.tld'

        put.return_value.status_code = sender.HTTP_CREATED
        put.return_value.text = 'Updated'

        # Test when the value doesn't get updated
        _get_alarm_id.return_value = None

        # init instance
        instance = plugin.Plugin(collectd=collectd, config=config)

        # send the value(doesn't update)
        instance.notify(data)
        collectd.error.assert_not_called()

        put.assert_not_called()

        # Test when an alarm will be updated
        _get_alarm_id.return_value = 'my-alarm-id'

        # send the value(updates)
        instance.notify(data)
        collectd.error.assert_not_called()

        # authentication client that has been created
        ClientV3.assert_called_once()

        # and values that have been sent
        put.assert_called_once_with(
            'https://test-aodh.tld' +
            '/v2/alarms/my-alarm-id/state',
            data='"insufficient data"',
            headers={'Content-type': 'application/json',
                     'X-Auth-Token': auth_client.auth_token},
            timeout=1.0)

        # reset post method
        put.reset_mock()

        # call shutdown
        instance.shutdown()

    @mock.patch.object(sender.Sender, '_get_alarm_id', autospec=True)
    @mock.patch.object(sender.Sender, '_update_alarm', autospec=True)
    @mock.patch.object(base.Meter, 'message', autospec=True)
    @mock.patch.object(base.Meter, 'meter_name', autospec=True)
    @mock.patch.object(base.Meter, 'severity', autospec=True)
    @mock.patch.object(base.Meter, 'resource_id', autospec=True)
    @mock.patch.object(sender, 'ClientV3', autospec=True)
    @mock_collectd()
    @mock_config()
    @mock_value()
    def test_update_alarm(self, data, config, collectd, ClientV3,
                          resource_id, severity, meter_name, message,
                          _update_alarm, _get_alarm_id):
        """Test the update alarm function."""
        auth_client = ClientV3.return_value
        # init instance
        instance = sender.Sender()

        # init values to send
        _get_alarm_id.return_value = 'my-alarm-id'
        message = message.return_value
        metername = meter_name.return_value
        severity = severity.return_value
        rid = resource_id.return_value

        # send the values
        instance.send(metername, severity, rid, message)

        # update the alarm 
        _update_alarm.assert_called_once_with(
            instance, 'my-alarm-id', message, auth_client.auth_token)

        # reset method
        _update_alarm.reset_mock()

    @mock.patch.object(requests, 'put', spec=callable)
    @mock.patch.object(sender, 'ClientV3', autospec=True)
    @mock.patch.object(sender, 'LOGGER', autospec=True)
    @mock_collectd()
    @mock_config()
    @mock_value()
    def test_notify_auth_failed(
            self, data, config, collectd, LOGGER, ClientV3, put):
        """Test authentication failure."""
        # tell the auth client to raise an exception
        ClientV3.side_effect = KeystoneException(
            "Missing name 'xxx' in received services",
            "exception",
            "services list")

        # init instance
        instance = plugin.Plugin(collectd=collectd, config=config)

        # notify of another value the value
        instance.notify(data)

        LOGGER.error.assert_called_once_with(
            "Suspending error logs until successful auth")
        LOGGER.log.assert_called_once_with(
            logging.ERROR, "Authentication error: %s",
            "Missing name 'xxx' in received services\nReason: exception",
            exc_info=0)

        # no requests method has been called
        put.assert_not_called()

    @mock.patch.object(sender.Sender, '_perform_post_request', spec=callable)
    @mock.patch.object(sender, 'ClientV3', autospec=True)
    @mock_collectd()
    @mock_config()
    @mock_value()
    def test_request_error(
            self, data, config, collectd, ClientV3, perf_req):
        """Test error raised by underlying requests module."""
        # tell POST request to raise an exception
        perf_req.side_effect = requests.RequestException('Test POST exception')

        # init instance
        instance = plugin.Plugin(collectd=collectd, config=config)

        #  the value
        self.assertRaises(requests.RequestException, instance.notify, data)

    @mock.patch.object(sender.Sender, '_get_alarm_id', autospec=True)
    @mock.patch.object(requests, 'put', spec=callable)
    @mock.patch.object(sender, 'ClientV3', autospec=True)
    @mock_collectd()
    @mock_config()
    @mock_value()
    def test_reauthentication(self, data, config, collectd,
                              ClientV3, put, _get_alarm_id):
        """Test re-authentication for update request."""
        # init instance
        instance = plugin.Plugin(collectd=collectd, config=config)

        # test for non update request
        _get_alarm_id.return_value = None

        # response returned on success
        response_ok = requests.Response()
        response_ok.status_code = requests.codes["OK"]

        # response returned on failure
        response_unauthorized = requests.Response()
        response_unauthorized.status_code = requests.codes["UNAUTHORIZED"]

        put.return_value = response_ok

        client = ClientV3.return_value
        client.auth_token = 'Test auth token'

        # notify of the value
        instance.notify(data)

        # de-assert the non-update request
        put.assert_not_called()

        # test for update request
        _get_alarm_id.return_value = 'my-alarm-id'

        # response returned on success
        response_ok = requests.Response()
        response_ok.status_code = requests.codes["OK"]

        # response returned on failure
        response_unauthorized = requests.Response()
        response_unauthorized.status_code = requests.codes["UNAUTHORIZED"]

        put.return_value = response_ok

        client = ClientV3.return_value
        client.auth_token = 'Test auth token'

        # notify of the value
        instance.notify(data)

        # verify the auth token
        put.assert_called_once_with(
            mock.ANY, data=mock.ANY,
            headers={u'Content-type': mock.ANY,
                     u'X-Auth-Token': 'Test auth token'},
            timeout=1.0)

        # POST response is unauthorized -> new token needs to be acquired
        put.side_effect = [response_unauthorized, response_ok]

        # set a new auth token
        client.auth_token = 'New test auth token'

        instance.notify(data)

        # verify the auth token:
        call_list = put.call_args_list
        # POST called three times
        self.assertEqual(len(call_list), 3)

        # the second call contains the old token
        token = call_list[1][1]['headers']['X-Auth-Token']
        self.assertEqual(token, 'Test auth token')
        # the third call contains the new token
        token = call_list[2][1]['headers']['X-Auth-Token']
        self.assertEqual(token, 'New test auth token')

    @mock.patch.object(sender, 'ClientV3', autospec=True)
    @mock.patch.object(plugin, 'Notifier', autospec=True)
    @mock.patch.object(plugin, 'LOGGER', autospec=True)
    @mock_collectd()
    @mock_config()
    @mock_value()
    def test_exception_value_error(self, data, config, collectd,
                                   LOGGER, Notifier, ClientV3):
        """Test exception raised during notify and shutdown."""
        notifier = Notifier.return_value
        notifier.notify.side_effect = ValueError('Test notify error')

        # init instance
        instance = plugin.Plugin(collectd=collectd, config=config)

        self.assertRaises(ValueError, instance.notify, data)

    @mock.patch.object(sender, 'ClientV3', autospec=True)
    @mock.patch.object(plugin, 'LOGGER', autospec=True)
    @mock_collectd()
    @mock_config()
    def test_exception_runtime_error(self, config, collectd,
                                     LOGGER, ClientV3):
        """Test exception raised during shutdown."""
        # init instance
        instance = plugin.Plugin(collectd=collectd, config=config)

        instance.shutdown
