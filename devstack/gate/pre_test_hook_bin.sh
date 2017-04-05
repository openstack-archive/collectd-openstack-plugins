#!/bin/bash

echo collectd-ceilometer-plugin pre-test-hook executed

# WA for https://github.com/pypa/setuptools_scm/issues/164
# it affects 15.5.3 version on gate mirror
# 15.5.5 not in sync yet
sudo -E git clone https://github.com/pypa/setuptools_scm
cd setuptools_scm
sudo -E python setup.py install
cd -

#if [ -f /usr/bin/yum ]; then
#    sudo yum -y install python-gnocchiclient
#elif [ -f /usr/bin/apt-get ]; then
#    sudo apt-get install -y python-gnocchiclient
#else
#    # w/o gnocchi client there is no sense in cont.
#    return 1 
#fi
