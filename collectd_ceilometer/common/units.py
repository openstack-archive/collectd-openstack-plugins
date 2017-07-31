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

    'chrony.clock_last_meas':    's',
    'chrony.clock_last_update':  's',
    'chrony.clock_mode':         '',
    'chrony.clock_reachability': '',
    'chrony.clock_skew_ppm':     'ppm',
    'chrony.clock_state':        '',
    'chrony.clock_stratum':      '',
    'chrony.frequency_error':    'ppm',
    'chrony.root_delay':         's',
    'chrony.root_dispersion':    '',
    'chrony.time_offset':        's',
    'chrony.time_offset_ntp':    's',
    'chrony.time_offset_rms':    's',
    'chrony.time_ref':           's',

    'conntrack': 'Entries',
    'contextswitch': 'Sw./s',
    'cpu': 'jiffies',
    'cpufreq': 'MHz',
    'cpusleep.total_time_in_ms': 'ms',

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

    'dpdkstat.derive':        'Errors',
    'dpdkstat.errors':        'Errors',
    'dpdkstat.if_rx_dropped': 'Dropped',
    'dpdkstat.if_rx_errors':  'Errors',
    'dpdkstat.if_rx_octets':  'Bytes',
    'dpdkstat.if_rx_packets': 'Packets',
    'dpdkstat.if_tx_errors':  'Errors',
    'dpdkstat.if_tx_octets':  'Bytes',
    'dpdkstat.if_tx_packets': 'Packets',
    'dpdkstat.operations':    '',

    'entropy': 'b',

    'filecount.files': 'Files',
    'filecount.bytes': 'B',

    'gps.dilution_of_precision': 'm',
    'gps.satellites':            'Satellites',

    'hddtemp': '°C',

    'hugepages.bytes':           'Bytes',
    'hugepages.vmpage_number':   'Pages',
    'hugepages.percent':         '%',

    'intel_rdt.ipc':               'instructions/s',
    'intel_rdt.memory_bandwidth':  '%',
    'intel_rdt.bytes':             'Bytes',

    'interface.if_dropped': 'Packets/s',
    'interface.if_errors':  'Errors/s',
    'interface.if_packets': 'Packets/s',
    'interface.if_octets':  'B/s',

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

    'mysql.cache_result':            'Queries/s',
    'mysql.cache_size':              'Queries',
    'mysql.mysql_bpool_bytes':       'Bytes',
    'mysql.mysql_bpool_counters':    'Counters',
    'mysql.mysql_bpool_pages':       'Pages',
    'mysql.mysql_commands':          'Commands/s',
    'mysql.mysql_handler':           'Invocations',
    'mysql.mysql_innodb_data':       '',
    'mysql.mysql_innodb_dblwr':      '',
    'mysql.mysql_innodb_log':        '',
    'mysql.mysql_innodb_pages':      'Pages',
    'mysql.mysql_innodb_row_lock':   '',
    'mysql.mysql_innodb_rows':       'Rows',
    'mysql.mysql_locks':             'locks',
    'mysql.mysql_log_position':      'Position',
    'mysql.mysql_octets':            'B/s',
    'mysql.mysql_qcache':            'Queries',
    'mysql.mysql_select':            '',
    'mysql.mysql_slow_queries':      'Queries',
    'mysql.mysql_sort':              '',
    'mysql.mysql_sort_merge_passes': 'Passes',
    'mysql.mysql_sort_rows':         'Rows',
    'mysql.mysql_threads':           'Threads',
    'mysql.threads':                 'Threads',
    'mysql.time_offset':             's',
    'mysql.total_threads':           'Threads',

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

    'ntpd':                  'ns',
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

    'powerdns.cache_result': '',
    'powerdns.cache_size':   'Bytes',
    'powerdns.counter':      '',
    'powerdns.dns_answer':   'Queries/s',
    'powerdns.dns_qtype':    '',
    'powerdns.dns_question': 'Queries',
    'powerdns.dns_rcode':    '',
    'powerdns.ipt_packets':  'Packets',
    'powerdns.latency':      's',
    'powerdns.total_bytes':  'Bytes',
    'powerdns.uptime':       's',

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

    'protocols.protocol_counter': 'Protocols',

    'redis.blocked_clients':       'Clients',
    'redis.cache_result':          '',
    'redis.current_connections':   'Connections',
    'redis.evicted_keys':          'Keys',
    'redis.expired_keys':          'Keys',
    'redis.memory':                'Bytes',
    'redis.memory_lua':            'Bytes',
    'redis.operations_per_second': 'Operations/s',
    'redis.pubsub':                'Channels',
    'redis.total_bytes':           'Bytes',
    'redis.total_connections':     'Connections',
    'redis.total_operations':      'Operations',
    'redis.uptime':                's',
    'redis.volatile_changes':      'Changes',

    'swap':         'B',
    'swap.swap_io': 'Pages',

    'table.gauge': '',
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

    'xencpu.percent': '%',

    'zfs_arc.cache_eviction':        'Bytes',
    'zfs_arc.cache_operation':       '',
    'zfs_arc.cache_ratio':           '',
    'zfs_arc.cache_result':          '',
    'zfs_arc.cache_size':            '',
    'zfs_arc.hash_collisions':       'Collisions',
    'zfs_arc.io_octets':             'B/s',
    'zfs_arc.memory_throttle_count': 'Bytes',
    'zfs_arc.mutex_operations':      'Operations',
}
