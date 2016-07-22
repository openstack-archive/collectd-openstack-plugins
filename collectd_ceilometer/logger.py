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

import logging
import traceback


class CollectdLogHandler(logging.Handler):
    """A handler class for collectd plugin"""

    def __init__(self, collectd, level=logging.NOTSET):
        super(CollectdLogHandler, self).__init__(level)
        self._collectd = collectd
        self._hooks = {
            logging.DEBUG: collectd.debug,
            logging.INFO: collectd.info,
            logging.WARNING: collectd.warning,
            logging.ERROR: collectd.error,
            logging.CRITICAL: collectd.error,
        }

    def emit(self, record):
        # pylint: disable=broad-except
        try:
            msg = self.format(record)
            logger = self._hooks[record.levelno]
            for i in range(0, len(msg), 1023):
                logger(msg[i:i + 1023])
        except Exception:
            traceback.print_exc()

    def set_verbose(self, verbose):
        if verbose:
            verbose_logger = self._collectd.info
        else:
            verbose_logger = self._collectd.debug
        self._hooks[logging.DEBUG] = verbose_logger
