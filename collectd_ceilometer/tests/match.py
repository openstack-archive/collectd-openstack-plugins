# -*- coding: utf-8 -*-

# Copyright (c) 2016 Intel Corporation.
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

import fnmatch
from json import loads
import re


def json(obj):
    return MatchJson(obj)


class MatchJson(object):

    def __init__(self, obj):
        self._obj = obj

    def __eq__(self, json_text):
        return self._obj == loads(json_text)

    def __repr__(self):
        return "MatchJson({})".format(repr(self._obj))


def wildcard(text):
    return MatchWildcard(text)


class MatchWildcard(object):

    def __init__(self, obj):
        self._text = text = repr(obj)
        self._reg = re.compile(fnmatch.translate(text))

    def __eq__(self, obj):
        return self._reg.match(repr(obj))

    def __repr__(self):
        return "MatchWildcard({})".format(self._text)
