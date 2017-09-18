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

from __future__ import unicode_literals

from collectd_ceilometer.common.meters.storage import SampleContainer
from collectd_ceilometer.gnocchi import sender as gnocchi_sender
from collections import namedtuple
import datetime
import json
import logging
import six

LOGGER = logging.getLogger(__name__)


class Sample(namedtuple('Sample', ['value', 'timestamp', 'meta',
                                   'unit', 'metername'])):
    """Sample data"""

    def to_payload(self):
        """Return a payload dictionary"""
        return {
            'value': self.value,
            'timestamp': self.timestamp,
        }


class Writer(object):
    """Data collector"""

    def __init__(self, meters, config):
        self._meters = meters
        self._samples = SampleContainer()
        self._sender = gnocchi_sender.Sender()
        self._config = config

    def write(self, vl, data):
        """Collect data from collectd

        example of vl: collectd.Values(type='vmpage_action',
        type_instance='interleave_hit',plugin='numa',plugin_instance='node0',
        host='localhost',time=1443092594.625033,interval=10.0,values=[21383])
        """
        # take the plugin (specialized or default) for parsing the data
        plugin = self._meters.get(vl.plugin)
        # prepare all data related to the sample
        metername = "{}@{}".format(
            plugin.resource_id(vl), plugin.meter_name(vl))

        unit = plugin.unit(vl)
        timestamp = datetime.datetime.utcfromtimestamp(vl.time).isoformat()

        LOGGER.debug(
            'Writing: plugin="%s", metername="%s"', vl.plugin, metername)

        # store sample for every value
        data = [
            Sample(
                value=value, timestamp=timestamp, meta=vl.meta,
                unit=unit, metername=metername
                )
            for value in vl.values
        ]

        # add data to cache and get the samples to send
        to_send = self._samples.add(metername, data,
                                    self._config.BATCH_SIZE)
        if to_send:
            self._send_data(metername, to_send, unit)

    def flush(self):
        """Flush all pending samples"""

        # get all stored samples
        to_send = self._samples.reset()

        # send all cached samples
        for key, samples in six.iteritems(to_send):
            if samples:
                self._send_data(key, samples)

    def _send_data(self, metername, to_send, unit=None):
        """Send data to gnocchi"""

        LOGGER.debug('Sending %d samples of %s',
                     len(to_send), metername)

        # gnocchi samples
        payload = json.dumps([sample.to_payload() for sample in to_send])

        self._sender.send(metername, payload, unit=unit)
