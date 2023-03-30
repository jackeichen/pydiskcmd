# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmd.system.os_tool import os_type

#####
CmdOPCode = 0x11
#####

if os_type == "Linux":
    from pydiskcmd.pynvme.nvme_command import LinCommand,build_int_by_bitmap
    ## linux command
    IOCTL_REQ = LinCommand.linux_req.get("NVME_IOCTL_ADMIN_CMD")
    class FWImageDownload(LinCommand):
        def __init__(self, 
                     data, 
                     offset):
            ### build command
            data_len = len(data)
            cdw10 = build_int_by_bitmap({"NUMD": (0xFFFFFFFF, 0, int(((data_len / 4) - 1)))})
            cdw11 = build_int_by_bitmap({"OFST": (0xFFFFFFFF, 0, offset)})   
            ##   
            super(FWImageDownload, self).__init__(IOCTL_REQ)
            self.build_command(opcode=CmdOPCode,
                               data_len=data_len,
                               data_in=data,
                               cdw10=cdw10,
                               cdw11=cdw11)

elif os_type == "Windows":
    from pydiskcmd.pynvme.nvme_command import WinCommand
    class FWImageDownload(WinCommand):
        ## TODO.
        pass
else:
    raise NotImplementedError("%s not support" % os_type)
