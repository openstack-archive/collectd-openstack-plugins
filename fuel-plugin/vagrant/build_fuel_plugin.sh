#!/bin/bash
sudo apt-get update -y
sudo apt-get install createrepo rpm dpkg-dev -y
sudo apt-get install python-setuptools -y
sudo apt-get install python-pip -y
sudo easy_install pip
sudo pip install fuel-plugin-builder
sudo apt-get install ruby -y
sudo gem install rubygems-update
sudo gem install fpm
cd /home/vagrant
cp -r /collectd-ceilometer .
rm -rf collectd-ceilometer/fuel-plugin/vagrant/.vagrant
fpb --debug --build collectd-ceilometer/fuel-plugin
cp collectd-ceilometer/fuel-plugin/*.rpm /vagrant
