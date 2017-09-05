# -*- coding: utf-8 -*-

# Copyright 2010-2011 OpenStack Foundation
# Copyright (c) 2015 Intel Corporation.
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

from __future__ import unicode_literals

from collectd_openstack.common.meters.storage import SampleContainer

import unittest

from collections import defaultdict


class TestSampleContainer(unittest.TestCase):
    """Test the common.meters.storage.SampleContainer class"""

    def setUp(self):
        super(TestSampleContainer, self).setUp()
        self.container = SampleContainer()

    def test_sample_container_init(self):
        """Test creating the SampleContainer

        Set-up: create a container
        Test: Container is empty
        Expected behaviour: container is an empty dict of lists
        """
        self.assertEqual({}, self.container._data)

    def test_sample_container_add(self):
        """Test adding an element to SampleContainer

        Set-up: create empty SampleContainer
        Test: add an element to the SampleContainer
        Expected behaviour: _data contains the added elements
        """
        retval = self.container.add("key1", ["value1"], 5)

        self.assertEqual(retval, None)
        self.assertEqual(["value1", ], self.container._data["key1"])

    def test_sample_container_add_exceeds_limit(self):
        """Test adding an element to the Container so len > limit.

        Set-up: len(SampleContainer._data ) < limit;
        Test: Add items to the container so len() > limit
        Expected behaviour: SampleContainer._data[key] is empty and add()
        returns a list of samples of length limit
        """
        self.assertEqual(self.container._data, defaultdict(list))

        retval = self.container.add("key1", ["1", "2", "3", ], 2)

        self.assertEqual(retval, ["1", "2", "3", ])
        self.assertEqual([], self.container._data["key1"])

    def test_sample_container_reset(self):
        """Test resetting the contents of a meter entry in SampleContainer

        Set-up: add some entries to the container (two meters)
        action: call container.reset
        Expected behaviour: the container will be equivalent to a default dict
        and reset returns the stored data
        """
        expected = {"key1": ["one", "two", "three", ],
                    "key2": ["1", "2", "3", ]}

        self.container.add("key1", expected["key1"], 42)
        self.container.add("key2", expected["key2"], 42)

        self.assertEqual(expected, self.container._data)

        retval = self.container.reset()

        self.assertEqual(expected, retval)
        self.assertEqual({}, self.container._data)
