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

================================================
collectd-ceilometer-plugin troubleshooting guide
================================================

If you experience issues while deploying or using collectd-ceilometer-plugin,
the information below can help diagnose the problem:

- What version of keystone is being used in the deployment?
   - Version 2 is used in stable/mitaka version of the plugin, but Keystone V2
     has been deprecated.
   - Support for Keystone V3 API is available for the Newton release and above.

- Is ceilometer-acompute service enabled?
   - The ceilometer-acompute service provides metrics as well.
   - If the metrics from ceilometer-acompute are available, then the issue is
     likely with authentication of collectd-ceilometer-plugin.
   - If the metrics from ceilometer-acompute are not available, then the issue
     is with the database/storage engine, since no metrics are being stored.

- Are the credentials in collectd-ceilometer-plugin.conf valid?
   - Export these credentials to your environment as OS_PROJECT_NAME,
     OS_USERNAME and OS_PASSWORD, and use the openstack client.
   - If the credentials are valid, you should be able to interact with the
     OpenStack services
   - If the credentials are invalid, then you should get a response telling
     you that.

- Is the correct OS_AUTH_URL is used?

    ::

      $ openstack catalog show keystone
      $ grep "OS_AUTH_URL" /path/to/collectd.conf.d/collectd-ceilometer-plugin.conf

- Is collectd-ceilometer-plugin.conf being parsed?

  - Does the collectd.conf have an Include block/directive?

      ::

         Include "/etc/collectd/collectd.conf.d/*.conf"

    OR

      ::

         <Include /etc/collectd/collectd.conf.d/>
           Filter "*.conf"
         </Include>

- Enable the logfile plugin in collectd for better information (sample
  configuration at `../etc/collectd.conf.d/logging.conf`_).

  - Make sure to set the LogLevel to “debug” for maximum information
  - Use "VERBOSE True" in collectd-ceilometer-plugin.conf, in order to elevate
    debug messages to LogLevel info.
