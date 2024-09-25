# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from .cdb_vroc_raid_passthrough import NVMePassThroughSRB
from . import win_ioctl
from pydiskcmdlib.pynvme.cdb_identify import CmdOPCode,CNSValue
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


class Identify(NVMePassThroughSRB):
    def __init__(self,
                 vroc_disk_id,
                 nsid,    # Namespace ID
                 cns,     # CDW10: 
                 cntid,
                 nvmsetid,
                 uuid,
                 data_length=4096,
                 ):
        cdw10 = build_int_by_bitmap({"cns": (0xFF, 0, cns), 
                                     "cntid": (0xFFFF, 1, cntid),
                                     })
        cdw11 = build_int_by_bitmap({"nvmsetid": (0xFFFF, 0, nvmsetid),}
                                     )
        cdw14 = build_int_by_bitmap({"uuid": (0x7F, 0, uuid),}
                                     )

        NVMePassThroughSRB.__init__(self,
                                    vroc_disk_id,
                                    CmdOPCode,
                                    nsid,
                                    cdw10,
                                    cdw11,
                                    0,
                                    0,
                                    cdw14,
                                    0,
                                    win_ioctl.NVME_FROM_DEV_TO_HOST,
                                    0, # 0 means admin command
                                    data_length,
                                    )


class IDCtrl(Identify):
    def __init__(self, vroc_disk_id, uuid=0):
        Identify.__init__(self,
                          vroc_disk_id,
                          0,  # nsid
                          CNSValue.IdentifyController.value,  # cns
                          0,  # cntid
                          0,  # nvmsetid
                          uuid,  # uuid
                          data_length=4096,
                          )


class IDNS(Identify):
    def __init__(self, vroc_disk_id, nsid, uuid=0):
        Identify.__init__(self,
                          vroc_disk_id,
                          nsid,  # nsid
                          CNSValue.IdentifyNamespace.value,  # cns
                          0,  # cntid
                          0,  # nvmsetid
                          uuid,  # uuid
                          data_length=4096,
                          )
