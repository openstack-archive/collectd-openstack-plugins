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
"""Aodh collectd plugin implementation"""

from __future__ import unicode_literals

from collectd_ceilometer.aodh.sender import Sender
from collections import defaultdict
from collections import namedtuple

import datetime
import json
import logging
import six
import threading

LOGGER = logging.getLogger(__name__)


class Sample(namedtuple('Sample', ['metername', 'resource_id',
                                   'severity', 'message'])):
    """Sample data"""

    def to_payload(self):
        """Return a notifcation dictionary"""
        return {
            'metername': self.metername,
            'resource_id': self.resource_id,
            'severity': self.severity,
            'message': self.message,
      }


class SampleContainer(object):
    """Sample storage"""

    def __init__(self):
        self._lock = threading.Lock()
        self._data = defaultdict(list)

    def add(self, key, samples, limit):
        """Store list of samples under the key

        Store the list of samples under the given key. If number of stored
        samples is greater than the given limit, all the samples are returned
        and the stored samples are dropped. Otherwise None is returned.

        @param key      key of the samples
        @param samples  list of samples
        @param limit    sample list limit
        """
        with self._lock:
            current = self._data[key]
            current += samples
            if len(current) >= limit:
                self._data[key] = []
                return current
        return None

    def reset(self):
        """Reset stored sample

        Returns all samples and removes them from the container.
        """
        with self._lock:
            retval = self._data
            self._data = defaultdict(list)
        return retval


class Notifier(object):
    """Data collector"""

    def __init__(self, meters, config):
        self._samples = SampleContainer()
        self._meters = meters
        self._sender = Sender()
        self._config = config

    def notify(self, vl, data):
        """Collect data from collectd"""

        # take the plugin (specialized or default) for parsing the data
        notification = self._meters.get(vl.plugin)
        # prepare all data related to the sample
        host = notification.hostname(vl)
        metername = notification.meter_name(vl)
        message = notification.message(vl)
        severity = notification.severity(vl)
        resource_id = notification.resource_id(vl)
        timestamp = datetime.datetime.utcfromtimestamp(vl.time).isoformat()

        LOGGER.debug(
            'Writing: plugin="%s", message="%s", severity="%s", time="%s',
            vl.plugin, message, severity, timestamp)

        # store sample for every notification
        data = [
            Sample(
                metername=metername, resource_id=resource_id,
                severity=vl.severity, message=vl.message)
        ]

        # add data to cache and get the samples to send
        to_send = self._samples.add(metername, data, self._config.BATCH_SIZE)
        if to_send:
            self._send_data(metername, to_send, severity, message, resource_id)

    def flush(self):
        """Flush all pending notifications"""

        # get all stored notifications
        to_send = self._samples.reset()

        # send all cached notifications
        for key, samples in six.iteritems(to_send):
            if samples:
                self._send_data(key, samples)

    def _send_data(self, metername, to_send, severity, message, resource_id):
        """Send data to aodh"""

        LOGGER.debug('Sending %d samples of %s',
                     len(to_send), metername)

        # aodh sample
        payload = json.dumps([sample.to_payload() for sample in to_send])
        self._sender.send(metername, payload, severity, message, resource_id)
