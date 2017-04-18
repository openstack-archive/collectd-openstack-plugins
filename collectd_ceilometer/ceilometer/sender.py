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

import logging

from collectd_ceilometer.common import sender as common_sender
from collectd_ceilometer.common.settings import Config


LOGGER = logging.getLogger(__name__)


class Sender(common_sender.Sender):
    """Sends the JSON serialized data to Ceilometer"""

    def __init__(self):
        """Create the Sender instance

        The cofinguration must be initialized before the object is created.
        """
        super(Sender, self).__init__()

    def _on_authenticated(self):
        endpoint = self._keystone.get_service_endpoint(
            "ceilometer",
            Config.instance().CEILOMETER_URL_TYPE)

        self._url_base = "{}/v2/meters/%s".format(endpoint)
        pass

    def _create_request_url(self, metername, **kwargs):
        return "post", self._url_base % metername

    def _handle_http_error(self, exc, metername, payload, auth_token, **kwargs):
        raise exc
