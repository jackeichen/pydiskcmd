# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmd.system.os_tool import os_type
from pydiskcmd.pynvme.nvme_command import Command,build_command

#####
CmdOPCode = 0x09
#####

if os_type == "Linux":
    ## linux command
    IOCTL_REQ = Command.linux_req.get("NVME_IOCTL_ADMIN_CMD")
    class SetFeature(Command):
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
            cdw10 = build_command({"FID": (0xFF, 0, feature_id),
                                   "SV": (0x80, 3, sv)})
            cdw14 = build_command({"UUID": (0x7F, 0, uuid_index),})    
            ##
            d_l = len(data_in) if data_in else 0        
            super(SetFeature, self).__init__(IOCTL_REQ,
                                             opcode=CmdOPCode,
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
    class SetFeature(object):
        ## TODO.
        pass


else:
    raise NotImplementedError("%s not support" % os_type)
