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

from collectd_openstack.common.logger import CollectdLogHandler
from collectd_openstack.common.settings import Config
from collectd_openstack.tests.mocking import patch_class


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

    def __init__(self, *args, **kwargs):
        """Declare additional class attributes"""
        super(TestCollectdLogHandler, self).__init__(*args, **kwargs)
        self.config = Config.instance()

    @patch_class(MockedCollectd)
    def test_registered_hooks_when_init(self, collectd):

        # When CollectdLogHandler is created
        handler = CollectdLogHandler(collectd=collectd, config=self.config)

        # Then collectd logging hooks are registered
        # pylint: disable=protected-access
        self.assertEqual(
            {logging.DEBUG: collectd.debug,
             logging.INFO: collectd.info,
             logging.WARNING: collectd.warning,
             logging.ERROR: collectd.error,
             logging.FATAL: collectd.error},
            handler.priority_map)

    @patch_class(MockedCollectd)
    def test_debug_when_emit(self, collectd):

        # Given
        handler = CollectdLogHandler(collectd=collectd, config=self.config)
        record = make_record(msg="message", level=logging.DEBUG)

        # When a debug record is emitted
        handler.emit(record=record)

        # Then debug hook is called
        collectd.debug.assert_called_once_with("message")

    @patch_class(MockedCollectd)
    def test_verbose_debug_when_emit(self, collectd):
        # Given
        handler = CollectdLogHandler(collectd=collectd, config=self.config)
        self.config.VERBOSE = True
        record = make_record(msg="message", level=logging.DEBUG)

        # When an info record is emitted
        handler.emit(record=record)

        # Then info hook is called
        collectd.info.assert_called_once_with("message")

    @patch_class(MockedCollectd)
    def test_info_when_emit(self, collectd):
        # Given
        handler = CollectdLogHandler(collectd=collectd, config=self.config)
        record = make_record(msg="message", level=logging.INFO)

        # When an info record is emitted
        handler.emit(record=record)

        # Then info hook is called
        collectd.info.assert_called_once_with("message")

    @patch_class(MockedCollectd)
    def test_warning_when_emit(self, collectd):
        # Given
        handler = CollectdLogHandler(collectd=collectd, config=self.config)
        record = make_record(msg="message", level=logging.WARNING)

        # When a warning record is emitted
        handler.emit(record=record)

        # Then info warning is called
        collectd.warning.assert_called_once_with("message")

    @patch_class(MockedCollectd)
    def test_error_when_emit(self, collectd):
        # Given
        handler = CollectdLogHandler(collectd=collectd, config=self.config)
        record = make_record(msg="message", level=logging.ERROR)

        # When an error record is emitted
        handler.emit(record=record)

        # Then error hook is called
        collectd.error.assert_called_once_with("message")

    @patch_class(MockedCollectd)
    def test_fatal_when_emit(self, collectd):
        # Given
        handler = CollectdLogHandler(collectd=collectd, config=self.config)
        record = make_record(msg="message", level=logging.FATAL)

        # When a fatal record is emitted
        handler.emit(record=record)

        # Then error hook is called
        collectd.error.assert_called_once_with("message")

    @patch_class(MockedCollectd)
    def test_long_message_when_emit(self, collectd):
        # Given
        long_message = "LONG " * 20 + "MESSAGE."
        handler = CollectdLogHandler(collectd=collectd, config=self.config)
        handler.max_message_length = 10
        record = make_record(msg=long_message)

        # When a long message is emitted
        handler.emit(record=record)

        # Then info hook is called n times with split message
        collectd.info.assert_has_calls([
            mock.call(long_message[i:i + 10])
            for i in range(0, len(long_message), 10)])

    @patch_class(MockedCollectd)
    def test_when_logger_debug(self, collectd):
        # Given
        handler = CollectdLogHandler(collectd=collectd, config=self.config)
        logger = logging.Logger('some_logger')
        logger.addHandler(handler)

        # When debug is called
        self.config.VERBOSE = False
        logger.debug('Say cheese: %s %d', 'string', 10)

        # Then debug hook is called
        collectd.debug.assert_called_once_with('Say cheese: string 10')
        collectd.info.assert_not_called()

    @patch_class(MockedCollectd)
    def test_verbose_when_logger_info(self, collectd):
        # Given
        handler = CollectdLogHandler(collectd=collectd, config=self.config)
        logger = logging.Logger('some_logger')
        logger.addHandler(handler)

        # When debug is called
        self.config.VERBOSE = True
        logger.debug('Say cheese: %s %d', 'string', 10)

        # Then info hook is called
        collectd.info.assert_called_once_with('Say cheese: string 10')
        collectd.debug.assert_not_called()

    @patch_class(MockedCollectd)
    def test_non_verbose_when_logger_info(self, collectd):
        # Given
        handler = CollectdLogHandler(collectd=collectd, config=self.config)
        handler.verbose = False
        logger = logging.Logger('some_logger')
        logger.addHandler(handler)

        # When debug is called
        logger.debug('Say cheese: %s %d', 'string', 10)

        # Then debug hook is called
        collectd.debug.assert_called_once_with('Say cheese: string 10')
        collectd.info.assert_not_called()

    @patch_class(MockedCollectd)
    def test_info_from_logger(self, collectd):
        # Given
        handler = CollectdLogHandler(collectd=collectd, config=self.config)
        logger = logging.Logger('some_logger')
        logger.addHandler(handler)

        # When info is called
        logger.info('Say cheese: %s %d', 'string', 10)

        # Then info hook is called
        collectd.info.assert_called_once_with('Say cheese: string 10')

    @patch_class(MockedCollectd)
    def test_warning_from_logger(self, collectd):
        # Given
        handler = CollectdLogHandler(collectd=collectd, config=self.config)
        logger = logging.Logger('some_logger')
        logger.addHandler(handler)

        # When warning is called
        logger.warning('Say cheese: %s %d', 'string', 10)

        # Then warning hook is called
        collectd.warning.assert_called_once_with('Say cheese: string 10')

    @patch_class(MockedCollectd)
    def test_error_from_logger(self, collectd):
        # Given
        handler = CollectdLogHandler(collectd=collectd, config=self.config)
        logger = logging.Logger('some_logger')
        logger.addHandler(handler)

        # When error is called
        logger.error('Say cheese: %s %d', 'string', 10)

        # Then error hook is called
        collectd.error.assert_called_once_with('Say cheese: string 10')

    @patch_class(MockedCollectd)
    def test_fatal_from_logger(self, collectd):
        # Given
        handler = CollectdLogHandler(collectd=collectd, config=self.config)
        logger = logging.Logger('some_logger')
        logger.addHandler(handler)

        # When fatal is called
        logger.fatal('Say cheese: %s %d', 'string', 10)

        # Then error hook is called
        collectd.error.assert_called_once_with('Say cheese: string 10')
