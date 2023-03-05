# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmd.system.os_tool import os_type
from pydiskcmd.pynvme.nvme_command import Command,build_command

#####
CmdOPCode = 0x80
#####

if os_type == "Linux":
    ## linux command
    IOCTL_REQ = Command.linux_req.get("NVME_IOCTL_ADMIN_CMD")
    class Format(Command):
        def __init__(self, 
                     lbaf, 
                     mset=0, 
                     pi=0, 
                     pil=1, 
                     ses=0, 
                     nsid=0xFFFFFFFF,
                     timeout=600000):
            ### build command
            cdw10 = build_command({"lbaf": (0x0F, 0, lbaf),
                                   "mset": (0x10, 0 ,mset),
                                   "pi": (0xE0, 0, pi),
                                   "pil": (0x01, 1, pil),
                                   "ses": (0x0E, 1, ses)})
            ##   
            super(Format, self).__init__(IOCTL_REQ,
                                         opcode=CmdOPCode,
                                         nsid=nsid,
                                         cdw10=cdw10,
                                         timeout_ms=timeout)

elif os_type == "Windows":
    class Format(object):
        pass
else:
    raise NotImplementedError("%s not support" % os_type)
