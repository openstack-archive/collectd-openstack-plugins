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

    _instance = None
    _priority_map = {}

    def emit(self, record):
        try:
            msg = self.format(record)

            try:
                logger = self._priority_map[record.levelno]
            except KeyError:
                logger = self._priority_map[logging.ERROR]

            # collectd limits log size to 1023B, this is workaround
            for i in range(0, len(msg), 1023):
                logger(msg[i:i + 1023])

        except Exception:
            traceback.print_exc()

    @classmethod
    def activate(cls):
        # pylint: disable=import-error
        import collectd
        # pylint: enable=import-error

        from collectd_ceilometer.settings import Config
        if Config.instance().VERBOSE:
            log_debug = collectd.info
        else:
            log_debug = collectd.debug

        cls._priority_map.update([
            (logging.INFO, collectd.info),
            (logging.WARNING, collectd.warning),
            (logging.ERROR, collectd.error),
            (logging.CRITICAL, collectd.error),
            (logging.DEBUG, log_debug)])

        instance = cls._instance
        if not instance:
            cls._instance = instance = cls()
        root_logger = logging.getLogger()
        if instance not in root_logger.handlers:
            root_logger.addHandler(instance)
            root_logger.setLevel(logging.NOTSET)
            logging.getLogger("requests").setLevel(logging.WARNING)
