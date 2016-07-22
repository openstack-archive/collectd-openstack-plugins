#!/bin/bash

# Vagrant provisioning script.

SOURCE_DIR="${SOURCE_DIR:-$(cd $(dirname $(dirname ${BASH_SOURCE[0]})) && pwd)}"
STACK_DIR="${STACK_DIR:-/opt/stack}"

PROXY_FILE="/etc/profile.d/proxy.sh"
COLLECTD_CEILOMETER_DIR="$STACK_DIR/collectd-ceilometer-plugin"
DEVSTACK_DIR="$STACK_DIR/devstack"
DEVSTACK_REPO="${GIT_BASE:-https://git.openstack.org}/openstack-dev/devstack.git"

echo "Start provisioning."
set -ex
export DEBIAN_FRONTEND="noninteractive"

# Make sure nameserver is configured
sudo bash -c 'echo nameserver 8.8.8.8 > /etc/resolv.conf'

echo "Update and install required packages."
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y git python-minimal python-setuptools\
    python-libvirt libvirt-bin

echo "Fix proxy variables."
if [ -r "$PROXY_FILE" ]; then
    echo "Fix proxy enviroment."
    TMP_PROXY_FILE=$(mktemp)
    python "$SOURCE_DIR/tools/get_proxy_env.py" > "$TMP_PROXY_FILE"
    sudo mv "$TMP_PROXY_FILE" "$PROXY_FILE"
    source "$PROXY_FILE"
fi

echo "Install and update main Python packages."
sudo easy_install pip
sudo pip install -U urllib3 pip setuptools tox

echo "Prepare devstack destination dir: $STACK_DIR."
sudo mkdir -p "$STACK_DIR"
sudo chown "$USER.$USER" $STACK_DIR

# This makes sure the collectd ceilometer plugin deployed is the one contained
# in the same folder as the Vagrantfile
if [ "$COLLECTD_CEILOMETER_DIR" != "$SOURCE_DIR" ]; then
    sudo rm -fR "$COLLECTD_CEILOMETER_DIR" || true
    sudo ln -sfn "$SOURCE_DIR" "$COLLECTD_CEILOMETER_DIR"
fi

if ! [ -d "$DEVSTACK_DIR" ]; then
    echo "Clone devstack."
    git clone "$DEVSTACK_REPO" "$DEVSTACK_DIR"
fi

pushd "$DEVSTACK_DIR"
    cp "$SOURCE_DIR/local.conf" .

    # unstack if stacking procedure has been already started before
    if [ -f ".stacking" ]; then
        echo "Unstack."
        (./unstack.sh && rm -fR ".stacking") || true
    fi

    echo "Start stacking."

    # GIT_BASE is forwarded from host machine to the guest virtual machine to make
    # devstack behaving like as it would have been executed on the bare host machine
    if [ -n "$GIT_BASE" ]; then
        # This is going to replace default values specified by devstack
        # but not the ones defined inside local.conf
        export GIT_BASE=$GIT_BASE
    fi

    touch ".stacking"
    # This tells collectd the source directory of the plugin is the one
    # where the Vagrantfile is (typically /vagrant)
    COLLECTD_CEILOMETER_DIR="$SOURCE_DIR" "./stack.sh"
popd

echo "Provisioned."
