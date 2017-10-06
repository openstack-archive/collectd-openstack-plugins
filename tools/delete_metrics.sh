#!/bin/bash

echo "Gnocchi plugin metrics are being deleted. This may take a few minutes.."

openstack metric delete $(openstack metric list | awk '{if (NR>3) {print $2}}')

echo "Done deleting metrics created by the collectd-gnocchi-plugin"
