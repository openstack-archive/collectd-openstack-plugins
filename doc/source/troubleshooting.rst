collectd-ceilometer-plugin troubleshooting guide
================================================

If you experience issues while deploying or using collectd-ceilometer-plugin, the information below can help diagnose the problem:


- What version of keystone is being used in the deployment?
   -  Version 2 is used in stable/mitaka version of the plugin, but Keystone V2 has recently been deprecated.

- Is ceilometer-acompute service enabled?
   - This service provides metrics as well
   - If the metrics from ceilometer-acompute are available, then the issue is likely with authentication of collectd-ceilometer-plugin
   - If the metrics from ceilometer-acompute are not available, then this indicates that the issue is with the database/storage engine, since no metrics are being stored.

- Are the credentials in collectd-ceilometer-plugin.conf valid?
   - Export these credentials to your environment as OS_TENANT_NAME|OS_PROJECT_NAME, OS_USERNAME and OS_PASSWORD, and use the openstack client.
   - If the credentials are valid, you should be able to interact with the OpenStack services
   - If the credentials are invalid, then you should get a response telling you that.

- Is the correct OS_AUTH_URL is used?

- Is collectd-ceilometer-plugin.conf being parsed?
  - Does the collectd.conf have an Include block/directive?
    ::
       Include "/etc/collectd/collectd.conf.d/*.conf"
    OR
    ::
       <Include /etc/collectd/collectd.conf.d/>
         Filter "*.conf"
       </Include>

- Enable the logfile plugin in collectd for better information (sample configuration at `../etc/collectd.conf.d/logging.conf`_)
   - Make sure to set the LogLevel to “debug” for maximum information
   - Use “VERBOSE True” in collectd-ceilometer-plugin.conf, in order to elevate debug messages to LogLevel info.
