===================================================
Installing Collectd-ceilometer-plugin with Devstack
===================================================

This guide outlines how to install the collectd-ceilometer-plugin using a
devstack deployment.

Pre-requisites
--------------

- Access to the internet

Installation of Devstack
========================

Follow the instructions provided in the following documentation to set up your
own Devstack deployment.

    http://docs.openstack.org/developer/devstack/guides/single-machine.html

Once Devstack is ready to be deployed, follow the configuration steps in the
next section to allow the installation of the plugin during deployment.

Configuration of Devstack
=========================

These configuration instructions only allow for the minimal installation of
collectd, ceilometer and the plugin. The sample local.conf provided must be
edited to enable additional services.

To configure Devstack to install the plugin, download the sample local.conf
from the collectd-ceilometer-plugin repo into your devstack directory.

| cd devstack
| wget https://github.com/openstack/collectd-ceilometer-plugin/blob/master/collectd_ceilometer/doc/source/examples/local.conf.minimal

Edit the "HOST_IP" varible in the file to appropriately match your environment.
Then change the name of this file to be "local.conf".

If you would like to enable any additional features read the "Additional
Features" section below before moving on to the next step.

Build your devstack environment.

| ./stack.sh

Verfication of Collectd-ceilometer-plugin
=========================================

Confirm that the collectd service is up and running.

| sudo systemctl status collectd.service

By default collectd enables the "cpu.cpu" meter. Check that the statistics for
this meter are being sent to ceilometer, thus confirming that collectd is
working with ceilometer.

| ceilometer sample-list --meter cpu.cpu

Additional Features
===================

Customizing units
-----------------

This feature enables you to customize the units of the data being collected.
To utilize this feature you must enable it before deploying Devstack. Follow
the instructions below to implement it:

  - Download the source code for the collectd-ceilometer-plugin.

| git clone https://github.com/openstack/collectd-ceilometer-plugin

  - Create a new branch of this code that you will use when deploying Devstack.

| cd collectd-ceilometer-plugin
| git checkout -b newB

  - In this branch, copy the contents of doc/source/example/units-collectd-ceilometer-plugin.conf
    to the file etc/collectd.conf.d/collectd-ceilometer-plugin.conf. Then,
    in this file edit the following line to include the meter and the units of
    the meter you want to change.

::

      UNIT "<meter>" "<units>"

    Additional lines of a similar nature can be added to change the units of
    more than one meter.

  - To ensure that this change gets deployed in devstack, commit the change to
    your new branch.

| git commit

  - Edit the line in your /home/stack/devstack/local.conf file that enables the
    collectd-ceilometer-plugin. Ensure that it calls the new branch you created
    with all of your unit changes.

::

     enable_plugin collectd-ceilometer-plugin /home/stack/collectd-ceilometer-plugin newB

  - Now you can deploy Devstack with your new customized units.

| cd /home/stack/devstack
| ./stack.sh

To verify that your units have been updated observe the ceilometer meter-list
or the sample-list and check the units of the meter that you changed.

| ceilometer meter-list | grep <meter>
| ceilometer sample-list | grep <meter>
