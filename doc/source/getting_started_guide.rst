=============================
Getting Started with Collectd
=============================

This is a getting started guide that describes the setup of collectd with
ceilometer plugin.

Pre-requisites
--------------

- Access to the internet
- Requires a working Openstack environment
- Keystone and Ceilometer services enabled

Linux Configuration
-------------------

Collectd Set-up
===============

Ensure that the binary package for your Linux distribution is installed
and up-to-date.

| sudo apt-get install build-essential

The plugins that collect the actual values depend on libraries that have
to be installed.

| sudo apt-get install flex bison automake pkg-config libtool python-dev

The source code for collectd can now be cloned from the github repo.

| git clone http://github.com/collectd/collectd

Currently there are two major versions of collectd; Version 4 and version 5.
Version 4 is outdated, so version 5 should be used for this setup. Hence, once
installed ensure you checkout the version 5.6 branch.

| cd collectd
| git checkout collectd-5.6

Then build this version.

| sudo ./build.sh

Once built collectd must be configured.

| sudo ./configure --enable-syslog --enable-plugin --enable-logfile --enable-debug --prefix=/usr

Now collectd can be installed.

| sudo make -j
| sudo make install

Setting Collectd as a Service
=============================

To enable collectd as a service on your system you must copy the .service
onto your system. This file is located in the "/collectd/contrib/" directory of
the repo.

| sudo cp contrib/systemd.collectd.service /lib/systemd/system

Now you can start collectd as a service, then check its status to ensure it is
running.

| sudo service systemd.collectd start
| sudo service systemd.collectd status

For further information on enabling collectd as a service:

 https://collectd.org/wiki/index.php/First_steps#Starting_the_daemon

Installation and Configuration of collectd-ceilometer-plugin
============================================================

To enable the collectd-ceilometer-plugin clone the source code from the repo.

| git clone https://github.com/openstack/collectd-ceilometer-plugin

By default the collectd.conf file is located in "/etc/collectd.conf", but
because you specified "--prefix=/usr" during configuration it is now located
"/usr/etc/collectd.conf".

Configurations for the plugin itself are specified in its own .conf file,
collectd-ceilometer-plugin.conf. The filepath to this file should be included
in the collectd.conf file.

| Include /path/to/collectd-ceilometer-plugin.conf

In the collectd-ceilometer-plugin.conf file a few variables have to be changed
to suit your environment:

* Set the "ModulePath" to be the location of your collectd-ceilometer-plugin
  directory.

* You must specify the service endpoint address, "OS_AUTH_URL". Generally in an
  openstack setup it will be in the format displayed below.

  | OS_AUTH_URL "http://your_IP_address:5000/v2.0"

  Otherwise, assuming you have a working openstack client, you could also check
  your credentials the openrc/localrc file provided. The format of your service
  endpoint address is usually supplied here.

* Finally, set the type of URL used for the ceilometer service to
  "internalURL".

  | CEILOMETER_URL_TYPE "internalURL"

Now, you can restart the collectd service and the plugin for ceilometer should
be working with collectd.

| sudo systemctl restart systemd.collectd.service

Verification of ceilometer
--------------------------

To verify that ceilometer is working with collectd you can use the ceilometer
client.

* Firstly, source the credentials required to use your openstack client.


  | source openrc

* To verify that the stats are going through to ceilometer, view the meter list
  for the ceilometer client.

  | ceilometer meter-list

  This list contains a number of meters being used. To confirm that ceilometer
  is working with collectd look for an entry labeled "cpu.cpu". This is one of
  the default metrics enabled by collectd.

Troubleshooting
===============

If you are unable to verify that ceilometer is working with collectd, try
restarting the service, then check the meter list again.

| systemctl restart systemd.collectd.service

Then you can also check the status of the service again or for further details
you can use the following command.

  | sudo journalctl -xe

This will allow you to examine any errors that are occuring.

If the plugin still doesn't appear to be working and the collectd service is
running correctly without any errors, try enabling a csv plugin. This will
allow you to check if collectd is generating any metrics.
Enable the csv plugin, restart collectd and check the destination directory
for the plugin. This will allow you to check if the plugin is loaded.

