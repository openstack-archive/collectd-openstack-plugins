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

import inspect

import mock


def full_class_name(cls):
    assert isinstance(cls, type)
    return inspect.getmodule(cls).__name__ + '.' + cls.__name__


def patch_class(cls, autospec=True, *args, **kwargs):
    name = full_class_name(cls)
    return mock.patch(name, autospec=autospec)
