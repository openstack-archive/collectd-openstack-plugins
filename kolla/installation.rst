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

      Convention for heading levels in networking-ovs-dpdk documentation:

      =======  Heading 0 (reserved for the title in a document)
      -------  Heading 1
      ~~~~~~~  Heading 2
      +++++++  Heading 3
      '''''''  Heading 4

      Avoid deeper levels because they do not render well.

===============================================
Deploying collectd-ceilometer-plugin with Kolla
===============================================

This document describes the steps required to install, configure and verify the
operation of collectd with ceilometer plugin with Kolla.

Pre-requisites
--------------

- Access to the internet
- Keystone and Ceilometer enabled

Installation of Kolla
---------------------

Please refer to this doc for instructions about how to install kolla.

    https://docs.openstack.org/kolla-ansible/latest/quickstart.html

For the simplest installation follow the instructions for evaluation and
development purposes.

Install Collectd with Kolla
---------------------------

To install collectd with kolla, edit the ``globals.yml`` file and change the
following settings:

* Enable collectd so that its container is created. Additionally, enable
  ceilometer and mongodb to ensure the ceilometer service is installed.

    ::

      enable_collectd: "yes"
      enable_ceilometer: "yes"
      enable_mongodb: "yes"

* Edit the network settings to suit your environment by changing the
  following:

    ::

       kolla_internal_vip_address:
       network_interface:
       neutron_external_interface:

* To customize the images that are built with kolla change:

    ::

      kolla_base_distro:
      kolla_install_type:

In the kolla-build.conf file uncomment/paste the following lines into
the plugins section.

  ::

      [collectd-plugin-collectd-ceilometer-plugin]
      type = git
      location = https://github.com/openstack/collectd-ceilometer-plugin.git
      reference = master

To build the collectd container with the collectd-ceilometer-plugin
repository, copy the ``template-override.json`` file to a local directory.
Run the following command to build the container.

  ::

      $ kolla-build --template-override <path_to_template_override_file>

Verification of Collectd
------------------------

To verify the successful build of the collectd image run the following command.

  ::

      $ docker images | grep -i collectd

Follow the steps in the Kolla documentation to install OpenStack, which are
provided above. Run the following command to check if the collectd container
is up and running.

  ::

      $ docker ps | grep -i collectd

The status of the collectd container should be "Up".

Configure collectd-ceilometer-plugin
------------------------------------

Edit the ``/kolla/etc/collectd-ceilometer-plugin.conf`` file and replace the
variables with appropriate values. The passwords and endpoints will be
provided by the operator. If these entries are not provided, run the
post-deploy script as mentioned in the Kolla guide to generate the passwords
and endpoints.

The other entries you need to edit in this file are outlined below:

* Include the "ModulePath" to the collectd-ceilometer-plugin directory.

    ::

      ModulePath "/path/to/module"

* Specify your endpoint address, OS_AUTH_URL "<OS_AUTH_URL>". To determine this
  address, use your openstack client, run the following command and select the
  keystone internalURL.

    ::

     $ openstack catalog list

* The CEILOMETER_URL_TYPE should be set for you, but if not set it to
  "internalURL".

Copy this config file to ``/etc/kolla/collectd/collectd.conf.d`` folder.

  ::

    $ sudo cp collectd-ceilometer-plugin.conf /etc/kolla/collectd/collectd.conf.d

Restart the collectd container for the changes to take affect.

  ::

   $ docker restart collectd

Verify the container is up and running.

Verification of collectd-ceilometer-plugin
------------------------------------------

To verify that the plugin is working, use the ceilometer client.

* Source the credentials provided by the kolla post-deploy script.

    ::

      $ source admin-openrc.sh

* To verify that the stats are going through to ceilometer, view the meter
  list created by ceilometer.

    ::

      $ ceilometer meter-list

Check this list for the default meters that are enabled by collectd. One of
these is "cpu.cpu". Check the ceilometer sample list for this meter, to
confirm it is enabled.

  ::

    $ ceilometer sample-list --meter cpu.cpu
