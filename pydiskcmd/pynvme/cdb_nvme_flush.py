# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmd.system.os_tool import os_type
from pydiskcmd.exceptions import CommandNotSupport

#####
CmdOPCode = 0x00
#####

if os_type == "Linux":
    from pydiskcmd.pynvme.nvme_command import LinCommand
    ## linux command
    IOCTL_REQ = LinCommand.linux_req.get("NVME_IOCTL_IO_CMD")
    class Flush(LinCommand):
        def __init__(self, ns_id):
            ##   
            super(Flush, self).__init__(IOCTL_REQ)
            self.build_command(opcode=CmdOPCode,
                               nsid=ns_id
                               )

elif os_type == "Windows":
    from pydiskcmd.pynvme.nvme_command import WinCommand
    class Flush(WinCommand):
        def __init__(self, *args, **kwargs):
            raise CommandNotSupport("Flush Not Support")

else:
    raise NotImplementedError("%s not support" % os_type)
