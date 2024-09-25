# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from .cdb_vroc_raid_passthrough import NVMePassThroughSRB
from . import win_ioctl
from pydiskcmdlib.pynvme.cdb_set_feature import CmdOPCode
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


class SetFeature(NVMePassThroughSRB):
    def __init__(self,
                 vroc_disk_id,
                 feature_id, 
                 nsid=0,
                 sv=0, 
                 uuid_index=0, 
                 cdw11=0, 
                 cdw12=0, 
                 cdw13=0, 
                 cdw15=0, 
                 data_out=None):
        if data_out:
            raise RuntimeError("No data from host to device support now!")
        ### build command
        cdw10 = build_int_by_bitmap({"FID": (0xFF, 0, feature_id),
                                     "SV": (0x80, 3, sv)})
        cdw14 = build_int_by_bitmap({"UUID": (0x7F, 0, uuid_index),})   
        ##
        NVMePassThroughSRB.__init__(self,
                                    vroc_disk_id,
                                    CmdOPCode,
                                    nsid,
                                    cdw10,
                                    cdw11,
                                    cdw12,
                                    cdw13,
                                    cdw14,
                                    cdw15,
                                    win_ioctl.NVME_FROM_HOST_TO_DEV if data_out else win_ioctl.NVME_NO_DATA_TX,
                                    0, # 0 means admin command
                                    len(data_out) if data_out else 0,
                                    )
