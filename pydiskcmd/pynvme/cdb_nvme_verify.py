# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmd.system.os_tool import os_type
from pydiskcmd.exceptions import CommandNotSupport

#####
CmdOPCode = 0x0C
#####

if os_type == "Linux":
    from pydiskcmd.pynvme.nvme_command import LinCommand,build_int_by_bitmap
    ## linux command
    IOCTL_REQ = LinCommand.linux_req.get("NVME_IOCTL_IO_CMD")
    class Verify(LinCommand):
        def __init__(self, 
                     ns_id,
                     slba, 
                     nlba,
                     prinfo=0,
                     fua=0,
                     lr=0,
                     eilbrt=0,
                     elbat=0,
                     elbatm=0):
            ### build command
            cdw10 = slba & 0xFFFFFFFF
            cdw11 = (slba >> 32) & 0xFFFFFFFF
            cdw12 = build_int_by_bitmap({"NLB": (0xFFFF, 0, nlba),
                                         "PRINFO": (0x3C, 3, prinfo),
                                         "FUA": (0x40, 3, fua),
                                         "LR": (0x80, 3, lr),
                                        })
            cdw14 = eilbrt
            cdw15 = build_int_by_bitmap({"ELBAT": (0xFFFF, 0, elbat),
                                         "ELBATM": (0xFFFF, 2, elbatm),
                                        }) 
            ##   
            super(Verify, self).__init__(IOCTL_REQ)
            self.build_command(opcode=CmdOPCode,
                               nsid=ns_id,
                               metadata=None,  ## Metadata Pointer
                               addr=None,      ## Data Pointer
                               metadata_len=0, ## Metadata length
                               data_len=0,     ## used to create data buffer
                               cdw10=cdw10,
                               cdw11=cdw11,
                               cdw12=cdw12,
                               cdw14=cdw14,
                               cdw15=cdw15,
                               )

elif os_type == "Windows":
    from pydiskcmd.pynvme.nvme_command import WinCommand
    class Verify(WinCommand):
        def __init__(self, *args, **kwargs):
            raise CommandNotSupport("Read Not Support")

else:
    raise NotImplementedError("%s not support" % os_type)
