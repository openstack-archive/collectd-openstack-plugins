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

import logging

from collectd_ceilometer.logger import CollectdLogHandler
from collectd_ceilometer.meters import MeterStorage
from collectd_ceilometer.settings import Config
from collectd_ceilometer.writer import Writer


LOG = logging.getLogger(__name__)


def main(collectd):
    # setup logging
    root_logger = logging.getLogger()
    root_logger.addHandler(CollectdLogHandler(collectd=collectd))
    root_logger.setLevel(logging.NOTSET)
    logging.getLogger("requests").setLevel(logging.WARNING)

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
    return instance


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
        # pylint: disable=broad-except
        try:
            self._config.read(cfg)
        except Exception:
            LOG.exception('Exception during config.')

    def init(self):
        """Initialization callback"""
        # pylint: disable=broad-except

        try:
            LOG.info('Initializing the collectd OpenStack python plugin')
            self._meters = MeterStorage(collectd=self._collectd)
            self._writer = Writer(self._meters, config=self._config)
        except Exception:
            LOG.exception('Exception during init.')

    def write(self, vl, data=None):
        """Collectd write callback"""
        # pylint: disable=broad-except
        # pass arguments to the writer
        try:
            self._writer.write(vl, data)
        except Exception:
            LOG.exception('Exception during write.')

    def shutdown(self):
        """Shutdown callback"""
        # pylint: disable=broad-except
        LOG.info("SHUTDOWN")
        try:
            self._writer.flush()
        except Exception:
            LOG.exception('Exception during shutdown.')
