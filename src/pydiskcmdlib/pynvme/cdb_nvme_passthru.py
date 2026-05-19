# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from enum import Enum
from pydiskcmdlib import os_type
from pydiskcmdlib.pynvme.nvme_command import NVMeCommand,linux_nvme_command,win_nvme_command
from typing import Optional


class NVMEDXFER(Enum):
    NVME_DXFER_NONE = 0
    NVME_DXFER_TO_DEV = 1
    NVME_DXFER_FROM_DEV = 2


class AdminPassthru(NVMeCommand):
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
        _req_id = win_nvme_command.IOCTLRequest.IOCTL_STORAGE_PROTOCOL_COMMAND.value
        # use default _cdb_bits, in win_nvme_command.cdb_bitmap
        # {
        #     "Version": [0xFFFFFFFF, 0],
        #     "Length": [0xFFFFFFFF, 4],
        #     "ProtocolType": [0xFFFFFFFF, 8],
        #     "Flags": [0xFFFFFFFF, 12],
        #     "ReturnStatus": [0xFFFFFFFF, 16],
        #     "ErrorCode": [0xFFFFFFFF, 20],
        #     "CommandLength": [0xFFFFFFFF, 24],
        #     "ErrorInfoLength": [0xFFFFFFFF, 28],
        #     "DataToDeviceTransferLength": [0xFFFFFFFF, 32],
        #     "DataFromDeviceTransferLength": [0xFFFFFFFF, 36],
        #     "TimeOutValue": [0xFFFFFFFF, 40],
        #     "ErrorInfoOffset": [0xFFFFFFFF, 44],
        #     "DataToDeviceBufferOffset": [0xFFFFFFFF, 48],
        #     "DataFromDeviceBufferOffset": [0xFFFFFFFF, 52],
        #     "CommandSpecific": [0xFFFFFFFF, 56],
        #     "Reserved0": [0xFFFFFFFF, 60],
        #     "FixedProtocolReturnData": [0xFFFFFFFF, 64],
        #     #"Reserved1": [0xFFFFFFFFFFFFFFFFFFFFFFFF, 68], # 68 + 3 * 4 = 80
        #     "OPC": [0xFF, 80],
        #     "FUSE": [0x03, 81],
        #     "Reserved0": [0x7C, 81],
        #     "PSDT": [0x80, 81],
        #     "CID": [0xFFFF, 82],
        #     "NSID": [0xFFFFFFFF, 84],
        #     # "Reserved0": [0xFFFFFFFFFFFFFFFF, 88],
        #     "MPTR": [0xFFFFFFFFFFFFFFFF, 96],
        #     "PRP1": [0xFFFFFFFFFFFFFFFF, 104],
        #     "PRP2": [0xFFFFFFFFFFFFFFFF, 112],
        #     "CDW10": [0xFFFFFFFF, 120],
        #     "CDW11": [0xFFFFFFFF, 124],
        #     "CDW12": [0xFFFFFFFF, 128],
        #     "CDW13": [0xFFFFFFFF, 132],
        #     "CDW14": [0xFFFFFFFF, 136],
        #     "CDW15": [0xFFFFFFFF, 140],
        # },

    def __init__(self,
                 opcode: int,
                 flags: int,
                 nsid: int,
                 cdw2: int,
                 cdw3: int,
                 metadata: Optional[bytes],
                 data: Optional[bytes],
                 metadata_len: int,
                 data_len: int,
                 cdw10: int,
                 cdw11: int,
                 cdw12: int,
                 cdw13: int,
                 cdw14: int,
                 cdw15: int,
                 dxfer_direction: int = NVMEDXFER.NVME_DXFER_NONE.value,
                 timeout: int = 600000):
        ##
        super(AdminPassthru, self).__init__()
        if os_type == "Linux":
            if data or data_len > 0:
                data_buffer = self.init_data_buffer(data_length=data_len, data_out=data)
            else:
                data_buffer = None
            if metadata or metadata_len > 0:
                metadata_buffer = self.init_metadata_buffer(data_length=metadata_len, data_out=metadata)
            else:
                metadata_buffer = None
            self.build_command(opcode=opcode,
                               flags=flags,
                               nsid=nsid,
                               cdw2=cdw2,
                               cdw3=cdw3,
                               metadata=None if metadata_buffer is None else metadata_buffer.addr,
                               addr=None if data_buffer is None else data_buffer.addr,
                               metadata_len=0 if metadata_buffer is None else metadata_buffer.data_length,
                               data_len=0 if data_buffer is None else data_buffer.data_length,
                               cdw10=cdw10,
                               cdw11=cdw11,
                               cdw12=cdw12,
                               cdw13=cdw13,
                               cdw14=cdw14,
                               cdw15=cdw15,
                               timeout_ms=timeout)
        elif os_type == "Windows":
            self.build_command(Flags=win_nvme_command.STORAGE_PROTOCOL_COMMAND_FLAG_ADAPTER_REQUEST,
                               DataToDeviceTransferLength=data_len if dxfer_direction == NVMEDXFER.NVME_DXFER_TO_DEV.value else 0,
                               DataFromDeviceTransferLength=data_len if dxfer_direction == NVMEDXFER.NVME_DXFER_FROM_DEV.value else 0,
                               TimeOutValue=int(timeout/1000),
                               CommandSpecific=win_nvme_command.STORAGE_PROTOCOL_SPECIFIC_NVME_ADMIN_COMMAND,
                               OPC=opcode,
                               FUSE=(flags & 0x03),
                               NSID=nsid,
                               CDW10=cdw10,
                               CDW11=cdw11,
                               CDW12=cdw12,
                               CDW13=cdw13,
                               CDW14=cdw14,
                               CDW15=cdw15,
                               )
            if data:
                self._cdb.data_buf = data
            if metadata:
                raise ValueError("metadata is not supported on Windows")
        else:
            raise NotImplementedError("os_type %s is not supported" % os_type)


class NVMPassthru(NVMeCommand):
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
        _req_id = win_nvme_command.IOCTLRequest.IOCTL_STORAGE_PROTOCOL_COMMAND.value
        # use default _cdb_bits, in win_nvme_command.cdb_bitmap
        # {
        #     "Version": [0xFFFFFFFF, 0],
        #     "Length": [0xFFFFFFFF, 4],
        #     "ProtocolType": [0xFFFFFFFF, 8],
        #     "Flags": [0xFFFFFFFF, 12],
        #     "ReturnStatus": [0xFFFFFFFF, 16],
        #     "ErrorCode": [0xFFFFFFFF, 20],
        #     "CommandLength": [0xFFFFFFFF, 24],
        #     "ErrorInfoLength": [0xFFFFFFFF, 28],
        #     "DataToDeviceTransferLength": [0xFFFFFFFF, 32],
        #     "DataFromDeviceTransferLength": [0xFFFFFFFF, 36],
        #     "TimeOutValue": [0xFFFFFFFF, 40],
        #     "ErrorInfoOffset": [0xFFFFFFFF, 44],
        #     "DataToDeviceBufferOffset": [0xFFFFFFFF, 48],
        #     "DataFromDeviceBufferOffset": [0xFFFFFFFF, 52],
        #     "CommandSpecific": [0xFFFFFFFF, 56],
        #     "Reserved0": [0xFFFFFFFF, 60],
        #     "FixedProtocolReturnData": [0xFFFFFFFF, 64],
        #     #"Reserved1": [0xFFFFFFFFFFFFFFFFFFFFFFFF, 68], # 68 + 3 * 4 = 80
        #     "OPC": [0xFF, 80],
        #     "FUSE": [0x03, 81],
        #     "Reserved0": [0x7C, 81],
        #     "PSDT": [0x80, 81],
        #     "CID": [0xFFFF, 82],
        #     "NSID": [0xFFFFFFFF, 84],
        #     # "Reserved0": [0xFFFFFFFFFFFFFFFF, 88],
        #     "MPTR": [0xFFFFFFFFFFFFFFFF, 96],
        #     "PRP1": [0xFFFFFFFFFFFFFFFF, 104],
        #     "PRP2": [0xFFFFFFFFFFFFFFFF, 112],
        #     "CDW10": [0xFFFFFFFF, 120],
        #     "CDW11": [0xFFFFFFFF, 124],
        #     "CDW12": [0xFFFFFFFF, 128],
        #     "CDW13": [0xFFFFFFFF, 132],
        #     "CDW14": [0xFFFFFFFF, 136],
        #     "CDW15": [0xFFFFFFFF, 140],
        # },

    def __init__(self,
                 opcode: int,
                 flags: int,
                 nsid: int,
                 cdw2: int,
                 cdw3: int,
                 metadata: Optional[bytes],
                 data: Optional[bytes],
                 metadata_len: int,
                 data_len: int,
                 cdw10: int,
                 cdw11: int,
                 cdw12: int,
                 cdw13: int,
                 cdw14: int,
                 cdw15: int,
                 dxfer_direction: int = NVMEDXFER.NVME_DXFER_NONE.value,
                 timeout: int = 600000):
        ##
        super(NVMPassthru, self).__init__()
        if os_type == "Linux":
            if data or data_len > 0:
                data_buffer = self.init_data_buffer(data_length=data_len, data_out=data)
            else:
                data_buffer = None
            if metadata or metadata_len > 0:
                metadata_buffer = self.init_metadata_buffer(data_length=metadata_len, data_out=metadata)
            else:
                metadata_buffer = None
            self.build_command(opcode=opcode,
                               flags=flags,
                               nsid=nsid,
                               cdw2=cdw2,
                               cdw3=cdw3,
                               metadata=None if metadata_buffer is None else metadata_buffer.addr,
                               addr=None if data_buffer is None else data_buffer.addr,
                               metadata_len=0 if metadata_buffer is None else metadata_buffer.data_length,
                               data_len=0 if data_buffer is None else data_buffer.data_length,
                               cdw10=cdw10,
                               cdw11=cdw11,
                               cdw12=cdw12,
                               cdw13=cdw13,
                               cdw14=cdw14,
                               cdw15=cdw15,
                               timeout_ms=timeout)
        elif os_type == "Windows":
            self.build_command(Flags=win_nvme_command.STORAGE_PROTOCOL_COMMAND_FLAG_ADAPTER_REQUEST,
                               DataToDeviceTransferLength=data_len if dxfer_direction == NVMEDXFER.NVME_DXFER_TO_DEV.value else 0,
                               DataFromDeviceTransferLength=data_len if dxfer_direction == NVMEDXFER.NVME_DXFER_FROM_DEV.value else 0,
                               TimeOutValue=int(timeout/1000),
                               CommandSpecific=win_nvme_command.STORAGE_PROTOCOL_SPECIFIC_NVME_NVM_COMMAND,
                               OPC=opcode,
                               FUSE=(flags & 0x03),
                               NSID=nsid,
                               CDW10=cdw10,
                               CDW11=cdw11,
                               CDW12=cdw12,
                               CDW13=cdw13,
                               CDW14=cdw14,
                               CDW15=cdw15,
                               )
            if data:
                self._cdb.data_buf = data
            if metadata:
                raise ValueError("metadata is not supported on Windows")
        else:
            raise NotImplementedError("os_type %s is not supported" % os_type)
