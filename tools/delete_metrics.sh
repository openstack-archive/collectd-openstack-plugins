#!/bin/bash

FILE="/opt/stack/collectd-ceilometer/collectd_ceilometer/gnocchi/metrics.txt"
echo "All gnocchi plugin metrics are being deleted. This may take a few minutes.."
while read -r line
do
    openstack metric metric delete $line
done < "$FILE"
echo "All metrics created by the collectd-gnocchi-plugin have been deleted"
>$FILE
