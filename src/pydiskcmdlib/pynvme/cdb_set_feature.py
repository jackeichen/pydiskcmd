# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmdlib import os_type
from pydiskcmdlib.pynvme.nvme_command import NVMeCommand,AdminCommandOpcode,CommandTimeout
from pydiskcmdlib.pynvme import linux_nvme_command,win_nvme_command
#####
CmdOPCode = AdminCommandOpcode.SetFeature.value
#####
class SetFeature(NVMeCommand):
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
                     "fid": [0xFF, 40],
                     "sv": [0x80, 43],
                     "cdw11":[0xFFFFFFFF, 44],
                     "cdw12":[0xFFFFFFFF, 48],
                     "cdw13":[0xFFFFFFFF, 52],
                     #"cdw14":[0xFFFFFFFF, 56],
                     "uuid": [0x7F, 56],
                     "cdw15":[0xFFFFFFFF, 60],
                     "timeout_ms":[0xFFFFFFFF, 64],
                     "result":[0xFFFFFFFF, 68],
                     }
    elif os_type == "Windows":
        _req_id = win_nvme_command.IOCTLRequest.RESERVED_REQUEST_ID.value

    def __init__(self, 
                 fid, 
                 nsid=0,
                 sv=0, 
                 uuid_index=0, 
                 cdw11=0, 
                 cdw12=0, 
                 cdw13=0, 
                 cdw15=0, 
                 data_out=b''):
        super(SetFeature, self).__init__()
        if os_type == "Linux":
            # init data buffer
            data_buffer = self.init_data_buffer(data_length=len(data_out), data_out=data_out)
            self.build_command(opcode=CmdOPCode,
                               nsid=nsid,
                               addr=data_buffer.addr,
                               data_len=data_buffer.data_length,
                               fid=fid,
                               sv=sv,
                               uuid=uuid_index,
                               cdw11=cdw11,
                               cdw12=cdw12, 
                               cdw13=cdw13, 
                               cdw15=cdw15, 
                               timeout_ms=CommandTimeout.admin.value,)
        elif os_type == "Windows":
            self.build_command()
