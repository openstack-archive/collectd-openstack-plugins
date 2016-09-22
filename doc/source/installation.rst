============
Installation
============

At the command line::

   - Run stack.sh with local.conf configured for ceilometer.

   - Configure the Openstack plugin - for more information see the file example.conf
     default configuration place is in /etc/collectd.d/collectd-ceilometer-plugin.conf

   - Enable some read plugins to get some stats in /etc/collectd.conf

   - $ sudo service collectd start

Manual install::
    
   - Run stack.sh with local.conf configured for ceilometer.

   - git clone https://github.com/openstack/collectd-ceilometer-plugin.git

   - Enable Python plugin in /etc/collectd.conf

        <LoadPlugin python>
          Globals true
        </LoadPlugin>

   - Enable the Openstack plugin in collectd configuration file:
     (use example.conf)

        <Plugin python>
           ModulePath "/path/to/your/pyton/modules"
           LogTraces true
           Interactive false
           Import "collectd_openstack_plugin"
        </Plugin>

   - Configure the Openstack plugin - for more information see the file example.conf

   - Enable some read plugins to get some stats

   - $ sudo service collectd start


Gnocchi
=======

To deploy with gnocchi using devstack, add the following to you local.conf:

    enable_plugin collectd-ceilometer-plugin /opt/stack/collectd-ceilometer-plugin-local/

    COLLECTD_INSTALL=True
    COLLECTD_CONF_DIR=/etc/collectd/collectd.conf.d/

    # GNOCCHI
    enable_plugin gnocchi https://github.com/openstack/gnocchi master
    enable_service gnocchi-api,gnocchi-metricd,gnocchi-statsd
    GNOCCHI_USE_KEYSTONE=True

Once deployment is complete, edit collectd-ceilometer-plugin.conf to point at the collectd_ceiloemter.gnocchi.plugin module.
