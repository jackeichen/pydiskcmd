# coding: utf-8
# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later

import traceback
from pydiskcmdlib import os_type
from pydiskcmdlib.exceptions import *
from pydiskcmdlib import log

## This is cmd type

if os_type == "Linux":
    from pydiskcmdlib.device.Lin_device import LinIOCTLDevice
    ## Linux device
    class NVMeDevice(LinIOCTLDevice):
        def __init__(self, 
                     device,
                     readwrite=False,
                     detect_replugged=True):
            log.debug("Opening NVMe device %s, read write flag %s, detect replugged %s" % (device, readwrite, detect_replugged))
            super(NVMeDevice, self).__init__(device, readwrite, detect_replugged)

        def execute(self, cmd):
            """
            execute a nvme command (admin, IO)

            :param cmd: a NVMe LinCommand Object
            :return: a NVMe LinCommand Object
            """
            cmd.cq_status = LinIOCTLDevice.execute(self, cmd.req_id, cmd.cdb)
            cmd.result = cmd.cq_status
            return cmd

elif os_type == "Windows":
    from pydiskcmdlib.device.win_device import WinIOCTLDevice,BytesReturnedStruc
    class NVMeDevice(WinIOCTLDevice):
        def __init__(self, 
                     device,
                     readwrite=True,
                     detect_replugged=True):
            log.debug("Opening NVMe device %s, read write flag is %s, detect replugged is %s" % (device, readwrite, detect_replugged))
            super(NVMeDevice, self).__init__(device, readwrite, detect_replugged)

        def execute(self, cmd):
            """
            execute a IOCTL command

            :param cmd: a NVMe WinCommand Object
            :param raise_if_fail: True to raise an exception if the command fails, False to return the result
            :return: a NVMe WinCommand Object
            """
            ## 
            if not cmd.cdb:
                raise CommandDataStrucError("Invalid Command Data Structure %s" % cmd.cdb)
            cmd.result = WinIOCTLDevice.execute(self, 
                                                cmd.req_id,  # IOControl Code to use, from winioctlcon
                                                cmd.cdb,      # datain
                                                cmd.cdb,
                                                BytesReturned=BytesReturnedStruc(0),
                                                raise_if_fail=False)
            # Usually 0 if it goes into here.
            cmd.cq_status = 0
            return cmd
else:
    raise NotImplementedError("%s not support" % os_type)
