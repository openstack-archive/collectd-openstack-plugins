# -*- coding: utf-8 -*-

# Copyright 2010-2011 OpenStack Foundation
# Copyright (c) 2017 Intel Corporation.
#
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

"""Plugin tests"""

import mock
import requests
import unittest

from collectd_ceilometer.common import sender as common_sender
from collectd_ceilometer.gnocchi import sender as gnocchi_sender


class TestGnocchiSender(unittest.TestCase):
    """Test the gnocchi sender"""

    def setUp(self):
        """Perform common set up code.
        """
        super(TestGnocchiSender, self).setUp()
        self.sender = gnocchi_sender.Sender()
