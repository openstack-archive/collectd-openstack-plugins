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
"""Meter storage"""

from __future__ import unicode_literals

import six

from collectd_ceilometer.meters.base import Meter
try:
    from collectd_ceilometer.meters.libvirt import LibvirtMeter
except ImportError:
    # libvirt is an optional requirement
    LibvirtMeter = None


class MeterStorage(object):
    """Meter storage"""

    # all plugins
    _classes = {}
    if LibvirtMeter:
        _classes['libvirt'] = LibvirtMeter

    def __init__(self, collectd):
        self._meters = {}
        self._default = Meter(collectd=collectd)

        # fill dict with specialized meters classes
        self._meters = {key: meter_class(collectd=collectd)
                        for key, meter_class in six.iteritems(self._classes)}

    def get(self, plugin):
        """Get meter for the collectd plugin"""
        # return specialized meter class for collectd plugin or default Meter
        return self._meters.get(plugin, self._default)
