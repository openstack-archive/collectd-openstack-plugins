#l -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language gov2/alarmsverning permissions and limitations
# under the License.
"""Gnocchi collectd plugin implementation"""

from __future__ import division
from __future__ import unicode_literals

import collectd_ceilometer
from collectd_ceilometer.common.keystone_light import ClientV3
from collectd_ceilometer.common.keystone_light import KeystoneException
from collectd_ceilometer.common.settings import Config
from collectd_ceilometer.common.manager import Manager

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
    """Sends the JSON serialized data to Gnocchi"""

    def __init__(self):
        """Create the Sender instance

        The cofinguration must be initialized before the object is created.
        """
        self._url_base = None
        self._keystone = None
        self._auth_token = None
        self._auth_lock = threading.Lock()
        self._failed_auth = False
        self._meter_ids = {}

    def _authenticate(self):
        """Authenticate and renew the authentication token"""

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

    def send(self, metername, payload, severity, message, resource_id):
        """Send the payload to Aodh"""

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

        # Check for an existing alarm
        #create_alarm = False
        alarm_name = metername + "(" + resource_id + ")"
        state = self.get_alarm_state(severity)
        endpoint = self._get_endpoint("aodh")
        _url_base = "{}/v2/alarms/".format(endpoint)

        # create request URL
        new, metric_id = self._get_metric_id(alarm_name, severity, state)
        #LOGGER.warning("id: %s", metric_id)
        url = self._url_base % (metric_id)

        # send the POST request
        result = self._perform_post_request(url, payload, auth_token)
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
               # and try to repost
              result = self._perform_post_request(url, payload, auth_token)

           if result.status_code == HTTP_NOT_FOUND:
              LOGGER.debug("Received 404 error when submitting %s sample, \
                         creating a new metric",
                         metername)

              #create metric (endpoint, metername)
              new, metric_id = self._get_metric_id(alarm_name, severity, alarm_state)

              LOGGER.info('metername: %s, meter_id: %s', metername, metric_id)
            # Set a new url for the request
           url = self._url_base % (metric_id)
            # TODO(emma-l-foley): Add error checking
            # Submit the sample
           result = self._perform_post_request(url, payload, auth_token)

        if result.status_code == HTTP_CREATED:
            LOGGER.debug('Result: %s', HTTP_CREATED)
        else:
            LOGGER.info('Result: %s %s',
                        result.status_code,
                        result.text)

    def _get_endpoint(self, service):
        # get the uri of service endpoint
        endpoint = self._keystone.get_service_endpoint(
            service,
            Config.instance().CEILOMETER_URL_TYPE)
        return endpoint

    def _get_metric_id(self, alarm_name, severity, alarm_state):

        try:
            return True, self._meter_ids[str(alarm_name)]
        except KeyError as ke:
            LOGGER.warn(ke)
            LOGGER.warn('No known ID for %s', alarm_name)

            endpoint = self._get_endpoint("aodh")
            self._meter_ids[alarm_name] = \
                self._create_metric(alarm_name, endpoint, severity, alarm_state)

        return False, self._meter_ids[alarm_name]

    def _create_metric(self, alarm_name, endpoint, severity, alarm_state):
        url = "{}/v2/alarms/".format(endpoint)
        rule = {"meter_name": alarm_name,
                "evaluation_periods": 60,         
                "threshold": 10}
#                "query": list(resource_id)}
        payload = json.dumps({"state": alarm_state,
                              "name": alarm_name,
           #                   "severity": severity,
                              "type": "threshold",
                              "threshold_rule": rule,
                             })
        result = self._perform_post_request(url, payload, self._auth_token)
        metric_id = json.loads(result.text)['alarm_id']
        LOGGER.debug("metric_id=%s", metric_id)
        
        return metric_id

    def list_alarms(self, url, auth_token): 
        # then try to get entity as name 
        response = self._perform_get_request(url, auth_token)
        alarms = list(response)
        #LOGGER.warning("response: %s\n", response.text)
        return alarms[0]

    def check_alarms(self, alarm_list, alarm_name):
        result = False
        existing = self.perform_check(alarm_list, "name")
        
        if existing == alarm_name:
           result = True
        #LOGGER.warning('exists; %s', result)
        return result

    def check_severity(self, alarm_list, alarm_severity):
        result = None
        existing = self.perform_check(alarm_list, "severity")

        if existing == alarm_severity:
           result = existing
        else:
           result = alarm_severity
        #LOGGER.warning('exists; %s', result)
        return result

    def perform_check(self, alarm_list, variable):
        characters = '"[{],'
        name = False
        severity = False
        existing = None
        for char in characters:
            alarm_list = str(alarm_list.replace(char, ""))
        alarm_list = alarm_list.split(' ')
        for a in alarm_list:
            if variable == 'name':
               if name == True:
                  existing = a
                  name = False
               if a == 'name:':
                  name = True
            elif variable == 'severity':
                 if severity == True:
                    existing = a
                    severity = False
                 if a == "severity:":
                    severity = True
        return existing

    def get_alarm_state(self, severity):
        """Get the state of the alarm"""
        if severity == 'critical' or  severity == 'moderate':
           alarm_state = 'alarm'
        elif severity == 'low':
            alarm_state = 'ok'
        return alarm_state

        
    @classmethod
    def _perform_post_request(cls, url, payload, auth_token):
        """Perform the POST request"""

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
            LOGGER.debug('Returning response from _perform_post_request(): %s',
                         response.status_code)
        return response

    @classmethod
    def _perform_get_request(cls, url, auth_token):
        """Perform the GET request"""

        LOGGER.debug('Performing request to %s', url)

        # request headers
        headers = {'X-Auth-Token': auth_token,
                   'Content-type': 'application/json'}
        # perform request and return its result
        response = None
        try:
            LOGGER.debug(
                "Performing request to: %s with data=%s and headers=%s",
                url, headers)

            response = requests.get(
                url, headers=headers,
                timeout=(Config.instance().CEILOMETER_TIMEOUT / 1000.))
            LOGGER.info('Response: %s: %s',
                        response.status_code, response.text
                        )
        except RequestException as exc:
            LOGGER.error('aodh request error: %s', six.text_type(exc))
        finally:
            LOGGER.debug('Returning response from _perform_get_request(): %s',
                         response.status_code)
            return response

    @classmethod
    def _perform_update_request(cls,url, auth_token, payload):
        """Perform the PUT request"""

        LOGGER.debug('Performing request to %s', url)

        # request headers
        headers = {'X-Auth-Token': auth_token,
                   'Content-type': 'application/json'}
        # perform request and return its result
        response = None
        try:
            LOGGER.debug(
                "Performing request to: %s with data=%s and headers=%s",
                url, headers)   
            response = requests.put(
                 url, data=payload, headers=headers,
                 timeout=(Config.instance().CEILOMETER_TIMEOUT / 1000.))
            LOGGER.warning('put result: %s', response.text)
            LOGGER.info('Response: %s: %s',
                        response.status_code, response.text
                        )
        except RequestException as exc:
            LOGGER.error('aodh request error: %s', six.text_type(exc))
        finally:
            LOGGER.debug('Returning response from _perform_put_request(): %s',
                         response.status_code)
            return response
