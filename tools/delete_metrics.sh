#!/bin/bash

echo "All gnocchi plugin metrics are being deleted. This may take a few minutes.."
for metric in `openstack metric metric list | awk 'NR > 2 {print $2}'`;
do
    openstack metric metric delete $metric
done
echo "All metrics created by the collectd-gnocchi-plugin have been deleted"
