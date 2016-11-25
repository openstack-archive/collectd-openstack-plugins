===================================================
Installing Collectd-ceilometer-plugin with Devstack
===================================================

This guide details how to install the collectd-ceilometer-plugin using a
devstack deployment.

Pre-requisites
--------------

- Access to the internet

Installation of Devstack
========================

Follow the instructions provided in the following document to set up your own
Devstack deployment.

    http://docs.openstack.org/developer/devstack/guides/single-machine.html

Once devstack, is installed edit the configuration file to enable the
installation of the collectd-ceilometer-plugin.

Configuration of Devstack
=========================

To configure Devstack for the plugin, edit the local.conf file. This should
be located in the following directory, devstack/local.conf. If this is not the
case create the file in that location.

For a basic installation of the plugin, fill in the local.conf file with the
following lines.

::

  [[local|localrc]]
  HOST_IP=<SINGLE NODE IP>

  MYSQL_PASSWORD=password
  DATABASE_PASSWORD=password
  RABBIT_PASSWORD=password
  ADMIN_PASSWORD=password
  SERVICE_PASSWORD=password
  HORIZON_PASSWORD=password
  SERVICE_TOKEN=tokentoken

  enable_plugin ceilometer https://github.com/openstack/ceilometer master
  enable_plugin collectd-ceilometer https://github.com/openstack/collectd-ceilometer-plugin master

  disable_all_services
  enable_service key
  enable_service mysql
  enable_service rabbit
  enable_service dstat
  enable_service ceilometer-acompute ceilometer-acentral ceilometer-collector ceilometer-api
  enable_service ceilometer-alarm-notifier ceilometer-alarm-evaluator

  COLLECTD_INSTALL=True
  COLLECTD_CEILOMETER_VERBOSE=True

Build your devstack environment.

| /.stack.sh

Start the collectd service.

| collectd

Verfication of Collectd-ceilometer-plugin
=========================================

Confirm that the collectd service is up and running.

| sudo systemctl status collectd.service

By default collectd enables the "cpu.cpu" meter. Check that the statistics for
this meter are being sent to ceilometer, thus confirming that collectd is
working with ceilometer.

| ceilometer sample-list --meter cpu.cpu
