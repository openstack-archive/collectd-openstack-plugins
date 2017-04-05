#!/bin/bash

echo collectd-ceilometer-plugin pre-test-hook executed

if [ -f /usr/bin/yum ]; then
    sudo yum -y install python-gnocchiclient
elif [ -f /usr/bin/apt-get ]; then
    sudo apt-get install -y python-gnocchiclient
else
    # w/o gnocchi client there is no sense in cont.
    return 1 
fi
