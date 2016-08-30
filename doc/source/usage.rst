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
    (<git branch>) Indicates which branch of collectd to checkout before
    compiling.

    Default: collectd-5.6

COLLECTD_CONF_DIR
    (directory) Specify a directory where collectd conf files reside.
    This is required if you use a distro other than Ubuntu or Fedora, or if
    the config file is in a non default location. This config directory will
    be created if it doesn't already exist.
    Default: /etc/collectd/collectd.conf.d (Ubuntu) /etc/collectd.d (Fedora)

COLLECTD_DIR
    (directory) Destination of the cloned collectd source code.
    Default: $DEST/collectd-$COLLECTD_BRANCH/

COLLECTD_INSTALL
    (True|False) Indicates whether to install collectd.

    Set this to False if you are running a pre-built version of collectd or do
    not want to upgrade installed version.

    Default: True

COLLECTD_BATCH_SIZE
    Set the amount of samples to be buffered before sending.
    Default: 1 i.e. no batching/buffering.


CEILOMETER_TIMEOUT
    Sets the ceilometer's request timeout. The value is passed in milliseconds.
    Default: 1000 i.e. 1 sec.


COLLECTD_CEILOMETER_VERBOSE
    (True|False) Set this to True to make collectd-ceilometer debugging
    messages visible as info messagges. This is useful when running the
    plugin inside a collectd compiled without debug message support.
    Default: False


COLLECTD_LOG_FILE
    (file) The path of the collectd log file.
    Default: /opt/stack/logs/collectd.log


COLLECTD_LOG_LEVEL
    (debug|info|notice|warning|err) All log messages with lower log level than
    this are going to be filtered out from the log file.
    Default: info


COLLECTD_INSTALL_TYPE
    (source|binary) Specify whether the collectd installation should use the
    package manager or install from source.

    Default: binary


COLLECTD_REPO
    (url) Location of git repo to clone collectd from.

    Default: https://github.com/collectd/collectd.git
