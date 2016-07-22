=======
Vagrant
=======

This project is distributed with a Vagrantfile intended to be used by
developers to run functional tests on a Linux virtual machine.

The software provided by the appliance are:
- Ubuntu Server 16.04 LTS appliance running inside Virtual Box
- The collectd provided by Ubuntu
- Python 2.7 and 3.4 provided by Ubuntu
- This plugin
- Project dependencies provided by PIP as specified by project requirements

To use Vagrant to test this plugin you have to install following software
up to date software on your host machine:
- Vagrant >= 1.8
- VirtualBox >= 5.1


Vagrant
-------

Documentation to install Vagrant can be found on there website at

    https://www.vagrantup.com/docs/installation/

A recent version of vagrant is required to utilize the vagrant file provided by
this repo. If you have an older version already installed please upgrade by
following the documentation at

    https://www.vagrantup.com/docs/installation/upgrading.html


Virtual Box
-----------

Virtual Box version greater than 5 should works fine.

Many Linux distributions should provide a valid version of VirtualBox.

The Virtual Box web site hosts some documentation and links to help you
downloading and installing Virtual Box on your machine. Please see it there:

    https://www.virtualbox.org/wiki/Downloads


Proxy configuration
-------------------

A fast internet connection is required to use Vagrant to test this project.
If you are working beside a proxy server then you have to install
vagrant-proxyconf plugin::

    vagrant plugin install vagrant-proxyconf

You can have more details about the plugin on below site:

    https://github.com/tmatilai/vagrant-proxyconf

To use it, before creating target appliance, you have to configure standard
enviroment variable on your host machine like below::

    export http_proxy=http://<some_proxy_server>:<some_port>/
    export https_proxy=$https_proxy
    export no_proxy=localhost,$(hostname)

    vagrant up


Create and use your appliance
-----------------------------

Once all required software is installed and configured you can create
and launch the appliance as follow (it can take several minutes) from
the project folder::

    vagrant up

During the provisioning process collectd and ceilometer are going to be
installed and launched.

To launch unit tests inside the appliance you can type following::

    vagrant ssh -c 'cd /opt/stack/collectd-ceilometer-plugin && tox'


Trouble shotting
----------------

Please report bugs to launch pad if you have some problems here:

    https://bugs.launchpad.net/collectd-ceilometer-plugin
