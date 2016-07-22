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


LOG = logging.getLogger(__name__)


class CollectdCeilometerPlugin(object):
    """Ceilometer plugin with collectd callbacks"""
    # NOTE: this is multithreaded class

    _meters = None
    _writer = None
    _instance = None
    _log_handler = None

    def config(self, cfg):
        """Configuration callback

        @param cfg configuration node provided by collectd
        """
        # pylint: disable=no-self-use
        from collectd_ceilometer.settings import Config
        Config.instance().read(cfg)

    def init(self):
        """Initialization callback"""

        LOG.info('Initializing the collectd OpenStack python plugin')
        from collectd_ceilometer.meters import MeterStorage
        from collectd_ceilometer.writer import Writer
        self._meters = MeterStorage()
        self._writer = Writer(self._meters)

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

    @classmethod
    def activate(cls):
        # pylint: disable=import-error
        import collectd
        # pylint: enable=import-error

        # Register plugin callbacks
        cls._instance = instance = cls()
        collectd.register_init(instance.init)
        collectd.register_config(instance.config)
        collectd.register_write(instance.write)
        collectd.register_shutdown(instance.shutdown)
        return instance
