# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmd.system.os_tool import os_type

#####
CmdOPCode = 0x09
#####

if os_type == "Linux":
    from pydiskcmd.pynvme.nvme_command import LinCommand,build_int_by_bitmap
    ## linux command
    IOCTL_REQ = LinCommand.linux_req.get("NVME_IOCTL_ADMIN_CMD")
    class SetFeature(LinCommand):
        def __init__(self, 
                     feature_id, 
                     ns_id=0,
                     sv=0, 
                     uuid_index=0, 
                     cdw11=0, 
                     cdw12=0, 
                     cdw13=0, 
                     cdw15=0, 
                     data_in=None):
            ### build command
            cdw10 = build_int_by_bitmap({"FID": (0xFF, 0, feature_id),
                                         "SV": (0x80, 3, sv)})
            cdw14 = build_int_by_bitmap({"UUID": (0x7F, 0, uuid_index),})    
            ##
            d_l = len(data_in) if data_in else 0        
            super(SetFeature, self).__init__(IOCTL_REQ)
            self.build_command(opcode=CmdOPCode,
                               nsid=ns_id,
                               data_len=d_l,
                               data_in=data_in,
                               cdw10=cdw10,
                               cdw11=cdw11,
                               cdw12=cdw12,
                               cdw13=cdw13,
                               cdw14=cdw14,
                               cdw15=cdw15,)

elif os_type == "Windows":
    from pydiskcmd.pynvme.nvme_command import WinCommand
    class SetFeature(WinCommand):
        ## TODO.
        pass

else:
    raise NotImplementedError("%s not support" % os_type)
