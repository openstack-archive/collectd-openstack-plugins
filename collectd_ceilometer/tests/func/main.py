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

import sys

from collectd_ceilometer.tests.func.runner import run_in_collectd

@run_in_collectd
def main(argv):
    stdout = sys.stdout
    stderr = sys.stderr
    sys.stderr = stdout
    import unittest2
    sys.stderr = stderr
    sys.argv = argv

    import collectd

    collectd.info('Run tests inside collectd: ' + str(argv[1:]))
    try:
        unittest2.main(module=None)
    finally:
        collectd.info('Test execution complete.')
        stdout.flush()

    return 0
