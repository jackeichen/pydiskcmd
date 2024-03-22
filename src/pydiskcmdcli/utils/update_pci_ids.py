# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import os
from pydiskcmdcli import os_type

def update_pci_ids_online(timeout: int = 5,
                          print_detail: bool = False):
    if os_type == 'Linux':
        from pydiskcmdlib.pypci.linux_pcie_lib import pci_ids_locations
    elif os_type == 'Windows':
        from pydiskcmdlib.pypci.windows_pcie_lib import pci_ids_locations
    else:
        pci_ids_locations = []
    for location in pci_ids_locations:
        if os.path.isfile(location):
            break
    else:
        if print_detail:
            print ("Cannot find pci.ids location in this OS.")
        return 1
    ret = os.system("wget -O %s -T %d -q https://pci-ids.ucw.cz/v2.2/pci.ids" % (location, timeout))
    if print_detail:
        if ret == 0:
            print ("Success to update pci.ids")
        elif (ret >> 8) == 4:  # check in unix system
            print ("Cannot connect to internet, check your network")
        else:
            print ("return code is %d" % ret)
    return ret
