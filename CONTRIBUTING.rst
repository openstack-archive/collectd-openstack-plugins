Contributing to Openstack
=========================

If you would like to contribute to the development of OpenStack, you must
follow the steps in this page:

   http://docs.openstack.org/infra/manual/developers.html

If you already have a good understanding of how the system works and your
OpenStack accounts are set up, you can skip to the development workflow
section of this documentation to learn how changes to OpenStack should be
submitted for review via the Gerrit tool:

   http://docs.openstack.org/infra/manual/developers.html#development-workflow

Pull requests submitted through GitHub will be ignored.

Bugs should be filed on Launchpad, not GitHub:

   https://bugs.launchpad.net/collectd-ceilometer-plugin

Contributing to collectd-ceilometer-plugin
==========================================

As well as following the OpenStack contribution guidelines, there are a few guidelines that should be observed for this project.

Blueprints
----------
Blueprints are generally not required for features. A bug should be opened in launchpad instead and tagged as "rfe".


Feature development
-------------------
Each feature should consist of a number of components, which can be submitted in separate, dependant patches:
- Feature enabling code

- Unit tests

- Documentation
  - How does the feature work?
  - How do you configure this feature when installing a) manually and b) using devstack.

- Deployment code
  - At a minimum, deployment code for devstack should be included, including any relevant config options, should be included.

- Release note
  - A reno entry needs to be included for every change::
    http://docs.openstack.org/developer/reno/
