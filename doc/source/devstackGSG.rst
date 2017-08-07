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

===================================================
Installing collectd-ceilometer-plugin with DevStack
===================================================

This guide outlines how to install the collectd-ceilometer-plugin using
DevStack.

Pre-requisites
--------------

- Access to the internet

Installation of DevStack
------------------------

Follow the instructions provided in the following documentation to set up your
own DevStack.

    https://docs.openstack.org/devstack/latest/guides/single-machine.html

Once DevStack is ready to be deployed, follow the configuration steps in the
next section to allow the installation of the plugin during deployment.

Configuration of DevStack
-------------------------

These configuration instructions only allow for the minimal installation of
collectd, gnocchi, aodh and the plugins in this repo. The sample local.conf
provided must be edited to enable additional services.

To configure DevStack for to install the plugin, download the sample local.conf
from the collectd-ceilometer-plugin repo into your DevStack directory.

  ::

    $ cd devstack
    $ wget https://github.com/openstack/collectd-ceilometer-plugin/blob/master/doc/source/examples/local.conf.minimal

Edit the "HOST_IP" varible to appropriately match your environment.

If you wish to enable any extra features please follow the instructions in the
"Additional Features" section below before moving on to the next step.

Create your DevStack environment:

  ::

    $ ./stack.sh

Verfication of collectd-gnocchi-plugin
--------------------------------------

Confirm that the collectd service is up and running:

  ::

    $ sudo systemctl status collectd.service

By default, collectd enables the "cpu.cpu" metric. Check that the statistics for
this metric are being sent to gnocchi, thus confirming that collectd is
working with gnocchi.

The commands you can use are:

  ::

    $ openstack metric metric list

to get a list of available metrics and

  ::

    $ openstack metric measures show <metric id>

to see the measures.

Additional Features
-------------------

Custom Units
~~~~~~~~~~~~

This feature enables users to define new units for existing meter values.
To enable this feature execute the following instructions:

* To include your new units, add the following line with your chosen units to
  your local.conf file.

    ::

      COLLECTD_CUSTOM_UNITS="<meter> <unit>"

* If you would like to add more than one new unit include them in the same line
  and seperate each meter and its unit with a comma, as shown below.

    ::

      COLLECTD_CUSTOM_UNITS="<meter> <unit>,<meter> <unit>"

Custom Packages Feature
------------------------

This feature enables users to define new packages to be installed when building
collectd.

* To include your new packages, add the following line with your chosen
  packages to your local.conf file.

| COLLECTD_ADDITIONAL_PACKAGES="package1 package2 package3"

Gnocchi
-------

To deploy with gnocchi using DevStack, add the following to you local.conf:

  ::

      enable_plugin collectd-ceilometer-plugin http://github.com/openstack/collectd-ceilometer-plugin

      COLLECTD_INSTALL=True

      # GNOCCHI
      enable_plugin gnocchi https://github.com/openstack/gnocchi master
      enable_service gnocchi-api,gnocchi-metricd,gnocchi-statsd
      GNOCCHI_USE_KEYSTONE=True
      COLLECTD_GNOCCHI_ENABLED=True

Gnocchi Tools
~~~~~~~~~~~~

 * delete_metrics
   A delete metrics tool is available to delete all metrics. This tool has to
   be used manually. See :doc:`<tools/delete_metrics.sh>`
   To delete all of the pre-existing metrics, just run the following command:

     ::

       $ . tools/delete_metrics.sh

Aodh
----

Aodh is an alarming service that allows an alarm to be created and/or updated
if there is something unusual happening with the system. When this service is
enabled via the collectd-ceilometer-plugin, it allows alarms to be
created/updated for all notifications sent from collectd. All notifications
sent from collectd are configured as event alarms in aodh.
To enable aodh with collectd, add the following to your local.conf:

  ::

     # AODH
     enable_plugin aodh https://git.openstack.org/openstack/aodh

     COLLECTD_AODH_ENABLED=True

This plugin allows you to specify the severity of the alarms that will be
created for meters.
To enable this add the following line to your local.conf, once you have enabled
the collectd-aodh-plugin:

::

  COLLECTD_AODH_SEVERITIES='"<meter>" <severity>'

You can set this severity to be one of three settings "low", "moderate" or
"critical". If you leave this unset for any of the meters that trigger an alarm
severity will default to "moderate".

In addition to this, alarms can be created manually via the aodh command line
based on the metrics generated by the gnocchi plugin.
For more information on this please read
:doc:`<alarms_guide.rst>`

Finally an alarm can also be created in a heat template. The instructions for
this are provided in :doc:`<heat_scaling_guide.rst>`

This enables you to scale a resource that you define based on the triggering of
an alarm.

Aodh Tools
~~~~~~~~~

 * delete_alarms
   When collectd is restarted duplicate alarms can be created if the same
   configuration is used. A delete alarms tool has been provided to allow
   deletion of all alarms before collectd restart.
   See :doc:`</tools/delete_alarms.sh>`
   To delete all of the alarms, just run the following command prior to
   restarting collectd:

     ::

       $ . tools/delete_alarms.sh
       $ sudo service collectd restart

Multi-Node Deployment
---------------------

The collectd-ceilometer-plugin can be used on a multi-node deployment. The
following is description of deployment options and configurations for a multi-
node setup:

* Set-up:
  To collect metrics from all of the nodes in your deployment collectd must be
  installed on each node. But the collectd-ceilometer-plugin only needs to be
  configured on the controller node.
* Configuration settings:
   - Set the configuration option that follows, in your local.conf on your
     controller node to True. This will configure the collectd network plugin:

    ::

        MULTI_NODE_DEPLOYMENT=True

   - Enable the collectd network plugin on all of your compute nodes that data
     is being collected from. Configure this plugin as follows:

    ::

        LoadPlugin network
        <Plugin network>
               Server "<CONTROLLER_NODE_HOST_IP>"
        </Plugin>

   - Enable the collectd virt plugin on all of your compute nodes as well. This
     is configured as follows:

    ::

        LoadPlugin virt
        <Plugin virt>
            Connection <HYPERVISOR_URI>
            HostnameFormat uuid
        </Plugin>


  .. note::

       Please refer to the following guide for more collectd network plugin
       configuration options:
       https://collectd.org/wiki/index.php/Plugin:Network
