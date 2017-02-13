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

from __future__ import unicode_literals

from collectd_ceilometer.aodh.sender import Sender

import datetime
import logging

LOGGER = logging.getLogger(__name__)


class Notifier(object):
    """Aodh notifier."""

    def __init__(self, meters, config):
        """Initialize Notifier."""
        self._meters = meters
        self._sender = Sender()
        self._config = config

    def notify(self, vl, data):
        """Collect data from collectd."""
        # take the plugin (specialized or default) for parsing the data
        notification = self._meters.get(vl.plugin)
        # prepare all data related to the sample
        metername = notification.meter_name(vl)
        message = notification.message(vl)
        severity = notification.severity(vl)
        resource_id = notification.resource_id(vl)
        timestamp = datetime.datetime.utcfromtimestamp(vl.time).isoformat()

        LOGGER.debug(
            'Writing: plugin="%s", message="%s", severity="%s", time="%s',
            vl.plugin, message, severity, timestamp)

        self._send_data(metername, severity, resource_id)

    def _send_data(self, metername, severity, resource_id):
        """Send data to Aodh."""
        LOGGER.debug('Sending alarm for %s',  metername)
        self._sender.send(metername, severity, resource_id)
