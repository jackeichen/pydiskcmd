# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmdlib import os_type
from pydiskcmdlib.pynvme.nvme_command import NVMeCommand,AdminCommandOpcode,CommandTimeout
from pydiskcmdlib.pynvme import linux_nvme_command,win_nvme_command
#####
CmdOPCode = AdminCommandOpcode.DeviceSelftest.value
#####

class SelfTest(NVMeCommand):
    if os_type == "Linux":
        _req_id = linux_nvme_command.IOCTLRequest.NVME_IOCTL_ADMIN_CMD.value
        _cdb_bits = {"opcode": [0xFF, 0],
                     "flags": [0xFF, 1],
                     "rsvd1": [0xFFFF, 2],
                     "nsid":[0xFFFFFFFF, 4],
                     "cdw2":[0xFFFFFFFF, 8],
                     "cdw3":[0xFFFFFFFF, 12],
                     "metadata":[0xFFFFFFFFFFFFFFFF, 16],
                     "addr":[0xFFFFFFFFFFFFFFFF, 24],
                     "metadata_len":[0xFFFFFFFF, 32],
                     "data_len":[0xFFFFFFFF, 36],
                     #"cdw10":[0xFFFFFFFF, 40],
                     "stc": [0x0F, 40],
                     "reserved": [0xFFFFF0, 41],
                     "cdw11":[0xFFFFFFFF, 44],
                     "cdw12":[0xFFFFFFFF, 48],
                     "cdw13":[0xFFFFFFFF, 52],
                     "cdw14":[0xFFFFFFFF, 56],
                     "cdw15":[0xFFFFFFFF, 60],
                     "timeout_ms":[0xFFFFFFFF, 64],
                     "result":[0xFFFFFFFF, 68],
                     }
    elif os_type == "Windows":
        _req_id = win_nvme_command.IOCTLRequest.IOCTL_STORAGE_PROTOCOL_COMMAND.value
        # use default _cdb_bits

    def __init__(self, 
                 stc,
                 nsid=0xFFFFFFFF,
                 timeout=CommandTimeout.admin.value):
        ##
        super(SelfTest, self).__init__()
        if os_type == "Linux":
            self.build_command(opcode=CmdOPCode,
                               nsid=nsid,
                               stc=stc,
                               timeout_ms=timeout)
        elif os_type == "Windows":
            self.build_command(Flags=win_nvme_command.STORAGE_PROTOCOL_COMMAND_FLAG_ADAPTER_REQUEST,
                               TimeOutValue=10,
                               CommandSpecific=win_nvme_command.STORAGE_PROTOCOL_SPECIFIC_NVME_ADMIN_COMMAND,
                               OPC=CmdOPCode,
                               NSID=0xFFFFFFFF,
                               CDW10=stc,
                               )
