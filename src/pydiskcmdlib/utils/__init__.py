# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later

from .converter import *
from .enum import *
from pydiskcmdlib import os_type

def init_device(dev, 
                read_write=(False if os_type == "Linux" else True), 
                open_t=None):
    '''
    initialize a device object
        :param dev: the device path
        :param readwrite: access type
        :param open_t: the open type of device, valid values is None, 'scsi', 'ata', 'nvme', 'vroc'
        :param backends: backend io engine type, valid parameters: 
            * 'ioctl'                ioctl type, alias ioctl_fcntl
            * 'ioctl_fcntl'          ioctl type, Send sgio request with ioctl (python fcntl.ioctl)
            * 'ioctl_sgio'           ioctl type, alias ioctl_sgio_local
            * 'ioctl_sgio_pyscsi'    ioctl type, Send sgio request with cython-sgio (python cython-sgio)
            * 'ioctl_sgio_local'     ioctl type, Send sgio request with local code (pydiskcmdlib.sgio)
            * 'io_uring'             under development
    '''
    if open_t == 'scsi' or open_t == 'ata':
        from pydiskcmdlib.pyscsi.scsi_device import SCSIDevice
        if os_type == "Windows" and dev.upper().startswith("PHYSICALDRIVE"): 
            dev = "\\\\.\\" + dev.upper()
        device = SCSIDevice(dev, read_write)
    elif open_t == 'nvme':
        from pydiskcmdlib.pynvme.nvme_device import NVMeDevice
        if os_type == "Windows" and dev.upper().startswith("PHYSICALDRIVE"):
            dev = "\\\\.\\" + dev.upper()
        device = NVMeDevice(dev, read_write)
    elif open_t == 'vroc':
        if os_type == "Windows":
            from pydiskcmdlib.vroc.vroc_device import VROCDevice
            if dev.startswith("Scsi"):
                dev = "\\\\.\\" + dev
            device = VROCDevice(dev, read_write)
        else:
            raise NotImplementedError('No backend implemented for %s' % dev)
    elif open_t == None and os_type == "Linux":
        if dev[:5] == '/dev/' and "nvme" in dev[5:]:
            from pydiskcmdlib.pynvme.nvme_device import NVMeDevice
            device = NVMeDevice(dev, read_write)
        elif dev[:5] == '/dev/':
            from pydiskcmdlib.pyscsi.scsi_device import SCSIDevice
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
