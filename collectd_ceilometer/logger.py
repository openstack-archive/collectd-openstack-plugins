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

import logging
import traceback

from collectd_ceilometer.settings import Config


class CollectdLogHandler(logging.Handler):
    """A handler class for collectd plugin"""

    def __init__(self, collectd, level=logging.NOTSET):
        super(CollectdLogHandler, self).__init__(level=level)
        self.priority_map = {
            logging.DEBUG: collectd.debug,
            logging.INFO: collectd.info,
            logging.WARNING: collectd.warning,
            logging.ERROR: collectd.error,
            logging.CRITICAL: collectd.error
        }
        self.cfg = Config.instance()

    def emit(self, record):
        try:
            msg = self.format(record)

            if self.cfg.VERBOSE and logging.DEBUG == record.levelno:
                logger = self.priority_map.get(logging.INFO)

            else:
                logger = self.priority_map.get(record.levelno)
                if not logger:
                    logger = self.priority_map.get(logging.ERROR)

            # collectd limits log size to 1023B, this is workaround
            for i in range(0, len(msg), 1023):
                logger(msg[i:i + 1023])

        except Exception:
            logger = self.priority_map.get(logging.ERROR)
            exception = traceback.format_exc()
            logger("Exception in logger:\n%s" % exception)
