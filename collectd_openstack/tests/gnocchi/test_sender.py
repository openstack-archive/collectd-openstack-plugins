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

"""Plugin tests"""

import mock
import requests
import unittest

from collectd_openstack.gnocchi import sender as gnocchi_sender


class TestGnocchiSender(unittest.TestCase):
    """Test the sender class."""

    def setUp(self):
        self.sender = gnocchi_sender.Sender()
        self.sender._url_base = \
            "http://my-endpoint/v1/metric/%s/measures"

    def test_init(self):
        """Make sure the right things are initialised.

        Set-up: None
        Test: Create instance of sender
        Expected behaviour:
          * sender instance has an empty dict of metric_id mappings
        """
        self.assertEqual(self.sender._meter_ids,
                         {})

    @mock.patch.object(gnocchi_sender.Sender, '_create_request_url')
    @mock.patch.object(gnocchi_sender.Sender, '_perform_request')
    def test_send(self, sender_perform_request, sender_create_request_url):
        """Test send() in normal  circumstances.

        Set-up: Define metername, payload and **kwargs
        Test: call send with some data
        Expected behaviour:
          * _perform_request is called with an unchanged payload
          * _handle_http_error is not called
        """
        self.sender._auth_token = "my-auth-token"

        sender_create_request_url.return_value = \
            "http://my-endpoint/v1/metric/my-metrid-id/measures"

        expected_args = (
            "http://my-endpoint/v1/metric/my-metrid-id/measures",
            "some-payload",
            "my-auth-token")

        self.sender.send("my-metername", "some-payload", unit="some-unit")
        sender_perform_request.assert_called_with(*expected_args)

    @mock.patch.object(gnocchi_sender.Sender, '_handle_http_error')
    @mock.patch('requests.post')
    @mock.patch.object(gnocchi_sender.Sender, '_create_request_url')
    @mock.patch.object(gnocchi_sender.Sender, '_authenticate')
    def test_send_error_404(self, sender_authenticate,
                            sender_create_request_url,
                            post,
                            sender_handle_http_err):
        """Test send when metric is not defined

        Tests what happens when metric is not defined i.e. 404 is returned

        Set-up:
        Test: post returns a 404 when attenpting to create a measure
        Expected behaviour:
          * _handle_http_request is called to handle the 404
        """
        response_not_found = requests.Response()
        response_not_found.status_code = 404
        exc = requests.exceptions.HTTPError(
            u'404 Client Error: None for url: None',
            response=response_not_found)

        # send() mock the steps moving up to _perform_request
        sender_authenticate.return_value = "my_auth_token"
        sender_create_request_url.return_value = "http://my-request-url"
        # When the request is made, it fails
        post.return_value = exc.response

        self.sender.send("my-meter", "payload", resource_id="my-resource")
        sender_handle_http_err.assert_called()

    @mock.patch.object(gnocchi_sender.Sender, '_get_endpoint')
    def test_on_authenticated(self, sender_get_endpoint):
        """Test sender._on_authenticated

        Set-up: None
        Test: Call sender._on_authenticated
        Expected behaviour: sender._url_base is set correctly
        """
        expected_url = \
            "http://my-endpoint/v1/metric/%s/measures"

        sender_get_endpoint.return_value = "http://my-endpoint"

        self.sender._on_authenticated()

        self.assertEqual(self.sender._url_base,
                         expected_url)

    @mock.patch.object(gnocchi_sender.Sender, '_get_metric_id')
    @mock.patch.object(gnocchi_sender.Sender, '_get_endpoint')
    def test_create_request_url(self, sender_get_endpoint,
                                sender_get_metric_id):
        """Test create_request_url

        Set-up: None
        Test: call _create_requet_url
        Expected behaviour: sender_url_base is is returned
        """
        expected_url = \
            "http://my-endpoint/v1/metric/my-metric-name/measures"

        sender_get_endpoint.return_value = "http://my-endpoint"
        sender_get_metric_id.return_value = "my-metric-name"

        url = self.sender._create_request_url("my-metric-name", unit="my-unit")
        self.assertEqual(url,
                         expected_url)

    def test_handle_http_error(self):
        """Tesing the response to a HTTPError that is not a 404.

        Set-up: Create an Exception to use as a parameter
        Test: Use exception as an input parameter
        Expected behaviour: exception is raised again
        """
        res = requests.Response()
        res.status_code = 402
        exc = requests.HTTPError("Oh no! there was an error!",
                                 response=res)

        self.assertRaises(requests.exceptions.HTTPError,
                          self.sender._handle_http_error,
                          exc, "my-meter", "some-payload", "my-auth-token")

    @mock.patch.object(gnocchi_sender.Sender, '_get_metric_id')
    @mock.patch.object(gnocchi_sender.Sender, '_perform_request', autospec=True)
    def test_handle_http_error_404(self, sender_perf_req,
                                   sender_get_metric_id):
        """Test response to a HTTP 404 Error

        Set-up: Create the HTTPError
        Test: Call _handle_http_error with appropriate inputs
        Expected behaviour:
          *  Sender will try to create_or_update_resource
        """
        res = requests.Response()
        res.status_code = 404
        exc = requests.exceptions.HTTPError("Oh no! It wasn't found!",
                                            response=res)
        success = requests.Response()
        success.status_code = 201
        sender_perf_req.return_value = success
        sender_get_metric_id.return_value = "my-metric-name"

        self.sender._handle_http_error(exc, "my-meter", "some-payload",
                                       "my-auth-token", unit="my-unit",
                                       resource_id="my-resource-id")
