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

from collectd_ceilometer.logger import CollectdLogHandler


mock_collectd = mock.patch(
    "collectd_ceilometer.tests.test_logger.MockedCollectd", spec=True)


class TestCollectdLogHandler(unittest.TestCase):

    @mock_collectd
    def test_registered_hooks_when_init(self, collectd):
        # When CollectdLogHandler is created
        handler = CollectdLogHandler(collectd=collectd)

        # Then collectd logging hooks are registered
        # pylint: disable=protected-access
        self.assertEqual(
            (collectd.debug, collectd.info, collectd.warning, collectd.error),
            handler._hooks)

    @mock_collectd
    def test_debug_when_emit(self, collectd):
        # Given
        handler = CollectdLogHandler(collectd=collectd)
        record = make_record(msg="message", level=logging.DEBUG)

        # When a debug record is emitted
        handler.emit(record=record)

        # Then debug hook is called
        collectd.debug.assert_called_once_with("message")

    @mock_collectd
    def test_verbose_debug_when_emit(self, collectd):
        # Given
        handler = CollectdLogHandler(collectd=collectd)
        handler.min_level = logging.INFO
        record = make_record(msg="message", level=logging.DEBUG)

        # When an info record is emitted
        handler.emit(record=record)

        # Then info hook is called
        collectd.info.assert_called_once_with("message")

    @mock_collectd
    def test_info_when_emit(self, collectd):
        # Given
        handler = CollectdLogHandler(collectd=collectd)
        record = make_record(msg="message", level=logging.INFO)

        # When an info record is emitted
        handler.emit(record=record)

        # Then info hook is called
        collectd.info.assert_called_once_with("message")

    @mock_collectd
    def test_warning_when_emit(self, collectd):
        # Given
        handler = CollectdLogHandler(collectd=collectd)
        record = make_record(msg="message", level=logging.WARNING)

        # When a warning record is emitted
        handler.emit(record=record)

        # Then info warning is called
        collectd.warning.assert_called_once_with("message")

    @mock_collectd
    def test_error_when_emit(self, collectd):
        # Given
        handler = CollectdLogHandler(collectd=collectd)
        record = make_record(msg="message", level=logging.ERROR)

        # When an error record is emitted
        handler.emit(record=record)

        # Then error hook is called
        collectd.error.assert_called_once_with("message")

    @mock_collectd
    def test_fatal_when_emit(self, collectd):
        # Given
        handler = CollectdLogHandler(collectd=collectd)
        record = make_record(msg="message", level=logging.FATAL)

        # When a fatal record is emitted
        handler.emit(record=record)

        # Then error hook is called
        collectd.error.assert_called_once_with("message")

    @mock_collectd
    def test_long_message_when_emit(self, collectd):
        # Given
        long_message = "LONG " * 20 + "MESSAGE."
        handler = CollectdLogHandler(collectd=collectd)
        handler.max_message_lenght = 10
        record = make_record(msg=long_message)

        # When a long message is emitted
        handler.emit(record=record)

        # Then info hook is called n times with split message
        collectd.info.assert_has_calls([
            mock.call(long_message[i:i + 10])
            for i in range(0, len(long_message), 10)])

    @mock_collectd
    def test_when_logger_debug(self, collectd):
        # Given
        handler = CollectdLogHandler(collectd=collectd)
        logger = logging.Logger('some_logger')
        logger.addHandler(handler)

        # When debug is called
        logger.debug('Say cheese: %s %d', 'string', 10)

        # Then debug hook is called
        collectd.debug.assert_called_once_with('Say cheese: string 10')
        collectd.info.assert_not_called()

    @mock_collectd
    def test_verbose_when_logger_info(self, collectd):
        # Given
        handler = CollectdLogHandler(collectd=collectd)
        handler.min_level = logging.INFO
        logger = logging.Logger('some_logger')
        logger.addHandler(handler)

        # When debug is called
        logger.debug('Say cheese: %s %d', 'string', 10)

        # Then info hook is called
        collectd.info.assert_called_once_with('Say cheese: string 10')
        collectd.debug.assert_not_called()

    @mock_collectd
    def test_non_verbose_when_logger_info(self, collectd):
        # Given
        handler = CollectdLogHandler(collectd=collectd)
        handler.min_level = logging.DEBUG
        logger = logging.Logger('some_logger')
        logger.addHandler(handler)

        # When debug is called
        logger.debug('Say cheese: %s %d', 'string', 10)

        # Then debug hook is called
        collectd.debug.assert_called_once_with('Say cheese: string 10')
        collectd.info.assert_not_called()

    @mock_collectd
    def test_info_from_logger(self, collectd):
        # Given
        handler = CollectdLogHandler(collectd=collectd)
        logger = logging.Logger('some_logger')
        logger.addHandler(handler)

        # When info is called
        logger.info('Say cheese: %s %d', 'string', 10)

        # Then info hook is called
        collectd.info.assert_called_once_with('Say cheese: string 10')

    @mock_collectd
    def test_warning_from_logger(self, collectd):
        # Given
        handler = CollectdLogHandler(collectd=collectd)
        logger = logging.Logger('some_logger')
        logger.addHandler(handler)

        # When warning is called
        logger.warning('Say cheese: %s %d', 'string', 10)

        # Then warning hook is called
        collectd.warning.assert_called_once_with('Say cheese: string 10')

    @mock_collectd
    def test_error_from_logger(self, collectd):
        # Given
        handler = CollectdLogHandler(collectd=collectd)
        logger = logging.Logger('some_logger')
        logger.addHandler(handler)

        # When error is called
        logger.error('Say cheese: %s %d', 'string', 10)

        # Then error hook is called
        collectd.error.assert_called_once_with('Say cheese: string 10')

    @mock_collectd
    def test_fatal_from_logger(self, collectd):
        # Given
        handler = CollectdLogHandler(collectd=collectd)
        logger = logging.Logger('some_logger')
        logger.addHandler(handler)

        # When fatal is called
        logger.fatal('Say cheese: %s %d', 'string', 10)

        # Then error hook is called
        collectd.error.assert_called_once_with('Say cheese: string 10')


def make_record(
        name=__name__, level=logging.INFO, pathname=__file__, lineno=0,
        msg="", args=tuple(), exc_info=None, func=None):
    "Creates a log record as done by loggers."
    record = logging.LogRecord(
        name=name, level=level, pathname=pathname, lineno=lineno, msg=msg,
        args=args, exc_info=exc_info, func=func)
    return record


class MockedCollectd(object):

    def debug(self, record):
        "Hook for debug messages"

    def info(self, record):
        "Hook for info messages"

    def warning(self, record):
        "Hook for warning messages"

    def error(self, record):
        "Hook for error messages"
