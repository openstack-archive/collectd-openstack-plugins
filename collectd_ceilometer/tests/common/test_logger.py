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

import logging
import unittest

import mock

from collectd_ceilometer.common.logger import CollectdLogHandler
from collectd_ceilometer.common.settings import Config
from collectd_ceilometer.tests.mocking import patch_class


class MockedCollectd(object):

    def debug(self, record):
        "Hook for debug messages"

    def info(self, record):
        "Hook for info messages"

    def warning(self, record):
        "Hook for warning messages"

    def error(self, record):
        "Hook for error messages"


def make_record(
        name=__name__, level=logging.INFO, pathname=__file__, lineno=0,
        msg="", args=tuple(), exc_info=None, func=None):
    "Creates a log record as done by loggers."
    record = logging.LogRecord(
        name=name, level=level, pathname=pathname, lineno=lineno, msg=msg,
        args=args, exc_info=exc_info, func=func)
    return record


class TestCollectdLogHandler(unittest.TestCase):

    @patch_class(MockedCollectd)
    def setUp(self, collectd):
        """Set up some attributes which are common to all tests."""
        super(TestCollectdLogHandler, self).setUp()

        self.collectd = collectd
        self.config = Config.instance()
        self.handler = CollectdLogHandler(collectd=self.collectd,
                                          config=self.config)
        self.logger = logging.Logger('some_logger')
        self.logger.addHandler(self.handler)

    def test_registered_hooks_when_init(self):

        # Then collectd logging hooks are registered
        # pylint: disable=protected-access
        self.assertEqual(
            {logging.DEBUG: self.collectd.debug,
             logging.INFO: self.collectd.info,
             logging.WARNING: self.collectd.warning,
             logging.ERROR: self.collectd.error,
             logging.FATAL: self.collectd.error},
            self.handler.priority_map)

    def test_debug_when_emit(self):

        # Given
        record = make_record(msg="message", level=logging.DEBUG)

        # When a debug record is emitted
        self.handler.emit(record=record)

        # Then debug hook is called
        self.collectd.debug.assert_called_once_with("message")

    def test_verbose_debug_when_emit(self):
        # Given
        self.config.VERBOSE = True
        record = make_record(msg="message", level=logging.DEBUG)

        # When an info record is emitted
        self.handler.emit(record=record)

        # Then info hook is called
        self.collectd.info.assert_called_once_with("message")

    def test_info_when_emit(self):
        # Given
        record = make_record(msg="message", level=logging.INFO)

        # When an info record is emitted
        self.handler.emit(record=record)

        # Then info hook is called
        self.collectd.info.assert_called_once_with("message")

    def test_warning_when_emit(self):
        # Given
        record = make_record(msg="message", level=logging.WARNING)

        # When a warning record is emitted
        self.handler.emit(record=record)

        # Then info warning is called
        self.collectd.warning.assert_called_once_with("message")

    def test_error_when_emit(self):
        # Given
        record = make_record(msg="message", level=logging.ERROR)

        # When an error record is emitted
        self.handler.emit(record=record)

        # Then error hook is called
        self.collectd.error.assert_called_once_with("message")

    def test_fatal_when_emit(self):
        # Given
        record = make_record(msg="message", level=logging.FATAL)

        # When a fatal record is emitted
        self.handler.emit(record=record)

        # Then error hook is called
        self.collectd.error.assert_called_once_with("message")

    def test_long_message_when_emit(self):
        # Given
        long_message = "LONG " * 20 + "MESSAGE."
        self.handler.max_message_length = 10
        record = make_record(msg=long_message)

        # When a long message is emitted
        self.handler.emit(record=record)

        # Then info hook is called n times with split message
        self.collectd.info.assert_has_calls([
            mock.call(long_message[i:i + 10])
            for i in range(0, len(long_message), 10)])

    def test_when_logger_debug(self):

        # When debug is called
        self.config.VERBOSE = False
        self.logger.debug('Say cheese: %s %d', 'string', 10)

        # Then debug hook is called
        self.collectd.debug.assert_called_once_with('Say cheese: string 10')
        self.collectd.info.assert_not_called()

    def test_verbose_when_logger_info(self):

        # When debug is called
        self.config.VERBOSE = True
        self.logger.debug('Say cheese: %s %d', 'string', 10)

        # Then info hook is called
        self.collectd.info.assert_called_once_with('Say cheese: string 10')
        self.collectd.debug.assert_not_called()

    def test_non_verbose_when_logger_info(self):
        # Given
        self.handler.verbose = False

        # When debug is called
        self.logger.debug('Say cheese: %s %d', 'string', 10)

        # Then debug hook is called
        self.collectd.debug.assert_called_once_with('Say cheese: string 10')
        self.collectd.info.assert_not_called()

    def test_info_from_logger(self):

        # When info is called
        self.logger.info('Say cheese: %s %d', 'string', 10)

        # Then info hook is called
        self.collectd.info.assert_called_once_with('Say cheese: string 10')

    def test_warning_from_logger(self):

        # When warning is called
        self.logger.warning('Say cheese: %s %d', 'string', 10)

        # Then warning hook is called
        self.collectd.warning.assert_called_once_with('Say cheese: string 10')

    def test_error_from_logger(self):

        # When error is called
        self.logger.error('Say cheese: %s %d', 'string', 10)

        # Then error hook is called
        self.collectd.error.assert_called_once_with('Say cheese: string 10')

    def test_fatal_from_logger(self):

        # When fatal is called
        self.logger.fatal('Say cheese: %s %d', 'string', 10)

        # Then error hook is called
        self.collectd.error.assert_called_once_with('Say cheese: string 10')
