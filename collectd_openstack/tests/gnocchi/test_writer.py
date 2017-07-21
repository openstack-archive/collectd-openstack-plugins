# -*- coding: utf-8 -*-

# Copyright 2010-2011 OpenStack Foundation
# Copyright (c) 2017 Intel Corporation.
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
"""Gnocchi Writer tests"""

import json
import mock
import requests
import unittest

from collectd_openstack.common.meters import MeterStorage
from collectd_openstack.gnocchi import sender as gnocchi_sender
from collectd_openstack.gnocchi import writer


def mock_collectd(**kwargs):
    "Returns collectd module with collectd logging hooks."
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
    "Returns collectd module with collectd logging hooks."
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


class TestGnocchiWriter(unittest.TestCase):
    """Test the gnocchi Writer class"""

    @mock_config()
    @mock_collectd()
    def setUp(self, collectd, config):
        super(TestGnocchiWriter, self).setUp()

        meters = MeterStorage(collectd=collectd)
        self.writer = writer.Writer(meters=meters, config=config)
        self.writer._sender._auth_token = "my_auth_token"

    @mock.patch.object(gnocchi_sender.Sender, '_create_request_url')
    @mock.patch.object(gnocchi_sender.Sender, '_get_endpoint')
    @mock.patch.object(gnocchi_sender.Sender, '_authenticate')
    @mock.patch('requests.post', autospec=True)
    @mock_value()
    def test_write(self, vl, post, sender_authenticate, sender_get_endpoint,
                   sender_create_request_url):
        """Test write with successful results

        Set-up: None
        Test: call write with expected data
        Expected behaviour:
          * POST is called successfully
          * No error occurs i.e. no error is raised
        """
        response_ok = requests.Response()
        response_ok.status_code = 200
        post.return_value = response_ok

        self.writer._sender._url_base = "my-url"
        sender_get_endpoint.return_value = "http://my-endpoint"
        sender_create_request_url.return_value = \
            "http://my-endpoint/v1/metrics/my-metric-id/measures"
        sender_authenticate.return_value = "auth_token"
        # Force the url to be updated without actually authenticating
        self.writer._sender._on_authenticated()

        expected_url = "http://my-endpoint/v1/metrics/my-metric-id/measures"
        expected_payload = json.dumps([
            {
                "value": 1234,
                "timestamp": "1973-11-29T21:33:09"
                },
            ])

        expected_kwargs = {"data": expected_payload,
                           "headers": mock.ANY,
                           "timeout": mock.ANY}

        self.writer.write(vl, None)
        post.assert_called_with(expected_url, **expected_kwargs)

    @mock.patch.object(gnocchi_sender.Sender, '_get_endpoint')
    @mock.patch.object(gnocchi_sender.Sender, '_authenticate')
    @mock.patch.object(gnocchi_sender.Sender, '_create_metric')
    @mock.patch('requests.post', autospec=True)
    @mock_value()
    def test_write_metric_none(self, vl, post,
                               sender_create_metric,
                               sender_authenticate,
                               sender_get_endpoint):
        """Test Writer.write() when there is no meter defined.

        Set-up:
        Test: Sender throws a HTTPError with status=404
        Expected behaviour:
            * _create_or_update_resource is called with appropriate args
        """

        response_not_found = requests.Response()
        response_not_found.status_code = 404

        response_ok = requests.Response()
        response_ok.status_code = 200

        # post will be called to submit sample before AND after handling
        # the error
        post.side_effect = [response_not_found, response_ok]

        self.writer._sender._url_base = "my-url"
        sender_get_endpoint.return_value = "http://my-endpoint"
        sender_authenticate.return_value = "auth_token"

        self.writer.write(vl, data=None)

        sender_create_metric.assert_called()

    @mock.patch.object(gnocchi_sender.Sender, 'send')
    @mock_value()
    def test_send_data(self, vl, sender_send):
        """Test _send_data() to make sure the correct payoad is being sent.

        Set-up: Create a sample
        Test: call _send_data
        Expected behaviour:
         *  Sender.send() is called with the correct payload and args
        """
        sample = writer.Sample(value=42, timestamp=0, meta=None,
                               unit="my-unit", metername="my-metername")
        # TODO(emma-l-foley): Add docstring to _send_data specifying the inputs.
        # to_send should be a list of Sample objects
        to_send = [sample]

        expected_payload = json.dumps([
            {
                "value": 42,
                "timestamp": 0
                }
            ])

        expected_args = ("my-metername", expected_payload)
        expected_kwargs = {"unit": "my-unit"}

        self.writer._send_data("my-metername", to_send,
                               unit="my-unit",)

        sender_send.assert_called_with(*expected_args, **expected_kwargs)
