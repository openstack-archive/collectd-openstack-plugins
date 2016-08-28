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
import sys
import unittest2


from collectd_ceilometer.tests.func.runner import run_in_collectd

__unittest = True

LOGGER = logging.getLogger(__name__)


@run_in_collectd
def main(argv):
    try:
        argv = ['unittest2'] +  argv[1:]
        LOGGER.debug('Run tests inside collectd:\n\t' + str(argv))
        unittest2.main(
            module=None,
            argv=argv,
            testRunner=unittest2.TextTestRunner(
                stream=sys.stdout, verbosity=2, buffer=True,
                descriptions=False, resultclass=LogTestResult))

    except SystemExit as ex:
        if ex.code and int(ex.code) > 1:
            LOGGER.exception("Error running tests.")
        sys.exit(ex.code)

    except Exception:
        LOGGER.exception("Error running tests.")
        sys.exit(1)

    else:
        return 0

    finally:
        LOGGER.debug('Test execution complete.')
        sys.stdout.flush()
        sys.stderr.flush()


class LogTestResult(unittest2.TestResult):
    """A test result class that can print formatted text results to a stream.

    Used by TextTestRunner.
    """
    separator1 = '=' * 70
    separator2 = '-' * 70
    old_errors_number = 0
    old_failures_number = 0
    old_unexpected_successes_number = 0
    old_skipped_number = 0

    def __init__(self, stream, descriptions, verbosity):
        super(LogTestResult, self).__init__(stream, descriptions, verbosity)
        self.stream = stream
        self.showAll = verbosity > 1
        self.dots = verbosity == 1
        self.descriptions = descriptions

    def startTest(self, test):
        LOGGER.info("%s ...", test.id())
        self.old_errors_number = len(self.errors)
        self.old_failures_number = len(self.failures)
        self.old_unexpected_successes_number = len(self.unexpectedSuccesses)
        self.old_skipped_number = len(self.skipped)
        super(LogTestResult, self).startTest(test)

    def stopTest(self, test):
        self._mirrorOutput = False
        super(LogTestResult, self).stopTest(test)

        failures = self.failures[self.old_failures_number:]
        errors = self.errors[self.old_errors_number:]
        skipped = self.skipped[self.old_skipped_number:]
        unexpected_successes = self.unexpectedSuccesses[
            self.old_unexpected_successes_number:]

        error_details = self.separator2 + "\n"
        for t, err in errors:
            assert t is test
            error_details += "ERROR: " +  t.id() + "\n" + str(err)
        for t, err in failures:
            assert t is test
            error_details += "FAIL: " +  t.id() + "\n" + str(err)
        error_details += self.separator2 + "\n"

        if failures:
            LOGGER.error('%s -> FAIL\n\n%s', test.id(), error_details)
        elif errors:
            LOGGER.error('%s -> ERROR\n\n%s', test.id(), error_details)
        elif skipped:
            LOGGER.info('%s -> SKIPPED: %s', test.id(), skipped[0][1])
        elif unexpected_successes:
            LOGGER.info('%s -> UNEXPECTED SUCCESS', test.id())

    def stopTestRun(self):
        super(LogTestResult, self).stopTestRun()
        self.printErrors()
