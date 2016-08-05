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

import six


class CollectdLogHandler(logging.Handler):
    """A handler class for collectd plugin"""

    # this maps the name of collecd log hooks to the logging levels supported
    # by this logging handler. Other levels are going to rounded to the nearest
    # level
    collectd_log_hooks = {
        logging.DEBUG: 'debug',
        logging.INFO: 'info',
        logging.WARNING: 'warning',
        logging.ERROR: 'error'}

    # this is the maximum message lenght supported by collectd
    # messages longer than this size has to be split
    max_message_lenght = 1023

    def __init__(self, collectd, level=logging.NOTSET):
        super(CollectdLogHandler, self).__init__(level=level)

        hooks = sorted(six.iteritems(self.collectd_log_hooks))

        # bind hooks to be used by emit method. Every logging level in _levels
        # must have an hook in the same position here.
        self._hooks = tuple(getattr(collectd, name) for _, name in hooks)

        # sorted list of logging level numbers to be used to look for hooks
        # this list is sorted because it is used by bisec function to look for
        # the best hook for any given message logging level
        self._levels = levels = tuple(level for level, _ in hooks)

        # all messages with a logging level lesser of greater to these are going
        # to be clamped inside this interval
        self.min_level = levels[0]
        self.max_level = levels[-1]

    def emit(self, record):
        "Called by loggers when a message has to be sent to collecd."

        # format the message
        message = self.format(record)

        # clamp the level between given min and max and
        # get the hook using binary search over valid levels
        level = max(self.min_level, min(record.levelno, self.max_level))
        hook = self._hooks[bisect.bisect_left(self._levels, level)]

        # collectd limits log size to 1023B, this is workaround
        step = self.max_message_lenght
        for i in range(0, len(message), step):
            hook(message[i:i + step])
