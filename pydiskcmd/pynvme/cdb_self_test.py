# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmd.system.os_tool import os_type

#####
CmdOPCode = 0x14
#####

if os_type == "Linux":
    from pydiskcmd.pynvme.nvme_command import LinCommand,build_int_by_bitmap
    ## linux command
    IOCTL_REQ = LinCommand.linux_req.get("NVME_IOCTL_ADMIN_CMD")
    class SelfTest(LinCommand):
        def __init__(self, 
                     stc,
                     ns_id=0xFFFFFFFF):
            ### build command
            cdw10 = build_int_by_bitmap({"stc": (0x0F, 0, stc),})
            ##   
            super(SelfTest, self).__init__(IOCTL_REQ)
            self.build_command(opcode=CmdOPCode,
                               nsid=ns_id,
                               cdw10=cdw10,)

elif os_type == "Windows":
    from pydiskcmd.pynvme.nvme_command import WinCommand
    class SelfTest(WinCommand):
        ## TODO.
        pass

else:
    raise NotImplementedError("%s not support" % os_type)
