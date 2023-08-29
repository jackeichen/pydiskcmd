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
##
NVME_MAX_LOG_SIZE = 4096
##
STORAGE_HW_FIRMWARE_REQUEST_FLAG_CONTROLLER = 1
STORAGE_HW_FIRMWARE_REQUEST_FLAG_LAST_SEGMENT = 2
STORAGE_HW_FIRMWARE_REQUEST_FLAG_FIRST_SEGMENT = 4
STORAGE_HW_FIRMWARE_REQUEST_FLAG_REPLACE_EXISTING_IMAGE = 1073741824
STORAGE_HW_FIRMWARE_REQUEST_FLAG_SWITCH_TO_EXISTING_FIRMWARE = 2147483648
STORAGE_HW_FIRMWARE_INVALID_SLOT = 255
STORAGE_HW_FIRMWARE_REVISION_LENGTH = 16


class STORAGE_SET_TYPE(Enum):
    PropertyStandardSet    = 0
    PropertyExistsSet      = 1
    PropertySetMaxDefined  = 2
##
class StoragePropertyID(Enum): 
    StorageDeviceProperty                                    = 0
    StorageAdapterProperty                                   = 1
    StorageDeviceIDProperty                                  = 2
    StorageDeviceUniqueIDProperty                            = 3
    StorageDeviceWriteCacheProperty                          = 4
    StorageMiniportProperty                                  = 5
    StorageAccessAlignmentProperty                           = 6
    StorageDeviceSeekPenaltyProperty                         = 7
    StorageDeviceTrimProperty                                = 8
    StorageDeviceWriteAggregationProperty                    = 9
    StorageDeviceDeviceTelemetryProperty                     = 10
    StorageDeviceLBProvisioningProperty                      = 11
    StorageDevicePowerProperty                               = 12
    StorageDeviceCopyOffloadProperty                         = 13
    StorageDeviceResiliencyProperty                          = 14
    StorageDeviceMediumProductType                           = 15
    StorageAdapterRpmbProperty                               = 16
    StorageAdapterCryptoProperty                             = 17
    StorageDeviceIoCapabilityProperty                        = 18
    StorageAdapterProtocolSpecificProperty                   = 19
    StorageDeviceProtocolSpecificProperty                    = 20
    StorageAdapterTemperatureProperty                        = 21
    StorageDeviceTemperatureProperty                         = 22
    StorageAdapterPhysicalTopologyProperty                   = 23
    StorageDevicePhysicalTopologyProperty                    = 24
    StorageDeviceAttributesProperty                          = 25
    StorageDeviceManagementStatus                            = 26
    StorageAdapterSerialNumberProperty                       = 27
    StorageDeviceLocationProperty                            = 28
    StorageDeviceNumaProperty                                = 29
    StorageDeviceZonedDeviceProperty                         = 30
    StorageDeviceUnsafeShutdownCount                         = 31
    StorageDeviceEnduranceProperty                           = 32

#

class STORAGE_PROTOCOL_TYPE(Enum):
    ProtocolTypeUnknown = 0x00
    ProtocolTypeScsi    = auto()
    ProtocolTypeAta     = auto()
    ProtocolTypeNvme    = auto()
    ProtocolTypeSd      = auto()

class STORAGE_PROTOCOL_SPECIFIC_NVME_COMMAND(Enum):
    ADMIN = 0x01   # STORAGE_PROTOCOL_SPECIFIC_NVME_ADMIN_COMMAND
    NVM   = 0x02   # STORAGE_PROTOCOL_SPECIFIC_NVME_NVM_COMMAND


class TStorageProtocolNVMeDataType(Enum):
    NVMeDataTypeUnknown = 0
    NVMeDataTypeIdentify = 1
    NVMeDataTypeLogPage = 2
    NVMeDataTypeFeature = 3

class NVME_FEATURES(Enum):
    NVME_FEATURE_ARBITRATION                            = 0x01,
    NVME_FEATURE_POWER_MANAGEMENT                       = 0x02,
    NVME_FEATURE_LBA_RANGE_TYPE                         = 0x03,
    NVME_FEATURE_TEMPERATURE_THRESHOLD                  = 0x04,
    NVME_FEATURE_ERROR_RECOVERY                         = 0x05,
    NVME_FEATURE_VOLATILE_WRITE_CACHE                   = 0x06,
    NVME_FEATURE_NUMBER_OF_QUEUES                       = 0x07,
    NVME_FEATURE_INTERRUPT_COALESCING                   = 0x08,
    NVME_FEATURE_INTERRUPT_VECTOR_CONFIG                = 0x09,
    NVME_FEATURE_WRITE_ATOMICITY                        = 0x0A,
    NVME_FEATURE_ASYNC_EVENT_CONFIG                     = 0x0B,
    NVME_FEATURE_AUTONOMOUS_POWER_STATE_TRANSITION      = 0x0C,
    NVME_FEATURE_HOST_MEMORY_BUFFER                     = 0x0D,
    NVME_FEATURE_TIMESTAMP                              = 0x0E,
    NVME_FEATURE_KEEP_ALIVE                             = 0x0F,
    NVME_FEATURE_HOST_CONTROLLED_THERMAL_MANAGEMENT     = 0x10,
    NVME_FEATURE_NONOPERATIONAL_POWER_STATE             = 0x11,
    #
    NVME_FEATURE_NVM_SOFTWARE_PROGRESS_MARKER           = 0x80,
    NVME_FEATURE_NVM_HOST_IDENTIFIER                    = 0x81,
    NVME_FEATURE_NVM_RESERVATION_NOTIFICATION_MASK      = 0x82,
    NVME_FEATURE_NVM_RESERVATION_PERSISTANCE            = 0x83,

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

    def dump_element(self):
        info = {}
        # check by _fields_
        for k, v in self._fields_:
            av = getattr(self, k)
            if type(v) == type(Structure):
                av = av.dump_dict()
            elif type(v) == type(Array):
                av = cast(av, c_char_p).value.decode()
            else:
                pass
            info[k] = av
        return info


class IOCTLSTORAGESETPROPERTY(Structure):
    _fields_ = [
        ("PropertyId", c_uint32),
        ("SetType", c_uint32),
        ("ProtocolType", c_uint32),
        ("DataType", c_uint32),
        ("ProtocolDataValue", c_uint32),
        ("ProtocolDataSubValue", c_uint32),
        ("ProtocolDataOffset", c_uint32),
        ("ProtocolDataLength", c_uint32),
        ("FixedProtocolReturnData", c_uint32),
        ("ProtocolDataSubValue2", c_uint32),
        ("ProtocolDataSubValue3", c_uint32),
        ("ProtocolDataSubValue4", c_uint32),
        ("ProtocolDataSubValue5", c_uint32),
        ("Reserved", c_uint32*5),
        ("DATA_DESCRIPTOR_EXT", c_uint8*NVME_MAX_LOG_SIZE)
        
    ]
    _pack_ = 1

    def __init__(
        self,
        PropertyId=StoragePropertyID.StorageAdapterProtocolSpecificProperty.value,
        SetType=STORAGE_SET_TYPE.PropertyStandardSet.value,
        ProtocolType=STORAGE_PROTOCOL_TYPE.ProtocolTypeNvme.value,
        DataType=TStorageProtocolNVMeDataType.NVMeDataTypeFeature.value,
        ProtocolDataValue=NVME_FEATURES.NVME_FEATURE_HOST_CONTROLLED_THERMAL_MANAGEMENT.value,
        CDW11=0,                     #ProtocolDataSubValue
        ProtocolDataOffset=0,
        ProtocolDataLength=0,
        CDW12=0,
        CDW13=0,
        CDW14=0,
        CDW15=0,
    ):
        self.PropertyId = PropertyId
        self.SetType = SetType
        self.ProtocolType = ProtocolType
        self.DataType = DataType
        self.ProtocolDataValue = ProtocolDataValue
        self.ProtocolDataSubValue = CDW11
        self.ProtocolDataOffset = ProtocolDataOffset
        self.ProtocolDataLength = ProtocolDataLength
        self.FixedProtocolReturnData = 0
        self.ProtocolDataSubValue2 = CDW12
        self.ProtocolDataSubValue3 = CDW13
        self.ProtocolDataSubValue4 = CDW14
        self.ProtocolDataSubValue5 = CDW15

    def dump_element(self):
        info = {}
        # check by _fields_
        for k, v in self._fields_:
            av = getattr(self, k)
            if type(v) == type(Structure):
                av = av.dump_dict()
            elif type(v) == type(Array):
                av = cast(av, c_char_p).value.decode()
            else:
                pass
            info[k] = av
        return info


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

    def dump_element(self):
        return self.nsqp.dump_element()


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

        def dump_element(self):
            return self.nsqp.dump_element()
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

    def dump_element(self):
        return self.nsqp.dump_element()


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

    def dump_element(self):
        return self.nsqp.dump_element()


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

    def dump_element(self):
        return self.nsqp.dump_element()


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
        ("Reserved1", c_uint32*3),
    ]
    _pack_ = 1

    def dump_element(self):
        info = {}
        # check by _fields_
        for k, v in self._fields_:
            av = getattr(self, k)
            if type(v) == type(Structure):
                av = av.dump_dict()
            elif type(v) == type(Array):
                av = cast(av, c_char_p).value.decode()
            else:
                pass
            info[k] = av
        return info


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

    def dump_element(self):
        info = {}
        # check by _fields_
        for k, v in self._fields_:
            av = getattr(self, k)
            if type(v) == type(Structure):
                av = av.dump_dict()
            elif type(v) == type(Array):
                av = cast(av, c_char_p).value.decode()
            else:
                pass
            info[k] = av
        return info


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

    def dump_element(self):
        info = self.spch.dump_element()
        info["nvme_command"] = self.nvme_command.dump_element()
        return info


class STORAGE_HW_FIRMWARE_DOWNLOAD(Structure):
    _fields_ = [
        ("Version", c_uint32),
        ("Size", c_uint32),
        ("Flags", c_uint32),
        ("Slot", c_uint8),
        ("Reserved", c_uint8 * 3),
        ("Offset", c_uint64),
        ("BufferSize", c_uint64),
        ("ImageBuffer", POINTER(c_ubyte)),
    ]
    _pack_ = 1

    def __init__(self,
                 Flags,
                 Slot,
                 Offset,
                 data,
                 ):
        self.Version = 32 # wait to verify? The version of this structure. This should be set to sizeof(STORAGE_HW_FIRMWARE_DOWNLOAD).
        self.Size = 0         #   The size of this structure and the download image buffer.
        self.Flags = Flags      # Flags associated with this download. The following are valid flags that this member can hold.
        self.Slot = Slot        # The slot number that the firmware image will be downloaded to.
        self.Offset = Offset    # The offset in this buffer of where the Image file begins. This should be aligned to ImagePayloadAlignment from STORAGE_HW_FIRMWARE_INFO.
        self.BufferSize = 0      # The buffer size of the ImageBuffer. This should be a multiple of ImagePayloadAlignment from STORAGE_HW_FIRMWARE_INFO.
        self.set_data(data)      #

    def set_data(self, value):
        if not isinstance(value, (bytes,)):
            raise ValueError("Bytes expected.")
        self.ImageBuffer = cast(value, POINTER(c_ubyte))
        self.BufferSize = len(value)
        self.Size = self.Version + self.BufferSize

    def dump_element(self):
        info = {}
        # check by _fields_
        for k, v in self._fields_:
            av = getattr(self, k)
            if type(v) == type(Structure):
                av = av.dump_dict()
            elif type(v) == type(Array):
                av = cast(av, c_char_p).value.decode()
            else:
                pass
            info[k] = av
        return info


class STORAGE_HW_FIRMWARE_ACTIVATE(Structure):
    _fields_ = [
        ("Version", c_uint32),
        ("Size", c_uint32),
        ("Flags", c_uint32),
        ("Slot", c_uint8),
        ("Reserved0", c_uint8 * 3),
    ]
    _pack_ = 1
    def __init__(self,
                 Flags,
                 Slot,
                 ):
        self.Version = 16  # The version of this structure. This should be set to sizeof(STORAGE_HW_FIRMWARE_ACTIVATE).
        self.Size = 16     # The size of this structure. This should be set to sizeof(STORAGE_HW_FIRMWARE_ACTIVATE).
        self.Flags = Flags # The flags associated with the activation request. The following are valid flags that can be set in this member.
        self.Slot = Slot   # The slot with the firmware image that is to be activated.

    def dump_element(self):
        info = {}
        # check by _fields_
        for k, v in self._fields_:
            av = getattr(self, k)
            if type(v) == type(Structure):
                av = av.dump_dict()
            elif type(v) == type(Array):
                av = cast(av, c_char_p).value.decode()
            else:
                pass
            info[k] = av
        return info
