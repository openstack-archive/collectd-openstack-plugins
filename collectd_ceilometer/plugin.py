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

import logging

import collectd_ceilometer
from collectd_ceilometer.logger import CollectdLogHandler
from collectd_ceilometer.meters import MeterStorage
from collectd_ceilometer.settings import Config
from collectd_ceilometer.writer import Writer


LOGGER = logging.getLogger(__name__)

# setup logging
ROOT_LOGGER = logging.getLogger(collectd_ceilometer.__name__)


def setup_plugin(collectd):
    ROOT_LOGGER.addHandler(CollectdLogHandler(collectd=collectd))
    ROOT_LOGGER.setLevel(logging.NOTSET)

    config = Config.instance()

    # The collectd plugin instance
    # pylint: disable=invalid-name
    instance = Plugin(collectd=collectd, config=config)
    # pylint: enable=invalid-name

    # Register plugin callbacks
    collectd.register_init(instance.init)
    collectd.register_config(instance.config)
    collectd.register_write(instance.write)
    collectd.register_shutdown(instance.shutdown)


class Plugin(object):
    """Ceilometer plugin with collectd callbacks"""
    # NOTE: this is multithreaded class

    def __init__(self, collectd, config):
        self._meters = None
        self._writer = None
        self._collectd = collectd
        self._config = config

    def config(self, cfg):
        """Configuration callback

        @param cfg configuration node provided by collectd
        """

        config = self._config
        config.read(cfg)

        writer = self._writer
        if writer:
            writer.batch_size = config.BATCH_SIZE

    def init(self):
        """Initialization callback"""

        LOGGER.info('Initializing the collectd OpenStack python plugin')
        self._meters = MeterStorage(collectd=self._collectd)
        self._writer = Writer(self._meters, config=self._config)

    def write(self, vl, data=None):
        """Collectd write callback"""
        self._writer.write(vl, data)

    def shutdown(self):
        """Shutdown callback"""
        LOGGER.info("SHUTDOWN")
        self._writer.flush()


try:
    # pylint: disable=import-error
    import collectd
    # pylint: enable=import-error
except ImportError:
    pass  # when running unit tests collectd is not avaliable
else:
    setup_plugin(collectd=collectd)
