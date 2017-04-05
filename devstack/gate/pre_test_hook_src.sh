#!/bin/bash

echo collectd-ceilometer-plugin pre-test-hook executed

# Gate repos contains old version of python-gnocchiclient
# that one is having an authentication issue with keystone
# returning 401Unauthorized, le'ts use newer instead
sudo -E git clone https://github.com/openstack/python-gnocchiclient
cd python-gnocchiclient
sudo -E git checkout 2.5.0
sudo -E python setup.py install
cd -
