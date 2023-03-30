# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmd.system.os_tool import os_type

#####
CmdOPCode = 0x02
#####

if os_type == "Linux":
    from pydiskcmd.pynvme.nvme_command import LinCommand,build_int_by_bitmap
    ## linux command
    IOCTL_REQ = LinCommand.linux_req.get("NVME_IOCTL_IO_CMD")
    class Read(LinCommand):
        def __init__(self, 
                     ns_id,
                     slba, 
                     nlba,
                     addr=None,      ## Data Pointer
                     data_len=0,     ## used to create data buffer
                     metadata=None,  ## Metadata Pointer
                     metadata_len=0, ## Metadata length
                     prinfo=0,
                     fua=0,
                     lr=0,
                     dsm=0,
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
            cdw13 = build_int_by_bitmap({"DSM": (0xFF, 0, dsm)})   
            cdw14 = eilbrt
            cdw15 = build_int_by_bitmap({"ELBAT": (0xFFFF, 0, elbat),
                                         "ELBATM": (0xFFFF, 2, elbatm),
                                        }) 
            ##   
            super(Read, self).__init__(IOCTL_REQ)
            self.build_command(opcode=CmdOPCode,
                               nsid=ns_id,
                               metadata=metadata,  ## Metadata Pointer
                               addr=addr,      ## Data Pointer
                               metadata_len=metadata_len, ## Metadata length
                               data_len=data_len,     ## used to create data buffer
                               cdw10=cdw10,
                               cdw11=cdw11,
                               cdw12=cdw12,
                               cdw13=cdw13,
                               cdw14=cdw14,
                               cdw15=cdw15,
                               )

elif os_type == "Windows":
    from pydiskcmd.pynvme.nvme_command import WinCommand
    class Read(WinCommand):
        ## TODO.
        pass

else:
    raise NotImplementedError("%s not support" % os_type)
