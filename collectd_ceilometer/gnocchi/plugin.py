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
"""Gnocchi collectd plugin"""

import logging

try:
    # pylint: disable=import-error
    import collectd
    # pylint: enable=import-error
except ImportError:
    collectd = None  # when running unit tests collectd is not avaliable

import collectd_ceilometer
from collectd_ceilometer.common.logger import CollectdLogHandler
from collectd_ceilometer.common.meters import MeterStorage
from collectd_ceilometer.common.settings import Config
from collectd_ceilometer.gnocchi.writer import Writer

LOGGER = logging.getLogger(__name__)
ROOT_LOGGER = logging.getLogger(collectd_ceilometer.__name__)


def register_plugin(collectd):
    "Bind plugin hooks to collectd and viceversa"

    config = Config.instance()

    # Setup loggging
    log_handler = CollectdLogHandler(collectd=collectd, config=config)
    ROOT_LOGGER.addHandler(log_handler)
    ROOT_LOGGER.setLevel(logging.DEBUG)

    # Creates collectd plugin instance
    instance = Plugin(collectd=collectd, config=config)

    # Register plugin callbacks
    collectd.register_init(instance.init)
    collectd.register_config(instance.config)
    collectd.register_write(instance.write)
    collectd.register_shutdown(instance.shutdown)


class Plugin(object):
    """Gnocchi plugin with collectd callbacks"""
    # NOTE: this is multithreaded class

    def __init__(self, collectd, config):
        self._config = config
        self._meters = MeterStorage(collectd=collectd)
        self._writer = Writer(self._meters, config=config)

    def config(self, cfg):
        """Configuration callback

        @param cfg configuration node provided by collectd
        """
        # pylint: disable=no-self-use
        self._config.read(cfg)

    def init(self):
        """Initialization callback"""

        collectd.info('Initializing the collectd OpenStack python plugin')
        self._meters = MeterStorage(collectd=collectd)
        # self._writer = Writer(self._meters)

    def write(self, vl, data=None):
        """Collectd write callback"""
        self._writer.write(vl, data)

    def shutdown(self):
        """Shutdown callback"""
        LOGGER.info("SHUTDOWN")
        self._writer.flush()


if collectd:
    register_plugin(collectd=collectd)
