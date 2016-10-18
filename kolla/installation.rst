Introduction
============

This document describes the steps to install, configure and verify the
operation of collectd with ceilometer plugin with Kolla.

Installation of Kolla
=====================

Please refer to doc for instructions about how to install kolla.

    http://docs.openstack.org/developer/kolla/quickstart.html

Install Collectd with Kolla
===========================

To install collectd with kolla, edit ``globals.yml`` file, go to monitoring
section. Change ``enable_collectd`` to ``yes``. Go to ``/etc/kolla`` folder
and edit ``kolla-build.conf`` file. Go to the plugins section. Paste the
following lines.

::

    [collectd-plugin-collectd-ceilometer-plugin]
    type = git
    location = https://github.com/openstack/collectd-ceilometer-plugin.git
    reference = master

To build the collectd container with the collectd-ceilometer-plugin
repository, copy the ``template-override.json`` file to a local directory.
Run the following command to build the container

::

    kolla-build --template-override <path_to_template_override_file>

Verification
============

To verify the successful build of collectd image run the following command.

::

    docker images | grep collectd

Follow the steps in the Kolla documentation to install OpenStack. Run the
following command to check if the collectd container is up and running.

::

    docker ps |grep -i collectd

The status of the collectd container should be up and running.

Configure collectd-ceilometer-plugin
====================================

Edit the ``collectd-ceilometer-plugin.conf`` file and replace the varaiables
with appropriate values. The passwords and endpoints will be provided by the
operator. If these entries are not provided, run the post-deploy script as
mentioned in the Kolla guide to generate the passwords and endpoints.

Copy this config file to ``collectd.conf.d`` folder under ``/etc/kolla``. Using
the following command restart the collectd container for the changes to get
effect.

::

    docker restart collectd

Verify the container is up and running.
