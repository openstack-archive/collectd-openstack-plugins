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
"""Default collectd meter"""

from __future__ import unicode_literals

from collectd_ceilometer.settings import Config


class Meter(object):
    """Default collectd meter"""

    def meter_name(self, vl):
        """Return meter name"""
        # pylint: disable=no-self-use
        resources = [vl.plugin, vl.type]
        return '.'.join([i for i in resources if i])

    def hostname(self, vl):
        """Get host name"""
        # pylint: disable=no-self-use
        return vl.host

    def resource_id(self, vl):
        """Get resource ID"""

        resources = [self.hostname(vl), vl.plugin_instance, vl.type_instance]
        return '-'.join([i for i in resources if i])

    def unit(self, vl):
        """Get meter unit"""
        # pylint: disable=no-self-use
        return Config.instance().unit(vl.plugin, vl.type)
