#!/usr/bin/env python3
#
# Copyright (C) 2018 VyOS maintainers and contributors
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 or later as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

import sys
import re
import syslog as sl
import subprocess

from vyos.config import Config
from vyos import ConfigError

def get_config():
  c = Config()
  if not c.exists_effective('interfaces ethernet'):
    return None		

  interfaces = {}
  for intf in c.list_effective_nodes('interfaces ethernet'):
    if not c.exists_effective('interfaces ethernet ' + intf + ' disable') and c.exists_effective('interfaces ethernet ' + intf + ' address'):
      interfaces[intf] = re.sub("\'", "", c.return_effective_values('interfaces ethernet ' + intf + ' address')).split()

  return interfaces 

def apply(c):
  if not c:
    return None

  for intf, addr in c.items(): 
    if not 'dhcp' in addr:
      sl.syslog(sl.LOG_NOTICE, "ip l s dev " + intf + " up")
      subprocess.call(['ip l s dev ' + intf + ' up ' + ' &>/dev/null'], shell=True)
      for a in addr:
        sl.syslog(sl.LOG_NOTICE, "ip a a " + a + " dev " + intf)
        subprocess.call(['ip a a dev ' + intf + ' ' + a + ' &>/dev/null'], shell=True)
    else:
      sl.syslog(sl.LOG_NOTICE, "calling /sbin/dhclient -q " + intf)
      subprocess.call(['/sbin/dhclient -q ' + intf + ' &>/dev/null'], shell=True) 

if __name__ == '__main__':
  try:
    c = get_config()
    apply(c)
  except ConfigError as e:
    print(e)
    sys.exit(1)

