========
Usage
========

To use collectd-ceilometer-plugin in collectd::

    Python plugin must be enabled in collectd

    collectd must be started
    (ex: systemctl start collectd)

local.conf settings
-------------------

COLLECTD_CONF_DIR
    (directory) Specify a directory where collectd conf files reside.
    This is required if you use a distro other than Ubuntu or Fedora, or if
    the config file is in a non default location.
    Default: /etc/collectd/collectd.conf.d (Ubuntu) /etc/collect.d (Fedora)


COLLECTD_INSTALL
    (True|False) Indicates whether to install collectd from package manager.
    Set this to False if you are running a custom collectd build or do not
    want to upgrade installed version.
    Default: True
