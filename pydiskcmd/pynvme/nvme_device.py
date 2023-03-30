# coding: utf-8
# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later

import os
import traceback
from pydiskcmd.system.os_tool import os_type
from pydiskcmd.exceptions import *


if os_type == "Linux":
    from pydiskcmd.common.Lin_device import LinDevice
    ## Linux device
    class NVMeDevice(LinDevice):
        def __init__(self, 
                     device,
                     readwrite=False,
                     detect_replugged=True):
            super(NVMeDevice, self).__init__(device, readwrite, detect_replugged)

        def execute(self, cmd):
            """
            execute a nvme command (admin, IO)

            :param cmd: a NVMe Command Object
            :return: a NVMe Command Object
            """
            try:
                cmd.cq_status = LinDevice.execute(self, cmd.req_id, cmd.cdb)
            except:
                traceback.print_exc()
            return cmd

elif os_type == "Windows":
    from pydiskcmd.common.win_device import WinDevice
    class NVMeDevice(WinDevice):
        def __init__(self, 
                     device,
                     readwrite=True,
                     detect_replugged=True):
            super(NVMeDevice, self).__init__(device, readwrite, detect_replugged)

        def execute(self, cmd):
            """
            execute a IOCTL command

            :param cmd: a Command Structure
            """
            ## 
            if not cmd.cdb:
                raise CommandDataStrucError("Invalid Command Data Structure %s" % cmd.cdb)
            WinDevice.execute(self, 
                              cmd.req_id,  # IOControl Code to use, from winioctlcon
                              cmd.cdb,      # datain
                              cmd.cdb)
            # Usually 0 if it goes into here.
            # 
            cmd.cq_status = 0
            return cmd
else:
    raise NotImplementedError("%s not support" % os_type)
