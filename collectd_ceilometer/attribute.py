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


# -- IMPORTANT NOTE FOR DEVELOPERS --
# To understand this code you need to know about following Python topics
#   - descriptors:
#         see https://docs.python.org/2.7/howto/descriptor.html
#   - metaclasses:
#         see https://docs.python.org/2.7/reference/datamodel.html


import abc
import collections

import six


# place older for required values
_REQUIRED = object()


class Attribute(object):
    """Implementation of descriptor interface for implementing following

    class MyClass(HasAttribute):

        my_attribute = Attribute("default value")

    obj1 = MyClass()
    assert obj.my_attribute == 'default value'
    obj1.my_attribute = 'assigned value'
    assert obj.my_attribute == 'assigned value'

    obj2 = MyClass(my_attribute='initial value')
    assert obj.my_attribute == 'initial value'

    To understand implementation details pleas read following documentation:
       https://docs.python.org/2.7/howto/descriptor.html
    """

    default = _REQUIRED
    is_constant = True

    def __init__(self, default=_REQUIRED):
        """Defines an attribure with given default value.

        If default value is not given then the attribute will not be
        automatically initialized.

        class MyClass(HasAttribute):

            my_attribute = Attribute()  # default value is not given

        obj1 = MyClass()
        assert hasattr(False, obj.my_attribute)

        obj.my_attribute = 'fist value'
        assert obj.my_attribute == 'fist value'
        """

        if default is not _REQUIRED:
            # il valore is normalized to be suer that it is transformed to
            # the type specified by specialized attribute type. Normalize will
            # be int for Integer, str for String, dict for Dictionary, ...
            self.default = self.normalize(default)

    def normalize(self, value):
        "To be overrided to convert or copy given value."
        return value

    def get(self, obj, cls=None):
        "Gets attribute value from given object."
        # pylint: disable=protected-access
        if obj:
            assert self in obj._all_attributes
            try:
                value = obj._attributes[self]
            except KeyError:
                # this mean that the instance has not a specific value
                value = self.default
                if value is _REQUIRED:
                    # even the attribute have no value for it
                    raise RequiredAttributeError(obj, self.names(obj))
                if not self.is_constant:
                    # make sure returned value is copied and a copy is stored
                    # before returning it
                    value = self.set(obj, value)
            return value
        else:
            return self
    __get__ = get

    def set(self, obj, value):
        "Sets given value from given object."
        # pylint: disable=protected-access
        assert self in obj._all_attributes
        obj._attributes[self] = value = self.normalize(value)
        return value
    __set__ = set

    def delete(self, obj):
        "Removes attribute value from given object."
        try:
            # pylint: disable=protected-access
            del obj._attributes[self]
        except KeyError:
            raise AttributeError("Attribute value has not been defined.")
    __delete__ = delete

    def is_required(self, obj):
        """Returns True if the object hasn't a value for this attribute.

        An attribute is required when accessing to it it would raise
        RequiredAttributeError

        class MyClass(HasAttribute):

            my_attribute = Attribute()  # default value is not given

        obj1 = MyClass()
        assert MyClass.my_attribute.is_required(obj1) is True

        obj.my_attribute = 'fist value'
        assert MyClass.my_attribute.is_required(obj1) is False
        """

        try:
            self.get(obj)
        except RequiredAttributeError:
            return True
        else:
            return False

    def names(self, obj):
        """Returns all names given to this attribute by given object.

        class MyClass(HasAttribute):

            my_name1 = Attribute()
            my_name2 = my_name2

        obj = MyClass()
        assert MyClass.my_name1 is MyClass.my_name2
        assert MyClass.my_name1.names(obj) == ('my_name1', 'my_name2')
        """

        # pylint: disable=protected-access
        return obj._all_attributes[self]


class Boolean(Attribute):
    """Defines an attribute of type bool

    class MyClass(HasAttribute):

        is_connected = Boolean()
        has_errors = Boolean()

    errors = []
    obj = MyClass(is_connected=1, has_errors=errors)

    assert obj.is_connected is True
    assert obj.has_errors is False
    """

    normalize = bool


class Integer(Attribute):
    """Defines an attribute of type int

    class MyClass(HasAttribute):

        number1 = Integer()
        number2 = Integer()

    obj = MyClass(number1=1.4, number2="20")
    assert obj.number1 == 1
    assert obj.number2 == 20
    """

    normalize = int


class String(Attribute):
    """Defines an attribute of type str

    class MyClass(HasAttribute):

        errors = String()

    numbers = [1, 2, 3]
    obj = MyClass(message=numbers)
    assert obj.numbers == '[1, 2, 3]'
    """

    normalize = str


class Dictionary(Attribute):
    """Defines an attribute of type dict

    class MyClass(HasAttribute):

        hooks = Dict()

    obj = MyClass()
    obj.hooks['on_load'] = on_load
    """

    normalize = dict
    is_constant = False


class HasAttributesMeta(abc.ABCMeta):

    def __new__(cls, clsname, bases, namespace):
        # gives all_attributes dictionary to the new class
        all_attributes = collections.OrderedDict()
        for name in sorted(six.iterkeys(namespace)):
            attribute = namespace[name]
            try:
                names = all_attributes.get(attribute)
            except TypeError:
                pass  # not all types can be used as hash keys
            else:
                if names:
                    # this attribute has more than one name
                    names.append(name)
                elif isinstance(attribute, Attribute):
                    # new attribute has been found
                    all_attributes[attribute] = names = [name]

        # froze produced structure
        all_attributes = tuple(
            (attribute, tuple(names))
            for attribute, names in six.iteritems(all_attributes))

        namespace['all_attributes'] = all_attributes  # for public use
        namespace['_all_attributes'] = dict(all_attributes)  # for internal use

        return super(HasAttributesMeta, cls).__new__(
            cls, clsname, bases, namespace)


@six.add_metaclass(HasAttributesMeta)
class HasAttributes(object):
    "Mixin for objects with attributes"

    # Tuple of pairs with all attributes and their names
    all_attributes = tuple()

    # Dictionary containing all attributes for this class:
    #    key: attribute instancd
    #    value: list of names the attribute is know as
    # It is going to be initialized by HasAttributesMeta metaclass:
    _all_attributes = {}

    def __init__(self, **attribute_values):
        """Initializes named attributes using given values.

        """

        # attribute values are going to be stored on this dictionary:
        #   key: attribute instance
        #   value: attribute value
        self._attributes = {}
        if attribute_values:
            self.set_attributes(**attribute_values)

    def set_attributes(self, **attribute_values):
        _attributes = self._attributes
        cls = type(self)
        for name, value in six.iteritems(attribute_values):
            # get Attribute instance from the class
            attribute = getattr(cls, name)
            if attribute in _attributes:
                # Please note that the same attribute can be know by more names
                raise ValueError(
                    "Attribute '{}' was required to be initialized "
                    "twice!".format(name))
            # normalize and initialize given attribute value
            attribute.set(self, value)

    def check_required_attributes(self):
        """Verifies that all required attributes are defined.

        Raises a required attribute error if it has attributes that has not
        been initialized and for which any default value was given.
        """

        required = []
        for attribute, names in self.all_attributes:
            if attribute.is_required(self):
                required.extend(names)
        if required:
            raise RequiredAttributeError(self, required)


class RequiredAttributeError(AttributeError):

    def __init__(self, obj, required):
        self.required = required
        message = "required attribute(s) of class '{}' not found ({})".format(
            obj, ', '.join(required))
        super(RequiredAttributeError, self).__init__(message)
