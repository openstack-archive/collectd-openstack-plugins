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

==========================
collectd-ceilometer-plugin
==========================

OpenStack Ceilometer plugin for collectd.

This plugin for collectd publishes telemetry data gathered by collectd to
Ceilometer. This enables a more comprehensive telemetry set to be made
available to Ceilometer which will enable smarter scheduling and environmental
service assurance monitoring.

* Free software: Apache license
* Source: https://git.openstack.org/cgit/openstack/collectd-ceilometer-plugin
* Installation:
   https://git.openstack.org/cgit/openstack/collectd-ceilometer-plugin/tree/doc/source/installation.rst
* Bugs: https://bugs.launchpad.net/collectd-ceilometer-plugin
* Usage:
   https://git.openstack.org/cgit/openstack/collectd-ceilometer-plugin/tree/doc/source/usage.rst
* Contact: E-mail the dev mailing list with the [collectd-ceilometer-plugin] tag
   mailto:openstack-dev@lists.openstack.org?subject=[collectd-ceilometer-plugin]

Collateral
----------

The following are links to background information, collateral and references
to provide a clearer view on the need for this plugin, what it does and how it
works:

* An overview of Ceilometer and its architecture:
   https://docs.openstack.org/ceilometer/latest/overview.html
   https://docs.openstack.org/ceilometer/latest/architecture.html
* Official collectd website:
   https://collectd.org/
* Information on how collectd is enabled for Openstack:
   https://01.org/openstack/blogs/emmalfoley/2016/collectd-enabling-openstack
* Presentation on how collectd, Ceilometer and DPDK work together:
   https://www.youtube.com/watch?v=BdebhsBFEJs

Features
--------

* Converts from collectd data sources to Ceilometer format
  * Adds units for Ceilometer
* Devstack plugin
  * Configure and deploy plugin

