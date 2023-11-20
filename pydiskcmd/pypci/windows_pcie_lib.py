# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
################
pci_ids_locations = []

CLASS_ALIASES = {  # noqa
    'nvme': 0x010802,
    'ethernet': 0x020000,
    'raid': 0x010400,
    'gpu': 0x030200,
}

CLASSCODE_NAME = {value: name for name,value in CLASS_ALIASES.items()}

EXPRESS_TYPES = {
    0x0: 'endpoint',
    0x1: 'legacy_endpoint',
    0x4: 'root_port',
    0x5: 'upstream_port',
    0x6: 'downstream_port',
    0x7: 'pci_bridge',
    0x8: 'pcie_bridge',
    0x9: 'root_complex_endpoint',
    0xa: 'root_complex_event_collector',
}

EXPRESS_SPEED = {
    1: "2.5GT/s",
    2: "5GT/s",
    3: "8GT/s",
    4: "16GT/s",
    5: "32GT/s",
    6: "64GT/s",
}

PCI_EXP_SLOT_CTL_ATTN_LED_VALUES = {
    0x00: 'reserved',
    0x00c0: 'off',
    0x0080: 'blink',
    0x0040: 'on',
}

################
def valid_pcie_bus_addr(bus_addr):
    temp = bus_addr.split(":")
    if len(temp) not in (2,3):
        return False
    for i in temp[:-1]:
        if not i.isdigit():
            return False
    temp = temp[-1].split(".")
    if len(temp) == 2 and temp[0].isdigit() and temp[1].isdigit():
        return True
    return False

class PCIeConfig(object):
    def __init__(self, config_path):
        raise NotImplementedError("Windows Not Support")


class NVMePCIe(PCIeConfig):
    def __init__(self, ctrl_name):
        raise NotImplementedError("Windows Not Support")


class PCIeBar(object):
    def __init__(self, bar_path):
        raise NotImplementedError("Windows Not Support")


class PCIeNVMeBar(PCIeBar):
    def __init__(self, ctrl_name):
        raise NotImplementedError("Windows Not Support")

