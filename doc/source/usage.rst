=====
Usage
=====

To use collectd-ceilometer-plugin in collectd::

    Python plugin must be enabled in collectd

    collectd must be started
    (ex: systemctl start collectd)

local.conf settings
-------------------

COLLECTD_CONF_DIR
    (directory) Specify a directory where collectd conf files reside.
    This is required if you use a distro other than Ubuntu or Fedora, or if
    the config file is in a non default location. This config directory will
    be created if it doesn't already exist.
    Default: /etc/collectd/collectd.conf.d (Ubuntu) /etc/collectd.d (Fedora)


COLLECTD_INSTALL
    (True|False) Indicates whether to install collectd from package manager.
    Set this to False if you are running a custom collectd build or do not
    want to upgrade installed version.
    Default: True


COLLECTD_BATCH_SIZE
    Set the amount of samples to be buffered before sending.
    Default: 1 i.e. no batching/buffering.


COLLECTD_DIR
    Specify collectd directory, this is required if collectd was installed
    manually.
    Default: /opt/collectd


CEILOMETER_TIMEOUT
    Sets the ceilometer's request timeout. The value is passed in milliseconds.
    Default: 1000 i.e. 1 sec.


COLLECTD_CEILOMETER_VERBOSE
    (True|False) Set this to True to make collectd-{ceilometer,gnocchi,aodh}
    debugging messages visible as info messagges. This is useful when running
    the plugin inside a collectd compiled without debug message support.
    Default: False


COLLECTD_LOG_FILE
    (file) The path of the collectd log file.
    Default: /opt/stack/logs/collectd.log


COLLECTD_LOG_LEVEL
    (debug|info|notice|warning|err) All log messages with lower log level than
    this are going to be filtered out from the log file.

    Default: info


COLLECTD_CUSTOM_UNITS
    (meter=unit) a comma seperated list of pairs, defining meters and their units.
    Allows existing units to be changed and new units to be set for new meters.
    The "meter" is generally in the form of "plugin.type", where plugin and
    plugin type are attributes of the collectd data.

    Example: COLLECTD_CUSTOM_UNITS="<meter> <unit>,<meter> <unit>"

COLLECTD_CEILOMETER_ENABLED
    (True|False) Toggle whether collectd-ceilometer-plugin is enabled.

    Default: False

COLLECTD_GNOCCHI_ENABLED
    (True|False) Toggles whether collectd-gnocchi-plugin is enabled.

    Default:True

COLLECTD_AODH_ENABLED
    (True|False) Toggles whether collectd-aodh-plugin is enabled.

    Default: False

Authenticating using Identity Server API v3
===========================================

following environment variables are used in this plugin for authentication
to Keystone API v3

OS_IDENTITY_API_VERSION
    specifies version of keystone API used, should be set to 3 as 2.0 is
    deprecated.
    Default: 3

OS_AUTH_URL
    url where keystone is listening
    Default: based on $KEYSTONE_AUTH_URI/v$IDENTITY_API_VERSION

OS_PASSWORD
    password for service tenant used for keystone authentication
    Default: based on $SERVICE_PASSWORD

OS_TENANT_NAME
    name of service tenant used for keystone authentication
    Default: based on $SERVICE_TENANT_NAME
