# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later

from pydiskcmd.system.os_tool import os_type
from .converter import *
from .enum import *


def init_device(dev, read_write=False, open_t=None):
    if open_t == 'scsi' or open_t == 'ata':
        from pydiskcmd.pyscsi.scsi_device import SCSIDevice
        if os_type == "Windows" and dev.upper().startswith("PHYSICALDRIVE"):
            dev = "\\\\.\\" + dev.upper()
        device = SCSIDevice(dev, read_write)
    elif open_t == 'nvme':
        from pydiskcmd.pynvme.nvme_device import NVMeDevice
        if os_type == "Windows" and dev.startswith("PHYSICALDRIVE"):
            dev = "\\\\.\\" + dev.upper()
        device = NVMeDevice(dev, read_write)
    elif open_t == None and os_type == "Linux":
        if dev[:5] == '/dev/' and "nvme" in dev[5:]:
            from pydiskcmd.pynvme.nvme_device import NVMeDevice
            device = NVMeDevice(dev, read_write)
        elif dev[:5] == '/dev/':
            from pydiskcmd.pyscsi.scsi_device import SCSIDevice
            device = SCSIDevice(dev, read_write)
        elif dev[:8] == 'iscsi://':
            from pyscsi.pyiscsi.iscsi_device import ISCSIDevice
            device = ISCSIDevice(dev)
        else:
            raise NotImplementedError('No backend implemented for %s' % dev)
    elif open_t == None and os_type == "Windows":
        raise NotImplementedError("Windows cannot used open_t=None, not support auto detect")
    else:
        raise NotImplementedError("open type should be None|scsi|ata|nvme")
    return device
