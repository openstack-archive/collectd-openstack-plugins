#!/bin/bash

FILE="/opt/stack/collectd-ceilometer/collectd_ceilometer/aodh/alarms.txt"
echo "collectd-aodh-plugin alarms are being deleted. This may take a few minutes.."
while read -r line
do
    aodh alarm delete $line
done < "$FILE"
echo "All alarms created by the collectd-aodh plugin have been deleted"
>$FILE
