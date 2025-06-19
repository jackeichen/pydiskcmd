# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmdlib import os_type
from pydiskcmdlib.pynvme.nvme_command import NVMeCommand,AdminCommandOpcode,CommandTimeout,build_int_by_bitmap
from pydiskcmdlib.pynvme import linux_nvme_command,win_nvme_command
#####
CmdOPCode = AdminCommandOpcode.Sanitize.value
#####
class Sanitize(NVMeCommand):
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
                     # "cdw10":[0xFFFFFFFF, 40],
                     "sanact":[0x07, 40],
                     "ause":[0x08, 40],
                     "owpass":[0xF0, 40],
                     "oipbp":[0x01, 41],
                     "no_deallocate":[0x02, 41],
                     "ovrpat":[0xFFFFFFFF, 44],
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
        # From Windows 10, Version 2004 / May 2020 Update, Windows Server Version 2004 (Server Core). 
        # WinPE only prior to Windows 11, Windows Server 2022 and only if the user uses

    def __init__(self,
                 sanact,
                 ause,
                 owpass,
                 oipbp,
                 no_deallocate,
                 ovrpat=0,
                 timeout=CommandTimeout.admin.value,
                 ):
        super(Sanitize, self).__init__()
        if sanact != 3:
            ovrpat = 0
        if os_type == "Linux":
            self.build_command(opcode=CmdOPCode,
                               sanact=sanact,
                               ause=ause,
                               owpass=owpass,
                               oipbp=oipbp,
                               no_deallocate=no_deallocate,
                               ovrpat=ovrpat,
                               timeout_ms=timeout)
        elif os_type == "Windows":
            cdw10 = build_int_by_bitmap({"sanact": (0x07, 0, sanact), 
                                         "ause": (0x08, 0 ,ause), 
                                         "owpass": (0xF0, 0, owpass),     
                                         "oipbp": (0x01, 1, oipbp), 
                                         "no_deallocate": (0x02, 1, no_deallocate)})  
            self.build_command(Flags=win_nvme_command.STORAGE_PROTOCOL_COMMAND_FLAG_ADAPTER_REQUEST,
                               TimeOutValue=10,
                               CommandSpecific=win_nvme_command.STORAGE_PROTOCOL_SPECIFIC_NVME_ADMIN_COMMAND,
                               OPC=CmdOPCode,
                               CDW10=cdw10,
                               CDW11=ovrpat,
                               )
