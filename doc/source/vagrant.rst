=======
Vagrant
=======

This project is distributed with a Vagrantfile intended to be use by developers
to run tests on a machine not capable of running collecd with this plugin.

The software required to run provided appliance is:
- An up to date Vagrant running on host machine
- A VirtualBox 4 or 5 to running on host machine

The provided by the appliance is:
- Ubuntu Server 14.04 LTS appliance running inside Virtual Box
- The collectd provided by Ubuntu
- Python 2.7 and 3.4 provided by Ubuntu
- This plugin
- Project dependencies provided by PIP as specified by project requirements

To use Vagrant to test this plugin you have to install following software
on your host machine.


Vagrant
_______

The Vagrant web site hosts a good documentation to install Vagrant on your
machine. Please see it there:

    https://www.vagrantup.com/docs/installation/

Please mind of having an up to date version of Vagrant installed on your
machine.


Virtual Box
-----------

Virtual Box version greater than 4 should works fine.

Many Linux distributions should provide a valid version of VirtualBox.

The Vagrant web site hosts some documentation and links to help you downloading
and installing Virtual Box on your machine. Please see it there:

    https://www.virtualbox.org/wiki/Downloads


Proxy configuration
-------------------

A fast internet connection is required to use Vagrant and tox to test this
project. If you are working beside a proxy server then you have to install
vagrant-proxyconf plugin::

    vagrant plugin install vagrant-proxyconf

You can have more details about the plugin on below site:

    https://github.com/tmatilai/vagrant-proxyconf

To use it, before creating target appliance, to use the Vagrantfile provided
by this project you have to configure standard enviroment variable on
your host machine like below::

    export http_proxy=http://<your.proxy.server>:<some_port?/
    export https_proxy=$https_proxy
    export no_proxy=localhost,$(hostname)

    vagrant up


Create and use your appliance
-----------------------------

Once all required software is installed your and configured you can create
and launch the appliance as follow (it can take several minutes) from
the project folder::

    vagrant up

Then to launch tests inside the appliance as follow::

    vagrant ssh -c 'cd /vagrant && tox'


Trouble shotting
----------------

Please report bugs to launch pad if you have some problems here:

    https://bugs.launchpad.net/collectd-ceilometer-plugin
