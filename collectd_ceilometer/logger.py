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
import traceback


class CollectdLogHandler(logging.Handler):
    """A handler class for collectd plugin"""

    # this is the maximum message lenght supported by collectd
    # messages longer than this size has to be split
    max_message_lenght = 1023

    # sorted list of logging level numbers to be used to look for hooks
    # this list is sorted because it is used by bisec function to look for
    # the best hook for any given message logging level
    _levels = (logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR)

    # all messages with a logging level lesser of greater to these are going
    # to be clamped inside this interval
    min_level = _levels[0]
    max_level = _levels[-1]

    def __init__(self, collectd, level=logging.NOTSET):
        super(CollectdLogHandler, self).__init__(level=level)

        # bind hooks to be used by emit method. Every logging level in _levels
        # must have an hook in the same position here.
        self._hooks = (
            collectd.debug, collectd.info, collectd.warning, collectd.error)

    def emit(self, record):
        "Called by loggers when a message has to be sent to collecd."
        # pylint: disable=broad-except

        # clamp the level between given min and max and
        # get the hook using binary search over valid levels
        level = max(self.min_level, min(record.levelno, self.max_level))

        try:
            message = self.format(record)
        except Exception:
            message = "Exception in logger:\n{}".format(traceback.format_exc())

        self.emit_message(message, level)

    def emit_message(self, message, level):
        hook = self._hooks[bisect.bisect_left(self._levels, level)]

        # collectd limits log size to 1023B, this is workaround
        for i in range(0, len(message), self.max_message_lenght):
            hook(message[i:i + self.max_message_lenght])
