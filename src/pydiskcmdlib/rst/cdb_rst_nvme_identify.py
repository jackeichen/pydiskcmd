# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from .cdb_rst_nvme_passthr import RSTNVMePass
from pydiskcmdlib.pynvme.cdb_identify import CmdOPCode,CNSValue
from pydiskcmdlib.pynvme.nvme_command import build_int_by_bitmap

class Identify(RSTNVMePass):
    def __init__(self,
                 path_id,
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

        RSTNVMePass.__init__(self,
                             path_id,     # Port number from Windows (non-RAID) or CSMI port number (GET_RAID_INFO and GET_RAID_CONFIG)
                             0,           # 0 for admincommand, 1 for iocommand
                             CmdOPCode,   # opcode
                             nsid,        # Namespace ID
                             cdw10,       # CDW10
                             cdw11,       # CDW11
                             0,           # CDW12
                             0,           # CDW13
                             cdw14,       # CDW14
                             0,           # CDW15
                             data_length, # data_buffer_len
                             0,           # metadata_buffer_len
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
