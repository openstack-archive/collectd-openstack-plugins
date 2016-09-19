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

    # pylint: disable=no-member
    cfg = Config.instance()

    def __init__(self, collectd, level=logging.NOTSET):
        super(CollectdLogHandler, self).__init__(level=level)
        self.priority_map = {
            logging.DEBUG: collectd.debug,
            logging.INFO: collectd.info,
            logging.WARNING: collectd.warning,
            logging.ERROR: collectd.error,
            logging.CRITICAL: collectd.error
        }

    def emit(self, record):
        try:
            self.emit_message(
                message=self.format(record),
                level=record.levelno)
        # pylint: disable=broad-except
        except Exception:
            self.emit_message(
                message="Error emitting message:\n{}".format(
                    traceback.format_exc()),
                level=logging.ERROR)

    def emit_message(self, message, level):
        if self.cfg.VERBOSE and level == logging.DEBUG:
            level = logging.INFO
        elif level not in self.priority_map:
            level = logging.ERROR
        hook = self.priority_map[level]

        # collectd limits log size to 1023B, this is workaround
        for i in range(0, len(message), 1023):
            hook(message[i:i + 1023])
