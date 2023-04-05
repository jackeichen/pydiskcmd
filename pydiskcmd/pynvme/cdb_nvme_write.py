# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmd.system.os_tool import os_type
from pydiskcmd.exceptions import CommandNotSupport

#####
CmdOPCode = 0x01
#####

if os_type == "Linux":
    from pydiskcmd.pynvme.nvme_command import LinCommand,build_int_by_bitmap
    ## linux command
    IOCTL_REQ = LinCommand.linux_req.get("NVME_IOCTL_IO_CMD")
    class Write(LinCommand):
        def __init__(self, 
                     ns_id,
                     slba, 
                     nlba,
                     data_buffer,      ## Data buffer
                     metadata_buffer=None,  ## Metadata buffer
                     dtype=0,
                     prinfo=0,
                     fua=0,
                     lr=0,
                     dsm=0,
                     dspec=0,
                     ilbrt=0,
                     lbat=0,
                     lbatm=0):
            ### build command
            cdw10 = slba & 0xFFFFFFFF
            cdw11 = (slba >> 32) & 0xFFFFFFFF
            cdw12 = build_int_by_bitmap({"NLB": (0xFFFF, 0, nlba),
                                         "DTYPE": (0xF0, 2, dtype),
                                         "PRINFO": (0x3C, 3, prinfo),
                                         "FUA": (0x40, 3, fua),
                                         "LR": (0x80, 3, lr),
                                        })
            cdw13 = build_int_by_bitmap({"DSM": (0xFF, 0, dsm),
                                         "DSPEC": (0xFFFF, 2, dspec),
                                        })   
            cdw14 = ilbrt
            cdw15 = build_int_by_bitmap({"LBAT": (0xFFFF, 0, lbat),
                                         "LBATM": (0xFFFF, 2, lbatm),
                                        }) 
            ##   
            super(Write, self).__init__(IOCTL_REQ)
            self.build_command(opcode=CmdOPCode,
                               nsid=ns_id,
                               metadata=metadata_buffer.addr if metadata_buffer else None,  ## Metadata Pointer
                               metadata_len=metadata_buffer.data_length if metadata_buffer else 0,
                               addr=data_buffer.addr,      ## Data Pointer
                               data_len=data_buffer.data_length,
                               cdw10=cdw10,
                               cdw11=cdw11,
                               cdw12=cdw12,
                               cdw13=cdw13,
                               cdw14=cdw14,
                               cdw15=cdw15,
                               )

elif os_type == "Windows":
    from pydiskcmd.pynvme.nvme_command import WinCommand
    class Write(WinCommand):
        def __init__(self, *args, **kwargs):
            raise CommandNotSupport("Write Not Support")

else:
    raise NotImplementedError("%s not support" % os_type)
