#!/bin/bash

# verify that db contains collectd metrics
# give it ~10 mins

retry_count=1
max_retry_count=20

export PATH=/usr/sbin:$PATH
source /opt/stack/new/devstack/openrc admin

while [ "$retry_count" -le "$max_retry_count" ]; do
    if [ $(gnocchi metric list | grep interface | wc -l) -eq 0 ] || [ $(ceilometer meter-list -l 1000 | grep
         echo "Testing metric interface not yet visible in db $retry_count/$max_retry_count"
    else
          echo "Testing metric obtained from db"
          exit 0
    fi
    let retry_count="$retry_count+1"
    sleep 30
done
echo "Testing metric interface not visible in db"
exit 1

