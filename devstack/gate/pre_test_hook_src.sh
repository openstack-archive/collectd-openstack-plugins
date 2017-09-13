#!/bin/bash

export DEVSTACK_LOCAL_CONFIG=$DEVSTACK_LOCAL_CONFIG'
COLLECTD_INSTALL_TYPE=source'

. pre_test_hook_bin.sh
