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
"""Collectd meter for libvirt plugin"""

from __future__ import unicode_literals

from collectd_ceilometer.meters.base import Meter
from collectd_ceilometer.settings import Config
import libvirt
import threading


class LibvirtMeter(Meter):
    """Specialization for libvirt plugin"""

    def __init__(self):
        self._cache_lock = threading.Lock()
        self._conn = None
        self._vms = {}

    def hostname(self, vl):
        """Get hostname based on the input"""

        hostname = self._vms.get(vl.host)
        if not hostname:
            with self._cache_lock:
                # check again with lock because another thread could
                # store the hostname meanwhile
                hostname = self._vms.get(vl.host)
                if not hostname:
                    if self._conn is None:
                        self._conn = libvirt.openReadOnly(
                            Config.instance().LIBVIRT_CONN_URI)

                    hostname = self._conn.lookupByName(vl.host).UUIDString()
                    self._vms[vl.host] = hostname
        return hostname
