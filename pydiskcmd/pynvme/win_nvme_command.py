# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from ctypes import *
from enum import Enum,auto
from pydiskcmd.exceptions import CommandNotSupport

## 
NVMeStorageQueryPropertyID = 50          # StorageDeviceProtocolSpecificProperty
NVMeStorageQueryPropertyQueryType = 0    # PropertyStandardQuery
NVMeStorageQueryPropertyProtocolType = 3 # ProtocolTypeNvme
NVMeStorageQueryPropertyDataType = 2     # NVMeDataTypeLogPage

STORAGE_PROTOCOL_COMMAND_FLAG_ADAPTER_REQUEST = 0x80000000
STORAGE_PROTOCOL_COMMAND_LENGTH_NVME = 0x40 # 64 bytes nvme command structure
STORAGE_PROTOCOL_STRUCTURE_VERSION = 0x1

class STORAGE_PROTOCOL_TYPE(Enum):
	ProtocolTypeUnknown = 0x00
	ProtocolTypeScsi    = auto()
	ProtocolTypeAta     = auto()
	ProtocolTypeNvme    = auto()
	ProtocolTypeSd      = auto()

class STORAGE_PROTOCOL_SPECIFIC_NVME_COMMAND(Enum):
    ADMIN = 0x01   # STORAGE_PROTOCOL_SPECIFIC_NVME_ADMIN_COMMAND
    NVM   = 0x02   # STORAGE_PROTOCOL_SPECIFIC_NVME_NVM_COMMAND

##
# https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddstor/ne-ntddstor-_storage_protocol_nvme_data_type
##

class NVMeStorageQueryPropertyHeader(Structure):
    _fields_ = [
        ("PropertyId", c_uint32),
        ("QueryType", c_uint32),
        ("ProtocolType", c_uint32),
        ("DataType", c_uint32),
        ("ProtocolDataRequestValue", c_uint32),
        ("ProtocolDataRequestSubValue", c_uint32),
        ("ProtocolDataOffset", c_uint32),
        ("ProtocolDataLength", c_uint32),
        ("FixedProtocolReturnData", c_uint32),
        ("ProtocolDataRequestSubValue2", c_uint32),
        ("ProtocolDataRequestSubValue3", c_uint32),
        ("ProtocolDataRequestSubValue4", c_uint32),
        ##c_ubyte * 4
        #("CSEDataAdmin", c_ubyte*1024),
        #("CSEDataIO", c_ubyte*1024),
        #("Reserved1", c_ubyte*2048),
    ]
    _pack_ = 1

    def __init__(
        self,
        PropertyId=0,
        QueryType=0,
        ProtocolType=3,
        DataType=0,
        RequestValue=0,
        RequestSubValue=0,
        ProtocolDataOffset=40,
        ProtocolDataLength=0,
        RequestSubValue2=0,
        RequestSubValue3=0,
        RequestSubValue4=0,
    ):
        self.PropertyId = PropertyId
        self.QueryType = QueryType
        self.ProtocolType = ProtocolType
        self.DataType = DataType
        self.ProtocolDataRequestValue = RequestValue
        self.ProtocolDataRequestSubValue = RequestSubValue
        self.ProtocolDataOffset = ProtocolDataOffset
        self.ProtocolDataLength = ProtocolDataLength
        self.FixedProtocolReturnData = 0
        self.ProtocolDataRequestSubValue2 = RequestSubValue2
        self.ProtocolDataRequestSubValue3 = RequestSubValue3
        self.ProtocolDataRequestSubValue4 = RequestSubValue4


class NVMeStorageQueryPropertyWithoutBuffer(Structure):
    _fields_ = [
        ('nsqp', NVMeStorageQueryPropertyHeader),
    ]

    _pack_ = 1

    def __init__(self, **kwargs):
        self.nsqp = NVMeStorageQueryPropertyHeader(**kwargs)

    @property
    def _data_buf(self):
        return None
    
    @property
    def _metadata_buf(self):
        return None

    @property
    def result(self):
        return self.nsqp.FixedProtocolReturnData


def get_NVMeStorageQueryPropertyWithBuffer(data_len):
    class NVMeStorageQueryPropertyWithBuffer(Structure):
        _fields_ = [
            ('nsqp', NVMeStorageQueryPropertyHeader),
            ('raw_data', c_ubyte * data_len)
        ]
        _pack_ = 1

        def __init__(self, **kwargs):
            self.nsqp = NVMeStorageQueryPropertyHeader(**kwargs)

        @property
        def _data_buf(self):
            return self.raw_data
        
        @property
        def _metadata_buf(self):
            return None

        @property
        def result(self):
            return self.nsqp.FixedProtocolReturnData
    return NVMeStorageQueryPropertyWithBuffer


class NVMeStorageQueryPropertyWithBuffer512(Structure):
    _fields_ = [
        ('nsqp', NVMeStorageQueryPropertyHeader),
        ('raw_data', c_ubyte * 512)
    ]

    _pack_ = 1

    def __init__(self, **kwargs):
        self.nsqp = NVMeStorageQueryPropertyHeader(**kwargs)

    @property
    def _data_buf(self):
        return self.raw_data
    
    @property
    def _metadata_buf(self):
        return None

    @property
    def result(self):
        return self.nsqp.FixedProtocolReturnData


class NVMeStorageQueryPropertyWithBuffer564(Structure):
    _fields_ = [
        ('nsqp', NVMeStorageQueryPropertyHeader),
        ('raw_data', c_ubyte * 564)
    ]

    _pack_ = 1

    def __init__(self, **kwargs):
        self.nsqp = NVMeStorageQueryPropertyHeader(**kwargs)

    @property
    def _data_buf(self):
        return self.raw_data

    @property
    def _metadata_buf(self):
        return None

    @property
    def result(self):
        return self.nsqp.FixedProtocolReturnData


class NVMeStorageQueryPropertyWithBuffer4096(Structure):
    _fields_ = [
        ('nsqp', NVMeStorageQueryPropertyHeader),
        ('raw_data', c_ubyte * 4096)
    ]

    _pack_ = 1

    def __init__(self, **kwargs):
        self.nsqp = NVMeStorageQueryPropertyHeader(**kwargs)

    @property
    def _data_buf(self):
        return self.raw_data

    @property
    def _metadata_buf(self):
        return None

    @property
    def result(self):
        return self.nsqp.FixedProtocolReturnData


class StorageProtocolCommandHeader(Structure):
    _fields_ = [
        ("Version", c_uint32),
        ("Length", c_uint32),
        ("ProtocolType", c_uint32),
        ("Flags", c_uint32),
        ("ReturnStatus", c_uint32),
        ("ErrorCode", c_uint32),
        ("CommandLength", c_uint32),
        ("ErrorInfoLength", c_uint32),
        ("DataToDeviceTransferLength", c_uint32),
        ("DataFromDeviceTransferLength", c_uint32),
        ("TimeOutValue", c_uint32),
        ("ErrorInfoOffset", c_uint32),
        ("DataToDeviceBufferOffset", c_uint32),
        ("DataFromDeviceBufferOffset", c_uint32),
        ("CommandSpecific", c_uint32),
        ("Reserved0", c_uint32),
        ("FixedProtocolReturnData", c_uint32),
        ("Reserved1_0", c_uint32),
        ("Reserved1_1", c_uint32),
        ("Reserved1_2", c_uint32),
    ]
    _pack_ = 1


class NVMECommand(Structure):
    _fields_ = [
        ("opcode", c_uint8),
        ("flags", c_uint8),
        ("cid", c_uint16),
        ("nsid", c_uint32),
        ("reserved0_0", c_uint32),
        ("reserved0_1", c_uint32),
        ("MPTR", c_uint64),
        ("PRP1", c_uint64),
        ("PRP2", c_uint64),
        ("cdw10", c_uint32),
        ("cdw11", c_uint32),
        ("cdw12", c_uint32),
        ("cdw13", c_uint32),
        ("cdw14", c_uint32),
        ("cdw15", c_uint32),
    ]
    _pack_ = 1

    def __init__(
        self,
        opcode=0,  ## opcode
        flags=0,   ## Fused Operation
        cid=0,
        nsid=0,    ## Namespace Identifier
        reserved0_0=0,
        reserved0_1=0,
        MPTR=0,    ## Reserved
        PRP1=0,    ## Reserved
        PRP2=0,    ## Reserved
        cdw10=0,   ## cdw10
        cdw11=0,   ## cdw11
        cdw12=0,   ## cdw12
        cdw13=0,   ## cdw13
        cdw14=0,   ## cdw14
        cdw15=0,   ## cdw15
    ):
        self.opcode = c_uint8(opcode)
        self.flags = c_uint8(flags)
        self.cid = c_uint16(cid)
        self.nsid = c_uint32(nsid)
        self.reserved0_0 = c_uint32(reserved0_0)
        self.reserved0_1 = c_uint32(reserved0_1)
        self.MPTR = MPTR
        self.PRP1 = PRP1
        self.PRP2 = PRP2
        self.cdw10 = c_uint32(cdw10)
        self.cdw11 = c_uint32(cdw11)
        self.cdw12 = c_uint32(cdw12)
        self.cdw13 = c_uint32(cdw13)
        self.cdw14 = c_uint32(cdw14)
        self.cdw15 = c_uint32(cdw15)


class StorageProtocolCommand(Structure):
    _fields_ = [
        ('spch', StorageProtocolCommandHeader),
        ('nvme_command', NVMECommand),
    ]
    _pack_ = 1

    def __init__(self,
                 h_version=0,
                 h_flags=0,
                 h_error_info_length=0,
                 h_d2d_transfer_length=0,
                 h_dfd_transfer_length=0,
                 h_timeout=10,
                 h_error_info_offset=0,
                 h_d2d_buffer_offset=0,
                 h_dfd_buffer_offset=0,
                 h_command_spec=0,
                 **kwargs,  # NVMECommand init value: 
                 ):
        raise CommandNotSupport("StorageProtocolCommand Is Not Ready!")
        self.spch.Version = h_version  # STORAGE_PROTOCOL_STRUCTURE_VERSION
        self.spch.Length = sizeof(StorageProtocolCommandHeader)
        self.spch.ProtocolType = STORAGE_PROTOCOL_TYPE.ProtocolTypeNvme.value #ProtocolTypeNvme
        self.spch.Flags = h_flags
        self.spch.ReturnStatus = 0
        self.spch.ErrorCode = 0
        self.spch.CommandLength = sizeof(NVMECommand)
        self.spch.ErrorInfoLength = h_error_info_length
        self.spch.DataToDeviceTransferLength = h_d2d_transfer_length
        self.spch.DataFromDeviceTransferLength = h_dfd_transfer_length
        self.spch.TimeOutValue = h_timeout
        self.spch.ErrorInfoOffset = h_error_info_offset
        self.spch.DataToDeviceBufferOffset = h_d2d_buffer_offset
        self.spch.DataFromDeviceBufferOffset = h_dfd_buffer_offset
        self.spch.CommandSpecific = h_command_spec
        self.spch.Reserved0 = 0
        self.spch.FixedProtocolReturnData = 0
        self.spch.Reserved1_0 = 0
        self.spch.Reserved1_1 = 0
        self.spch.Reserved1_2 = 0
        self.nvme_command = NVMECommand(**kwargs)

    @property
    def _data_buf(self):
        ## TODO.
        return None

    @property
    def _metadata_buf(self):
        ## TODO.
        return None

    @property
    def result(self):
        return self.spch.FixedProtocolReturnData

