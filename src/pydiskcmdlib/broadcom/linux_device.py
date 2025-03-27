# coding: utf-8
# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later

import traceback
from pydiskcmdlib.exceptions import *
from pydiskcmdlib import log
from .megaraid_ioctl_structures import MEGASAS_IOC_FIRMWARE,MFI_STAT_OK,MEGAIOCCMD
from .linux_command import megasas_dcmd_cmd,MegasasCmd,megadev_cmd


## This is cmd type
from pydiskcmdlib.device.Lin_device import LinIOCTLDevice
# Linux device
class DcmdDevice(LinIOCTLDevice):
    def __init__(self, 
                 device,
                 readwrite=False,
                 detect_replugged=True):
        log.debug("Opening Broadcom:DCMD device %s, read write flag %s, detect replugged %s" % (device, readwrite, detect_replugged))
        super(DcmdDevice, self).__init__(device, readwrite, detect_replugged)

    def execute(self, cmd: megasas_dcmd_cmd) -> megasas_dcmd_cmd:
        """
        """
        result = LinIOCTLDevice.execute(self, MEGASAS_IOC_FIRMWARE, cmd.cdb)
        if result < 0:
            raise IOError("IOCTL execute failed, result %s" % result)
        if cmd.statusp is not None:
            cmd.statusp = cmd.cdb.frame.megasas_dcmd_frame.cmd_status
        elif cmd.cdb.frame.dcmd.cmd_status != MFI_STAT_OK:
            raise IOError("command %x returned error status %x" % (cmd.cdb.frame.megasas_dcmd_frame.opcode, 
                                                                   cmd.cdb.frame.megasas_dcmd_frame.cmd_status))
        return cmd

    def execute_megasas(self, cmd: MegasasCmd) -> MegasasCmd:
        """
        """
        result = LinIOCTLDevice.execute(self, MEGASAS_IOC_FIRMWARE, cmd.cdb)
        if result < 0:
            raise IOError("IOCTL execute failed, result %s" % result)
        if cmd.pthru.cmd_status == 12:
            raise DeviceNotFound("megasas_cmd: Device %d does not exist" % cmd.cdb.pathru.target_id)
        elif cmd.pthru.cmd_status:
            raise IOError("megasas_cmd result: %d.%d = %d/%d" % (cmd.uio.host_no,
                                                                 cmd.pthru.target_id,
                                                                 result,
                                                                 cmd.pthru.cmd_status,))
        return cmd

    def execute_megadev(self, cmd: megadev_cmd) -> megadev_cmd:
        """
        """
        result = LinIOCTLDevice.execute(self, MEGAIOCCMD, cmd.cdb)
        if result < 0:
            raise IOError("IOCTL execute failed, result %s" % result)
        if cmd.cdb.pthru.scsistatus:
            raise IOError("megadev_cmd result: %d" % cmd.cdb.pthru.scsistatus)
        return cmd

