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
"""Ceilometer collectd plugin configuration"""

from __future__ import unicode_literals

from collectd_ceilometer.singleton import Singleton
from collectd_ceilometer.units import UNITS
from collections import namedtuple
import logging
import six

LOGGER = logging.getLogger(__name__)


class BadConfigError(Exception):
    """Configuration exception"""
    pass


class CfgParam(namedtuple('CfgParam', ['key', 'default', 'data_type'])):
    """Configuration parameter definition"""

    def value(self, data):
        """Convert a string to the parameter type"""

        try:
            return self.data_type(data)
        except (ValueError, TypeError) as exc:
            LOGGER.info('Config value exception: %s', six.text_type(exc))
            raise BadConfigError(
                'Invalid value "%s" for configuration parameter "%s"' % (
                    data, self.key))


@Singleton
class Config(object):
    """Plugin confguration"""

    _configuration = [
        CfgParam('BATCH_SIZE', 1, int),
        CfgParam('OS_AUTH_URL', None, six.text_type),
        CfgParam('CEILOMETER_URL_TYPE', 'internalURL', six.text_type),
        CfgParam('CEILOMETER_TIMEOUT', 1000, int),
        CfgParam('OS_USERNAME', None, six.text_type),
        CfgParam('OS_PASSWORD', None, six.text_type),
        CfgParam('OS_TENANT_NAME', None, six.text_type),
        CfgParam('VERBOSE', False, bool),

        CfgParam('LIBVIRT_CONN_URI', 'qemu:///system', six.text_type),
    ]

    _config_dict = {cfg.key: cfg for cfg in _configuration}
    _config_keys = _config_dict.keys()

    def __init__(self):
        """Set the default values"""

        # init all parameters to default values
        for cfg in self._configuration:
            setattr(self, cfg.key, cfg.default)

        # dictionary for user-defined units
        self._user_units = {}
        self._units = UNITS.copy()

    def read(self, cfg):
        """Read the collectd configuration

        @param cfg configuration provided by collectd
        """
        LOGGER.info('Reading the OS plugin configuration')
        assert 'MODULE' == cfg.key.upper()
        self._read_node(cfg)

        # verify the configuration
        error = False
        for key in self._config_keys:
            if getattr(self, key, None) is None:
                LOGGER.error('Configuration parameter %s not set.', key)
                error = True
        if error:
            LOGGER.error(
                'Collectd plugin for Ceilometer will not work properly')
        else:
            LOGGER.info('Configuration OK')

    def unit(self, plugin, pltype):
        """Get unit for plugin and type"""

        if pltype:
            unit = self._units.get('%s.%s' % (plugin, pltype))
            if unit:
                return unit
        return self._units.get(plugin, "None")

    def _read_node(self, node):
        """Read a configuration node

        @param node collectd configuration node
        """

        key = node.key.upper()

        # if the node is 'UNITS' call the units function
        if key == 'UNITS':
            self._read_units(node.children)
            return

        # if we have a root node read only all its children
        # as we don't expect any value here
        if node.children:
            for child in node.children:
                self._read_node(child)
            return

        # if the configuration key is known
        if key in self._config_keys:
            try:
                # read, normalize and check the value
                val = self._config_dict[key].value(node.values[0])

                # and store it as a attribute of current instance
                setattr(self, key, val)

            except (IndexError, TypeError):
                # the variable node.value is an empty list
                # or it is not a list at all
                LOGGER.error('No configuration value found for "%s"', key)
                return
            except BadConfigError as exc:
                LOGGER.error(six.text_type(exc))
                return

            # do not show the password in the logs
            if key == 'OS_PASSWORD':
                val = '*****'
            LOGGER.info(
                'Got configuration parameter: %s -> "%s"', key, val)
        else:
            LOGGER.error('Unknown configuration parameter "%s"', key)

    def _read_units(self, nodes):
        """Read user-defined units

        @param node collectd configuration nodes
        """
        for node in nodes:
            if node.key.upper() == 'UNIT':
                if len(node.values) == 2:
                    key, val = node.values
                    self._user_units[key] = val
                    LOGGER.info(
                        'Got user defined unit "%s" for "%s"', val, key)
                else:
                    LOGGER.error(
                        'Invalid unit configuration: unit %s' % ' '.join(
                            ['"%s"' % i for i in node.values]))
            else:
                LOGGER.error(
                    'Invalid unit configuration: %s', node.key.upper())
        self._units.update(self._user_units)
