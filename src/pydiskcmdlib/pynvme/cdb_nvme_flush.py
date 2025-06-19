# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmdlib import os_type
from pydiskcmdlib.pynvme.nvme_command import NVMeCommand,NVMCommandOpcode,CommandTimeout
from pydiskcmdlib.pynvme import linux_nvme_command,win_nvme_command
#####
CmdOPCode = NVMCommandOpcode.Flush.value
#####
class Flush(NVMeCommand):
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
                     "cdw10":[0xFFFFFFFF, 40],
                     "cdw11":[0xFFFFFFFF, 44],
                     "cdw12":[0xFFFFFFFF, 48],
                     "cdw13":[0xFFFFFFFF, 52],
                     "cdw14":[0xFFFFFFFF, 56],
                     "cdw15":[0xFFFFFFFF, 60],
                     "timeout_ms":[0xFFFFFFFF, 64],
                     "result":[0xFFFFFFFF, 68],
                     }
    elif os_type == "Windows":
        _req_id = win_nvme_command.IOCTLRequest.RESERVED_REQUEST_ID.value
        _cdb_bits = {}

    def __init__(self,
                 nsid,    # Namespace ID
                 timeout=CommandTimeout.nvm.value,
                 ):
        super(Flush, self).__init__()
        if os_type == "Linux":
            self.build_command(opcode=CmdOPCode,
                               nsid=nsid,
                               timeout_ms=timeout)
        elif os_type == "Windows":
            self.build_command()


from pydiskcmdlib.pyscsi.scsi_cdb_synchronizecache import SynchronizeCache16
from pyscsi.pyscsi.scsi_enum_command import sbc
#####
SCSICmdOPCode = sbc.SYNCHRONIZE_CACHE_16
#####
class SCSI2NVMeFlush(SynchronizeCache16):
    def __init__(self,
                 nsid,   # ignored by command
                 timeout=CommandTimeout.nvm.value, # ignored by command
                 ):
        SynchronizeCache16.__init__(self,
                                    SCSICmdOPCode,
                                    0,   # start fronm lba 0
                                    0,   # all lbas that start form lba 0
                                    )
