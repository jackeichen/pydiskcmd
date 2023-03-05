# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmd.system.os_tool import os_type
from pydiskcmd.pynvme.nvme_command import Command,build_command

#####
CmdOPCode = 0x10
#####

if os_type == "Linux":
    ## linux command
    IOCTL_REQ = Command.linux_req.get("NVME_IOCTL_ADMIN_CMD")
    class FWCommit(Command):
        def __init__(self, 
                     fw_slot, 
                     action,
                     bpid=0):
            ### build command
            cdw10 = build_command({"FS": (0x07, 0, fw_slot),
                                   "CA": (0x38, 0, action),
                                   "BPID": (0x80, 3, bpid)})
            ##   
            super(FWCommit, self).__init__(IOCTL_REQ,
                                           opcode=CmdOPCode,
                                           cdw10=cdw10)

elif os_type == "Windows":
    class FWCommit(object):
        pass
else:
    raise NotImplementedError("%s not support" % os_type)
