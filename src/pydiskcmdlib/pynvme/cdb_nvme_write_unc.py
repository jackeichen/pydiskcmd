# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmdlib import os_type
from pydiskcmdlib.pynvme.nvme_command import NVMeCommand,NVMCommandOpcode,CommandTimeout,build_int_by_bitmap
from pydiskcmdlib.pynvme import linux_nvme_command,win_nvme_command

#####
CmdOPCode = NVMCommandOpcode.WriteUncorrectable.value
#####
class WriteUncorrectable(NVMeCommand):
    if os_type == "Linux":
        _req_id = linux_nvme_command.IOCTLRequest.NVME_IOCTL_IO_CMD.value
    elif os_type == "Windows":
        _req_id = win_nvme_command.IOCTLRequest.RESERVED_REQUEST_ID.value
        _cdb_bits = {}

    def __init__(self,
                 nsid,    # Namespace ID
                 slba, 
                 nlba,
                 timeout=CommandTimeout.nvm.value,
                 ):
        super(WriteUncorrectable, self).__init__()
        if os_type == "Linux":
            self.build_command(opcode=CmdOPCode,
                               nsid=nsid,
                               metadata=0,
                               addr=0,
                               metadata_len=0,
                               data_len=0,
                               cdw10=(slba & 0xFFFFFFFF),
                               cdw11=((slba >> 32) & 0xFFFFFFFF),
                               cdw12=(nlba & 0xFFFF),
                               timeout_ms=timeout)
        elif os_type == "Windows":
            self.build_command()
