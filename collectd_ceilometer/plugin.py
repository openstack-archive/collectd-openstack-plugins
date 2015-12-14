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
"""Ceilometer collectd plugin"""

from __future__ import unicode_literals

# pylint: disable=import-error
import collectd
# pylint: enable=import-error

from collectd_ceilometer.logger import CollectdLogHandler
from collectd_ceilometer.meters import MeterStorage
from collectd_ceilometer.settings import Config
from collectd_ceilometer.writer import Writer
import logging

logging.getLogger().addHandler(CollectdLogHandler())
logging.getLogger().setLevel(logging.NOTSET)
LOGGER = logging.getLogger(__name__)


class Plugin(object):
    """Ceilometer plugin with collectd callbacks"""
    # NOTE: this is multithreaded class

    def __init__(self):
        self._meters = None
        self._writer = None
        logging.getLogger("requests").setLevel(logging.WARNING)

    def config(self, cfg):
        """Configuration callback

        @param cfg configuration node provided by collectd
        """
        # pylint: disable=no-self-use
        Config.instance().read(cfg)

    def init(self):
        """Initialization callback"""

        collectd.info('Initializing the collectd OpenStack python plugin')
        self._meters = MeterStorage()
        self._writer = Writer(self._meters)

    def write(self, vl, data=None):
        """Collectd write callback"""
        # pylint: disable=broad-except
        # pass arguments to the writer
        try:
            self._writer.write(vl, data)
        except Exception as exc:
            if collectd is not None:
                collectd.error('Exception during write: %s' % exc)

    def shutdown(self):
        """Shutdown callback"""
        # pylint: disable=broad-except
        collectd.info("SHUTDOWN")
        try:
            self._writer.flush()
        except Exception as exc:
            if collectd is not None:
                collectd.error('Exception during shutdown: %s' % exc)


# The collectd plugin instance
# pylint: disable=invalid-name
instance = Plugin()
# pylint: enable=invalid-name

# Register plugin callbacks
collectd.register_init(instance.init)
collectd.register_config(instance.config)
collectd.register_write(instance.write)
collectd.register_shutdown(instance.shutdown)
