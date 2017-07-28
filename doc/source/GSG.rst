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

This is a getting started guide that describes the manual setup of collectd
and the configuration of the plugins contained in this repository (Gnocchi, Aodh).

Pre-requisites
--------------

- Access to the internet
- A working OpenStack environment
- Keystone service enabled
- Gnocchi and/or Aodh service(s) enabled


Collectd Installation
---------------------

This section describes how to install collectd.

* Ensure that the binary packages for your Linux distribution are installed and
  up-to-date.

  ::

    $ sudo apt-get update && sudo apt-get upgrade
    # OR
    $ sudo yum update

* Install packages required for the collectd OpenStack plugins

  ::

    $ sudo apt-get install libvirt-bin libvirt-dev python-libvirt
    # OR
    $ sudo yum install libvirt libvirt-devel libvirt-python

.. note::
   The following instructions are for building collectd from source, if you
   want to install from the package manager instead, then run the following
   commands instead and jump to `Configuration of collectd openstack plugins`_

     ::

       $ sudo apt-get install collectd
       # OR
       $ sudo yum installl collectd

* Install the libraries to are needed to build collectd:

  ::

    $ sudo apt-get install byacc flex bison build-essential automake libgcrypt20 libtool
    # OR
    $ sudo yum install flex bison automake autoconf libtool


* Install plugin prerequisites.
  If the requirements for a plugin are installed, collectd will build this
  plugin. Collectd documentation provides a
  `list of requirements for each plugin <https://github.com/collectd/collectd/blob/master/README>`_.

* Clone the source code from the repo:

  ::

    $ git clone http://github.com/collectd/collectd

The current major version of collectd is version 5

* Checkout the version 5.7 branch (or use master)

  ::

    $ cd collectd
    $ git checkout collectd-5.7

* Generate the config script

  ::

    $ ./build.sh

* Configure the build

  ``<COLLECTD_PREFIX>`` is the location where collectd will be built, common
  values are /usr and /opt/collectd.
  Substitute it in the following commands.

  ::

     $ ./configure --enable-python --enable-debug \
     --enable-logging --enable-syslog --prefix=<COLLECTD_PREFIX>

* Compile and install collectd

  ::

    $ make -j all
    $ sudo make install

Configure the Collectd Service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This section covers configuring the collectd service if your system uses systemd to
manage services.

To enable collectd to run as a service:

* Add the collectd unit file to your system.
  This file is located in the "contrib/" directory of the collectd repo.

  ::

    $ sudo cp contrib/systemd.collectd.service /etc/systemd/system/collectd.service

* Edit the file so that it points to the collectd binary.

  ::

    ExecStart=<COLLECTD_PREFIX>/sbin/collectd -C <COLLECTD_PREFIX>/etc/collectd.conf

* Enable collectd

  ::

    $ sudo systemctl enable collectd

* Start the collectd service:

  ::

    $ sudo systemctl start collectd

* Check the status of collectd

  ::

    $ sudo systemctl status collectd

For further information on enabling collectd as a service:
 https://collectd.org/wiki/index.php/First_steps#Starting_the_daemon

Configuring Collectd
--------------------

* Locate collectd.conf

  * If you installed collectd from a package manager, ``collectd.conf`` is
    located in ``/etc/collectd.conf``.

  * If you built from source, ``collectd.conf`` is located at
    ``<COLLECTD_PREFIX>/etc/collectd.conf``.

* Configure some `collectd plugins <https://collectd.org/documentation/manpages/collectd.conf.5.shtml>`_.

* Update collectd.conf to ensure that the files in the configuration directory are loaded.

  ::

    $ cat << EOF | sudo -E tee -a $<COLLECTD_PREFIX>/etc/collectd.conf

         <Include "<COLLECTD_PREFIX/etc/collectd.conf.d/">
             Filter "*.conf"
         </Include>
      EOF

* Configure some collectd plugins

Collectd openstack plugins
--------------------------
This section describes the steps to installing and configuring the collectd
plugins for Ceiloemter, Gnocchi and Aodh.

* Clone the collectd-ceilometer-plugin code.

  ::

    $ git clone https://github.com/openstack/collectd-ceilometer-plugin
    $ cd collectd-ceilometer-plugin

* Install the module and requirements

  ::

    $ sudo pip install .

Sample configurations for each of the plugins in this repo are included under
``collectd-ceilometer-plugin/etc/collectd.conf.d/``
These files should be copied into the collectd configuration directory
``<COLLECTD_PREFIX>/etc/collectd.conf.d/``, and updated to reflect your environment

* Copy the sample plugin configurations to the configuration directory:

  ::

    $ sudo cp etc/collectd.conf.d/collectd-*-plugin.conf <COLLECTD_PREFIX>/etc/collectd.conf.d/

* To ensure that logging is enabled before any other plugin, copy the sample log
  file to the configuration directory

  ::

    $ sudo cp $COLLECTD_CEILOMETER_DIR/etc/collectd.conf.d/logfile.conf <COLLECTD_PREFIX>/etc/collectd.conf.d/01-logfile.conf


The following instructions apply to collect-gnocchi and collectd-aodh plugins.


In the collectd-{gnocchi,aodh}-plugin.conf file a few variables
have to be changed to suit your environment:

* Set the ``ModulePath`` to be the location of your collectd-ceilometer-plugin
  directory (this values will be the same for Gnocchi and Aodh plugins).

  ::

    <Plugin python>
        ModulePath "/path/to/collectd-ceilometer-plugin"
        ...

* You must specify the service endpoint address, ``OS_AUTH_URL``. In an openstack
  setup you can use the openstack client to identify this.

  * Find the keystone service endpoint

    ::

      $ openstack catalog list

  * Update collectd-{gnocchi,aodh}-plugin.conf

    ::

      OS_AUTH_URL "http://<KEYSTONE_HOST>/identity/v3"


* Modify the credentials for the openstack service that the plugin is using.
  These will be different for gnocchi and aodh.
  These values are set when creating the Aodh and Gnocchi services in OpenStack.
  If you used an installer, some typical values are shown below.

  ::

        # Service user creds
        OS_USERNAME "aodh"|"gnocchi"|etc
        OS_PASSWORD <password for the user>
        OS_TENANT_NAME "service"|"services"|etc


If you would like to enable any additional features please follow the
instructions provided in the `Additional Features`_ section below before moving
on to the next step.

* Restart the collectd service to load the new configuration:

    ::

      $  sudo systemctl restart collectd

Verification
------------

To verify that the plugins are working with collectd, use the OpenStack client.

* Source the credentials required to use the OpenStack client.

    ::

      $ source openrc

The following commands vary, depending on which plugins are configured.

If you are using collectd-gnocchi-plugin:

* Verify that the metrics are being created in gnocchi:

  ::

    $ openstack metric metric list

* Check on individual metrics:

  ::

    $ openstack metric measures show <metric_ID>


If you are using collectd-aodh-plugin, it is harder to verify that this is
working, as collectd-aodh sends notifications, and not regular metrics.

To verify, you can use the
`collectd-threshold <https://collectd.org/documentation/manpages/collectd-threshold.5.shtml>`_
plugin, and set some really low thresholds in order to generate notifications
for collectd_aodh to send.

Additional Features
-------------------


Customized Units
~~~~~~~~~~~~~~~~

This feature enables you to customize the units of the data being collected. It
can be used to update existing units or add in new units by updating the plugin
to unit mappings. If you are creating a new meter by enabling a plugin which
doesn't provide its own unit mappings, this feature can be used to add in the
new units for this meter.

  .. NOTE::

     This feature is for collectd-gnocchi

* In your collectd-gnocchi-plugin.conf file add in the following lines
  at the end of the <Module> section. Edit the line to include the name of
  of your chosen meter and its new units.

    ::

      <UNITS>
        UNIT <meter_name> <units>
      </UNITS>

* Additional lines of a similar nature can be added to change the units of
  multiple meters.

* Restart the collectd service and your customized units will be updated.

    ::

      $  sudo systemctl restart collectd

* Verify that the units have been changed:

  ::
    # For Gnocchi:
    $ openstack metric metric list | grep <metric_name>
    # OR
    $ openstack metric measures show <metric_id>

Troubleshooting
---------------

If you are unable to verify that Gnocchi is working with collectd, try
restarting the service, then check the metric list again.

  ::

    $ sudo systemctl restart collectd

Then you can also check the status of the service again or for further details
you can use the following command.

  ::

    $ sudo journalctl -xe

This will allow you to examine any errors that are occurring.

If the plugin still doesn't appear to be working and the collectd service is
running correctly without any errors, try enabling the csv plugin. This will
allow you to check if collectd is generating any metrics.
Enable the csv plugin, restart collectd and check the destination directory
for the plugin. This will allow you to check if the plugin is loaded.
