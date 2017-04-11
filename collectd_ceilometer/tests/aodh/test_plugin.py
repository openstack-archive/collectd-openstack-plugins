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

    @mock.patch.object(sender.Sender, '_update_or_create_alarm', autospec=True)
    @mock.patch.object(sender.Sender, '_get_alarm_name', autospec=True)
    @mock.patch.object(base, 'Meter', autospec=True)
    @mock.patch.object(sender, 'ClientV3', autospec=True)
    @mock_collectd()
    @mock_config()
    @mock_value()
    def test_update_or_create_alarm(self, data, config, collectd,
                                    ClientV3, meter,
                                    _get_alarm_name, _update_or_create_alarm):
        """Test the update/create alarm function"""
        auth_client = ClientV3.return_value
        auth_client.get_service_endpoint.return_value = \
            'https://test-aodh.tld'

        _update_or_create_alarm.return_value = requests.Response()

        # init sender instance
        instance = sender.Sender()

        _get_alarm_name.return_value = 'my-alarm'
        meter_name = meter.meter_name.return_value
        severity = meter.severity.return_value
        resource_id = meter.resource_id.return_value

        # send the values
        instance.send(meter_name, severity, resource_id)

        # check that the function is called
        _update_or_create_alarm.assert_called_once_with(
            instance, 'my-alarm', auth_client.auth_token,
            severity, meter_name)

        # reset function
        _update_or_create_alarm.reset_mock()

        # run test again for failed attempt
        _update_or_create_alarm.return_value = None

        instance.send(meter_name, severity, resource_id)

        # and values that have been sent
        _update_or_create_alarm.assert_called_once_with(
            instance, 'my-alarm', auth_client.auth_token,
            severity, meter_name)

        # reset post method
        _update_or_create_alarm.reset_mock()

    @mock.patch.object(sender.Sender, '_create_alarm', autospec=True)
    @mock.patch.object(sender.Sender, '_get_alarm_id', autospec=True)
    @mock.patch.object(sender.Sender, '_update_alarm', autospec=True)
    @mock.patch.object(base, 'Meter', autospec=True)
    @mock.patch.object(sender.Sender, '_get_alarm_name', autospec=True)
    @mock.patch.object(sender, 'ClientV3', autospec=True)
    @mock_collectd()
    @mock_config()
    @mock_value()
    def test_update_alarm(self, data, config, collectd, ClientV3,
                          _get_alarm_name, meter, _update_alarm,
                          _get_alarm_id, _create_alarm):
        """Test the update alarm function."""
        auth_client = ClientV3.return_value
        auth_client.get_service_endpoint.return_value = \
            'https://test-aodh.tld'

        # init instance
        instance = sender.Sender()

        # init values to send
        _get_alarm_id.return_value = 'my-alarm-id'
        metername = meter.meter_name.return_value
        severity = meter.severity.return_value
        rid = meter.resource_id.return_value

        # send the values
        instance.send(metername, severity, rid)

        # update the alarm
        _update_alarm.assert_called_once_with(
            instance, 'my-alarm-id', severity, auth_client.auth_token)

        # reset method
        _update_alarm.reset_mock()

        _get_alarm_id.side_effect = KeyError()
        _get_alarm_name.return_value = 'my-alarm'
        _create_alarm.return_value = requests.Response(), 'my-alarm-id'

        # send the values
        instance.send(metername, severity, rid)

        _create_alarm.assert_called_once_with(
            instance, 'https://test-aodh.tld', severity, metername,
            'my-alarm')

        _create_alarm.reset_mock()

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

    @mock.patch.object(sender.Sender, '_get_alarm_state', spec=callable)
    @mock.patch.object(base.Meter, 'severity', spec=callable)
    def test_get_state(self, severity, _get_alarm_state):
        """Test the setting of the state of the alarm"""
        instance = sender.Sender()

        # run test for moderate severity
        severity.return_value = 'moderate'
        _get_alarm_state.return_value = 'alarm'

        instance._get_alarm_state(severity.return_value)

        _get_alarm_state.assert_called_once_with('moderate')

        severity.reset_mock()
        _get_alarm_state.reset_mock()

        # run test for critical severity
        severity.return_value = 'critical'
        instance._get_alarm_state(severity.return_value)

        _get_alarm_state.assert_called_once_with('critical')

        severity.reset_mock()
        _get_alarm_state.reset_mock()

        # run test for low severity
        severity.return_value = 'low'
        _get_alarm_state.return_value = 'ok'

        instance._get_alarm_state(severity.return_value)
        _get_alarm_state.assert_called_once_with('low')

        severity.reset_mock()
        _get_alarm_state.reset_mock()

        # run test for other
        severity.return_value = None
        _get_alarm_state.return_value = 'insufficient data'

        instance._get_alarm_state(severity.return_value)

        _get_alarm_state.assert_called_once_with(None)

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

    @mock.patch.object(sender.Sender, '_update_or_create_alarm', autospec=True)
    @mock.patch.object(sender.Sender, '_get_alarm_name', autospec=True)
    @mock.patch.object(base, 'Meter', autospec=True)
    @mock.patch.object(sender, 'ClientV3', autospec=True)
    @mock_collectd()
    @mock_config()
    @mock_value()
    def test_reauthentication(self, data, config, collectd,
                              ClientV3, meter, _get_alarm_name,
                              _update_or_create_alarm):
        """Test re-authentication for update request."""

        # response returned on success
        response_ok = requests.Response()
        response_ok.status_code = requests.codes["OK"]

        # response returned on failure
        response_unauthorized = requests.Response()
        response_unauthorized.status_code = requests.codes["UNAUTHORIZED"]

        _update_or_create_alarm.return_value = response_ok

        client = ClientV3.return_value
        client.auth_token = 'Test auth token'

        # init instance attempt to update/create alarm
        instance = sender.Sender()

        alarm_name = _get_alarm_name.return_value
        meter_name = meter.meter_name.return_value
        severity = meter.severity.return_value
        resource_id = meter.resource_id.return_value

        # send the data
        instance.send(meter_name, severity, resource_id)

        _update_or_create_alarm.assert_called_once_with(
            instance, alarm_name, client.auth_token,
            severity, meter_name)

        # de-assert the request
        _update_or_create_alarm.reset_mock()

        # response returned on success
        response_ok = requests.Response()
        response_ok.status_code = requests.codes["OK"]

        # response returned on failure
        response_unauthorized = requests.Response()
        response_unauthorized.status_code = requests.codes["UNAUTHORIZED"]

        _update_or_create_alarm.return_value = response_ok

        client = ClientV3.return_value
        client.auth_token = 'Test auth token'

        # send the data
        instance.send(meter_name, severity, resource_id)

        _update_or_create_alarm.assert_called_once_with(
            instance, alarm_name, client.auth_token,
            severity, meter_name)

        # update/create response is unauthorized -> new token needs
        # to be acquired
        _update_or_create_alarm.side_effect = [response_unauthorized,
                                               response_ok]

        # set a new auth token
        client.auth_token = 'New test auth token'

        # send the data again
        instance.send(meter_name, severity, resource_id)

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
