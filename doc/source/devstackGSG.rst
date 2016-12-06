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
