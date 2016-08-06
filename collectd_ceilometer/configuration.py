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


import collections
import logging

import six

from collectd_ceilometer import attribute
from collectd_ceilometer import units


LOG = logging.getLogger(__name__)


class Configuration(attribute.HasAttributes):

    BATCH_SIZE = attribute.Integer(1)
    CEILOMETER_URL_TYPE = attribute.String('internalURL')
    CEILOMETER_TIMEOUT = attribute.Integer(1000)
    OS_AUTH_URL = attribute.String()
    OS_USERNAME = attribute.String()
    OS_PASSWORD = attribute.String()
    OS_TENANT_NAME = attribute.String()
    VERBOSE = attribute.Boolean(False)
    UNITS = attribute.Dictionary(units.UNITS)

    def read_collectd_configuration(self, configuration):
        assert configuration.key.upper() == 'MODULE'

        # store data by name
        children = collections.OrderedDict(
            (child.key.upper(), child) for child in configuration.children)

        units = children.pop('UNITS', None)
        if units:
            for child in units.children:
                if child.key.upper() != 'UNIT':
                    LOG.warning(
                        "Unknow unit entry name %r, expected"
                        " 'UNIT'", child.key)
                elif len(child.values) != 2:
                    raise ValueError(
                        "Unit entries must have values.")
                else:
                    key, value = child.values
                    self.UNITS[key] = value

        # parse main configuration options
        for name, attr in self.all_attributes():
            try:
                child = children.pop(name)
            except KeyError:
                attr.get(self)  # this could raise RequiredAttributeError
            else:
                if len(child.values) != 1:
                    raise ValueError(
                        "Configuration option '{}' can have only one "
                        "value.".format(name))
                attr.set(self, child.values[0])

        # Warn the user that if some node haven't been parsed
        for name in six.iterkeys(children):
            LOG.warning("Ignored unknow configuration option: %r", name)
