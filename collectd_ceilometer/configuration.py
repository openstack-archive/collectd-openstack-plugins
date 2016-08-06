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


import logging


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
