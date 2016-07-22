#!/bin/bash

SOURCE_DIR="${SOURCE_DIR:-$(cd $(dirname $(dirname ${BASH_SOURCE[0]})) && pwd)}"
STACK_DIR="${STACK_DIR:-/opt/stack}"

GIT_BASE="${GIT_BASE:-https://git.openstack.org}"
PROXY_FILE="/etc/profile.d/proxy.sh"
COLLECTD_CEILOMETER_DIR="$STACK_DIR/collectd-ceilometer-plugin"
DEVSTACK_DIR="$STACK_DIR/devstack"
DEVSTACK_REPO="$GIT_BASE/openstack-dev/devstack.git"

echo "Start provisioning."
set -ex
export DEBIAN_FRONTEND="noninteractive"

echo "Update and install required packages."
# echo | sudo add-apt-repository cloud-archive:mitaka || true
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y git python-minimal python-setuptools libvirt-bin

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
sudo rm -fR "$COLLECTD_CEILOMETER_DIR" || true
sudo ln -sfn "$SOURCE_DIR" "$COLLECTD_CEILOMETER_DIR"

if ! [ -d "$DEVSTACK_DIR" ]; then
    echo "Clone devstack."
    git clone "$DEVSTACK_REPO" "$DEVSTACK_DIR"
fi

pushd "$DEVSTACK_DIR"
    cp "$SOURCE_DIR/local.conf" .

    if [ -f ".stacking" ]; then
        echo "Unstack."
        (./unstack.sh && rm -fR ".stacking") || true
    fi

    echo "Stack."
    touch ".stacking" && GIT_BASE="$GIT_BASE" COLLECTD_CEILOMETER_DIR="$SOURCE_DIR" "./stack.sh"
popd

echo "Provisioned."
