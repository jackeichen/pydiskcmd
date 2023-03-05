# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmd.system.os_tool import os_type
from pydiskcmd.pynvme.nvme_command import Command,build_command

#####
CmdOPCode = 0x14
#####

if os_type == "Linux":
    ## linux command
    IOCTL_REQ = Command.linux_req.get("NVME_IOCTL_ADMIN_CMD")
    class SelfTest(Command):
        def __init__(self, 
                     stc,
                     ns_id=0xFFFFFFFF):
            ### build command
            cdw10 = build_command({"stc": (0x0F, 0, stc),})
            ##   
            super(SelfTest, self).__init__(IOCTL_REQ,
                                           opcode=CmdOPCode,
                                           nsid=ns_id,
                                           cdw10=cdw10,)

elif os_type == "Windows":
    class SelfTest(object):
        ## TODO.
        pass

else:
    raise NotImplementedError("%s not support" % os_type)
