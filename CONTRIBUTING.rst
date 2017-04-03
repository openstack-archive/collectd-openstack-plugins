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

=========================
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
------------------------------------------

As well as following the OpenStack contribution guidelines, there are a few
guidelines that should be observed for this project.

Blueprints
~~~~~~~~~~
Blueprints are generally not required for features. A bug should be opened in
launchpad instead and tagged as "rfe".


Feature development
~~~~~~~~~~~~~~~~~~~
Each feature should consist of a number of components (below), which can be submitted
in separate, dependant patches.

Each patch should function independently, and should work even if the
following patches are not applied.

The patches should include the following:

- Feature enabling code
  - For larger features, there might be several smaller patches.

- Unit tests
  - Tests should be included with the relevant feature code.

- Documentation
  - How does the feature work?
  - How do you configure this feature when installing a) manually and b) using
    devstack?
  - What configuration options were introduced/changed?
  - Examples for particular scenarios should be included in the
    doc/source/examples/ directory.
  - Updates to individual config options should be included in doc/source/usage.rst.

- Deployment code
  - At a minimum, deployment code for devstack, including
    any relevant config options, should be added.
  - Deployment code includes any changes to the given configurations.

- Release note
  - A reno entry needs to be included for every change:
    http://docs.openstack.org/developer/reno/usage.html#creating-new-release-notes


Bug Fixes
~~~~~~~~~
A bug fix will typically be a single patch, with any relevant changes to
documantation, configuration, etc included.

Release notes should be created using the bug number in the following way::
  reno new bug-123456

Release notes should reference the bug number and have a brief description
of the bug e.g.::
  critical|security|fixes:
    - Fixed bug #123456: Authentication token now automatically renews after
      expiry.
