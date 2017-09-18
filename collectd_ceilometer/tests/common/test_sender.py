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

"""Sender tests."""

import mock
import requests
import unittest

from collectd_ceilometer.common import sender as common_sender


class TestSender(unittest.TestCase):
    """Test the Sender class."""

    def setUp(self):
        super(TestSender, self).setUp()
        self.sender = common_sender.Sender()

        self.sender._url_base = \
            "http://my-gnocchi-endpoint/v1/action"

    @mock.patch('time.sleep')
    @mock.patch.object(common_sender.Sender, '_create_request_url')
    @mock.patch.object(common_sender, 'LOGGER')
    @mock.patch.object(common_sender.Sender, '_perform_request')
    def test_send_readtimeout_error(self, sender_perf_req,
                                    logger, sender_create_request_url,
                                    time_sleep):
        """Tests the behaviour of send when a timeout error occurs.

        Set-up: There is a ReadTimeout side effect from _perform_request
        Test: Call send
        Expected behaviour: Send will be called a second time.
        """
        response_created = requests.Response()
        response_created.status_code = 201

        self.sender._auth_token = "my-auth-token"

        sender_perf_req.side_effect = [requests.exceptions.ReadTimeout,
                                       response_created]

        self.sender.send(metername="my-metername",
                         payload="my-payload",
                         retry=1
                         )

        logger.debug.assert_called_with("ReadTimeout Error.. trying again...")

    @mock.patch('time.sleep')
    @mock.patch.object(common_sender.Sender, '_create_request_url')
    @mock.patch.object(common_sender, 'LOGGER')
    @mock.patch.object(common_sender.Sender, '_perform_request')
    def test_send_readtimeout_error_retry_0(self, sender_perf_req, logger,
                                            sender_create_request_url,
                                            time_sleep):
        """Tests that ReadTimeout error is raised when retry=0.

        Set-up: There is a ReadTimeout side effect from _perform_request.
        Test: Call send(.... retry=0)
        Expected behaviour:
          * ReadTimeout is raised from send()
          * there are no re-send attempts (perform_request is only called once)
        """
        self.sender._auth_token = "my-auth-token"

        sender_perf_req.side_effect = requests.exceptions.ReadTimeout

        with self.assertRaises(requests.exceptions.ReadTimeout):
            self.sender.send(metername="my-metername",
                             payload="my-payload",
                             retry=0
                             )
        logger.debug.assert_not_called()
        sender_perf_req.called_once()
        logger.error.assert_called_with("Too many timeouts trying to send\n",
                                        mock.ANY)

    @mock.patch('time.sleep')
    @mock.patch.object(common_sender.Sender, '_create_request_url')
    @mock.patch.object(common_sender, 'LOGGER')
    @mock.patch.object(common_sender.Sender, '_perform_request')
    def test_send_timeout_recurrant(self, sender_perf_req, logger,
                                    sender_create_request_url,
                                    time_sleep):
        """Test that resending is attepted when there's a ReadTimout error.

        Set-up:
        Test: Call send() with retry=<some_number>
        Expected behaviour:
          * TimeoutError will be re-raised after attempting multiple times
        """
        self.sender._auth_token = "my-auth-token"
        sender_perf_req.side_effect = requests.exceptions.ReadTimeout

        with self.assertRaises(requests.exceptions.ReadTimeout):
            self.sender.send(metername="my-metername",
                             payload="my-payload",
                             retry=5
                             )

        logger.debug.assert_called_with("ReadTimeout Error.. trying again...")
        sender_perf_req.assert_called()
        time_sleep.assert_has_calls([mock.call(1)] * 5)

    @mock.patch.object(requests, 'post')
    @mock.patch.object(requests, 'get')
    def test_perform_request_req_type_get(self, get, post):
        """Test the behaviour when performing a get request

        Set-up: None
        Test: call _perform_request with req_type="get"
        Expected behaviour:
          * requests.get is called with appropriate params
          * requests.post is not called
        """
        self.sender._perform_request("my-url", "some payload",
                                     "some headers", req_type="get")

        post.assert_not_called()
        get.assert_called_with("my-url", params="some payload",
                               headers=mock.ANY, timeout=mock.ANY)

    @mock.patch.object(requests, 'post')
    @mock.patch.object(requests, 'put')
    def test_perform_request_req_type_put(self, put, post):
        """Test the behaviour when performing a post request

        Set-up: None
        Test: call _perform_request with req_type="put"
        Expected behaviour:
          * requests.put is called
          * requests.post is not called (i.e. no fall back to default)
        """
        self.sender._perform_request("my-url", "some payload",
                                     "some headers", req_type="put")

        post.assert_not_called()
        put.assert_called_with("my-url", data="some payload",
                               headers=mock.ANY, timeout=mock.ANY)

    @mock.patch.object(requests, 'post')
    @mock.patch.object(requests, 'get')
    def test_perform_request_req_type_post(self, get, post):
        """Test the behaviour when performing a post request

        Set-up: None
        Test: call _perform_request with no req_type
        Expected behaviour:
          * requests.get is not called
          * requests.post is called with appropriate params
        """
        self.sender._perform_request("my-url", "some payload",
                                     "some headers")

        get.assert_not_called()
        post.assert_called_with("my-url", data="some payload",
                                headers=mock.ANY, timeout=mock.ANY)
