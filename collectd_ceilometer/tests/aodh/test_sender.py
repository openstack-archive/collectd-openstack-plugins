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

from collectd_ceilometer.aodh import sender as aodh_sender


class TestSender(unittest.TestCase):
    """Test the Sender class."""

    def setUp(self):
        super(TestSender, self).setUp()
        self.sender = aodh_sender.Sender()

    @unittest.expectedFailure
    def test_get_alarm_id_no_local_alarm(self):
        """Test the behaviour when the alarm id doesn't exist locally.

        Set-up:
        Test: call _get_alarm_id when no local alarm exists.
        Expected behaviour:
          * _get_remote_alarm_id is called
          * self._alarm_ids is updated
        """
        raise Exception("Not implemented")

    @unittest.expectedFailure
    @mock.patch.object(requests, 'post', spec=callable)
    def test_get_remote_alarm_id(self):
        """Test behaviour of _get_remote_alarm_id

        Set-up:
        Test: Call _get_remote_alarm_id with typical parameters
        Expected behaviour:
          * requests.get is called with correct args
          * Alarm ID is returned
        """
        raise Exception("Not implemented")

    @unittest.expectedFailure
    def test_get_remote_alarm_id_exception_not_found(self):
        """Test behaviour of _get_remote_alarm_id when alarm does not exist

        Set up:
        Test:
          * _call_get_remote_alarm_id
          * requests.get/sender._perform_request return an error
        Expected behaviour: _create_alarm is called
        """
        raise Exception("Not implemented")
