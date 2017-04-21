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

=============================
Getting Started with Collectd
=============================

This is a getting started guide that describes the setup of collectd with
ceilometer plugin.

Pre-requisites
--------------

- Access to the internet
- A working Openstack environment
- Keystone and Ceilometer services enabled

Collectd Set-up
---------------

Ensure that the binary packages for your Linux distribution are installed
and up-to-date.

::

  sudo apt-get install build-essential

Install the libraries that allow the plugins to collect the actual values:

::
 
  sudo apt-get install flex bison automake pkg-config libtool python-dev

Clone the source code from the repo:

::

  git clone http://github.com/collectd/collectd

Currently there are two major versions of collectd; Version 4 and version 5.
Version 4 is outdated, so version 5 should be used for this setup.
Checkout the version 5.6 branch:

::

  cd collectd
  git checkout collectd-5.6

Build this version:

::

  sudo ./build.sh

Configure collectd:

::

  sudo ./configure --enable-syslog --enable-plugin --enable-logfile --enable-debug --prefix=/usr

Install collectd:

::

  sudo make -j
  sudo make install

Configure Collectd as a Service
-------------------------------

To enable collectd as a service on your system copy the .service onto your
system. This file is located in the "/collectd/contrib/" directory of the repo.

::

  sudo cp contrib/systemd.collectd.service /lib/systemd/system

Start collectd as a service:

::

  sudo service systemd.collectd start

Check the status of collectd:

::

  sudo service systemd.collectd status

For further information on enabling collectd as a service:
 https://collectd.org/wiki/index.php/First_steps#Starting_the_daemon

Installation and Configuration of collectd-ceilometer-plugin
------------------------------------------------------------

Clone the collectd-ceilometer-plugin code.

::

  git clone https://github.com/openstack/collectd-ceilometer-plugin

By default, the collectd.conf file is located in "/etc/collectd.conf",
but because you specified "--prefix=/usr" during configuration it is now
located "/usr/etc/collectd.conf".

Configurations for the plugin itself are specified in its own .conf file,
collectd-ceilometer-plugin.conf.

Copy collectd-celiometer-plugin/etc/collectd.conf.d/collectd-ceilometer-plugin.conf
onto your machine. Include the filepath to this file in your collectd.conf file:

::

  Include /path/to/collectd-ceilometer-plugin.conf

In the collectd-ceilometer-plugin.conf file a few variables have to be changed
to suit your environment:

* Set the "ModulePath" to be the location of your collectd-ceilometer-plugin
  directory.

* You must specify the service endpoint address, "OS_AUTH_URL". In an openstack
  setup you can use the openstack client to identify this. Look for the keystone
  internalURL to and use it as your "OS_AUTH_URL".

  ::

       openstack catalog list

* Finally, set the type of URL used for the ceilometer service to
  "internalURL".

  ::
  
    CEILOMETER_URL_TYPE "internalURL"

* If you would like to enable any additional features please follow the
  instructions provided in the "Additional Features" section below before
  moving on to the next step.

Restart the collectd service:

::

  sudo service systemd.collectd restart

Verification of ceilometer
--------------------------

To verify that ceilometer is working with collectd use the ceilometer client.

* Source the credentials required to use your openstack client.

  ::

    source openrc

* To verify that the stats are going through to ceilometer, view the ceilometer
  meter list.

  ::

    ceilometer meter-list

  Specifically, one of the default meters that is enabled by collectd is
  "cpu.cpu". Check that this meter is enabled.

  ::

    ceilometer sample-list --meter cpu.cpu

Additional Features
-------------------

Customized Units
~~~~~~~~~~~~~~~

This feature enables you to customize the units of the data being collected. It
can be used to update existing units or add in new units by updating the plugin
to unit mappings. If you are creating a new meter by enabling a plugin which
doesn't provide its own unit mappings, this feature can be used to add in the
new units for this meter.

To utilize this feature you must enable it before restarting the service.
Follow the instructions below:

  - In your collectd-ceilometer-plugin.conf file add in the following lines
    at the end of the <Module> section. Edit the line to include the name of
    of your chosen meter and its new units.

   ::
 
      <UNITS>
        UNIT <meter_name> <units>
      </UNITS>

  - Additional lines of a similar nature can be added to change the units of
    multiple meters.

  - Restart the collectd service and your customized units will
    have been updated.

To verify that the units have been changed, observe the ceilometer meter-list
or the sample-list and check the units of the meter that you changed.

::

  ceilometer meter-list | grep <meter_name>
  ceilometer sample-list | grep <meter_name>


Troubleshooting
---------------

If you are unable to verify that ceilometer is working with collectd, try
restarting the service, then check the meter list again.

::

  systemctl restart systemd.collectd.service

Then you can also check the status of the service again or for further details
you can use the following command.

::

  sudo journalctl -xe

This will allow you to examine any errors that are occurring.

If the plugin still doesn't appear to be working and the collectd service is
running correctly without any errors, try enabling the csv plugin. This will
allow you to check if collectd is generating any metrics.
Enable the csv plugin, restart collectd and check the destination directory
for the plugin. This will allow you to check if the plugin is loaded.

