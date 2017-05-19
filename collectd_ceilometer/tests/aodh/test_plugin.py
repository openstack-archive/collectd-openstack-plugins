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

import unittest

import mock

import requests

from collectd_ceilometer.aodh import plugin
from collectd_ceilometer.aodh import sender as aodh_sender

from collectd_ceilometer.common.keystone_light import KeystoneException
from collectd_ceilometer.common.meters import base
from collectd_ceilometer.common import sender as common_sender

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

    @mock.patch.object(aodh_sender.Sender, '_get_alarm_id', autospec=True)
    @mock.patch.object(aodh_sender.Sender, '_get_alarm_state', autospec=True)
    @mock.patch.object(requests, 'put', spec=callable)
    @mock.patch.object(common_sender, 'ClientV3', autospec=True)
    @mock_collectd()
    @mock_config()
    @mock_value()
    def test_update_alarm(self, data, config, collectd, ClientV3,
                          put, _get_alarm_state, _get_alarm_id):
        """Test the update alarm function.

        Set-up: get an alarm-id for some notification values to be sent
        Test: perform an update request
        Expected behaviour:
         - If alarm-id present a put request is performed
        """
        auth_client = ClientV3.return_value
        auth_client.get_service_endpoint.return_value = \
            'https://test-aodh.tld'

        # init instance
        instance = plugin.Plugin(collectd=collectd, config=config)

        # init values to send
        _get_alarm_id.return_value = 'my-alarm-id'
        _get_alarm_state.return_value = 'insufficient data'

        # notify aodh of the update
        instance.notify(data)

        # update the alarm with a put request
        put.assert_called_once_with(
            'https://test-aodh.tld' +
            '/v2/alarms/my-alarm-id/state',
            data='"insufficient data"',
            headers={'Content-type': 'application/json',
                     'X-Auth-Token': auth_client.auth_token},
            timeout=1.0)

        # reset method
        put.reset_mock()

    @mock.patch.object(aodh_sender.Sender, '_create_alarm', autospec=True)
    @mock.patch.object(aodh_sender.Sender, '_get_alarm_id', autospec=True)
    @mock.patch.object(requests, 'put', spec=callable)
    @mock.patch.object(common_sender, 'ClientV3', autospec=True)
    @mock_collectd()
    @mock_config()
    @mock_value()
    def test_alarm_not_updated(self, data, config, collectd, ClientV3,
                               put, _get_alarm_id, _create_alarm):
        """Test if the is no alarm id the alarm won't be updated.

        Set-up: create a client and an instance to send an update to
                throw a side-effect when looking for an id
        Test: send a notification for a new alarm
        Expected behaviour:
         - if an alarm is create an update request is not performed
        """
        auth_client = ClientV3.return_value
        auth_client.get_service_endpoint.return_value = \
            'https://test-aodh.tld'

        instance = plugin.Plugin(collectd=collectd, config=config)

        # init values to send
        _get_alarm_id.return_value = None
        _create_alarm.return_value = 'my-alarm-id'

        # try and perform an update without an id
        instance.notify(data)

        put.assert_not_called()

        put.reset_mock()

    @mock.patch.object(requests, 'put', spec=callable)
    @mock.patch.object(common_sender, 'ClientV3', autospec=True)
    @mock.patch.object(common_sender, 'LOGGER', autospec=True)
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

    @mock.patch.object(aodh_sender.Sender, '_get_alarm_state', spec=callable)
    @mock.patch.object(base.Meter, 'collectd_severity', spec=callable)
    def test_low_severity(self, severity, _get_alarm_state):
        """Test _get_alarm_state if severity is 'low'

        Set-up: create a sender instance, set severity to low
        Test: call _get_alarm_state method with severity=low
        Expected-behaviour: returned state value should equal 'ok'
            and won't equal 'alarm' or insufficient data'
        """
        instance = aodh_sender.Sender()

        # run test for moderate severity
        severity.return_value = 'low'
        _get_alarm_state.return_value = 'ok'

        self.assertEqual(instance._get_alarm_state('low'), 'ok')

        self.assertNotEqual(instance._get_alarm_state('low'), 'alarm')

        self.assertNotEqual(instance._get_alarm_state('low'),
                            'insufficient data')

    @mock.patch.object(aodh_sender.Sender, '_get_alarm_state', spec=callable)
    @mock.patch.object(base.Meter, 'collectd_severity', spec=callable)
    def test_moderate_severity(self, severity, _get_alarm_state):
        """Test _get_alarm_state if severity is 'moderate'

        Set-up: create a sender instance, set severity to moderate
        Test: call _get_alarm_state method with severity=moderate
        Expected-behaviour: returned state value should equal 'alarm'
            and won't equal 'ok' or insufficient data'
        """
        instance = aodh_sender.Sender()

        # run test for moderate severity
        severity.return_value = 'moderate'
        _get_alarm_state.return_value = 'alarm'

        self.assertEqual(instance._get_alarm_state('moderate'), 'alarm')

        self.assertNotEqual(instance._get_alarm_state('moderate'), 'ok')

        self.assertNotEqual(instance._get_alarm_state('moderate'),
                            'insufficient data')

    @mock.patch.object(aodh_sender.Sender, '_get_alarm_state', spec=callable)
    @mock.patch.object(base.Meter, 'collectd_severity', spec=callable)
    def test_critical_severity(self, severity, _get_alarm_state):
        """Test _get_alarm_state if severity is 'critical'

        Set-up: create a sender instance, set severity to critical
        Test: call _get_alarm_state method with severity=critical
        Expected-behaviour: returned state value should equal 'alarm'
            and won't equal 'ok' or 'insufficient data'
        """
        instance = aodh_sender.Sender()

        # run test for moderate severity
        severity.return_value = 'critical'
        _get_alarm_state.return_value = 'alarm'

        self.assertEqual(instance._get_alarm_state('critical'), 'alarm')

        self.assertNotEqual(instance._get_alarm_state('critical'), 'ok')

        self.assertNotEqual(instance._get_alarm_state('critical'),
                            'insufficient data')

    @mock.patch.object(aodh_sender.Sender, '_get_alarm_state', spec=callable)
    @mock.patch.object(base.Meter, 'collectd_severity', spec=callable)
    def test_other_severity(self, severity, _get_alarm_state):
        """Test _get_alarm_state if severity is not low/moderate/critical

        Set-up: create a sender instance, set severity to None
        Test: call _get_alarm_state method with severity=None
        Expected-behaviour: returned state value should equal
            'insufficient data' and won't equal 'ok' or 'alarm'
        """
        instance = aodh_sender.Sender()

        # run test for moderate severity
        severity.return_value = None
        _get_alarm_state.return_value = 'insufficient data'

        self.assertEqual(instance._get_alarm_state(None), 'insufficient data')

        self.assertNotEqual(instance._get_alarm_state('critical'), 'ok')

        self.assertNotEqual(instance._get_alarm_state('critical'), 'alarm')

    @mock.patch.object(aodh_sender.Sender, '_perform_request', spec=callable)
    @mock.patch.object(common_sender, 'ClientV3', autospec=True)
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

    @mock.patch.object(aodh_sender.Sender, '_get_alarm_state', autospec=True)
    @mock.patch.object(aodh_sender.Sender, '_get_alarm_id', autospec=True)
    @mock.patch.object(requests, 'put', spec=callable)
    @mock.patch.object(common_sender, 'ClientV3', autospec=True)
    @mock_collectd()
    @mock_config()
    @mock_value()
    def test_reauthentication(self, data, config, collectd,
                              ClientV3, put, _get_alarm_id, _get_alarm_state):
        """Test re-authentication for update request."""
        # response returned on success
        response_ok = requests.Response()
        response_ok.status_code = requests.codes["OK"]

        # response returned on failure
        response_unauthorized = requests.Response()
        response_unauthorized.status_code = requests.codes["UNAUTHORIZED"]

        # set-up client
        client = ClientV3.return_value
        client.auth_token = 'Test auth token'
        client.get_service_endpoint.return_value = \
            'https://test-aodh.tld'

        # init instance attempt to update/create alarm
        instance = plugin.Plugin(collectd=collectd, config=config)

        put.return_value = response_ok
        _get_alarm_id.return_value = 'my-alarm-id'
        _get_alarm_state.return_value = 'insufficient data'

        # send notification to aodh
        instance.notify(data)

        # put/update is called
        put.assert_called_once_with(
            'https://test-aodh.tld' +
            '/v2/alarms/my-alarm-id/state',
            data='"insufficient data"',
            headers={u'Content-type': 'application/json',
                     u'X-Auth-Token': 'Test auth token'},
            timeout=1.0)

        # PUT response is unauthorized -> new token needs to be acquired
        put.side_effect = [response_unauthorized, response_ok]

        # set a new auth token
        client.auth_token = 'New test auth token'

        # send another notification
        instance.notify(data)

        # verify the auth token:
        call_list = put.call_args_list
        # PUT called three times
        self.assertEqual(len(call_list), 3)

        # the second call contains the old token
        token = call_list[1][1]['headers']['X-Auth-Token']
        self.assertEqual(token, 'Test auth token')
        # the third call contains the new token
        token = call_list[2][1]['headers']['X-Auth-Token']
        self.assertEqual(token, 'New test auth token')

    @mock.patch.object(common_sender, 'ClientV3', autospec=True)
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

    @mock.patch.object(common_sender, 'ClientV3', autospec=True)
    @mock.patch.object(plugin, 'LOGGER', autospec=True)
    @mock_collectd()
    @mock_config()
    def test_exception_runtime_error(self, config, collectd,
                                     LOGGER, ClientV3):
        """Test exception raised during shutdown."""
        # init instance
        instance = plugin.Plugin(collectd=collectd, config=config)

        instance.shutdown
