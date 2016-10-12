===============================
collectd-ceilometer-plugin
===============================

OpenStack Ceilometer plugin for collectd.

This plugin for collectd publishes telemetry data gathered by collectd to
Ceilometer. This enables a more comprehensive telemetry set to be made
available to Ceilometer which will enable smarter scheduling and environmental
service assurance monitoring.

* Free software: Apache license
* Source: http://git.openstack.org/cgit/openstack/collectd-ceilometer-plugin
* Installation:
   https://github.com/openstack/collectd-ceilometer-plugin/blob/master/doc/source/installation.rst
* Bugs: http://bugs.launchpad.net/collectd-ceilometer-plugin
* Usage:
   https://github.com/openstack/collectd-ceilometer-plugin/blob/master/doc/source/usage.rst
* Code Reviews:
   https://review.openstack.org/#/q/status:open+project:openstack/collectd-ceilometer-plugin
* Contact: E-mail the dev mailing list with the [collectd-ceilometer-plugin] tag
   mailto:openstack-dev@lists.openstack.org?subject=[collectd-ceilometer-plugin]

Collateral
----------

The following are links to background information, collateral and references
to provide a clearer view on the need for this plugin, what it does and how it
works:

* An overview of Ceilometer and its architecture:
   http://docs.openstack.org/developer/ceilometer/overview.html
   http://docs.openstack.org/developer/ceilometer/architecture.html
* Official collectd website:
   https://collectd.org/
* Information on how collectd is enabled for Openstack:
   https://01.org/openstack/blogs/emmalfoley/2016/collectd-enabling-openstack
* Ceilometer and collectd are part of Openstacks telemetry project, the
  the following is the mission statement for this project:
   https://wiki.openstack.org/wiki/Telemetry
* Presentation on how collectd, Ceilometer and DPDK work together:
   https://www.youtube.com/watch?v=BdebhsBFEJs

Features
--------

* Converts from collectd data sources to Ceilometer format
  * Adds units for Ceilometer
* Devstack plugin
  * Configure and deploy plugin

