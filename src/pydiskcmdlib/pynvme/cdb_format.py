# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmdlib import os_type
from pydiskcmdlib.pynvme.nvme_command import NVMeCommand,AdminCommandOpcode

#####
CmdOPCode = AdminCommandOpcode.FormatNVM.value
#####

class Format(NVMeCommand):
    if os_type == "Linux":
        from pydiskcmdlib.pynvme.linux_nvme_command import IOCTLRequest
        _req_id = IOCTLRequest.NVME_IOCTL_ADMIN_CMD.value
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
                     "lbaf": [0x0F, 40],
                     "mset": [0x10, 40],
                     "pi": [0xE0, 40],
                     "pil": [0x01, 41],
                     "ses": [0x0E, 41],
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
        from pydiskcmdlib.pynvme.win_nvme_command import IOCTLRequest
        _req_id = IOCTLRequest.IOCTL_STORAGE_REINITIALIZE_MEDIA.value

    def __init__(self, 
                 lbaf, 
                 mset=0, 
                 pi=0, 
                 pil=0, 
                 ses=0, 
                 nsid=0xFFFFFFFF,
                 timeout=600000):
        ##
        super(Format, self).__init__()
        self.build_command(opcode=CmdOPCode,
                           nsid=nsid,
                           lbaf=lbaf,
                           mset=mset,
                           pi=pi,
                           pil=pil,
                           ses=ses,
                           timeout_ms=timeout)
