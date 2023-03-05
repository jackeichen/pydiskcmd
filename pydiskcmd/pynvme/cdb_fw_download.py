# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmd.system.os_tool import os_type
from pydiskcmd.pynvme.nvme_command import Command,build_command

#####
CmdOPCode = 0x11
#####

if os_type == "Linux":
    ## linux command
    IOCTL_REQ = Command.linux_req.get("NVME_IOCTL_ADMIN_CMD")
    class FWImageDownload(Command):
        def __init__(self, 
                     data, 
                     offset):
            ### build command
            data_len = len(data)
            cdw10 = build_command({"NUMD": (0xFFFFFFFF, 0, int(((data_len / 4) - 1)))})
            cdw11 = build_command({"OFST": (0xFFFFFFFF, 0, offset)})   
            ##   
            super(FWImageDownload, self).__init__(IOCTL_REQ,
                                                  opcode=CmdOPCode,
                                                  data_len=data_len,
                                                  data_in=data,
                                                  cdw10=cdw10,
                                                  cdw11=cdw11)

elif os_type == "Windows":
    class FWImageDownload(object):
        ## TODO.
        pass
else:
    raise NotImplementedError("%s not support" % os_type)
