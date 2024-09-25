# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from .cdb_vroc_raid_passthrough import NVMePassThroughSRB
from . import win_ioctl
from pydiskcmdlib.pynvme.cdb_self_test import CmdOPCode
from pydiskcmdlib.pynvme.nvme_command import build_int_by_bitmap

#       def __init__(self,
#                  vroc_disk_id,
#                  opc,
#                  nsid,
#                  cdw10,
#                  cdw11,
#                  cdw12,
#                  cdw13,
#                  cdw14,
#                  cdw15,
#                  direction,  # 0,1,2
#                  queue_id,   # 0 means admin command, otherwise IO command
#                  data_buffer_len, # data length
#                  metadata_len=0,  # TODO, Not support now
#                  ):


class SelfTest(NVMePassThroughSRB):
    def __init__(self,
                 vroc_disk_id,
                 stc,
                 nsid=0xFFFFFFFF):
        ### build command
        cdw10 = build_int_by_bitmap({"stc": (0x0F, 0, stc),}) 
        ##
        NVMePassThroughSRB.__init__(self,
                                    vroc_disk_id,
                                    CmdOPCode,
                                    nsid,
                                    cdw10,
                                    0,
                                    0,
                                    0,
                                    0,
                                    0,
                                    win_ioctl.NVME_NO_DATA_TX,
                                    0, # 0 means admin command
                                    0, # data length
                                    )
