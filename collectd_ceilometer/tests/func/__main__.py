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

from collectd_ceilometer.tests.func.main import main

import sys

argv = sys.argv
if len(argv) < 2:
    argv = [
        'unittest2', 'discover', '--locals',
        '--start-directory', './collectd_ceilometer/tests/func',
        '--pattern', 'test_*.py', '--top-level-directory', '.']

sys.exit(main(argv=argv))
