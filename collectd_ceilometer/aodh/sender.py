# -*- coding: utf-8 -*-

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

"""Aodh collectd plugin implementation."""

from __future__ import division
from __future__ import unicode_literals

import json
import logging
import requests


import collectd_ceilometer
from collectd_ceilometer.common import sender as common_sender
from collectd_ceilometer.common.settings import Config
from collections import OrderedDict

LOGGER = logging.getLogger(__name__)
ROOT_LOGGER = logging.getLogger(collectd_ceilometer.__name__)

# HTTP status codes
HTTP_CREATED = 201
HTTP_UNAUTHORIZED = 401
HTTP_NOT_FOUND = 404


class Sender(common_sender.Sender):
    """Sends the JSON serialized data to Aodh."""

    def __init__(self):
        """Create the Sender instance.

        The configuration must be initialized before the object is created.
        """
        super(Sender, self).__init__()

        self._alarm_ids = {}

    def _on_authenticated(self):
        # get the uri of service endpoint for an alarm state update
        endpoint = self._get_endpoint("aodh")

        self._url_base = "{}/v2/alarms/%s/state".format(endpoint)

    def _create_request_url(self, metername, **kwargs):
        """Create the request url for an alarm update."""
        severity = kwargs['severity']
        resource_id = kwargs['resource_id']
        alarm_severity = kwargs['alarm_severity']
        alarm_name = self._get_alarm_name(metername, resource_id)
        alarm_id = self._get_alarm_id(alarm_name,
                                      severity, metername, alarm_severity)
        payload = self._get_alarm_payload(**kwargs)

        # Create a url if an alarm already exists
        if alarm_id is not None:
            url = self._url_base % (alarm_id)
            try:
                self._perform_request(url, payload, self._auth_token, "put")
            except requests.exceptions.HTTPError as exc:
                # This is an error and it has to be forwarded
                self._handle_http_error(exc, metername, payload,
                                        self._auth_token, **kwargs)

        return None

    def _handle_http_error(self, exc, metername,
                           payload, auth_token, **kwargs):
        """Handle and log a http error request."""
        severity = kwargs['severity']
        resource_id = kwargs['resource_id']
        alarm_name = self._get_alarm_name(metername, resource_id)
        response = exc.response
        if response.status_code == common_sender.Sender.HTTP_NOT_FOUND:
            LOGGER.debug("Received 404 error when submitting %s update, \
                         updating a new alarm",
                         alarm_name)

            # get alarm id for
            alarm_id = self._get_alarm_id(alarm_name, severity, metername)

            LOGGER.info('alarmname: %s, alarm_id: %s', alarm_name, alarm_id)

            # Set a new url for the request
            url = self._url_base % (alarm_id)

            # Get the responses for the alarm
            result = self._perform_request(url, payload, auth_token, "put")

            if result.status_code == common_sender.Sender.HTTP_CREATED:
                LOGGER.debug('Result: %s', common_sender.Sender.HTTP_CREATED)
            else:
                LOGGER.info('Result: %s %s',
                            result.status_code,
                            result.text)
        else:
            raise exc

    def _get_endpoint(self, service):
        """Get the uri of service endpoint."""
        endpoint = self._keystone.get_service_endpoint(
            service,
            Config.instance().CEILOMETER_URL_TYPE)
        return endpoint

    def _get_remote_alarm_id(self, endpoint, alarm_name):
        """Request alarm with given name."""
        url = "{}/v2/alarms".format(endpoint)
        # request id from a server. openstack service can
        # handle only predefined order of args: q.field=&q.op=&q.value=
        # in other cases it will fail
        params = OrderedDict([("q.field", "name"), ("q.op", "eq"),
                              ("q.value", alarm_name)])
        alarm_id = None
        try:
            result = self._perform_request(url, params, self._auth_token,
                                           req_type="get")
        except Exception as exc:
            LOGGER.warn('Invalid response from server for alarm:'
                        ' %s error = %s %s' % (alarm_name, type(exc), exc))
            return None

        try:
            # parse response
            alarm_id = json.loads(result.text)[0]['alarm_id']
        except (KeyError, ValueError, IndexError):
            LOGGER.warn('NO alarm on the server: %s' % alarm_name)
        return alarm_id

    def _get_alarm_id(self, alarm_name, severity, metername, alarm_severity):
        # check for an alarm and update
        try:
            return self._alarm_ids[alarm_name]

        except KeyError as ke:
            LOGGER.warn(ke)
            LOGGER.warn('No ID in a cache for %s', alarm_name)

            endpoint = self._get_endpoint("aodh")
            alarm_id = self._get_remote_alarm_id(endpoint, alarm_name)
            # create new alarm
            if alarm_id is None:
                alarm_id = \
                    self._create_alarm(endpoint, severity,
                                       metername, alarm_name, alarm_severity)
            if alarm_id is not None:
                # Add alarm ids/names to relevant dictionaries/lists
                self._alarm_ids[alarm_name] = alarm_id
            return alarm_id

    def _create_alarm(self, endpoint, severity, metername,
                      alarm_name, alarm_severity):
        """Create a new alarm with a new alarm_id."""
        url = "{}/v2/alarms/".format(endpoint)

        rule = {'event_type': metername, }
        payload = json.dumps({'state': self._get_alarm_state(severity),
                              'name': alarm_name,
                              'severity': alarm_severity,
                              'type': "event",
                              'event_rule': rule,
                              })

        result = self._perform_request(url, payload, self._auth_token, "post")
        alarm_id = json.loads(result.text)['alarm_id']
        LOGGER.debug("alarm_id=%s", alarm_id)
        return alarm_id

    def _get_alarm_state(self, severity):
        """Get the state of the alarm."""
        if severity in ('critical', 'moderate'):
            alarm_state = "alarm"
        elif severity == 'low':
            alarm_state = "ok"
        else:
            alarm_state = "insufficient data"
        return alarm_state

    def _get_alarm_name(self, metername, resource_id):
        """Get the alarm name."""
        alarm_name = metername + "(" + resource_id + ")"
        return alarm_name

    def _get_alarm_payload(self, **kwargs):
        """Get the payload for the update/post request of the alarm."""
        severity = kwargs['severity']
        payload = json.dumps(self._get_alarm_state(severity))
        return payload
