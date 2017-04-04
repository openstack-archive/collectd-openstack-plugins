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

Follow the instructions provided in the following document to set up your own
Devstack deployment.

    http://docs.openstack.org/developer/devstack/guides/single-machine.html

Once Devstack is ready to be deployed, follow the configuration steps in the
next section to allow the installation of the plugin during deployment.

Configuration of Devstack
=========================

These configuration instructions only allow for the minimal installation of
collectd, ceilometer and the plugin. The sample local.conf provided must be
edited to enable additional services.

To configure Devstack for to install the plugin, download the sample local.conf
from the collectd-ceilometer-plugin repo into your devstack directory.

| cd devstack
| wget https://github.com/openstack/collectd-ceilometer-plugin/blob/master/collectd_ceilometer/doc/source/examples/local.conf.minimal

Edit the "HOST_IP" varible to appropriately match your environment.

Also include your chosen "CEILOMETER_BACKEND", as there is no default backend for
ceilometer. The options for this backend include mysql,es,postgresql or mongodb.

If you wish to enable any extra features please follow the instructions in the
"Additional Features" section below before moving on to the next step.

Finally, build your devstack environment.

| ./stack.sh

Verfication of Collectd-ceilometer-plugin
=========================================

Confirm that the collectd service is up and running.

| sudo systemctl status collectd.service

By default collectd enables the "cpu.cpu" meter. Check that the statistics for
this meter are being sent to ceilometer, thus confirming that collectd is
working with ceilometer.

| ceilometer sample-list --meter cpu.cpu

Addtional Features
==================

Custom Units Feature
--------------------

This feature enables users to define new units for existing meter values.
To enable this feature execute the following instructions:

* To include your new units, add the following line with your chosen units to
  your local.conf file.

| COLLECTD_CUSTOM_UNITS="<meter> <unit>"

  If you would like to add more than one new unit include them in the same line
  and seperate each meter and its unit with a comma, as shown below.

| COLLECTD_CUSTOM_UNITS="<meter> <unit>,<meter> <unit>"

Custome Packages Feature
------------------------

This feature enables users to define new packages to be installed when building
collectd. To enable this feature execute the following line instruction:

* To include your new packages, add the following line with your chosen
  packages to your local.conf file.

| COLLECTD_ADDITIONAL_PACKAGES="package1 package2 package3"

Gnocchi
=======

To deploy with gnocchi using devstack, add the following to you local.conf:

    enable_plugin collectd-ceilometer-plugin http://github.com/openstack/collectd-ceilometer-plugin

    COLLECTD_INSTALL=True

    # GNOCCHI
    enable_plugin gnocchi https://github.com/openstack/gnocchi master
    enable_service gnocchi-api,gnocchi-metricd,gnocchi-statsd
    GNOCCHI_USE_KEYSTONE=True
    COLLECTD_GNOCCHI_ENABLED=True

Aodh
====

Aodh is an alarming service that allows an alarm to be created and/or updated
if there is something unusual happening with the system. When this service is
enabled via the collectd-ceilometer-plugin, it allows alarms to be
created/updated for all notifications sent from collectd. All notifications
sent from collectd are configured as event alarms in Aodh.
To enable aodh with collectd, add the following to your local.conf:

   #AODH
   enable_plugin aodh https://git.openstack.org/openstack/aodh

   enable_plugin collectd-ceilometer-plugin http://github.com/openstack/collectd-ceilometer-plugin
   COLLECTD_AODH_ENABLED=True
