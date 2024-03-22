# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmdlib import os_type
from pydiskcmdlib.pynvme.nvme_command import NVMeCommand,NVMCommandOpcode,CommandTimeout
from pydiskcmdlib.pynvme import linux_nvme_command,win_nvme_command

#####
CmdOPCode = NVMCommandOpcode.Read.value
#####
class Read(NVMeCommand):
    if os_type == "Linux":
        _req_id = linux_nvme_command.IOCTLRequest.NVME_IOCTL_IO_CMD.value
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
                     "slbal":[0xFFFFFFFF, 40],
                     "slbau":[0xFFFFFFFF, 44],
                     # "cdw12":[0xFFFFFFFF, 48],
                     "nlba":[0xFFFF, 48],
                     "prinfo":[0x3C, 51],
                     "fua":[0x40, 51],
                     "lr":[0x80, 51],
                     # "cdw13":[0xFFFFFFFF, 52],
                     "dsm":[0xFFFFFFFF, 52],
                     # "cdw14":[0xFFFFFFFF, 56],
                     "eilbrt":[0xFFFFFFFF, 56],
                     # "cdw15":[0xFFFFFFFF, 60],
                     "elbat":[0xFFFF, 60],
                     "elbatm":[0xFFFF, 62],
                     "timeout_ms":[0xFFFFFFFF, 64],
                     "result":[0xFFFFFFFF, 68],
                     }
    elif os_type == "Windows":
        _req_id = win_nvme_command.IOCTLRequest.RESERVED_REQUEST_ID.value
        _cdb_bits = {}

    def __init__(self,
                 nsid,    # Namespace ID
                 slba, 
                 nlba,
                 data_buffer=None,      ## Data Pointer
                 data_len=0,     ## used to create data buffer
                 metadata_buffer=None,  ## Metadata Pointer
                 metadata_len=0, ## Metadata length
                 prinfo=0,
                 fua=0,
                 lr=0,
                 dsm=0,
                 eilbrt=0,
                 elbat=0,
                 elbatm=0,
                 timeout=CommandTimeout.nvm.value,
                 ):
        super(Read, self).__init__()
        if os_type == "Linux":
            data_buffer = self.init_data_buffer(data_length=data_len, data_buffer=data_buffer)
            metadata_buffer = self.init_metadata_buffer(data_length=metadata_len, data_buffer=metadata_buffer)
            self.build_command(opcode=CmdOPCode,
                               nsid=nsid,
                               metadata=metadata_buffer.addr,
                               addr=data_buffer.addr,
                               metadata_len=metadata_buffer.data_length,
                               data_len=data_buffer.data_length,
                               slbal=(slba & 0xFFFFFFFF),
                               slbau=((slba >> 32) & 0xFFFFFFFF),
                               nlba=nlba,
                               prinfo=prinfo,
                               fua=fua,
                               lr=lr,
                               dsm=dsm,
                               eilbrt=eilbrt,
                               elbat=elbat,
                               elbatm=elbatm,
                               timeout_ms=timeout)
        elif os_type == "Windows":
            self.build_command()
