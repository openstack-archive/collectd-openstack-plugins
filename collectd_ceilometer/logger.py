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


class CollectdLogHandler(logging.Handler):
    """A handler class for collectd plugin"""

    MAX_MESSAGE_LENGHT = 1023

    def __init__(self, collectd, level=logging.NOTSET):
        super(CollectdLogHandler, self).__init__(level=level)

        # hooks to be used by emit method
        self._hooks = {
            logging.DEBUG: collectd.debug,
            logging.INFO: collectd.info,
            logging.WARNING: collectd.warning,
            logging.ERROR: collectd.error,
            logging.CRITICAL: collectd.error}

        # hook to be used when verbose is False
        self._collectd_debug = collectd.debug

    def emit(self, record):
        # pylint: disable=broad-except
        try:
            max_lenght = self.MAX_MESSAGE_LENGHT
            logger = self._hooks[record.levelno]
            message = self.format(record)
            for i in range(0, len(message), max_lenght):
                logger(message[i:i + max_lenght])
        except Exception:
            traceback.print_exc()

    def set_verbose(self, verbose):
        if verbose:
            # debug messages has to be show as regular infos
            verbose_logger = self._hooks[logging.INFO]
        else:
            # debug messages has to be show as debug infos
            verbose_logger = self._collectd_debug
        self._hooks[logging.DEBUG] = verbose_logger
