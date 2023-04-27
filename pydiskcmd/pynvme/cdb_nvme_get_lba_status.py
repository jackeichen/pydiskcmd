# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmd.system.os_tool import os_type
from pydiskcmd.exceptions import CommandNotSupport

#####
CmdOPCode = 0x86
#####

if os_type == "Linux":
    from pydiskcmd.pynvme.nvme_command import LinCommand,build_int_by_bitmap
    ## linux command
    IOCTL_REQ = LinCommand.linux_req.get("NVME_IOCTL_ADMIN_CMD")
    class GetLBAStatus(LinCommand):
        def __init__(self, 
                     nsid,
                     slba,
                     mndw,
                     atype,
                     rl,
                     timeout=600000):
            ### build command
            cdw10 = slba & 0xFFFFFFFF
            cdw11 = (slba >> 32) & 0xFFFFFFFF
            cdw12 = mndw
            cdw13 = build_int_by_bitmap({"RL": (0xFFFF, 0, rl),
                                         "ATYPE": (0xFF, 3, atype),
                                        })
            ##   
            super(GetLBAStatus, self).__init__(IOCTL_REQ)
            self.build_command(opcode=CmdOPCode,
                               nsid=nsid,
                               data_len=(mndw+1)*4,
                               cdw10=cdw10,
                               cdw11=cdw11,
                               cdw12=cdw12,
                               cdw13=cdw13,
                               timeout_ms=timeout)

elif os_type == "Windows":
    from pydiskcmd.pynvme.nvme_command import WinCommand
    class GetLBAStatus(WinCommand):
        def __init__(self, *args, **kwargs):
            raise CommandNotSupport("Format Not Support")
else:
    raise NotImplementedError("%s not support" % os_type)
