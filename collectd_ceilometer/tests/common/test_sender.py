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
          * requests.post is not called (i.e. no fall back to default
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
