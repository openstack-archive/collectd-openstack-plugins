#!/bin/bash

git clone http://www.github.com/gnocchixyz/gnocchi /opt/stack/new/gnocchi

if [[ `uname -a` =~ 'Ubuntu' ]]; then
    sudo apt-get install -y python-gnocchiclient
    # Update apache config to allow access to metric db, otherwise, apache2 will block communication
    echo $PWD
    ls /opt/stack/new/
    TEMP_DIR=$PWD
    cd /opt/stack/new/gnocchi/devstack
    sed -i '/IfVersion>/a         <Location \/v1\/metric>\n        Require all granted\n    <\/Location>' apache-ported-gnocchi.template
    cat apache-ported-gnocchi.template

    # DEBUG: commit it so devstack picks it up.
    git config user.name "Name"
    git config user.email "name@example.org"
    git commit -a -m "Updating apache-ported-gnocchi.template"
    cd $TEMP_DIR
else
    # Using CentOS
    sudo yum install bridge-utils -y
    # The default gnocchi client doesn't work, so we have to install a particular version for CentOS
    # install python-gnocchiclient stable/2.6
    TEMP_DIR=$PWD
    cd /tmp
    sudo  git clone https://github.com/openstack/python-gnocchiclient
    cd python-gnocchiclient
    sudo git checkout remotes/origin/stable/2.6
    sudo python setup.py install
    cd $TEMP_DIR

    # bypass uwsgi problem on CentOS
    export DEVSTACK_LOCAL_CONFIG=$DEVSTACK_LOCAL_CONFIG'
    WSGI_MODE="mod_wsgi"'
fi
