# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmd.system.os_tool import os_type
from pydiskcmd.exceptions import CommandNotSupport

#####
CmdOPCode = 0x84
#####

if os_type == "Linux":
    from pydiskcmd.pynvme.nvme_command import LinCommand,build_int_by_bitmap
    ## linux command
    IOCTL_REQ = LinCommand.linux_req.get("NVME_IOCTL_ADMIN_CMD")
    class Sanitize(LinCommand):
        def __init__(self,
                     action,
                     ause,
                     owpass,
                     oipbp,
                     no_deallocate,
                     ovrpat=0,
                     ):
            ##
            cdw10 = build_int_by_bitmap({"SANACT": (0x07, 0, action),
                                         "AUSE": (0x08, 0, ause),
                                         "OWPASS": (0xF0, 0, owpass),
                                         "LR": (0x01, 1, oipbp),
                                         "No-Deallocate": (0x02, 1, no_deallocate),
                                        })
            if action == 3:
                cdw11 = ovrpat
            else:
                cdw11 = 0
            ##
            super(Sanitize, self).__init__(IOCTL_REQ)
            self.build_command(opcode=CmdOPCode,
                               cdw10=cdw10,
                               cdw11=cdw11,
                               )

elif os_type == "Windows":
    from pydiskcmd.pynvme.nvme_command import WinCommand
    class Sanitize(WinCommand):
        def __init__(self, *args, **kwargs):
            raise CommandNotSupport("Sanitize Not Support")

else:
    raise NotImplementedError("%s not support" % os_type)
