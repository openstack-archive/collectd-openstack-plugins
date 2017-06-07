..
      Licensed under the Apache License, Version 2.0 (the "License"); you may
      not use this file except in compliance with the License. You may obtain
      a copy of the License at

          http://www.apache.org/licenses/LICENSE-2.0

      Unless required by applicable law or agreed to in writing, software
      distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
      WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
      License for the specific language governing permissions and limitations
      under the License.

      Convention for heading levels in collectd-ceilometer-plugin documentation:

      =======  Heading 0 (reserved for the title in a document)
      -------  Heading 1
      ~~~~~~~  Heading 2
      +++++++  Heading 3
      '''''''  Heading 4

      Avoid deeper levels because they do not render well.

=====
Usage
=====

To use collectd-ceilometer-plugin in collectd::

    Python plugin must be enabled in collectd

    collectd must be started
    (ex: systemctl start collectd)

local.conf settings
-------------------

COLLECTD_BRANCH
~~~~~~~~~~~~~~~
    (<git branch>) Indicates which branch of collectd to checkout before
    compiling.

    Default: collectd-5.7

COLLECTD_CONF_DIR
~~~~~~~~~~~~~~~~~
    (directory) Specify a directory where collectd conf files reside.
    This is required if you use a distro other than Ubuntu or Fedora, or if
    the config file is in a non default location. This config directory will
    be created if it doesn't already exist.
    Default: /etc/collectd/collectd.conf.d (Ubuntu) /etc/collectd.d (Fedora)

COLLECTD_DIR
~~~~~~~~~~~~
    (directory) Destination of the cloned collectd source code.
    Default: $DEST/collectd-$COLLECTD_BRANCH/


COLLECTD_INSTALL
~~~~~~~~~~~~~~~~
    (True|False) Indicates whether to install collectd.
    Set this to False if you are running a pre-built version of collectd or do
    not want to upgrade installed version.

    Default: True


COLLECTD_BATCH_SIZE
~~~~~~~~~~~~~~~~~~~
    Set the amount of samples to be buffered before sending.
    Default: 1 i.e. no batching/buffering.


CEILOMETER_TIMEOUT
~~~~~~~~~~~~~~~~~~
    Sets the ceilometer's request timeout. The value is passed in milliseconds.
    Default: 1000 i.e. 1 sec.


COLLECTD_LOG_FILE
~~~~~~~~~~~~~~~~~
    (file) The path of the collectd log file.
    Default: /opt/stack/logs/collectd.log


COLLECTD_LOG_LEVEL
~~~~~~~~~~~~~~~~~~
    (debug|info|notice|warning|err) All log messages with lower log level than
    this are going to be filtered out from the log file.
    Default: info


COLLECTD_CEILOMETER_CUSTOM_UNITS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    (meter=unit) a comma seperated list of pairs, defining meters and their units.
    Allows existing units to be changed and new units to be set for new meters.
    The "meter" is generally in the form of "plugin.type", where plugin and
    plugin type are attributes of the collectd data.

    Example: COLLECTD_CEILOMETER_CUSTOM_UNITS="<meter> <unit>,<meter> <unit>"


COLLECTD_GNOCCHI_CUSTOM_UNITS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    (meter=unit) a comma seperated list of pairs, defining meters and their units.
    Allows existing units to be changed and new units to be set for new meters.
    The "meter" is generally in the form of "plugin.type", where plugin and
    plugin type are attributes of the collectd data.

    Example: COLLECTD_GNOCCHI_CUSTOM_UNITS="<meter> <unit>,<meter> <unit>"


COLLECTD_CEILOMETER_ENABLED
~~~~~~~~~~~~~~~~~~~~~~~~~~~
    (True|False) Toggle whether collectd-ceilometer-plugin is enabled.

    Default: False

COLLECTD_GNOCCHI_ENABLED
~~~~~~~~~~~~~~~~~~~~~~~~
    (True|False) Toggles whether collectd-gnocchi-plugin is enabled.

    Default: True

COLLECTD_AODH_ENABLED
~~~~~~~~~~~~~~~~~~~~~
    (True|False) Toggles whether collectd-aodh-plugin is enabled.

    Default: False

COLLECTD_CEILOMETER_VERBOSE
~~~~~~~~~~~~~~~~~~~~~~~~~~~
    (True|False) Set this to True to make collectd-ceilometer debugging messages
    visible as info messages. This is useful when running the plugin inside a
    collectd compiled without debug message support.

    Default: False

COLLECTD_GNOCCHI_VERBOSE
~~~~~~~~~~~~~~~~~~~~~~~~
    (True|False) Set this to True to make collectd-gnocchi debugging messages
    visible as info messages. This is useful when running the plugin inside a
    collectd compiled without debug message support.

    Default: $COLLECTD_CEILOMETER_VERBOSE

COLLECTD_AODH_VERBOSE
~~~~~~~~~~~~~~~~~~~~~
    (True|False) Set this to True to make collectd-aodh debugging messages
    visible as info messages. This is useful when running the plugin inside
    a collectd compiled without debug message support.

    Default: $COLLECTD_CEILOMETER_VERBOSE

COLLECTD_INSTALL_TYPE
~~~~~~~~~~~~~~~~~~~~~
    (source|binary) Specify whether the collectd installation should use the
    package manager or install from source.

    Default: binary


COLLECTD_REPO
~~~~~~~~~~~~~
    (url) Location of git repo to clone collectd from.

    Default: https://github.com/collectd/collectd.git


COLLECTD_PREFIX
~~~~~~~~~~~~~~~
    (directory) The directory to install collectd under.

    Default: /usr/

COLLECTD_ADDITIONAL_PACKAGES
    Specify additional packages to be installed before collectd is
    built/installed. This is useful when building collectd from source it
    will make sure the packages are installed. Collectd plugins are
    automatically installed/built if requirements are met, so there is no need
    for manual installation. A space separates packages.

    Example: COLLECTD_ADDITIONAL_PACKAGES="package1 package2 package3"


LIBVIRT_METER_ENABLED
~~~~~~~~~~~~~~~~~~~~~
    (True|False) Deprecating the libvirt meter. This configuration option
    allows you to enable it before it is removed.
    If this is false the virt meter for collectd is enabled on deployment.

    Default: False

Authenticating using Identity Server API v3
-------------------------------------------

following environment variables are used in this plugin for authentication
to Keystone API v3

OS_IDENTITY_API_VERSION
~~~~~~~~~~~~~~~~~~~~~~~
    specifies version of keystone API used, should be set to 3 as 2.0 is
    deprecated.
    Default: 3

OS_AUTH_URL
~~~~~~~~~~~
    url where keystone is listening
    Default: based on $KEYSTONE_AUTH_URI/v$IDENTITY_API_VERSION

OS_PASSWORD
~~~~~~~~~~~
    password for service tenant used for keystone authentication
    Default: based on $SERVICE_PASSWORD

OS_TENANT_NAME
~~~~~~~~~~~~~~
    name of service tenant used for keystone authentication
    Default: based on $SERVICE_TENANT_NAME
