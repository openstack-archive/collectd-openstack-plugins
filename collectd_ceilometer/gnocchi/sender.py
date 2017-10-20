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
"""Gnocchi collectd plugin implementation"""

from __future__ import division
from __future__ import unicode_literals

import collectd_ceilometer
from collectd_ceilometer.common import sender as common_sender
from collectd_ceilometer.common.settings import Config

import json
import logging

LOGGER = logging.getLogger(__name__)
ROOT_LOGGER = logging.getLogger(collectd_ceilometer.__name__)


class Sender(common_sender.Sender):
    """Sends the JSON serialized data to Gnocchi"""

    def __init__(self):
        """Create the Sender instance

        The cofinguration must be initialized before the object is created.
        """
        super(Sender, self).__init__()
        self._meter_ids = {}

    def _on_authenticated(self):
        # get the uri of service endpoint
        endpoint = self._get_endpoint("gnocchi")

        self._url_base = "{}/v1/metric/%s/measures".format(endpoint)

    def _create_request_url(self, metername, **kwargs):
        unit = kwargs['unit']
        metric_id = self._get_metric_id(metername, unit)
        return self._url_base % (metric_id)

    def _handle_http_error(self, exc, metername,
                           payload, auth_token, **kwargs):
        response = exc.response
        if response.status_code == common_sender.Sender.HTTP_NOT_FOUND:
            LOGGER.debug("Received 404 error when submitting %s sample, \
                         creating a new metric",
                         metername)

            # create metric (endpoint, metername)
            unit = kwargs['unit']
            metric_id = self._get_metric_id(metername, unit)

            LOGGER.info('metername: %s, meter_id: %s', metername, metric_id)
            # Set a new url for the request
            url = self._url_base % (metric_id)
            # TODO(emma-l-foley): Add error checking
            # Submit the sample
            result = self._perform_request(url, payload, auth_token)
            if result.status_code == common_sender.Sender.HTTP_CREATED:
                LOGGER.debug('Result: %s', common_sender.Sender.HTTP_CREATED)
            else:
                LOGGER.info('Result: %s %s',
                            result.status_code,
                            result.text)

        else:
            raise exc

    def _get_endpoint(self, service):
        # get the uri of service endpoint
        endpoint = self._keystone.get_service_endpoint(
            service,
            Config.instance().CEILOMETER_URL_TYPE)
        return endpoint

    def _get_metric_id(self, metername, unit):

        try:
            return self._meter_ids[metername]
        except KeyError as ke:
            LOGGER.warn(ke)
            LOGGER.warn('No known ID for %s', metername)

            endpoint = self._get_endpoint("gnocchi")
            self._meter_ids[metername] = \
                self._create_metric(metername, endpoint, unit)

        return self._meter_ids[metername]

    def _create_metric(self, metername, endpoint, unit):
        url = "{}/v1/metric/".format(endpoint)
        payload = json.dumps({"name": metername,
                              "unit": unit,
                              })
        result = self._perform_request(url, payload, self._auth_token)
        metric_id = json.loads(result.text)['id']
        LOGGER.debug("metric_id=%s", metric_id)
        return metric_id
