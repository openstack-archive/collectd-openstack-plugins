#!/bin/bash

if [[ `uname -a` =~ 'Ubuntu' ]]; then
    sudo apt-get install -y python-gnocchiclient
    # Update apache config to allow access to metric db, otherwise, apache2 will block communication
    # TODO(emma-l-foley): remove this debug line
    echo $PWD
    ls .
    ls ../
    ls ../../
    sudo find / | grep collectd-celometer-plugin
    ls /opt/stack/new/

    cd /opt/stack/new/gnocchi/devstack
    sed -i '/IfVersion>/a <Location \/v1\/metric>\n        Require all granted\n    <\/Location>' apache-ported-gnocchi.template
    cd -
else
    # Using CentOS
    # The default gnocchi client doesn't work, so we have to install a particular version for CentOS
    # install python-gnocchiclient stable/2.6
    TEMP_DIR=$PWD
    cd /tmp
    sudo  git clone https://github.com/openstack/python-gnocchiclient
    cd python-gnocchiclient
    sudo git checkout remotes/origin/stable/2.6
    sudo python setup.py install
    cd $TEMP_DIR

    # bypass uwsgi proble on CentOS
    export DEVSTACK_LOCAL_CONFIG=$DEVSTACK_LOCAL_CONFIG'
    WSGI_MODE="mod_wsgi"'
fi
