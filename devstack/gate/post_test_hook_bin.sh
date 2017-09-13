#!/bin/bash

# we need to verify that db contains collectd metrics
# give it ~10 mins

date
echo "Stacking is finished with all endpoints/services running"
echo "Need to restart collectd, which went into some wrong state"
echo "or ceilometer-collectd-plugin timeouts before establishing"
echo "connections to gnocchi"
sudo service collectd status
sudo service collectd restart

retry_count=1
max_retry_count=20
export PATH=/usr/sbin:$PATH
source /opt/stack/new/devstack/openrc admin

while [ "$retry_count" -le "$max_retry_count" ]; do
    # TODO: remove this debug
    # Getting message about deprecated command, advice to use "metric list" instead
    openstack metric list
    if [ $(openstack metric metric list | wc -l) -gt 4 ]; then
         echo "Testing metric interface not yet visible in db $retry_count/$max_retry_count"
    else
          echo "Testing metric obtained from db"
          exit 0
    fi
    let retry_count="$retry_count+1"
    sleep 30
done

echo "DEBUG:"
echo $(openstack metric metric list)
date
echo "[ERROR] Testing metric interface not visible in db!"
echo "Let's check collectd status:"
sudo service collectd status

exit 1
