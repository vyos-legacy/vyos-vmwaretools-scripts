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
import subprocess

from vyos.config import Config


def main():
    c = Config()

    for intf in c.list_effective_nodes('interfaces ethernet'):
        # skip interfaces that are disabled or is configured for dhcp
        check_disable = "interfaces ethernet {} disable".format(intf)
        check_dhcp = "interfaces ethernet {} address dhcp".format(intf)
        if c.exists_effective(check_disable) or c.exists_effective(check_dhcp):
            continue

        # bring the interface up
        cmd = ["ip", "link", "set", "dev", intf, "up"]
        subprocess.call(cmd)

        # add configured addresses to interface
        intf_addresses = c.return_effective_values(
            "interfaces ethernet {} address".format(intf)
        )
        for addr in intf_addresses.split():
            addr = addr.strip("'")
            cmd = ["ip", "address", "add", addr, "dev", intf]
            subprocess.call(cmd)
    return 0


if __name__ == '__main__':
    sys.exit(main())
