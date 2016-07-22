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

"""The purpose of this script is generating environment variables used to
configure /etc/profile inside of the virtual machine.

The main purpose of this script is allowing vagrant to configure properly
the no_proxy environment variable adding entries that could break openstack
components internal connectivity.
"""

import os
import subprocess
import sys


PROXY_ENV = '''
export HTTP_PROXY={http_proxy}
export http_proxy={http_proxy}
export HTTPS_PROXY={https_proxy}
export https_proxy={https_proxy}
export NO_PROXY={no_proxy}
export no_proxy={no_proxy}
'''


def get_proxy_env():
    """Get proxy profile file content to be sourced by Bash

    It produces the content of proxy profile file sourced by bash
    to have proxy env set up in the VM
    """

    return PROXY_ENV.format(
        http_proxy=os.environ.get('http_proxy', ''),
        https_proxy=os.environ.get('https_proxy', ''),
        no_proxy=','.join(get_no_proxy()))


def get_no_proxy_hosts():
    "Gets current host names contained inside the no_proxy variable"
    for e in os.environ.get('no_proxy', '').split(','):
        yield e.strip()


def get_host_ips():
    "Gets all known IPS addresses of the host."
    for line in subprocess.check_output(['ifconfig']).split('\n'):
        fields = line.strip().split(' ', 2)
        if fields[0] == 'inet':
            if fields[1].startswith('addr:'):
                yield fields[1].split(':', 1)[1].strip()


def get_known_hosts():
    "Gets all known host names and IPs find in /etc/hosts."
    with open('/etc/hosts', 'r') as hosts_file:
        for line in hosts_file.readlines():
            # strip out all comments
            stripped_line = line.split('#', 1)[0].strip()
            for e in stripped_line.split():
                yield e.strip()


def get_no_proxy():
    """Get content for no_proxy environment variable.

    Get a list of addresses and ips to connect wich the proxy shouldn't be used
    """

    # the resulted list is returned sorted to improve reapeatibily over
    # produced output over multiple executions. Sets are know being
    # not reliable acording the order items are iterated.
    return sorted(
        (set(get_no_proxy_hosts()) |  # take existing no_proxy entries
         set(get_host_ips()) |  # add ips assinged to all existing ifaces
         set(get_known_hosts()))  # add all hosts and ips taken from /etc/hosts
        - set(['']))  # remove empty string that could be here by mistake


if __name__ == '__main__':
    # stdout is used to produce the result of this script
    out = sys.stdout
    # redirect stdout to stderr to avoid to pollute the output
    sys.stdout = sys.stderr
    out.write(get_proxy_env())
