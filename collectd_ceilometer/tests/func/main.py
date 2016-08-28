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
import unittest


from collectd_ceilometer.tests.func.runner import run_in_collectd

__unittest = True

LOGGER = logging.getLogger(__name__)


@run_in_collectd
def main(argv):
    from collectd_ceilometer.logger import CollectdLogHandler

    logger = logging.getLogger()
    logger.addHandler(CollectdLogHandler())

    try:
        LOGGER.info('Run tests inside collectd: ' + str(argv))
        unittest.main(
            argv=argv,
            testRunner=unittest.TextTestRunner(stream=sys.stdout))

    except Exception:
        LOGGER.exception("Error running tests.")
        sys.exit(1)

    else:
        return 0

    finally:
        LOGGER.info('Test execution complete.')
        sys.stdout.flush()
        sys.stderr.flush()
