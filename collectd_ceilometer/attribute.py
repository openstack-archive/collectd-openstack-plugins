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


class Attribute(object):

    default = _REQUIRED

    def __init__(self, default=_REQUIRED):
        if default is not _REQUIRED:
            self.default = self.normalize(default)

    def normalize(self, value):
        return value

    def get(self, obj, cls=None):
        if obj:
            value = obj.attributes.get(self, self.default)
            if value is _REQUIRED:
                raise RequiredAttributeError(
                    "Attribute value has not been defined.")
            return value
        else:
            return self
    __get__ = get

    def set(self, obj, value):
        obj.attributes[self] = self.normalize(value)
    __set__ = set

    def delete(self, obj):
        try:
            del obj.attributes[self]
        except KeyError:
            raise AttributeError("Attribute value has not been defined.")
    __delete__ = delete


class Boolean(Attribute):

    normalize = bool


class Integer(Attribute):

    normalize = int


class String(Attribute):

    normalize = str


class Dictionary(Attribute):

    normalize = dict


class RequiredAttributeError(AttributeError):
    pass
