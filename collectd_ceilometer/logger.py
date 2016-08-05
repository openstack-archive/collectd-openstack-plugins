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


import collections
import logging

import six


class CollectdLogHandler(logging.Handler):
    """A handler class for collectd plugin"""

    MAX_MESSAGE_LENGHT = 1023

    def __init__(self, collectd, level=logging.NOTSET):
        super(CollectdLogHandler, self).__init__(level=level)

        # hooks to be used by emit method
        self._hooks = collections.OrderedDict(
            sorted([(logging.DEBUG, collectd.debug),
                    (logging.INFO, collectd.info),
                    (logging.WARNING, collectd.warning),
                    (logging.ERROR, collectd.error),
                    (logging.CRITICAL, collectd.error)]))

        # hook to be used when verbose is False
        self._collectd_debug = collectd.debug
        self.addFilter(self)

    def emit(self, record):
        # pylint: disable=broad-except
        max_lenght = self.MAX_MESSAGE_LENGHT
        hook = getattr(record, 'hook', None)
        # filters out hook level befor formatting
        if hook:
            message = self.format(record)
            for i in range(0, len(message), max_lenght):
                hook(message[i:i + max_lenght])

    def filter(self, record):
        if record.levelno >= self.level:
            for hook_level, hook in six.iteritems(self._hooks):
                if record.levelno <= hook_level:
                    record.hook = hook
                    return 1
        return 0

    def set_verbose(self, verbose):
        if verbose:
            # debug messages has to be show as regular infos
            self._hooks[logging.DEBUG] = self._hooks[logging.INFO]
        else:
            # debug messages has to be show as debug infos
            self._hooks[logging.DEBUG] = self._collectd_debug
