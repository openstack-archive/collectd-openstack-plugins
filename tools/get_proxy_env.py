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
    return PROXY_ENV.format(
        http_proxy=os.environ.get('http_proxy', ''),
        https_proxy=os.environ.get('https_proxy', ''),
        no_proxy=','.join(get_no_proxy()))


def get_host_ips():
    for line in subprocess.check_output(['ifconfig']).split('\n'):
        fields = line.strip().split(' ', 2)
        if fields[0] == 'inet':
            if fields[1].startswith('addr:'):
                yield fields[1].split(':', 1)[1].strip()


def get_no_proxy():
    # get current no proxy entries
    no_proxy = set(
        e.strip() for e in os.environ.get('no_proxy', '').split(','))

    # add this host IPs
    no_proxy.update(get_host_ips())

    # add all those hosts and ips named in /etc/hosts
    with open('/etc/hosts', 'r') as hosts_file:
        for line in hosts_file.readlines():
            # strip out all comments
            stripped_line = line.split('#', 1)[0].strip()
            no_proxy.update(e.strip() for e in stripped_line.split())

    try:
        # Remove empty entries
        no_proxy.remove('')
    except KeyError:
        pass

    return sorted(no_proxy)


if __name__ == '__main__':
    out = sys.stdout
    sys.stdout = sys.stderr  # redirect stdout to stderr to avoid pollution
    out.write(get_proxy_env())
