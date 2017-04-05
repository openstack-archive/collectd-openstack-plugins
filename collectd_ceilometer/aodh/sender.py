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

import collectd_ceilometer
from collectd_ceilometer.common.keystone_light import ClientV3
from collectd_ceilometer.common.keystone_light import KeystoneException
from collectd_ceilometer.common.settings import Config

import json
import logging
import requests
from requests.exceptions import RequestException
import six
import threading

LOGGER = logging.getLogger(__name__)
ROOT_LOGGER = logging.getLogger(collectd_ceilometer.__name__)

# HTTP status codes
HTTP_CREATED = 201
HTTP_UNAUTHORIZED = 401
HTTP_NOT_FOUND = 404


class Sender(object):
    """Sends the JSON serialized data to Aodh."""

    def __init__(self):
        """Create the Sender instance.

        The cofiguration must be initialized before the object is created.
        """
        self._url_base = None
        self._keystone = None
        self._auth_token = None
        self._auth_lock = threading.Lock()
        self._failed_auth = False
        self._alarm_ids = {}

    def _authenticate(self):
        """Authenticate and renew the authentication token."""
        # if auth_token is available, just return it
        if self._auth_token is not None:
            return self._auth_token

        # aquire the authentication lock
        with self._auth_lock:
            # re-check the auth_token as another thread could set it
            if self._auth_token is not None:
                return self._auth_token

            LOGGER.debug('Authenticating request')
            # pylint: disable=broad-except
            try:
                # create a keystone client if it doesn't exist
                if self._keystone is None:
                    cfg = Config.instance()
                    self._keystone = ClientV3(
                        auth_url=cfg.OS_AUTH_URL,
                        username=cfg.OS_USERNAME,
                        password=cfg.OS_PASSWORD,
                        tenant_name=cfg.OS_TENANT_NAME
                    )
                # store the authentication token
                self._auth_token = self._keystone.auth_token

                # get the uri of service endpoint
                endpoint = self._get_endpoint("aodh")

                self._url_base = "{}/v2/alarms/%s/state".format(endpoint)

                LOGGER.info('Authenticating request - success')
                self._failed_auth = False

            except KeystoneException as exc:
                log_level = logging.DEBUG

                if not self._failed_auth:

                    log_level = logging.ERROR
                    LOGGER.error(
                        'Suspending error logs until successful auth'
                    )

                LOGGER.log(log_level, 'Authentication error: %s',
                           six.text_type(exc),
                           exc_info=0)

                if exc.response:
                    LOGGER.debug('Response: %s', exc.response)

                self._auth_token = None
                self._failed_auth = True

        return self._auth_token

    def send(self, metername, severity, resource_id, message):
        """Send the payload to Aodh."""
        # get the auth_token
        auth_token = self._authenticate()
        LOGGER.info('Auth_token: %s',
                    auth_token,
                    )
        # if auth_token is not set, there is nothing to do
        if auth_token is None:
            LOGGER.debug('Unable to send data. Not authenticated')
            return

        if self._url_base is None:
            LOGGER.debug(
                'Unable to send data. Missing endpoint from ident server')
            return

        # Create alarm name
        alarm_name = self._get_alarm_name(metername, resource_id)

        # Update or create this alarm
        result = self._update_or_create_alarm(alarm_name, message, auth_token,
                                              severity, metername)

        if result is None:
            return

        LOGGER.info('Result: %s %s',
                    six.text_type(result.status_code),
                    result.text)

        # if the request failed due to an auth error
        if result.status_code == HTTP_UNAUTHORIZED:
            # reset the auth token in order to force the subsequent
            # _authenticate() call to renew it
            # Here, it can happen that the token is reset right after
            # another thread has finished the authentication and thus
            # the authentication may be performed twice
            self._auth_token = None

            # renew the authentication token
            auth_token = self._authenticate()

            if auth_token is not None:
                result = self._update_or_create_alarm(alarm_name, message,
                                                      auth_token, severity,
                                                      metername)

        if result.status_code == HTTP_NOT_FOUND:
            LOGGER.debug("Received 404 error when submitting %s notification, \
                         creating a new alarm",
                         alarm_name)

            # check for and/or get alarm_id
            result = self._update_or_create_alarm(alarm_name, message,
                                                  auth_token, severity,
                                                  metername)

        if result.status_code == HTTP_CREATED:
            LOGGER.debug('Result: %s', HTTP_CREATED)
        else:
            LOGGER.info('Result: %s %s',
                        result.status_code,
                        result.text)

    def _get_endpoint(self, service):
        """Get the uri of service endpoint."""
        endpoint = self._keystone.get_service_endpoint(
            service,
            Config.instance().CEILOMETER_URL_TYPE)
        return endpoint

    def _update_or_create_alarm(self, alarm_name, message, auth_token,
                                severity, metername):
        # check for an alarm and update
        try:
            alarm_id = self._alarm_ids[alarm_name]
            result = self._update_alarm(alarm_id, message, auth_token)

        # or create a new alarm
        except KeyError as ke:
            LOGGER.warn(ke)

            endpoint = self._get_endpoint("aodh")
            LOGGER.warn('No known ID for %s', alarm_name)
            result, self._alarm_ids[alarm_name] = \
                self._create_alarm(endpoint, severity,
                                   metername, alarm_name, message)
        return result

    def _create_alarm(self, endpoint, severity, metername,
                      alarm_name, message):
        """Create a new alarm with a new alarm_id."""
        url = "{}/v2/alarms/".format(endpoint)

        rule = {'event_type': metername, }
        payload = json.dumps({'state': self._get_alarm_state(message),
                              'name': alarm_name,
                              'severity': severity,
                              'type': "event",
                              'event_rule': rule,
                              })

        result = self._perform_post_request(url, payload, self._auth_token)
        alarm_id = json.loads(result.text)['alarm_id']
        LOGGER.debug("alarm_id=%s", alarm_id)
        return result, alarm_id

    def _get_alarm_state(self, message):
        """Get the state of the alarm."""
        message = message.split()
        if 'above' in message:
            alarm_state = "alarm"
        elif 'within' in message:
            alarm_state = "ok"
        else:
            alarm_state = "insufficient data"
        return alarm_state

    def _get_alarm_name(self, metername, resource_id):
        """Get the alarm name."""
        alarm_name = metername + "(" + resource_id + ")"
        return alarm_name

    def _update_alarm(self, alarm_id, message, auth_token):
        """Perform the alarm update."""
        url = self._url_base % (alarm_id)
        # create the payload and update the state of the alarm
        payload = json.dumps(self._get_alarm_state(message))
        return self._perform_update_request(url, auth_token, payload)

    @classmethod
    def _perform_post_request(cls, url, payload, auth_token):
        """Perform the POST request."""
        LOGGER.debug('Performing request to %s', url)

        # request headers
        headers = {'X-Auth-Token': auth_token,
                   'Content-type': 'application/json'}
        # perform request and return its result
        response = None
        try:
            LOGGER.debug(
                "Performing request to: %s with data=%s and headers=%s",
                url, payload, headers)

            response = requests.post(
                url, data=payload, headers=headers,
                timeout=(Config.instance().CEILOMETER_TIMEOUT / 1000.))
            LOGGER.info('Response: %s: %s',
                        response.status_code, response.text
                        )
        except RequestException as exc:
            LOGGER.error('aodh request error: %s', six.text_type(exc))
        finally:
            LOGGER.debug(
                "Returning response from _perform_post_request(): %s",
                response.status_code)
            return response

    @classmethod
    def _perform_update_request(cls, url, auth_token, payload):
        """Perform the PUT/update request."""
        LOGGER.debug('Performing request to %s', url)

        # request headers
        headers = {'X-Auth-Token': auth_token,
                   'Content-type': 'application/json'}
        # perform request and return its result
        response = None
        try:
            LOGGER.debug(
                "Performing request to: %s with data=%s and headers=%s",
                url, payload, headers)
            response = requests.put(
                url, data=payload, headers=headers,
                timeout=(Config.instance().CEILOMETER_TIMEOUT / 1000.))
            LOGGER.info('Response: %s: %s',
                        response.status_code, response.text
                        )
        except RequestException as exc:
            LOGGER.error('aodh request error: %s', six.text_type(exc))
        finally:
            LOGGER.debug(
                'Returning response from _perform_update_request(): %s',
                response.status_code)
            return response
