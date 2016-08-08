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


import abc
import collections

import six


# place older for required values
_REQUIRED = object()


class Attribute(object):

    default = _REQUIRED
    constant = True

    def __init__(self, default=_REQUIRED):
        if default is not _REQUIRED:
            self.default = self.normalize(default)

    def normalize(self, value):
        return value

    def get(self, obj, cls=None):
        if obj:
            try:
                # pylint: disable=protected-access
                value = obj._attributes[self]
            except KeyError:
                value = self.default
                if value is _REQUIRED:
                    raise RequiredAttributeError(obj, self.names(obj))
                if not self.constant:
                    value = self.set(obj, value)
            return value
        else:
            return self
    __get__ = get

    def set(self, obj, value):
        # pylint: disable=protected-access
        obj._attributes[self] = value = self.normalize(value)
        return value
    __set__ = set

    def delete(self, obj):
        try:
            # pylint: disable=protected-access
            del obj._attributes[self]
        except KeyError:
            raise AttributeError("Attribute value has not been defined.")
    __delete__ = delete

    def is_required(self, obj):
        try:
            self.get(obj)
        except RequiredAttributeError:
            return True
        else:
            return False

    def names(self, obj):
        # pylint: disable=protected-access
        return obj._all_attributes[self]


class Boolean(Attribute):

    normalize = bool


class Integer(Attribute):

    normalize = int


class String(Attribute):

    normalize = str


class Dictionary(Attribute):

    normalize = dict
    constant = False


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
