#!/bin/bash

# we need gnocchi client for the check
# verify that db contains collectd metrics
# give it ~10 mins

retry_count=1
max_retry_count=20
export PATH=/usr/sbin:$PATH
source /opt/stack/new/devstack/openrc admin

#if [ -f /usr/bin/yum ]; then
#    sudo yum update
#    sudo yum -y install python-gnocchiclient
#elif [ -f /usr/bin/apt-get ]; then
#    sudo apt-get update
#    sudo apt-get install -y python-gnocchiclient
#else
#    # w/o gnocchi client there is no sense in cont.
#    return 1
#fi

#####################
# print more debug  #
#####################
date
env | grep OS
gnocchi metric list || true
sleep 5
date
ceilometer meter-list || true
date
cat /etc/collectd/collectd.conf.d/*
date
mysql --user=root --password=secretmysql gnocchi -h 127.0.0.1 -e "show tables" || true
mysql --user=root --password=secretmysql gnocchi -h 127.0.0.1 -e "select name from metric" || true
mysql --user=root --password=secretmysql ceilometer -h 127.0.0.1 -e "show tables" || true
mysql --user=root --password=secretmysql ceilometer -h 127.0.0.1 -e "select name from meter" || true

#######################

while [ "$retry_count" -le "$max_retry_count" ]; do
    if [ $(gnocchi metric list | grep interface | wc -l) -eq 0 ] || [ $(ceilometer meter-list -l 1000 | grep interface | wc -l) -eq 0 ]; then
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

