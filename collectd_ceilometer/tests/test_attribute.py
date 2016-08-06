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


import unittest


from collectd_ceilometer import attribute


class HasSomeAttributes(attribute.HasAttributes):

    required = attribute.Attribute()

    default = attribute.Attribute(default=None)

    integer = attribute.Integer("10")

    string = attribute.String("hello")

    dictionary = attribute.Dictionary({1: 2})

    boolean = attribute.Boolean(True)


class TestAttribute(unittest.TestCase):

    def test_init(self):
        obj = attribute.HasAttributes()
        self.assertEqual({}, obj.attributes)

    def test_init_with_attribute(self):
        obj = HasSomeAttributes(required=10)
        self.assertEqual(10, obj.required)

    def test_class_attribute(self):
        instance = HasSomeAttributes.required
        self.assertIsInstance(instance, attribute.Attribute)

    def test_required_attribute(self):
        obj = HasSomeAttributes()
        self.assertRaises(
            attribute.RequiredAttributeError, lambda: obj.required)

    def test_default_attribute(self):
        obj = HasSomeAttributes()
        self.assertIsNone(obj.default)

    def test_init_integer(self):
        obj = HasSomeAttributes(integer=20.1)
        self.assertEqual(20, obj.integer)

    def test_get_integer(self):
        obj = HasSomeAttributes()
        self.assertEqual(HasSomeAttributes.integer.default, obj.integer)

    def test_set_integer(self):
        obj = HasSomeAttributes()
        obj.integer = "15"
        self.assertEqual(15, obj.integer)

    def test_init_boolean(self):
        obj = HasSomeAttributes(boolean=20.1)
        self.assertIs(True, obj.boolean)

    def test_get_boolean(self):
        obj = HasSomeAttributes()
        self.assertIs(HasSomeAttributes.boolean.default, obj.boolean)

    def test_set_boolean(self):
        obj = HasSomeAttributes()
        obj.boolean = []
        self.assertIs(False, obj.boolean)

    def test_init_string(self):
        obj = HasSomeAttributes(string=20.1)
        self.assertEqual("20.1", obj.string)

    def test_get_string(self):
        obj = HasSomeAttributes()
        self.assertIs(HasSomeAttributes.string.default, obj.string)

    def test_set_string(self):
        obj = HasSomeAttributes()
        obj.string = None
        self.assertEqual("None", obj.string)

    def test_init_dictionary(self):
        obj = HasSomeAttributes(dictionary=[(3, 5)])
        self.assertEqual({3: 5}, obj.dictionary)

    def test_get_dictionary(self):
        obj = HasSomeAttributes()
        self.assertIs(HasSomeAttributes.dictionary.default, obj.dictionary)

    def test_set_dictionary(self):
        obj = HasSomeAttributes()
        obj.dictionary = {4: 3}
        self.assertEqual({4: 3}, obj.dictionary)
