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


class TestCollectdLogHandler(unittest.TestCase):

    def test_init(self):
        collectd = mock_collectd()

        handler = CollectdLogHandler(collectd=collectd)

        self.assertEqual(
            [(logging.DEBUG, collectd.debug),
             (logging.INFO, collectd.info),
             (logging.WARNING, collectd.warning),
             (logging.ERROR, collectd.error),
             (logging.FATAL, collectd.error)],
            list(handler._hooks.items()))
        self.assertEqual([handler], handler.filters)

    def test_filter_when_disabled(self):
        collectd = mock_collectd()
        handler = CollectdLogHandler(collectd=collectd, level=logging.INFO + 1)
        record = mock_record(msg="a_message", level=logging.INFO)

        result = handler.filter(record)

        self.assertFalse(result)
        self.assertFalse(hasattr(record, 'hook'))

    def test_filter_debug(self):
        collectd = mock_collectd()
        handler = CollectdLogHandler(collectd=collectd)
        record = mock_record(msg="a_message", level=logging.DEBUG)

        result = handler.filter(record)

        self.assertTrue(result)
        self.assertIs(collectd.debug, record.hook)

    def test_filter_info(self):
        collectd = mock_collectd()
        handler = CollectdLogHandler(collectd=collectd)
        record = mock_record(msg="a_message", level=logging.INFO)

        result = handler.filter(record)

        self.assertTrue(result)
        self.assertIs(collectd.info, record.hook)

    def test_filter_warning(self):
        collectd = mock_collectd()
        handler = CollectdLogHandler(collectd=collectd)
        record = mock_record(msg="a_message", level=logging.WARNING)

        result = handler.filter(record)

        self.assertTrue(result)
        self.assertIs(collectd.warning, record.hook)

    def test_filter_error(self):
        collectd = mock_collectd()
        handler = CollectdLogHandler(collectd=collectd)
        record = mock_record(msg="a_message", level=logging.ERROR)

        result = handler.filter(record)

        self.assertTrue(result)
        self.assertIs(collectd.error, record.hook)

    def test_filter_fatal(self):
        collectd = mock_collectd()
        handler = CollectdLogHandler(collectd=collectd)
        record = mock_record(msg="a_message", level=logging.FATAL)

        result = handler.filter(record)

        self.assertTrue(result)
        self.assertIs(collectd.error, record.hook)

    def test_emit_with_hook(self):
        collectd = mock_collectd()
        handler = CollectdLogHandler(collectd=collectd)
        record = mock_record(msg="message", has_hook=True)

        handler.emit(record=record)

        record.hook.assert_called_once_with("message")

    def test_emit_with_hook_and_long_message(self):
        collectd = mock_collectd()
        handler = CollectdLogHandler(collectd=collectd)
        record = mock_record(msg="m" * 2000, has_hook=True)

        handler.emit(record=record)

        record.hook.assert_has_calls(
            [mock.call('m' * CollectdLogHandler.MAX_MESSAGE_LENGHT),
             mock.call('m' * (2000 - CollectdLogHandler.MAX_MESSAGE_LENGHT))])

    def test_emit_without_hook(self):
        collectd = mock_collectd()
        handler = CollectdLogHandler(collectd=collectd)
        record = mock_record(msg="a_message", level=logging.DEBUG)

        handler.emit(record=record)

    def test_debug_from_logger(self):
        collectd = mock_collectd()
        handler = CollectdLogHandler(collectd=collectd)
        logger = logging.Logger('some_logger')
        logger.addHandler(handler)
        handler.set_verbose(False)

        logger.debug('Say cheese: %s %d', 'string', 10)

        collectd.debug.assert_called_once_with('Say cheese: string 10')
        collectd.info.assert_not_called()

    def test_debug_from_logger_when_verbose(self):
        collectd = mock_collectd()
        handler = CollectdLogHandler(collectd=collectd)
        logger = logging.Logger('some_logger')
        logger.addHandler(handler)
        handler.set_verbose(True)

        logger.debug('Say cheese: %s %d', 'string', 10)

        collectd.info.assert_called_once_with('Say cheese: string 10')
        collectd.debug.assert_not_called()

    def test_info_from_logger(self):
        collectd = mock_collectd()
        handler = CollectdLogHandler(collectd=collectd)
        logger = logging.Logger('some_logger')
        logger.addHandler(handler)

        logger.info('Say cheese: %s %d', 'string', 10)

        collectd.info.assert_called_once_with('Say cheese: string 10')

    def test_warning_from_logger(self):
        collectd = mock_collectd()
        handler = CollectdLogHandler(collectd=collectd)
        logger = logging.Logger('some_logger')
        logger.addHandler(handler)

        logger.info('Say cheese: %s %d', 'string', 10)

        collectd.info.assert_called_once_with('Say cheese: string 10')

    def test_error_from_logger(self):
        collectd = mock_collectd()
        handler = CollectdLogHandler(collectd=collectd)
        logger = logging.Logger('some_logger')
        logger.addHandler(handler)

        logger.error('Say cheese: %s %d', 'string', 10)

        collectd.error.assert_called_once_with('Say cheese: string 10')

    def test_fatal_from_logger(self):
        collectd = mock_collectd()
        handler = CollectdLogHandler(collectd=collectd)
        logger = logging.Logger('some_logger')
        logger.addHandler(handler)

        logger.fatal('Say cheese: %s %d', 'string', 10)

        collectd.error.assert_called_once_with('Say cheese: string 10')


def mock_collectd():
    return mock.MagicMock(spec=MockedCollectd)


def mock_record(
        name=__name__, level=logging.NOTSET, pathname=__file__, lineno=0,
        msg="", args=tuple(), exc_info=None, func=None, has_hook=False):
    record = logging.LogRecord(
        name=name, level=level, pathname=pathname, lineno=lineno, msg=msg,
        args=args, exc_info=exc_info, func=func)
    if has_hook:
        record.hook = mock.MagicMock(spec=callable)
    return record


class MockedCollectd(object):

    def debug(self, record):
        pass

    def info(self, record):
        pass

    def warning(self, record):
        pass

    def error(self, record):
        pass
