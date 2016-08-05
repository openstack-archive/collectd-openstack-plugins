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
    min_level = _levels[0]
    max_level = _levels[-1]

    def __init__(self, collectd, level=logging.NOTSET):
        super(CollectdLogHandler, self).__init__(level=level)

        # hooks to be used by emit method
        self._hooks = [
            collectd.debug, collectd.info, collectd.warning, collectd.error]

    def emit(self, record):
        # clamp the level between given min and max
        level = max(self.min_level, min(record.levelno, self.max_level))
        # get the hook using binary search over valid levels
        hook = self._hooks[bisect.bisect_left(self._levels, level)]
        message = self.format(record)

        # collectd limits log size to 1023B, this is workaround
        step = self.max_message_lenght
        for i in range(0, len(message), step):
            hook(message[i:i + step])
