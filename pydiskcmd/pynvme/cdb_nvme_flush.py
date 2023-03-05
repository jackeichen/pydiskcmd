# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmd.system.os_tool import os_type

#####
CmdOPCode = 0x00
#####

if os_type == "Linux":
    from pydiskcmd.pynvme.nvme_command import Command
    ## linux command
    IOCTL_REQ = Command.linux_req.get("NVME_IOCTL_IO_CMD")
    class Flush(Command):
        def __init__(self, ns_id):
            ##   
            super(Flush, self).__init__(IOCTL_REQ,
                                       opcode=CmdOPCode,
                                       nsid=ns_id
                                       )

elif os_type == "Windows":
    class Flush(object):
        ## TODO.
        pass

else:
    raise NotImplementedError("%s not support" % os_type)
