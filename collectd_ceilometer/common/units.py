# -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
"""Ceilometer collectd plugin units definition"""

from __future__ import unicode_literals


# Unit mappings in alphabetical order
UNITS = {
    'apache.apache_idle_workers':   'Workers',
    'apache.apache_bytes':          'B/s',
    'apache.apache_requests':       'Req/s',
    'apache.apache_scoreboard':     'Slots',
    'apache.apache_connections':    'Connections',

    'apcups.timeleft':      's',
    'apcups.temperature':   '°C',
    'apcups.percent':       'Load',
    'apcups.charge':        'Ah',
    'apcups.frequency':     'Hz',
    'apcups.voltage':       'V',

    # 'ascent': 'None',

    'battery.current': 'A',
    'battery.charge':  'Ah',
    'battery.voltage': 'V',

    # 'bind': 'None',

    'conntrack': 'Entries',
    'contextswitch': 'Sw./s',
    'cpu': 'jiffies',
    'cpufreq': 'MHz',

    'dbi': 'Count',
    'dbi.mysql_databasesize': 'B',
    'dbi.pg_db_size': 'MB',

    'df': 'B',

    'disk.disk_merged':     'Ops/s',
    'disk.disk_octets':     'B/s',
    'disk.disk_ops':        'Ops/s',
    'disk.disk_time':       's',

    'dns.dns_opcode':   'Queries/s',
    'dns.dns_qtype':    'Queries/s',
    'dns.dns_octets':   'b/s',
    'dns.dns_rcode':    'Queries/s',

    'entropy': 'b',

    'filecount.files': 'Files',
    'filecount.bytes': 'B',

    'hddtemp': '°C',

    'interface.if_octets': 'B/s',
    'interface.if_errors': 'Errors/s',
    'interface.if_packets': 'Packets/s',

    'ipmi.fanspeed':    'RPM',
    'ipmi.temperature': '°C',
    'ipmi.voltage':     'V',

    'iptables.ipt_bytes':   'B',
    'iptables.ipt_packets': 'Packets',

    'irq': 'Irq/s',

    'libvirt.if_octets':        'B/s',
    'libvirt.virt_cpu_total':   'ms',
    'libvirt.disk_octets':      'B/s',
    'libvirt.virt_vcpu':        'ms',
    'libvirt.if_dropped':       'Packets/s',
    'libvirt.if_errors':        'Errors/s',
    'libvirt.if_packets':       'Packets/s',
    'libvirt.disk_ops':         'Ops/s',

    'load': '',
    'lvm': 'B',
    # 'madwifi': 'None',
    # 'mbmon': 'None',
    'md': 'Disks',

    'memcached.memcached_command':      'Commands',
    'memcached.memcached_items':        'Items',
    'memcached.df':                     'B',
    'memcached.memcached_ops':          'Commands',
    'memcached.ps_count':               'Threads',
    'memcached.percent':                '%',
    'memcached.memcached_connections':  'Connections',
    'memcached.memcached_octets':       'B',
    'memcached.ps_cputime':             'Jiffies',

    'memory': 'B',

    'mysql.mysql_commands':     'Commands/s',
    'mysql.mysql_qcache':       'Queries',
    'mysql.mysql_locks':        'locks',
    'mysql.cache_result':       'Queries/s',
    'mysql.total_threads':      'Threads',
    'mysql.mysql_handler':      'Invocations',
    'mysql.threads':            'Threads',
    'mysql.mysql_octets':       'B/s',
    'mysql.mysql_log_position': 'Position',
    'mysql.cache_size':         'Queries',
    'mysql.time_offset':        's',
    'mysql.mysql_threads':      'Threads',

    'netlink.if_rx_errors':     'Errors/s',
    'netlink.if_octets':        'B/s',
    'netlink.if_multicast':     'Packets/s',
    'netlink.if_dropped':       'Packets/s',
    'netlink.if_errors':        'Errors/s',
    'netlink.if_packets':       'Packets/s',
    'netlink.if_tx_errors':     'Errors/s',
    'netlink.if_collisions':    'Collisions/s',

    'nfs': 'Calls',

    'nginx.connections':        'Connections',
    'nginx.nginx_requests':     'Requests/s',
    'nginx.nginx_connections':  'Connections/s',

    'ntpd': 's',
    'ntpd.frequency_offset': 'ppm',

    'numa': 'Actions',

    'nut.timeleft':     's',
    'nut.temperature':  '°C',
    'nut.power':        'VA',
    'nut.percent':      '%',
    'nut.frequency':    'Hz',
    'nut.voltage':      'V',

    'openvpn.if_octets': 'B/s',
    'openvpn.users':     'Users',

    # 'pinba': 'None',
    'ping': 'ms',

    'postgresql.pg_blks':           'Blocks',
    'postgresql.pg_xact':           'Transactions',
    'postgresql.pg_n_tup_g':        'Rows',
    'postgresql.pg_numbackends':    'Backends',
    'postgresql.pg_n_tup_c':        'Rows',
    'postgresql.pg_db_size':        'B',
    'postgresql.pg_scan':           'Scans/Rows',

    'processes':                'Processes',
    'processes.fork_rate':      'forks/s',
    'processes.ps_cputime':     'Jiffies',
    'processes.ps_disk_octets': 'B/s',
    'processes.ps_disk_ops':    'Ops/s',
    'processes.ps_pagefaults':  'Pagefaults',
    'processes.ps_rss':         'B',
    'processes.ps_vm':          'B',
    'processes.ps_stacksize':   'B',
    'processes.ps_code':        'B',
    'processes.ps_data':        'B',

    'swap': 'B',
    'swap.swap_io': 'Pages',

    'tcpconns': 'Connections',
    'thermal': '°C',
    'uptime': 's',
    'users': 'Users',

    'varnish.total_sessions':   'Sessions',
    'varnish.cache':            'Hits',
    'varnish.cache_result':     'Hits',
    'varnish.connections':      'Hits',
    'varnish.total_threads':    'Thread',
    'varnish.http_requests':    'Operations',
    'varnish.total_bytes':      'B',
    'varnish.threads':          'Thread',
    'varnish.total_requests':   'Requests',
    'varnish.total_operations': 'Operations',

    'vmem.vmpage_action':   'Actions',
    'vmem.vmpage_faults':   'Faults/s',
    'vmem.vmpage_io':       'Pages/s',
    'vmem.vmpage_number':   'Pages',

    'wireless.signal_quality':  '',
    'wireless.signal_power':    'dBm',
    'wireless.signal_noise':    'dBm',
}
