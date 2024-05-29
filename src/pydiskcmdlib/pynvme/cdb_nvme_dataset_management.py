# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmdlib import os_type
from pydiskcmdlib.pynvme.nvme_command import NVMeCommand,NVMCommandOpcode,CommandTimeout,build_int_by_bitmap
from pydiskcmdlib.pynvme import linux_nvme_command,win_nvme_command

#####
CmdOPCode = NVMCommandOpcode.DatasetManagement.value
#####
class DatasetManagement(NVMeCommand):
    if os_type == "Linux":
        _req_id = linux_nvme_command.IOCTLRequest.NVME_IOCTL_IO_CMD.value
    elif os_type == "Windows":
        _req_id = win_nvme_command.IOCTLRequest.RESERVED_REQUEST_ID.value
        _cdb_bits = {}

    def __init__(self,
                 nsid,    # Namespace ID
                 nr,
                 idr,
                 idw,
                 ad,
                 data,
                 timeout=CommandTimeout.nvm.value,
                 ):
        super(DatasetManagement, self).__init__()
        if os_type == "Linux":
            data_buffer = self.init_data_buffer(data_length=4096, data_out=data)
            cdw11 = build_int_by_bitmap({"idr": (0x01, 0, idr), 
                                         "idw": (0x02, 0 , idw),
                                         "ad": (0x04, 0, ad),}) 
            self.build_command(opcode=CmdOPCode,
                               nsid=nsid,
                               metadata=0,
                               addr=data_buffer.addr,
                               metadata_len=0,
                               data_len=data_buffer.data_length,
                               cdw10=(nr & 0xFF),
                               cdw11=cdw11,
                               timeout_ms=timeout)
        elif os_type == "Windows":
            self.build_command()
