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

from __future__ import unicode_literals

from collectd_ceilometer.sender import Sender
from collectd_ceilometer.settings import Config
from collections import defaultdict
from collections import namedtuple
import json
import logging
import six
import threading
import time

LOGGER = logging.getLogger(__name__)


class Sample(namedtuple('Sample', ['value', 'timestamp', 'meta',
                                   'resource_id', 'unit', 'metername'])):
    """Sample data"""

    def to_payload(self):
        """Return a payload dictionary"""
        return {
            'counter_name': self.metername,
            'counter_type': 'gauge',
            'counter_unit': self.unit,
            'counter_volume': self.value,
            'timestamp': self.timestamp,
            'resource_metadata': self.meta,
            'source': 'collectd',
            'resource_id': self.resource_id,
        }


class SampleContainer(object):
    """Sample storage"""

    def __init__(self):
        self._lock = threading.Lock()
        self._data = defaultdict(list)

    def add(self, key, samples, limit):
        """Store list of samples under the key

        Store the list of samples under the given key. If numer of stored
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
        """Reset stored samples

        Returns all samples and removes them from the container.
        """
        with self._lock:
            retval = self._data
            self._data = defaultdict(list)
        return retval


class Writer(object):
    """Data collector"""

    def __init__(self, meters):
        self._meters = meters
        self._samples = SampleContainer()
        self._sender = Sender()

    def write(self, vl, data):
        """Collect data from collectd

        example of vl: collectd.Values(type='vmpage_action',
        type_instance='interleave_hit',plugin='numa',plugin_instance='node0',
        host='localhost',time=1443092594.625033,interval=10.0,values=[21383])
        """

        # take the plugin (specialized or default) for parsing the data
        plugin = self._meters.get(vl.plugin)
        # prepare all data related to the sample
        resource_id = plugin.resource_id(vl)
        metername = plugin.meter_name(vl)
        unit = plugin.unit(vl)
        timestamp = time.asctime(time.gmtime(vl.time))

        LOGGER.debug(
            'Writing: plugin="%s", metername="%s", unit="%s"',
            vl.plugin, metername, unit)

        # store sample for every value
        data = [
            Sample(
                value=value, timestamp=timestamp, meta=vl.meta,
                resource_id=resource_id, unit=unit, metername=metername)
            for value in vl.values
        ]

        # add data to cache and get the samples to send
        to_send = self._samples.add(metername, data,
                                    Config.instance().BATCH_SIZE)
        if to_send:
            self._send_data(metername, to_send)

    def flush(self):
        """Flush all pending samples"""

        # get all stored samples
        to_send = self._samples.reset()

        # send all cached samples
        for key, samples in six.iteritems(to_send):
            if samples:
                self._send_data(key, samples)

    def _send_data(self, metername, to_send):
        """Send data to ceilometer"""

        LOGGER.debug('Sending %d samples of %s',
                     len(to_send), metername)

        # ceilometer samples
        payload = json.dumps([sample.to_payload() for sample in to_send])
        self._sender.send(metername, payload)
