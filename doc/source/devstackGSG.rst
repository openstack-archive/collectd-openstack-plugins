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

Once devstack is installed follow the configuration instructions to install the
plugin.

Configuration of Devstack
=========================

To configure Devstack for to install the plugin, copy
/home/stack/devstack/doc/source/examples/local.conf to /home/stack/devstack/.

| cp /home/stack/devstack/doc/source/examples/local.conf /home/stack/devstack/

Edit the "HOST_IP" varible to appropriately match your environment.

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
