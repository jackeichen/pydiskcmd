# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmdlib import os_type
from pydiskcmdlib.pynvme.nvme_command import NVMeCommand,AdminCommandOpcode,CommandTimeout
from pydiskcmdlib.pynvme import linux_nvme_command,win_nvme_command
#####
CmdOPCode = AdminCommandOpcode.GetFeature.value
#####
class GetFeature(NVMeCommand):
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
                     "sel": [0x07, 41],
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
        _req_id = win_nvme_command.IOCTLRequest.IOCTL_STORAGE_QUERY_PROPERTY.value
        _cdb_bits = {"PropertyId": [0xFFFFFFFF, 0],
                     "QueryType": [0xFFFFFFFF, 4],
                     "ProtocolType": [0xFFFFFFFF, 8],
                     "DataType": [0xFFFFFFFF, 12],
                     # "ProtocolDataRequestValue": [0xFFFFFFFF, 16],
                     "fid": [0xFF, 16],  # ProtocolDataRequestValue Field
                     "sel": [0x07, 17],
                     # "ProtocolDataRequestSubValue": [0xFFFFFFFF, 20],
                     "cdw11": [0xFFFFFFFF, 20],
                     "ProtocolDataOffset": [0xFFFFFFFF, 24],
                     "ProtocolDataLength": [0xFFFFFFFF, 28],
                     "FixedProtocolReturnData": [0xFFFFFFFF, 32],
                     "ProtocolDataRequestSubValue2": [0xFFFFFFFF, 36],
                     "ProtocolDataRequestSubValue3": [0xFFFFFFFF, 40],
                     "ProtocolDataRequestSubValue4": [0xFFFFFFFF, 44],
                    }

    def __init__(self, 
                 feature_id, 
                 nsid=0, 
                 sel=0, 
                 uuid_index=0, 
                 cdw11=0, 
                 data_len=0):
        super(GetFeature, self).__init__()
        if os_type == "Linux":
            # init data buffer
            datain_buffer = self.init_data_buffer(data_length=data_len)
            self.build_command(opcode=CmdOPCode,
                               nsid=nsid,
                               addr=datain_buffer.addr if datain_buffer else 0,
                               data_len=data_len,
                               fid=feature_id,
                               sel=sel,
                               cdw11=cdw11,
                               uuid=uuid_index,
                               timeout_ms=CommandTimeout.admin.value,)
        elif os_type == "Windows":
            self.build_command(PropertyId=win_nvme_command.StoragePropertyID.StorageDeviceProtocolSpecificProperty.value,
                               QueryType=win_nvme_command.StorageQueryType.PropertyStandardQuery.value,
                               ProtocolType=win_nvme_command.StroageProtocolType.ProtocolTypeNvme.value,
                               DataType=win_nvme_command.StorageProtocolNVMeDataType.NVMeDataTypeFeature.value,
                               ProtocolDataOffset=0,
                               ProtocolDataLength=0,
                               fid=feature_id,
                               sel=sel,
                               cdw11=cdw11,
                               )
