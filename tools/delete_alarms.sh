#!/bin/bash

echo "collectd-aodh-plugin alarms are being deleted. This may take a few minutes.."
for alarm in `aodh alarm list | awk 'NR > 2 {print $2}'`;
do
    aodh alarm delete $alarm
done
echo "All alarms created by the collectd-aodh plugin have been deleted"
