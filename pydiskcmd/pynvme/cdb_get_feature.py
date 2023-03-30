# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmd.system.os_tool import os_type

#####
CmdOPCode = 0x0A
#####

if os_type == "Linux":
    from pydiskcmd.pynvme.nvme_command import LinCommand,build_int_by_bitmap
    ## linux command
    IOCTL_REQ = LinCommand.linux_req.get("NVME_IOCTL_ADMIN_CMD")
    class GetFeature(LinCommand):
        def __init__(self, 
                     feature_id, 
                     ns_id=0, 
                     sel=0, 
                     uuid_index=0, 
                     cdw11=0, 
                     data_len=0):
            ### build command
            cdw10 = build_int_by_bitmap({"FID": (0xFF, 0, feature_id),
                                         "SEL": (0x07, 1, sel)})
            cdw14 = build_int_by_bitmap({"UUID": (0x7F, 0, uuid_index),})   
            ##     
            super(GetFeature, self).__init__(IOCTL_REQ)
            self.build_command(opcode=CmdOPCode,
                               nsid=ns_id,
                               data_len=data_len,
                               cdw10=cdw10,
                               cdw11=cdw11,
                               cdw14=cdw14)

elif os_type == "Windows":
    from pydiskcmd.pynvme.nvme_command import WinCommand
    class GetFeature(WinCommand):
        ## TODO.
        pass
else:
    raise NotImplementedError("%s not support" % os_type)
