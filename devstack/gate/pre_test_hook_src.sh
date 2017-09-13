#!/bin/bash

export DEVSTACK_LOCAL_CONFIG=$DEVSTACK_LOCAL_CONFIG'
COLLECTD_INSTALL_TYPE=source'

cd /opt/stack/new/collectd-ceilometer-plugin/devstack/gate/
. ./pre_test_hook_bin.sh
cd -