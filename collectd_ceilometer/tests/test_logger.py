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

        # pylint: disable=protected-access
        self.assertEqual(
            [collectd.debug, collectd.info, collectd.warning, collectd.error],
            handler._hooks)

    def test_emit(self):
        collectd = mock_collectd()
        handler = CollectdLogHandler(collectd=collectd)
        record = make_record(msg="message", level=logging.INFO)

        handler.emit(record=record)

        collectd.info.assert_called_once_with("message")

    def test_emit_with_long_message(self):
        collectd = mock_collectd()
        handler = CollectdLogHandler(collectd=collectd)
        record = make_record(msg="m" * 2000, level=logging.INFO)

        handler.emit(record=record)

        collectd.info.assert_has_calls(
            [mock.call('m' * handler.max_message_lenght),
             mock.call('m' * (2000 - handler.max_message_lenght))])

    def test_debug_from_logger(self):
        collectd = mock_collectd()
        handler = CollectdLogHandler(collectd=collectd)
        logger = logging.Logger('some_logger')
        logger.addHandler(handler)

        logger.debug('Say cheese: %s %d', 'string', 10)

        collectd.debug.assert_called_once_with('Say cheese: string 10')
        collectd.info.assert_not_called()

    def test_debug_from_logger_when_verbose(self):
        collectd = mock_collectd()
        handler = CollectdLogHandler(collectd=collectd)
        handler.min_level = logging.INFO
        logger = logging.Logger('some_logger')
        logger.addHandler(handler)

        logger.debug('Say cheese: %s %d', 'string', 10)

        collectd.info.assert_called_once_with('Say cheese: string 10')
        collectd.debug.assert_not_called()

    def test_debug_from_logger_when_not_verbose(self):
        collectd = mock_collectd()
        handler = CollectdLogHandler(collectd=collectd)
        handler.min_level = logging.DEBUG
        logger = logging.Logger('some_logger')
        logger.addHandler(handler)

        logger.debug('Say cheese: %s %d', 'string', 10)

        collectd.debug.assert_called_once_with('Say cheese: string 10')
        collectd.info.assert_not_called()

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


def make_record(
        name=__name__, level=logging.NOTSET, pathname=__file__, lineno=0,
        msg="", args=tuple(), exc_info=None, func=None):
    record = logging.LogRecord(
        name=name, level=level, pathname=pathname, lineno=lineno, msg=msg,
        args=args, exc_info=exc_info, func=func)
    return record


def mock_collectd():
    return mock.MagicMock(spec=MockedCollectd)


class MockedCollectd(object):

    def debug(self, record):
        pass

    def info(self, record):
        pass

    def warning(self, record):
        pass

    def error(self, record):
        pass
