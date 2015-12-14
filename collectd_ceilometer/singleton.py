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
"""Generic singleton implementation"""

from __future__ import unicode_literals

import threading


class Singleton(object):
    """Generic singleton"""

    def __init__(self, decorated):
        self._decorated = decorated
        self._lock = threading.Lock()

    def __call__(self, *args, **kwargs):
        raise TypeError('Singleton must be accessed through instance() method')

    def instance(self):
        """Return singleton instance"""
        # pylint: disable=attribute-defined-outside-init
        try:
            return self._instance
        except AttributeError:
            with self._lock:
                if not hasattr(self, '_instance'):
                    self._instance = self._decorated()
            return self._instance
