# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmd.system.os_tool import os_type
from pydiskcmd.exceptions import CommandNotSupport

#####
CmdOPCode = 0x10
#####

if os_type == "Linux":
    from pydiskcmd.pynvme.nvme_command import LinCommand,build_int_by_bitmap
    ## linux command
    IOCTL_REQ = LinCommand.linux_req.get("NVME_IOCTL_ADMIN_CMD")
    class FWCommit(LinCommand):
        def __init__(self, 
                     fw_slot, 
                     action,
                     bpid=0):
            ### build command
            cdw10 = build_int_by_bitmap({"FS": (0x07, 0, fw_slot),
                                         "CA": (0x38, 0, action),
                                         "BPID": (0x80, 3, bpid)})
            ##   
            super(FWCommit, self).__init__(IOCTL_REQ)
            self.build_command(opcode=CmdOPCode,
                               cdw10=cdw10)

elif os_type == "Windows":
    from pydiskcmd.pynvme.nvme_command import WinCommand
    from pydiskcmd.pynvme.win_nvme_command import (
        STORAGE_HW_FIRMWARE_ACTIVATE,
        STORAGE_HW_FIRMWARE_REQUEST_FLAG_CONTROLLER,
        STORAGE_HW_FIRMWARE_REQUEST_FLAG_SWITCH_TO_EXISTING_FIRMWARE,
    )
    IOCTL_REQ = WinCommand.win_req.get("IOCTL_STORAGE_FIRMWARE_ACTIVATE")
    class FWCommit(WinCommand):
        def __init__(self, 
                     fw_slot, 
                     action,
                     bpid=0):
            super(FWCommit, self).__init__(IOCTL_REQ)
            flags = STORAGE_HW_FIRMWARE_REQUEST_FLAG_CONTROLLER | STORAGE_HW_FIRMWARE_REQUEST_FLAG_SWITCH_TO_EXISTING_FIRMWARE
            self.build_command(flags, fw_slot)
            raise CommandNotSupport("FWCommit Not Support")

        def build_command(self, Flags, Slot):
            self.cdb = STORAGE_HW_FIRMWARE_ACTIVATE(Flags, Slot)
            return self.cdb
else:
    raise NotImplementedError("%s not support" % os_type)
