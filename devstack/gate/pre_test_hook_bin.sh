#!/bin/bash
DEVSTACK_LOCAL_CONFIG=$DEVSTACK_LOCAL_CONFIG'
RECLONE=True
'

if [[ `uname -a` =~ 'Ubuntu' ]]; then
    sudo apt-get install -y python-gnocchiclient
    # Update apache config to allow access to metric db, otherwise, apache2 will block communication
    # TODO(emma-l-foley): remove this debug line
    echo "DEBUGGING INFORMATION :)"
    echo $PWD
    ls /opt/stack/new/
    TEMP_DIR=$PWD
    cd /opt/stack/new/gnocchi
    git status
    echo "Current gnocchi HEAD"
    git log -1
    git branch -a
    git remote -v
    echo "Add a new remote for gnocchi"
    git remote add github http://www.github.com/gnocchixyz/gnocchi.git
    git fetch github
    echo "Check out the stable branch"
    git checkout github/stable/3.1
    ls
    echo "Current gnocchi HEAD"
    git log -1

    cd /opt/stack/new/gnocchi/devstack
    echo "What's in the gnocchi/devstack directory?"
    ls
    sed -i '/IfVersion>/a <Location \/v1\/metric>\n        Require all granted\n    <\/Location>' apache-ported-gnocchi.template
    cat apache-ported-gnocchi.template
    cd $TEMP_DIR
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
