# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from enum import Enum
from pydiskcmdlib import os_type
from pydiskcmdlib.pynvme.nvme_command import NVMeCommand,AdminCommandOpcode,CommandTimeout
from pydiskcmdlib.pynvme import linux_nvme_command,win_nvme_command
#####
CmdOPCode = AdminCommandOpcode.Identify.value
#####
class CNSValue(Enum):
    IdentifyNamespace                = 0x00
    IdentifyController               = 0x01
    ActiveNamespaceID                = 0x02
    NamespaceIdentificationDescriptor= 0x03
    NVMSetList                       = 0x04
    AllocatedNamespaceID             = 0x10
    IdentifyNamespaceOfAllocated     = 0x11
    AttachedControllerList           = 0x12
    ExistControllerList              = 0x13
    PrimaryControllerCapabilities    = 0x14
    SecondaryControllerList          = 0x15
    NamespaceGranularityList         = 0x16
    UUIDList                         = 0x17
#####
class Identify(NVMeCommand):
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
                     "cns": [0xFF, 40],
                     "cntid": [0xFFFF, 42],
                     #"cdw11":[0xFFFFFFFF, 44],
                     "nvmsetid": [0xFFFF, 44],
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
                     "cns":  [0xFFFFFFFF, 16],  # ProtocolDataRequestValue Field
                     # "ProtocolDataRequestSubValue": [0xFFFFFFFF, 20],
                     "nsid": [0xFFFFFFFF, 20], # ProtocolDataRequestSubValue,
                     "ProtocolDataOffset": [0xFFFFFFFF, 24],
                     "ProtocolDataLength": [0xFFFFFFFF, 28],
                     "FixedProtocolReturnData": [0xFFFFFFFF, 32],
                     "ProtocolDataRequestSubValue2": [0xFFFFFFFF, 36],
                     "ProtocolDataRequestSubValue3": [0xFFFFFFFF, 40],
                     "ProtocolDataRequestSubValue4": [0xFFFFFFFF, 44],
                     "Reserved": [0xFFFFFFE0, 44],
                    }

    def __init__(self,
                 nsid,    # Namespace ID
                 cns,     # CDW10: 
                 cntid,
                 nvmsetid,
                 uuid,
                 data_length=4096,
                 data_buffer=None,
                 timeout=CommandTimeout.admin.value,
                 ):
        '''
        Some ways to set Data buffer, the priority is:
        1. Set the data_buffer/metadata_buffer, DataBuffer of the target data;
        2. If set the data_out/metadata_out, data_length/metadata_length is need;
        3. Set the data_length/metadata_length, then a 0 based buffer is created
        '''
        super(Identify, self).__init__()
        if os_type == "Linux":
            ## init data buffer
            data_buffer = self.init_data_buffer(data_length=data_length, data_buffer=data_buffer)
            ##
            self.build_command(opcode=CmdOPCode,
                               nsid=nsid,
                               addr=data_buffer.addr,
                               data_len=data_buffer.data_length,
                               cns=cns,
                               cntid=cntid,
                               nvmsetid=nvmsetid,
                               uuid=uuid,
                               timeout_ms=timeout)
        elif os_type == "Windows":
            self.build_command(PropertyId=win_nvme_command.StoragePropertyID.StorageAdapterProtocolSpecificProperty.value,
                               QueryType=win_nvme_command.StorageQueryType.PropertyStandardQuery.value,
                               ProtocolType=win_nvme_command.StroageProtocolType.ProtocolTypeNvme.value,
                               DataType=win_nvme_command.StorageProtocolNVMeDataType.NVMeDataTypeIdentify.value,
                               ProtocolDataOffset=win_nvme_command.sizeof(win_nvme_command.StorageProtocolSpecificData),
                               ProtocolDataLength=data_length,
                               cns=cns,
                               nsid=nsid,
                               )


class IDNS(Identify):
    def __init__(self, nsid, uuid=0):
        Identify.__init__(self,
                          nsid,  # nsid
                          CNSValue.IdentifyNamespace.value,  # cns
                          0,  # cntid
                          0,  # nvmsetid
                          uuid,  # uuid
                          data_length=4096,
                          )


class IDCtrl(Identify):
    def __init__(self, uuid=0):
        Identify.__init__(self,
                          0,  # nsid
                         CNSValue.IdentifyController.value,  # cns
                          0,  # cntid
                          0,  # nvmsetid
                          uuid,  # uuid
                          data_length=4096,
                          )


class IDActiveNS(Identify):
    def __init__(self, nsid):
        Identify.__init__(self,
                          nsid,  # nsid
                          CNSValue.ActiveNamespaceID.value,  # cns
                          0,  # cntid
                          0,  # nvmsetid
                          0,  # uuid
                          data_length=4096,
                          )

class IDAllocatedNS(Identify):
    def __init__(self, nsid):
        Identify.__init__(self,
                          nsid,  # nsid
                          CNSValue.AllocatedNamespaceID.value,  # cns
                          0,  # cntid
                          0,  # nvmsetid
                          0,  # uuid
                          data_length=4096,
                          )


class IDCtrlListAttachedToNS(Identify):
    def __init__(self, nsid, cnt_id):
        Identify.__init__(self,
                          nsid,  # nsid
                          CNSValue.AttachedControllerList.value,  # cns
                          cnt_id,  # cntid
                          0,  # nvmsetid
                          0,  # uuid
                          data_length=4096,
                          )


class IDCtrlListInSubsystem(Identify):
    def __init__(self, cnt_id):
        Identify.__init__(self,
                          0,  # nsid
                          CNSValue.ExistControllerList.value,  # cns
                          cnt_id,  # cntid
                          0,  # nvmsetid
                          0,  # uuid
                          data_length=4096,
                          )


class UUIDList(Identify):
    def __init__(self):
        Identify.__init__(self,
                          0,  # nsid
                          CNSValue.UUIDList.value,  # cns
                          0,  # cntid
                          0,  # nvmsetid
                          0,  # uuid
                          data_length=4096,
                          )
