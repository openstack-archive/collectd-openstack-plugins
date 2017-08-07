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

<<<<<<< HEAD
Collectd plugins for publishing to OpenStack (Gnocchi and Aodh).

This repositiory contains collectd plugins for publishing telemetry data
(metrics and events) gathered by collectd to Gnocchi and Aodh.
=======
Collectd plugins for publishing to OpenStack (ceilometer, gnocchi and aodh).

This repositiory contains collectd plugins for publishing telemetry data
(metrics and events) gathered by collectd to ceilometer, gnocchi and aodh.
>>>>>>> 5f200f9... Inconsistent capitalization on Gnocchi, Aodh, OpenStack in docs
This allows a more comprehensive set of platform telemetry to be made available
to OpenStack which enables service assurance, fault management and  monitoring.

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

<<<<<<< HEAD
=======
* An overview of ceilometer and its architecture:
   http://docs.openstack.org/developer/ceilometer/overview.html
   http://docs.openstack.org/developer/ceilometer/architecture.html
>>>>>>> 5f200f9... Inconsistent capitalization on Gnocchi, Aodh, OpenStack in docs
* Official collectd website:
   https://collectd.org/
* Information on how collectd is enabled for Openstack:
   https://01.org/openstack/blogs/emmalfoley/2016/collectd-enabling-openstack
* Presentation on how collectd, ceilometer and DPDK work together:
   https://www.youtube.com/watch?v=BdebhsBFEJs

Features
--------

<<<<<<< HEAD
=======
* Ceilometer plugin (for collectd)
  ** Converts from collectd data sources to ceilometer format
  ** Adds units for ceilometer
>>>>>>> 5f200f9... Inconsistent capitalization on Gnocchi, Aodh, OpenStack in docs
* Gnocchi plugin (for collectd)
  ** Store collectd metrics in gnocchi
* Aodh plugin (for collectd)
  ** Forward collectd notifications to aodh
* Devstack plugin (for deploying the contents of this repo)
  ** Configure and deploy plugins
  ** Build collectd from source
