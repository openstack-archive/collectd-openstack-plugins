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
    Default: /etc/collectd/collectd.conf.d (Ubuntu) /etc/collect.d (Fedora)


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
    (0|1) Sets this to 1 to make collectd-ceilometer debuggin messages visible
    as info messagges. This could be useful when running the plugin inside a
    collectd compiled without debug messages support.
    Default: 0


COLLECTD_LOG_FILE
    (file) The path of the collectd log file.
    Default: /opt/stack/logs/collectd.log


COLLECTD_LOG_LEVEL
    (debug|info|notice|warning|err) All log messages with lower criticity than
    this are going to be filtered out from the log file
    Default: info
