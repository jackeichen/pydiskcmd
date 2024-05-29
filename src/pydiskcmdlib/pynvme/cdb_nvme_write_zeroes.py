# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmdlib import os_type
from pydiskcmdlib.pynvme.nvme_command import NVMeCommand,NVMCommandOpcode,CommandTimeout,build_int_by_bitmap
from pydiskcmdlib.pynvme import linux_nvme_command,win_nvme_command

#####
CmdOPCode = NVMCommandOpcode.WriteZeroes.value
#####
class WriteZeroes(NVMeCommand):
    if os_type == "Linux":
        _req_id = linux_nvme_command.IOCTLRequest.NVME_IOCTL_IO_CMD.value
    elif os_type == "Windows":
        _req_id = win_nvme_command.IOCTLRequest.RESERVED_REQUEST_ID.value
        _cdb_bits = {}

    def __init__(self,
                 nsid,    # Namespace ID
                 slba, 
                 nlba,
                 deac=0,
                 prinfo=0,
                 fua=0,
                 lr=0,
                 dsm=0,
                 dspec=0,
                 ilbrt=0,
                 lbat=0,
                 lbatm=0,
                 timeout=CommandTimeout.nvm.value,
                 ):
        super(WriteZeroes, self).__init__()
        if os_type == "Linux":
            cdw12 = build_int_by_bitmap({"nlb": (0xFFFF, 0, nlba), 
                                         "deac": (0x02, 3 , deac),
                                         "prinfo": (0x3C, 3, prinfo), 
                                         "fua": (0x40, 3, fua),
                                         "lr": (0x80, 3, lr)}) 
            cdw15 = build_int_by_bitmap({"lbat": (0xFFFF, 0, lbat), 
                                         "lbatm": (0xFFFF, 2, lbatm)}) 

            self.build_command(opcode=CmdOPCode,
                               nsid=nsid,
                               metadata=0,
                               addr=0,
                               metadata_len=0,
                               data_len=0,
                               cdw10=(slba & 0xFFFFFFFF),
                               cdw11=((slba >> 32) & 0xFFFFFFFF),
                               cdw12=cdw12,
                               cdw14=ilbrt,
                               cdw15=cdw15,
                               timeout_ms=timeout)
        elif os_type == "Windows":
            self.build_command()
