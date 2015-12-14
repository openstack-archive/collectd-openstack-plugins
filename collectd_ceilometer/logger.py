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

# pylint: disable=import-error
import collectd
# pylint: enable=import-error
from collectd_ceilometer.settings import Config
import logging


class CollectdLogHandler(logging.Handler):
    """A handler class for collectd plugin"""

    priority_map = {
        logging.DEBUG: collectd.debug,
        logging.INFO: collectd.info,
        logging.WARNING: collectd.warning,
        logging.ERROR: collectd.error,
        logging.CRITICAL: collectd.error
    }
    cfg = Config.instance()

    def emit(self, record):
        try:
            msg = self.format(record)

            logger = self.priority_map.get(record.levelno, collectd.error)

            if self.cfg.VERBOSE and logging.DEBUG == record.levelno:
                logger = collectd.info
            logger(msg)

        except Exception as e:
            collectd.info("Exception in logger %s" % e)
