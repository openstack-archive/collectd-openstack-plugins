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
"""Ceilometer collectd plugin implementation"""

from __future__ import division
from __future__ import unicode_literals

import collections
import logging
import threading

import requests
import six

from collectd_ceilometer.keystone_light import ClientV2 as keystoneClientV2
from collectd_ceilometer.keystone_light import KeystoneException
from collectd_ceilometer.settings import Config


LOGGER = logging.getLogger(__name__)

HTTP_UNAUTHORIZED = requests.codes['UNAUTHORIZED']
HTTP_CREATED = requests.codes['CREATED']

# Lookup dictionary for getting code status name from code status number
STATUS_NAMES = collections.defaultdict(
    lambda: 'UNKNOWN',
    {code_status: code_name
     for code_name, code_status in six.iteritems(requests.codes.__dict__)})


class Sender(object):
    """Sends the JSON serialized data to Ceilometer"""

    def __init__(self):
        """Create the Sender instance

        The cofinguration must be initialized before the object is created.
        """
        self._url_base = None
        self._keystone = None
        self._auth_token = None
        self._auth_lock = threading.Lock()
        self._failed_auth = False

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
                    self._keystone = keystoneClientV2(
                        auth_url=cfg.OS_AUTH_URL,
                        username=cfg.OS_USERNAME,
                        password=cfg.OS_PASSWORD,
                        tenant_name=cfg.OS_TENANT_NAME
                    )
                # store the authentication token
                self._auth_token = self._keystone.auth_token

                # get the uri of service endpoint
                endpoint = self._keystone.get_service_endpoint(
                    "ceilometer",
                    Config.instance().CEILOMETER_URL_TYPE)

                self._url_base = "{}/v2/meters/%s".format(endpoint)
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

    def send(self, metername, payload):
        """Send the payload to Ceilometer"""

        # get the auth_token
        auth_token = self._authenticate()

        # if auth_token is not set, there is nothing to do
        if auth_token is None:
            LOGGER.debug('Unable to send data. Not authenticated')
            return

        if self._url_base is None:
            LOGGER.debug(
                'Unable to send data. Missing endpoint from ident server')
            return

        # create request URL
        url = self._url_base % metername

        # send the POST request
        try:
            self._perform_request(url, payload, auth_token)

        except requests.exceptions.HTTPError as exc:
            response = exc.response

            # if the request failed due to an auth error
            if response.status_code == HTTP_UNAUTHORIZED:
                LOGGER.info('Renew authentication.')

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
                    self._perform_request(url, payload, auth_token)

            else:
                # This is an error and it has to be forwarded
                raise

    @staticmethod
    def _perform_request(url, data, auth_token):
        """Perform the POST request"""

        LOGGER.debug('Performing request to %s', url)

        # request headers
        headers = {'X-Auth-Token': auth_token,
                   'Content-type': 'application/json'}

        # perform request and return its result
        response = requests.post(
            url, data=data, headers=headers,
            timeout=(Config.instance().CEILOMETER_TIMEOUT / 1000.))

        # Raises exception if there was an error
        try:
            response.raise_for_status()

        except requests.exceptions.HTTPError:
            if response.status_code == HTTP_UNAUTHORIZED:
                log = LOGGER.info
            else:
                log = LOGGER.exception

            # always forward http errors
            raise

        else:
            if response.status_code == HTTP_CREATED:
                # reduce verbosity
                log = LOGGER.debug
            else:
                log = LOGGER.info
            return response

        finally:
            # Log out the result of the request
            status_name = STATUS_NAMES[response.status_code]
            log('Result: %d, %s, %r', status_name, response.status_code,
                response.text)
