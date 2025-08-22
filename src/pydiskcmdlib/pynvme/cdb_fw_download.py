# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmdlib import os_type
from pydiskcmdlib.pynvme.nvme_command import NVMeCommand,AdminCommandOpcode,CommandTimeout
from pydiskcmdlib.exceptions import BuildNVMeCommandError
#####
CmdOPCode = AdminCommandOpcode.FirmwareImageDownload.value
#####
class FWImageDownload(NVMeCommand):
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
                     "numd": [0xFFFFFFFF, 40],
                     "ofst":[0xFFFFFFFF, 44],
                     "cdw12":[0xFFFFFFFF, 48],
                     "cdw13":[0xFFFFFFFF, 52],
                     "cdw14":[0xFFFFFFFF, 56],
                     "cdw15":[0xFFFFFFFF, 60],
                     "timeout_ms":[0xFFFFFFFF, 64],
                     "result":[0xFFFFFFFF, 68],
                     }
    elif os_type == "Windows":
        from pydiskcmdlib.pynvme import win_nvme_command
        #_req_id = win_nvme_command.IOCTLRequest.IOCTL_SCSI_MINIPORT.value
        _req_id = win_nvme_command.IOCTLRequest.IOCTL_STORAGE_FIRMWARE_DOWNLOAD.value
        _cdb_bits = {"HeaderLength": [0xFFFFFFFF, 0],
                     "Signature": ('b', 4, 8),
                     "Timeout": [0xFFFFFFFF, 12],
                     "ControlCode": [0xFFFFFFFF, 16],
                     "ReturnCode": [0xFFFFFFFF, 20],
                     "Length": [0xFFFFFFFF, 24],       # 
                     "Version": [0xFFFFFFFF, 28],
                     "Size": [0xFFFFFFFF, 32],
                     "Function": [0xFFFFFFFF, 36],
                     "Flags": [0xFFFFFFFF, 40],
                     "DataBufferOffset": [0xFFFFFFFF, 44],
                     "DataBufferLength": [0xFFFFFFFF, 48], # 
                     "fdVersion": [0xFFFFFFFF, 52],
                     "fdSize": [0xFFFFFFFF, 56],
                     "fdOffset": [0xFFFFFFFFFFFFFFFF, 60],
                     "fdBufferSize": [0xFFFFFFFFFFFFFFFF, 68],
                     #"fdImageBuffer": ['b', 76, 0],
                     }

    def __init__(self, 
                 data, 
                 offset):
        super(FWImageDownload, self).__init__()
        #
        data_len = len(data)
        if (data_len % 4):
            raise BuildNVMeCommandError("data length should be dword aligned")
        dataout_buffer = self.init_data_buffer(data_length=data_len)
        dataout_buffer.data_buffer = data
        if os_type == "Linux":
            self.build_command(opcode=CmdOPCode,
                               addr=dataout_buffer.addr,
                               data_len=dataout_buffer.data_length,
                               numd=int(((data_len / 4) - 1)),
                               ofst=offset,
                               timeout_ms=CommandTimeout.admin.value)
        elif os_type == "Windows":
            self.build_command(ControlCode=FWImageDownload.win_nvme_command.IOCTL_SCSI_MINIPORT_FIRMWARE,
                               Function=FWImageDownload.win_nvme_command.FIRMWARE_FUNCTION.DOWNLOAD.value,
                               fdOffset=offset,
                               fdBufferSize=len(data),
                               )
