# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import os
import re
from typing import List
#####
PCIeMappingPath = "/sys/class/nvme/%s/address"
excluded_block_devices = ('sr', 'zram', 'dm-', 'md', 'loop')
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

def get_block_devs(print_detail=True) -> List[str]:
    """Determine the list of block devices by looking at /sys/block"""
    devs = [dev for dev in os.listdir('/sys/block')
            if not dev.startswith(excluded_block_devices)]
    if print_detail:
        print (f'{len(devs)} devices detected')
    return devs 

def get_nvme_dev_info():
    """
    Return: a list that contain ctrl_id, like ["nvme0", "nvme1"]
    """
    if os.path.exists('/sys/class/nvme'):
        return [dev for dev in os.listdir('/sys/class/nvme') if dev.startswith("nvme")]
    return []
