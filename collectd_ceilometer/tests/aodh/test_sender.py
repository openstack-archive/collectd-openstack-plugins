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
from collections import OrderedDict

valid_resp = '[{"alarm_actions": [], "event_rule": {"query": [],'\
             '"event_type": "events.gauge"}, "ok_actions": [],'\
             '"name": "alarm", "severity": "moderate",'\
             '"timestamp": "2017-08-22T06:22:46.790949", "enabled": true,'\
             '"alarm_id": "11af9327-8c3a-4120-8a74-bbc672c90f0a",'\
             '"time_constraints": [], "insufficient_data_actions": []}]'

valid_alarm_id = "valid_alarm_id"


class response(object):

    __attrs__ = [
        '_content', 'status_code', 'headers', 'url', 'history',
        'encoding', 'reason', 'cookies', 'elapsed', 'request', 'text'
    ]

    def __init__(self, text, code):
        self.text = text
        self.status_code = code

    def raise_for_status(self):
        pass


class TestSender(unittest.TestCase):
    """Test the Sender class."""

    def setUp(self):
        super(TestSender, self).setUp()
        self.sender = aodh_sender.Sender()

    @mock.patch.object(aodh_sender.Sender, "_get_remote_alarm_id",
                       autospec=True)
    @mock.patch.object(aodh_sender.Sender, "_get_endpoint", autospec=True)
    @mock.patch.object(aodh_sender.Sender, "_create_alarm", spec=callable)
    def test_get_alarm_id_no_local_alarm(self, _create_alarm, _get_endpoint,
                                         _get_remote_alarm_id):
        """Test the behaviour when the alarm id doesn't exist locally.

        Set-up:
        Test: call _get_alarm_id when no local alarm exists.
        Expected behaviour:
          * _get_remote_alarm_id is called
          * self._alarm_ids is updated
        """
        _get_remote_alarm_id.return_value = valid_alarm_id
        alarm_id = self.sender._get_alarm_id("alarm", "critical", "link status",
                                             "critical")
        if (alarm_id != valid_alarm_id):
            raise Exception("_get_remote_alarm_id is not called")
        _get_remote_alarm_id.assert_called_once_with(mock.ANY, mock.ANY,
                                                     "alarm")
        _create_alarm.assert_not_called()
        _get_endpoint.assert_called_once_with(mock.ANY, "aodh")
        if (not ("alarm" in self.sender._alarm_ids)):
            raise Exception("self._alarm_ids is not updated")

    @mock.patch.object(aodh_sender.Sender, "_create_alarm", spec=callable)
    @mock.patch.object(requests, 'get', spec=callable)
    def test_get_remote_alarm_id(self, get, _create_alarm):
        """Test behaviour of _get_remote_alarm_id

        Set-up:
        Test: Call _get_remote_alarm_id with typical parameters
        Expected behaviour:
          * requests.get is called with correct args
          * Alarm ID is returned
        """
        resp = response(valid_resp, 200)
        get.return_value = resp
        alarm_id = self.sender._get_remote_alarm_id(u"endpoint", u"alarm")
        if (alarm_id != "11af9327-8c3a-4120-8a74-bbc672c90f0a"):
            raise Exception("invalid alarm id ")
        _create_alarm.assert_not_called()

        params = OrderedDict([(u"q.field", u"name"), (u"q.op", u"eq"),
                              (u"q.value", u"alarm")])
        get.assert_called_once_with(u"endpoint/v2/alarms", params=params,
                                    headers=mock.ANY, timeout=mock.ANY)

    @mock.patch.object(aodh_sender.Sender, "_get_endpoint", autospec=True)
    @mock.patch.object(aodh_sender.Sender, "_create_alarm", spec=callable)
    @mock.patch.object(requests, 'get', spec=callable)
    def test_get_alarm_id_not_found(self, get, _create_alarm, _get_endpoint):
        """Test behaviour of _get_alarm_id when alarm does not exist

        Set up:
        Test:
          * call _get_alarm_id
          * requests.get/sender._perform_request return an error
        Expected behaviour: _create_alarm is called
        """
        resp = response("some invalide response", 404)
        get.return_value = resp
        _create_alarm.return_value = valid_alarm_id
        alarm_id = self.sender._get_alarm_id("alarm", "critical", "link status",
                                             "critical")
        _create_alarm.assert_called_once_with(
            mock.ANY, "critical", "link status", "alarm", "critical")
        _get_endpoint.assert_called_once_with(mock.ANY, "aodh")
        if (alarm_id != valid_alarm_id):
            raise Exception("invalid alarm id")
