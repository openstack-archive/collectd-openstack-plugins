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


import bisect
import logging


class CollectdLogHandler(logging.Handler):
    """A handler class for collectd plugin"""

    max_message_lenght = 1023

    _levels = (logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR)
    _min_level = _levels[0]
    _max_level = _levels[-1]

    def __init__(self, collectd, level=logging.NOTSET):
        super(CollectdLogHandler, self).__init__(level=level)

        # hooks to be used by emit method
        self._hooks = [
            collectd.debug, collectd.info, collectd.warning, collectd.error]
        self.addFilter(self)

    def emit(self, record):
        # clamp the level to min and max
        level = max(self._min_level, min(record.levelno, self._max_level))
        hook = self._hooks[bisect.bisect_left(self._levels, level)]
        message = self.format(record)
        step = self.max_message_lenght
        for i in range(0, len(message), step):
            hook(message[i:i + step])

    def filter(self, record):
        return record.levelno >= self.level

    def set_verbose(self, verbose):
        if verbose:
            self._min_level = logging.INFO
        else:
            self._min_level = logging.DEBUG
