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
"""Common collectd plugin sender implementation"""

from __future__ import division
from __future__ import unicode_literals

import logging
import threading

import requests
import six
import time

from collectd_openstack.common.keystone_light import ClientV3
from collectd_openstack.common.keystone_light import KeystoneException
from collectd_openstack.common.settings import Config


LOGGER = logging.getLogger(__name__)


# Lookup dictionary for getting code status name from code status number
# this is the inverse mapping of requests.codes dictionary
STATUS_NAMES = {
    status_code: status_name
    for status_name, status_code in six.iteritems(requests.codes.__dict__)}


def get_status_name(status_code):
    """Get an human friendly name for given status code"""
    return STATUS_NAMES.get(status_code, str(status_code))


class Sender(object):
    """Sends the JSON serialized data to Gnocchi/Aodh"""

    HTTP_CREATED = requests.codes['CREATED']
    HTTP_UNAUTHORIZED = requests.codes['UNAUTHORIZED']
    HTTP_NOT_FOUND = requests.codes['NOT_FOUND']

    def __init__(self):
        """Create the Sender instance

        The configuration must be initialized before the object is created.
        """
        self._url_base = None
        self._keystone = None
        self._auth_token = None
        self._auth_lock = threading.Lock()
        self._failed_auth = False

    def _on_authenticated(self):
        pass

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

                self._on_authenticated()

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

    def _create_request_url(self, metername, *args, **kwargs):
        return None

    def _handle_http_error(self, exc, metername, payload, auth_token):
        raise exc

    def send(self, metername, payload, retry=0, **kwargs):
        """Send the payload to Gnocchi/Aodh

        :param retry: The number of times to attempt sending when the request
            times out. Default is 0, which does not retry.
        """

        # get the auth_token
        auth_token = self._authenticate()
        LOGGER.info('Auth_token: %s', auth_token)

        # if auth_token is not set, there is nothing to do
        if auth_token is None:
            LOGGER.debug('Unable to send data. Not authenticated')
            return

        if self._url_base is None:
            LOGGER.debug(
                'Unable to send data. Missing endpoint from ident server')
            return

        # create request URL
        url = self._create_request_url(metername, **kwargs)
        if url is None:
            LOGGER.debug("_create_request_url returned None, aborting send")
            return

        # send the POST request
        try:
            return self._perform_request(url, payload, auth_token)
        except requests.exceptions.HTTPError as exc:
            response = exc.response

            # if the request failed due to an auth error
            if response.status_code == Sender.HTTP_UNAUTHORIZED:
                LOGGER.info('Renewing authentication.')

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
                    return self._perform_request(url, payload, auth_token)
            else:
                # This is an error and it has to be forwarded
                self._handle_http_error(exc, metername, payload,
                                        auth_token, **kwargs)

        except requests.exceptions.ReadTimeout as rto:
            if retry > 0:
                LOGGER.debug("ReadTimeout Error.. trying again...")
                time.sleep(1)
                self.send(metername, payload, retry=(retry - 1), **kwargs)
            else:
                LOGGER.error("Too many timeouts trying to send\n", rto)
                raise rto

    @classmethod
    def _perform_request(cls, url, payload, auth_token, req_type="post"):
        """Perform the POST/PUT request."""
        LOGGER.debug('Performing request to %s, payload=%s, req_type = %s' %
                     (url, payload, req_type))

        # request headers
        headers = {'X-Auth-Token': auth_token,
                   'Content-type': 'application/json'}
        # perform request and return its result
        if req_type == "get":
            response = requests.get(
                url, params=payload, headers=headers,
                timeout=(Config.instance().CEILOMETER_TIMEOUT / 1000.))
        elif req_type == "put":
            response = requests.put(
                url, data=payload, headers=headers,
                timeout=(Config.instance().CEILOMETER_TIMEOUT / 1000.))
        else:
            response = requests.post(
                url, data=payload, headers=headers,
                timeout=(Config.instance().CEILOMETER_TIMEOUT / 1000.))

        # Raises exception if there was an error
        try:
            response.raise_for_status()
        # pylint: disable=broad-except
        except Exception:
            exc_info = 1
            raise
        else:
            exc_info = 0
        finally:
            # Log out the result of the request for debugging purpose
            LOGGER.debug(
                'Result: %s, %d, %r',
                get_status_name(response.status_code),
                response.status_code, response.text, exc_info=exc_info)
        return response
