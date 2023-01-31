# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import os
import re

#####
PCIeMappingPath = "/sys/class/nvme/%s/address"
#####

def map_pcie_addr_by_nvme_ctrl_path(dev_path):
    addr = None
    if check_nvme_if_ctrl_path(dev_path):
        path = PCIeMappingPath % dev_path.replace("/dev/", "")
        if os.path.exists(path):
            with open(path, 'r') as f:
                addr = f.read()
            addr = addr.strip()
    return addr

def check_nvme_if_ns_path(dev_path):
    g = re.match(r'/dev/nvme[0-9]+n[0-9]+', dev_path)
    return (g is not None)

def check_nvme_if_ctrl_path(dev_path):
    g = re.match(r'/dev/nvme[0-9]+', dev_path)
    return ((g is not None) and not check_nvme_if_ns_path(dev_path))
