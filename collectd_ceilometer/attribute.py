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


import six


_REQUIRED = object()


class HasAttributes(object):

    def __init__(self, **kwargs):
        self.attributes = {}

        cls = type(self)
        for name, value in six.iteritems(kwargs):
            attribute = getattr(cls, name)
            attribute.set(self, value)

    _all_attributes = None

    @classmethod
    def all_attributes(cls):
        attributes = cls._all_attributes
        if attributes is None:
            attributes = []
            for name in dir(cls):
                attribute = getattr(cls, name)
                if isinstance(attribute, Attribute):
                    attributes.append((name, attribute))
            cls._all_attributes = attributes = tuple(attributes)
        return attributes

    def check_required_attributes(self):
        required = ', '.join(
            repr(name)
            for name, attribute in self.all_attributes()
            if attribute.is_required(self))
        if required:
            raise RequiredAttributeError(
                "required attributes not found ({})".format(required))


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
                value = obj.attributes[self]
            except KeyError:
                value = self.default
                if value is _REQUIRED:
                    raise RequiredAttributeError(
                        "Attribute value has not been defined.")
                if not self.constant:
                    value = self.set(obj, value)
            return value
        else:
            return self
    __get__ = get

    def set(self, obj, value):
        obj.attributes[self] = value = self.normalize(value)
        return value
    __set__ = set

    def delete(self, obj):
        try:
            del obj.attributes[self]
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


class Boolean(Attribute):

    normalize = bool


class Integer(Attribute):

    normalize = int


class String(Attribute):

    normalize = str


class Dictionary(Attribute):

    normalize = dict
    constant = False


class RequiredAttributeError(AttributeError):
    pass
