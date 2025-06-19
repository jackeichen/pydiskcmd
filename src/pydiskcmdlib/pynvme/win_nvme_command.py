# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from ctypes import (Structure,
                    Union,
                    c_uint8,
                    c_uint16,
                    c_uint32,
                    c_uint64,
                    c_ubyte,
                    sizeof,
                    c_ulonglong,
                    )
from enum import Enum,auto
from pydiskcmdlib.pyscsi.win_scsi_structures import (
    SCSIPassThroughDirectWithBuffer,
    SCSIPassThroughDirectWithBufferEx,
)
##
from pydiskcmdlib.os.win_ioctl_request import IOCTLRequest    # used by pynvme, Do Not delete
from pydiskcmdlib.os.win_ioctl_structures import (
    SRB_IO_CONTROL,
    FIRMWARE_REQUEST_BLOCK,
    STORAGE_FIRMWARE_DOWNLOAD,
    STORAGE_FIRMWARE_ACTIVATE,
)
from pydiskcmdlib.os.win_ioctl_utils import (
    IOCTL_SCSI_MINIPORT_FIRMWARE,       # Do Not Delete
    IOCTL_MINIPORT_SIGNATURE_FIRMWARE,  # Do Not Delete
    FIRMWARE_REQUEST_BLOCK_STRUCTURE_VERSION,
    FIRMWARE_REQUEST_FLAG_CONTROLLER,
    FIRMWARE_FUNCTION,
    FIRMWARE_STATUS,
)
##
from pydiskcmdlib.utils.converter import decode_bits
##
cdb_bitmap = {IOCTLRequest.IOCTL_STORAGE_QUERY_PROPERTY.value: {
                "PropertyId": [0xFFFFFFFF, 0],
                "QueryType": [0xFFFFFFFF, 4],
                "ProtocolType": [0xFFFFFFFF, 8],
                "DataType": [0xFFFFFFFF, 12],
                "ProtocolDataRequestValue": [0xFFFFFFFF, 16],
                "ProtocolDataRequestSubValue": [0xFFFFFFFF, 20],
                "ProtocolDataOffset": [0xFFFFFFFF, 24],
                "ProtocolDataLength": [0xFFFFFFFF, 28],
                "FixedProtocolReturnData": [0xFFFFFFFF, 32],
                "ProtocolDataRequestSubValue2": [0xFFFFFFFF, 36],
                "ProtocolDataRequestSubValue3": [0xFFFFFFFF, 40],
                "ProtocolDataRequestSubValue4": [0xFFFFFFFF, 44],
                },
              IOCTLRequest.IOCTL_STORAGE_PROTOCOL_COMMAND.value: {
                "Version": [0xFFFFFFFF, 0],
                "Length": [0xFFFFFFFF, 4],
                "ProtocolType": [0xFFFFFFFF, 8],
                "Flags": [0xFFFFFFFF, 12],
                "ReturnStatus": [0xFFFFFFFF, 16],
                "ErrorCode": [0xFFFFFFFF, 20],
                "CommandLength": [0xFFFFFFFF, 24],
                "ErrorInfoLength": [0xFFFFFFFF, 28],
                "DataToDeviceTransferLength": [0xFFFFFFFF, 32],
                "DataFromDeviceTransferLength": [0xFFFFFFFF, 36],
                "TimeOutValue": [0xFFFFFFFF, 40],
                "ErrorInfoOffset": [0xFFFFFFFF, 44],
                "DataToDeviceBufferOffset": [0xFFFFFFFF, 48],
                "DataFromDeviceBufferOffset": [0xFFFFFFFF, 52],
                "CommandSpecific": [0xFFFFFFFF, 56],
                "Reserved0": [0xFFFFFFFF, 60],
                "FixedProtocolReturnData": [0xFFFFFFFF, 64],
                #"Reserved1": [0xFFFFFFFFFFFFFFFFFFFFFFFF, 68], # 68 + 3 * 4 = 80
                "OPC": [0xFF, 80],
                "FUSE": [0x03, 81],
                "Reserved0": [0x7C, 81],
                "PSDT": [0x80, 81],
                "CID": [0xFFFF, 82],
                "NSID": [0xFFFFFFFF, 84],
                # "Reserved0": [0xFFFFFFFFFFFFFFFF, 88],
                "MPTR": [0xFFFFFFFFFFFFFFFF, 96],
                "PRP1": [0xFFFFFFFFFFFFFFFF, 104],
                "PRP2": [0xFFFFFFFFFFFFFFFF, 112],
                "CDW10": [0xFFFFFFFF, 120],
                "CDW11": [0xFFFFFFFF, 124],
                "CDW12": [0xFFFFFFFF, 128],
                "CDW13": [0xFFFFFFFF, 132],
                "CDW14": [0xFFFFFFFF, 136],
                "CDW15": [0xFFFFFFFF, 140],
                },
              IOCTLRequest.IOCTL_STORAGE_SET_PROPERTY.value: {
                "PropertyId": [0xFFFFFFFF, 0],
                "SetType": [0xFFFFFFFF, 4],
                "ProtocolType": [0xFFFFFFFF, 8],
                "DataType":[0xFFFFFFFF, 12],
                "ProtocolDataValue":[0xFFFFFFFF, 16],
                "ProtocolDataSubValue":[0xFFFFFFFF, 20],  # This will pass to CDW11
                "ProtocolDataOffset":[0xFFFFFFFF, 24],
                "ProtocolDataLength":[0xFFFFFFFF, 28],
                "FixedProtocolReturnData":[0xFFFFFFFF, 32],
                "ProtocolDataRequestSubValue2":[0xFFFFFFFF, 36],  # This will pass to CDW12
                "ProtocolDataRequestSubValue3":[0xFFFFFFFF, 40],  # This will pass to CDW13
                "ProtocolDataRequestSubValue4":[0xFFFFFFFF, 44],  # This will pass to CDW14
                "ProtocolDataRequestSubValue5":[0xFFFFFFFF, 48],  # This will pass to CDW15
                "Reserved_0":[0xFFFFFFFF, 52],
                "Reserved_1":[0xFFFFFFFF, 56],
                "Reserved_2":[0xFFFFFFFF, 60],
                "Reserved_3":[0xFFFFFFFF, 64],
                "Reserved_4":[0xFFFFFFFF, 68],
                "data": ['b', 72, 0],
                },
             }
##
SRB_IO_CONTROL_LEN = sizeof(SRB_IO_CONTROL)
NVME_PT_TIMEOUT = 40
SCSI_FIRMWARE_TIMEOUT = 30
## 
STORAGE_PROTOCOL_COMMAND_FLAG_ADAPTER_REQUEST = 0x80000000
STORAGE_PROTOCOL_COMMAND_LENGTH = 0x54   # sizeof(STORAGE_PROTOCOL_COMMAND) = 84
STORAGE_PROTOCOL_COMMAND_LENGTH_NVME = 0x40 # 64 bytes nvme command structure
STORAGE_PROTOCOL_STRUCTURE_VERSION = 0x1
STORAGE_PROTOCOL_SPECIFIC_NVME_ADMIN_COMMAND = 0x01
STORAGE_PROTOCOL_SPECIFIC_NVME_NVM_COMMAND = 0x02
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
##

class STORAGE_SET_TYPE(Enum):
    PropertyStandardSet    = 0
    PropertyExistsSet      = 1
    PropertySetMaxDefined  = 2
###########
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
    # StorageDeviceIoCapabilityProperty                        = 18
    # StorageAdapterProtocolSpecificProperty                   = 19
    # StorageDeviceProtocolSpecificProperty                    = 20
    # StorageAdapterTemperatureProperty                        = 21
    # StorageDeviceTemperatureProperty                         = 22
    # StorageAdapterPhysicalTopologyProperty                   = 23
    # StorageDevicePhysicalTopologyProperty                    = 24
    # StorageDeviceAttributesProperty                          = 25
    # StorageDeviceManagementStatus                            = 26
    # StorageAdapterSerialNumberProperty                       = 27
    # StorageDeviceLocationProperty                            = 28
    # StorageDeviceNumaProperty                                = 29
    # StorageDeviceZonedDeviceProperty                         = 30
    # StorageDeviceUnsafeShutdownCount                         = 31
    # StorageDeviceEnduranceProperty                           = 32
    StorageDeviceIoCapabilityProperty                        = 48
    StorageAdapterProtocolSpecificProperty                   = 49
    StorageDeviceProtocolSpecificProperty                    = 50
    StorageAdapterTemperatureProperty                        = 51
    StorageDeviceTemperatureProperty                         = 52
    StorageAdapterPhysicalTopologyProperty                   = 53
    StorageDevicePhysicalTopologyProperty                    = 54
    StorageDeviceAttributesProperty                          = 55
    StorageDeviceManagementStatus                            = 56
    StorageAdapterSerialNumberProperty                       = 57
    StorageDeviceLocationProperty                            = 58
    StorageDeviceNumaProperty                                = 59
    StorageDeviceZonedDeviceProperty                         = 60
    StorageDeviceUnsafeShutdownCount                         = 61
    StorageDeviceEnduranceProperty                           = 62

class StorageQueryType(Enum):
    PropertyStandardQuery   = 0
    PropertyExistsQuery     = 1
    PropertyMaskQuery       = 2
    PropertyQueryMaxDefined = 3

class StroageProtocolType(Enum):
    ProtocolTypeUnknown     = 0x00
    ProtocolTypeScsi        = auto()
    ProtocolTypeAta         = auto()
    ProtocolTypeNvme        = auto()
    ProtocolTypeSd          = auto()
    ProtocolTypeProprietary = 0x7E
    ProtocolTypeMaxReserved = 0x7F

class StorageProtocolNVMeDataType(Enum):
    NVMeDataTypeUnknown  = 0
    NVMeDataTypeIdentify = 1
    NVMeDataTypeLogPage  = 2
    NVMeDataTypeFeature  = 3
    UnusedMaxValue       = 4

class NvmeIdentifyCnsCode(Enum):
    NVME_IDENTIFY_CNS_SPECIFIC_NAMESPACE = 0
    NVME_IDENTIFY_CNS_CONTROLLER = 1
    NVME_IDENTIFY_CNS_ACTIVE_NAMESPACES = 2 # A list of up to 1024 active namespace IDs is returned to the host containing active namespaces with a namespace identifier greater than the value specified in the Namespace Identifier (CDW1.NSID) field.

class StorageProtocalSpecificNVMECommand(Enum):
    ADMIN = 0x01   # STORAGE_PROTOCOL_SPECIFIC_NVME_ADMIN_COMMAND
    NVM   = 0x02   # STORAGE_PROTOCOL_SPECIFIC_NVME_NVM_COMMAND


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
class StoragePropertyQuery(Structure):
    """
    https://learn.microsoft.com/en-us/windows/win32/api/winioctl/ns-winioctl-storage_property_query
    """
    _fields_ = [
        ("PropertyId", c_uint32),
        ("QueryType", c_uint32),
    ]
    _pack_ = 1

    def __init__(
        self,
        PropertyId: int,
        QueryType: int,
    ):
        self.PropertyId = PropertyId
        self.QueryType = QueryType

class StorageProtocolSpecificData(Structure):
    """
    https://learn.microsoft.com/en-us/windows/win32/api/winioctl/ns-winioctl-storage_protocol_specific_data
    """
    _fields_ = [
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
    ]
    _pack_ = 1

    def __init__(
        self,
        ProtocolType: int,
        DataType: int,
        ProtocolDataRequestValue: int,
        ProtocolDataRequestSubValue: int,
        ProtocolDataOffset: int,
        ProtocolDataLength: int,
        FixedProtocolReturnData: int,
        ProtocolDataRequestSubValue2: int,
        ProtocolDataRequestSubValue3: int,
        ProtocolDataRequestSubValue4: int,
    ):
        self.ProtocolType = ProtocolType
        self.DataType = DataType
        self.ProtocolDataRequestValue = ProtocolDataRequestValue
        self.ProtocolDataRequestSubValue = ProtocolDataRequestSubValue
        self.ProtocolDataOffset = ProtocolDataOffset
        self.ProtocolDataLength = ProtocolDataLength
        self.FixedProtocolReturnData = FixedProtocolReturnData
        self.ProtocolDataRequestSubValue2 = ProtocolDataRequestSubValue2
        self.ProtocolDataRequestSubValue3 = ProtocolDataRequestSubValue3
        self.ProtocolDataRequestSubValue4 = ProtocolDataRequestSubValue4


class StorageQueryWithoutBuffer(Structure):
    _fields_ = [
        ('query', StoragePropertyQuery),
        ('protocol_specific', StorageProtocolSpecificData),
    ]
    _pack_ = 1

    def __init__(self, 
                 PropertyId,
                 QueryType,
                 *args,
                ):
        self.query = StoragePropertyQuery(PropertyId, QueryType)
        self.protocol_specific = StorageProtocolSpecificData(*args)

    @property
    def command_buf(self):
        return self

    @property
    def data_buf(self):
        return None

    @property
    def data_len(self):
        return 0

    @property
    def metadata_buf(self):
        return None

    @property
    def result(self):
        return self.protocol_specific.FixedProtocolReturnData

    def dump_element(self):
        return {}


class STORAGE_PROTOCOL_DATA_DESCRIPTOR(Structure):
    _fields_ = [
        ('Version', c_uint32),
        ('Size', c_uint32),
        ('protocol_specific', StorageProtocolSpecificData),
    ]
    _pack_ = 1


def GetStorageQueryWithBuffer(buffer_len:int):
    class StorageQueryWithBuffer(Structure):
        _fields_ = [
            ('query_without_buffer', StorageQueryWithoutBuffer),
            ('data_buffer', c_ubyte * buffer_len)
        ]
        _pack_ = 1

        def __init__(self, 
                     PropertyId: int = 0,
                     QueryType: int = StorageQueryType.PropertyStandardQuery.value,
                     ProtocolType: int = StroageProtocolType.ProtocolTypeNvme.value,
                     DataType: int = 0,
                     ProtocolDataRequestValue: int = 0,
                     ProtocolDataRequestSubValue: int = 0,
                     ProtocolDataOffset: int = sizeof(StorageProtocolSpecificData),
                     ProtocolDataLength: int = buffer_len,
                     FixedProtocolReturnData: int = 0,
                     ProtocolDataRequestSubValue2: int = 0,
                     ProtocolDataRequestSubValue3: int = 0,
                     ProtocolDataRequestSubValue4: int = 0,
                     **kwargs, ## ignore the invalid key-value
                     ):
            self.query_without_buffer = StorageQueryWithoutBuffer(PropertyId,
                                                                  QueryType,
                                                                  ProtocolType,
                                                                  DataType,
                                                                  ProtocolDataRequestValue,
                                                                  ProtocolDataRequestSubValue,
                                                                  ProtocolDataOffset,
                                                                  ProtocolDataLength,
                                                                  FixedProtocolReturnData,
                                                                  ProtocolDataRequestSubValue2,
                                                                  ProtocolDataRequestSubValue3,
                                                                  ProtocolDataRequestSubValue4,
                                                                  )

        @property
        def command_buf(self):
            return self.query_without_buffer

        @property
        def data_buf(self):
            return self.data_buffer

        @property
        def data_len(self):
            return self.query_without_buffer.protocol_specific.ProtocolDataLength

        @property
        def metadata_buf(self):
            return None

        @property
        def result(self):
            return self.query_without_buffer.result

        def dump_element(self):
            return {}
    return StorageQueryWithBuffer


# typedef union {
#   struct {
#     ULONG OPC : 8;
#     ULONG FUSE : 2;
#     ULONG Reserved0 : 5;
#     ULONG PSDT : 1;
#     ULONG CID : 16;
#   } DUMMYSTRUCTNAME;
#   ULONG  AsUlong;
# } NVME_COMMAND_DWORD0, *PNVME_COMMAND_DWORD0;
class NVME_COMMAND_DWORD0(Structure):
    _fields_ = [
        ('OPC', c_uint8),
        ('MIDV', c_uint8),
        ('CID', c_uint16),
    ]
    _pack_ = 1
    def __init__(self):
        pass

    @property
    def FUSE(self):
        return (self.MIDV & 0x03)

    @FUSE.setter
    def FUSE(self, value):
        if value < 4:
            self.MIDV = value + (self.MIDV & 0xFC)

    @property
    def Reserved0(self):
        return ((self.MIDV & 0x7C) >> 2)

    @Reserved0.setter
    def Reserved0(self, value):
        if value < 32:
            self.MIDV = (self.MIDV & 0x03) + (value << 2) + (self.MIDV & 0x80)

    @property
    def PSDT(self):
        return ((self.MIDV & 0x80) >> 7)

    @PSDT.setter
    def PSDT(self, value):
        if value < 2:
            self.MIDV = (self.MIDV & 0x7F) + (value << 7)

# typedef struct {
#   NVME_COMMAND_DWORD0 CDW0;
#   ULONG               NSID;
#   ULONG               Reserved0[2];
#   ULONGLONG           MPTR;
#   ULONGLONG           PRP1;
#   ULONGLONG           PRP2;
#   union {
#     struct {
#       ULONG CDW10;
#       ULONG CDW11;
#       ULONG CDW12;
#       ULONG CDW13;
#       ULONG CDW14;
#       ULONG CDW15;
#     } GENERAL;
#     struct {
#       NVME_CDW10_IDENTIFY CDW10;
#       NVME_CDW11_IDENTIFY CDW11;
#       ULONG               CDW12;
#       ULONG               CDW13;
#       ULONG               CDW14;
#       ULONG               CDW15;
#     } IDENTIFY;
#     struct {
#       NVME_CDW10_ABORT CDW10;
#       ULONG            CDW11;
#       ULONG            CDW12;
#       ULONG            CDW13;
#       ULONG            CDW14;
#       ULONG            CDW15;
#     } ABORT;
#     struct {
#       NVME_CDW10_GET_FEATURES CDW10;
#       NVME_CDW11_FEATURES     CDW11;
#       ULONG                   CDW12;
#       ULONG                   CDW13;
#       ULONG                   CDW14;
#       ULONG                   CDW15;
#     } GETFEATURES;
#     struct {
#       NVME_CDW10_SET_FEATURES CDW10;
#       NVME_CDW11_FEATURES     CDW11;
#       NVME_CDW12_FEATURES     CDW12;
#       NVME_CDW13_FEATURES     CDW13;
#       NVME_CDW14_FEATURES     CDW14;
#       NVME_CDW15_FEATURES     CDW15;
#     } SETFEATURES;
#     struct {
#       union {
#         NVME_CDW10_GET_LOG_PAGE     CDW10;
#         NVME_CDW10_GET_LOG_PAGE_V13 CDW10_V13;
#       };
#       NVME_CDW11_GET_LOG_PAGE CDW11;
#       NVME_CDW12_GET_LOG_PAGE CDW12;
#       NVME_CDW13_GET_LOG_PAGE CDW13;
#       NVME_CDW14_GET_LOG_PAGE CDW14;
#       ULONG                   CDW15;
#     } GETLOGPAGE;
#     struct {
#       NVME_CDW10_CREATE_IO_QUEUE CDW10;
#       NVME_CDW11_CREATE_IO_CQ    CDW11;
#       ULONG                      CDW12;
#       ULONG                      CDW13;
#       ULONG                      CDW14;
#       ULONG                      CDW15;
#     } CREATEIOCQ;
#     struct {
#       NVME_CDW10_CREATE_IO_QUEUE CDW10;
#       NVME_CDW11_CREATE_IO_SQ    CDW11;
#       ULONG                      CDW12;
#       ULONG                      CDW13;
#       ULONG                      CDW14;
#       ULONG                      CDW15;
#     } CREATEIOSQ;
#     struct {
#       NVME_CDW10_DATASET_MANAGEMENT CDW10;
#       NVME_CDW11_DATASET_MANAGEMENT CDW11;
#       ULONG                         CDW12;
#       ULONG                         CDW13;
#       ULONG                         CDW14;
#       ULONG                         CDW15;
#     } DATASETMANAGEMENT;
#     struct {
#       NVME_CDW10_SECURITY_SEND_RECEIVE CDW10;
#       NVME_CDW11_SECURITY_SEND         CDW11;
#       ULONG                            CDW12;
#       ULONG                            CDW13;
#       ULONG                            CDW14;
#       ULONG                            CDW15;
#     } SECURITYSEND;
#     struct {
#       NVME_CDW10_SECURITY_SEND_RECEIVE CDW10;
#       NVME_CDW11_SECURITY_RECEIVE      CDW11;
#       ULONG                            CDW12;
#       ULONG                            CDW13;
#       ULONG                            CDW14;
#       ULONG                            CDW15;
#     } SECURITYRECEIVE;
#     struct {
#       NVME_CDW10_FIRMWARE_DOWNLOAD CDW10;
#       NVME_CDW11_FIRMWARE_DOWNLOAD CDW11;
#       ULONG                        CDW12;
#       ULONG                        CDW13;
#       ULONG                        CDW14;
#       ULONG                        CDW15;
#     } FIRMWAREDOWNLOAD;
#     struct {
#       NVME_CDW10_FIRMWARE_ACTIVATE CDW10;
#       ULONG                        CDW11;
#       ULONG                        CDW12;
#       ULONG                        CDW13;
#       ULONG                        CDW14;
#       ULONG                        CDW15;
#     } FIRMWAREACTIVATE;
#     struct {
#       NVME_CDW10_FORMAT_NVM CDW10;
#       ULONG                 CDW11;
#       ULONG                 CDW12;
#       ULONG                 CDW13;
#       ULONG                 CDW14;
#       ULONG                 CDW15;
#     } FORMATNVM;
#     struct {
#       NVME_CDW10_DIRECTIVE_RECEIVE CDW10;
#       NVME_CDW11_DIRECTIVE_RECEIVE CDW11;
#       NVME_CDW12_DIRECTIVE_RECEIVE CDW12;
#       ULONG                        CDW13;
#       ULONG                        CDW14;
#       ULONG                        CDW15;
#     } DIRECTIVERECEIVE;
#     struct {
#       NVME_CDW10_DIRECTIVE_SEND CDW10;
#       NVME_CDW11_DIRECTIVE_SEND CDW11;
#       NVME_CDW12_DIRECTIVE_SEND CDW12;
#       ULONG                     CDW13;
#       ULONG                     CDW14;
#       ULONG                     CDW15;
#     } DIRECTIVESEND;
#     struct {
#       NVME_CDW10_SANITIZE CDW10;
#       NVME_CDW11_SANITIZE CDW11;
#       ULONG               CDW12;
#       ULONG               CDW13;
#       ULONG               CDW14;
#       ULONG               CDW15;
#     } SANITIZE;
#     struct {
#       ULONG                 LBALOW;
#       ULONG                 LBAHIGH;
#       NVME_CDW12_READ_WRITE CDW12;
#       NVME_CDW13_READ_WRITE CDW13;
#       ULONG                 CDW14;
#       NVME_CDW15_READ_WRITE CDW15;
#     } READWRITE;
#     struct {
#       NVME_CDW10_RESERVATION_ACQUIRE CDW10;
#       ULONG                          CDW11;
#       ULONG                          CDW12;
#       ULONG                          CDW13;
#       ULONG                          CDW14;
#       ULONG                          CDW15;
#     } RESERVATIONACQUIRE;
#     struct {
#       NVME_CDW10_RESERVATION_REGISTER CDW10;
#       ULONG                           CDW11;
#       ULONG                           CDW12;
#       ULONG                           CDW13;
#       ULONG                           CDW14;
#       ULONG                           CDW15;
#     } RESERVATIONREGISTER;
#     struct {
#       NVME_CDW10_RESERVATION_RELEASE CDW10;
#       ULONG                          CDW11;
#       ULONG                          CDW12;
#       ULONG                          CDW13;
#       ULONG                          CDW14;
#       ULONG                          CDW15;
#     } RESERVATIONRELEASE;
#     struct {
#       NVME_CDW10_RESERVATION_REPORT CDW10;
#       NVME_CDW11_RESERVATION_REPORT CDW11;
#       ULONG                         CDW12;
#       ULONG                         CDW13;
#       ULONG                         CDW14;
#       ULONG                         CDW15;
#     } RESERVATIONREPORT;
#     struct {
#       NVME_CDW10_ZONE_MANAGEMENT_SEND CDW1011;
#       ULONG                           CDW12;
#       NVME_CDW13_ZONE_MANAGEMENT_SEND CDW13;
#       ULONG                           CDW14;
#       ULONG                           CDW15;
#     } ZONEMANAGEMENTSEND;
#     struct {
#       NVME_CDW10_ZONE_MANAGEMENT_RECEIVE CDW1011;
#       ULONG                              DWORDCOUNT;
#       NVME_CDW13_ZONE_MANAGEMENT_RECEIVE CDW13;
#       ULONG                              CDW14;
#       ULONG                              CDW15;
#     } ZONEMANAGEMENTRECEIVE;
#     struct {
#       NVME_CDW10_ZONE_APPEND CDW1011;
#       NVME_CDW12_ZONE_APPEND CDW12;
#       ULONG                  CDW13;
#       ULONG                  ILBRT;
#       NVME_CDW15_ZONE_APPEND CDW15;
#     } ZONEAPPEND;
#   } u;
# } NVME_COMMAND, *PNVME_COMMAND;
class NVME_COMMAND(Structure):
    '''
    Total 64 Bytes command
    '''
    _fields_ = [
        ('CDW0', NVME_COMMAND_DWORD0),
        ('NSID', c_uint32),
        ('Reserved0', c_uint32 * 2),
        ('MPTR', c_uint64),
        ('PRP1', c_uint64),
        ('PRP2', c_uint64),
        ('CDW10', c_uint32),
        ('CDW11', c_uint32),
        ('CDW12', c_uint32),
        ('CDW13', c_uint32),
        ('CDW14', c_uint32),
        ('CDW15', c_uint32),
    ]
    _pack_ = 1

# class STORAGE_PROTOCOL_COMMAND(EasyCastStructure):
#     Version: UInt32
#     Length: UInt32
#     ProtocolType: win32more.Windows.Win32.System.Ioctl.STORAGE_PROTOCOL_TYPE
#     Flags: UInt32
#     ReturnStatus: UInt32
#     ErrorCode: UInt32
#     CommandLength: UInt32
#     ErrorInfoLength: UInt32
#     DataToDeviceTransferLength: UInt32
#     DataFromDeviceTransferLength: UInt32
#     TimeOutValue: UInt32
#     ErrorInfoOffset: UInt32
#     DataToDeviceBufferOffset: UInt32
#     DataFromDeviceBufferOffset: UInt32
#     CommandSpecific: UInt32
#     Reserved0: UInt32
#     FixedProtocolReturnData: UInt32
#     Reserved1: UInt32 * 3
#     Command: Byte * 64
class STORAGE_PROTOCOL_COMMAND(Structure):
    _fields_ = [
        ('Version', c_uint32),
        ('Length', c_uint32),
        ('ProtocolType', c_uint32),
        ('Flags', c_uint32),
        ('ReturnStatus', c_uint32),
        ('ErrorCode', c_uint32),
        ('CommandLength', c_uint32),
        ('ErrorInfoLength', c_uint32),
        ('DataToDeviceTransferLength', c_uint32),
        ('DataFromDeviceTransferLength', c_uint32),
        ('TimeOutValue', c_uint32),
        ('ErrorInfoOffset', c_uint32),
        ('DataToDeviceBufferOffset', c_uint32),
        ('DataFromDeviceBufferOffset', c_uint32),
        ('CommandSpecific', c_uint32),
        ('Reserved0', c_uint32),
        ('FixedProtocolReturnData', c_uint32),
        ('FixedProtocolReturnData2', c_uint32),
        ('Reserved1', c_uint32 * 2),
        ('Command', NVME_COMMAND),
    ]
    _pack_ = 1
    def __init__(self):
        pass

    @property
    def command_buf(self):
        return self

    @property
    def data_buf(self):
        return None

    @property
    def data_len(self):
        return 0

    @property
    def metadata_buf(self):
        return None

    @property
    def result(self):
        # TODO, not check
        return self.FixedProtocolReturnData


def GetStorageProtocolCommandWithBuffer(buffer_len:int):
    class STORAGE_PROTOCOL_COMMAND_With_Buffer(Structure):
        _fields_ = [
            ('storage_protocal_command', STORAGE_PROTOCOL_COMMAND),
            ('data_buffer', c_ubyte * buffer_len)
        ]
        _pack_ = 1

        def __init__(self):
            pass

        @property
        def command_buf(self):
            return self.storage_protocal_command

        @property
        def error_info(self):
            return bytes(self.data_buffer)[:self.storage_protocal_command.ErrorInfoLength]

        @property
        def data_buf(self):
            return bytes(self.data_buffer)[self.storage_protocal_command.ErrorInfoLength:]

        @property
        def data_len(self):
            return (self.data_buffer.size - self.storage_protocal_command.ErrorInfoLength)

        @property
        def metadata_buf(self):
            return None

        @property
        def result(self):
            return self.storage_protocal_command.result
    return STORAGE_PROTOCOL_COMMAND_With_Buffer
# typedef union {
#   struct {
#     USHORT P : 1;
#     USHORT SC : 8;
#     USHORT SCT : 3;
#     USHORT Reserved : 2;
#     USHORT M : 1;
#     USHORT DNR : 1;
#   } DUMMYSTRUCTNAME;
#   USHORT AsUshort;
# } NVME_COMMAND_STATUS, *PNVME_COMMAND_STATUS;
class NVME_COMMAND_STATUS(Structure):
    class DUMMYSTRUCTNAME(Structure):
        _fields_ = [
        ('VALUE', c_uint16),
        ]
        _pack_ = 1
        def __init__(self):
            pass

        @property
        def P(self):
            return (self.VALUE & 0x01)

        @property
        def SC(self):
            return ((self.VALUE >> 1) & 0xFF)

        @property
        def SCT(self):
            return ((self.VALUE >> 9) & 0x07)

        @property
        def M(self):
            return ((self.VALUE >> 14) & 0x01)

        @property
        def DNR(self):
            return ((self.VALUE >> 15) & 0x01)


    _fields_ = [
        ('DUMMYSTRUCTNAME', DUMMYSTRUCTNAME),
        ('AsUshort', c_uint16),
    ]
    _pack_ = 1
# class NVME_ERROR_INFO_LOG(EasyCastStructure):
#     ErrorCount: UInt64
#     SQID: UInt16
#     CMDID: UInt16
#     Status: win32more.Windows.Win32.Storage.Nvme.NVME_COMMAND_STATUS
#     ParameterErrorLocation: _ParameterErrorLocation_e__Struct
#     Lba: UInt64
#     NameSpace: UInt32
#     VendorInfoAvailable: Byte
#     Reserved0: Byte * 3
#     CommandSpecificInfo: UInt64
#     Reserved1: Byte * 24
#     class _ParameterErrorLocation_e__Struct(EasyCastStructure):
#         _bitfield: UInt16
class NVME_ERROR_INFO_LOG(Structure):
    class ParameterErrorLocation(Structure):
        _fields_ = [
        ('VALUE', c_uint16),
        ]
        _pack_ = 1
        def __init__(self):
            pass
        @property
        def Byte(self):
            return (self.VALUE & 0xFF)
        @property
        def Bit(self):
            return ((self.VALUE >> 8) & 0x07)
        @property
        def Reserved(self):
            return ((self.VALUE >> 11) & 0x07)

    _fields_ = [
        ('ErrorCount', c_uint64),
        ('SQID', c_uint16),
        ('CMDID', c_uint16),
        ('Status', NVME_COMMAND_STATUS),
        ('ParameterErrorLocation', ParameterErrorLocation),
        ('Lba', c_uint64),
        ('NameSpace', c_uint32),
        ('VendorInfoAvailable', c_ubyte),
        ('Reserved0', c_ubyte * 3),
        ('CommandSpecificInfo', c_uint64),
        ('Reserved1', c_ubyte * 24),
    ]
    _pack_ = 1


class STORAGE_PROPERTY_SET(Structure):
    _fields_ = [
        ("PropertyId", c_uint32),
        ("SetType", c_uint32),
        ("AdditionalParameters", c_ubyte),
    ]
    _pack_ = 1


class _STORAGE_PROPERTY_SET(Structure):
    _fields_ = [
        ("PropertyId", c_uint32),
        ("SetType", c_uint32),
    ]
    _pack_ = 1


class STORAGE_PROTOCOL_SPECIFIC_DATA_EXT(Structure):
    _fields_ = [
        ("ProtocolType", c_uint32),
        ("DataType", c_uint32),
        ("ProtocolDataValue", c_uint32),
        ("ProtocolDataSubValue", c_uint32),
        ("ProtocolDataOffset", c_uint32),
        ("ProtocolDataLength", c_uint32),
        ("FixedProtocolReturnData", c_uint32),
        ("ProtocolDataRequestSubValue2", c_uint32),
        ("ProtocolDataRequestSubValue3", c_uint32),
        ("ProtocolDataRequestSubValue4", c_uint32),
        ("ProtocolDataRequestSubValue5", c_uint32),
        ("Reserved", c_uint32 * 5),
    ]
    _pack_ = 1


class IOCTL_STORAGE_SET_PROPERTY(Structure):
    _fields_ = [
        ("setProperty", _STORAGE_PROPERTY_SET),
        ("protocolData", STORAGE_PROTOCOL_SPECIFIC_DATA_EXT),
    ]
    _pack_ = 1
    def __init__(self):
        pass

    @property
    def command_buf(self):
        return self

    @property
    def data_buf(self):
        return None

    @property
    def data_len(self):
        return 0

    @property
    def metadata_buf(self):
        return None

    @property
    def result(self):
        return self.protocolData.FixedProtocolReturnData

    def dump_element(self):
        return {}


def GetIOCTLStorageSetPropertyWithBuffer(buffer_len:int):
    class IOCTL_STORAGE_SET_PROPERTY_WITH_BUFFER(Structure):
        _fields_ = [
            ("set_property_without_buffer", IOCTL_STORAGE_SET_PROPERTY),
            ('data_buffer', c_ubyte * buffer_len),
        ]
        _pack_ = 1
        def __init__(self):
            pass

        @property
        def setProperty(self):
            return self.set_property_without_buffer.setProperty

        @property
        def protocolData(self):
            return self.set_property_without_buffer.protocolData

        @property
        def command_buf(self):
            return self.set_property_without_buffer

        @property
        def data_buf(self):
            return self.data_buffer

        @property
        def data_len(self):
            return self.protocolData.ProtocolDataLength

        @property
        def metadata_buf(self):
            return None

        @property
        def result(self):
            return self.protocolData.FixedProtocolReturnData

        def dump_element(self):
            return {}
    return IOCTL_STORAGE_SET_PROPERTY_WITH_BUFFER


class SCSI_MINIPORT_FIRMWARE_HEADER(Structure):
    _fields_ = [
        ('srbIoCtrl', SRB_IO_CONTROL),
        ("firmwareRequest", FIRMWARE_REQUEST_BLOCK),
    ]
    _pack_ = 1


class SCSI_MINIPORT_FIRMWARE_DOWNLOAD_HEADER(Structure):
    _fields_ = [
        ('srbIoCtrl', SRB_IO_CONTROL),
        ("firmwareRequest", FIRMWARE_REQUEST_BLOCK),
        ("firmwareDownload", STORAGE_FIRMWARE_DOWNLOAD),
    ]
    _pack_ = 1
    def __init__(self):
        pass

    @property
    def command_buf(self):
        return self

    @property
    def data_buf(self):
        return None

    @property
    def data_len(self):
        return 0

    @property
    def metadata_buf(self):
        return None

    @property
    def result(self):
        return

    def dump_element(self):
        return {}


def GetScsiMiniportFirmwareDownload(buffer_len:int):
    class IOCTL_MINIPORT_FIRMWARE_DOWNLOAD_WITH_BUFFER(Structure):
        _fields_ = [
            ("firmwareDownloadHeader", SCSI_MINIPORT_FIRMWARE_DOWNLOAD_HEADER),
            ('ImageBuffer', c_ubyte * buffer_len),
        ]
        _pack_ = 1
        def __init__(self):
            pass

        @property
        def srbIoCtrl(self):
            return self.firmwareDownloadHeader.srbIoCtrl

        @property
        def firmwareRequest(self):
            return self.firmwareDownloadHeader.firmwareRequest

        @property
        def firmwareDownload(self):
            return self.firmwareDownloadHeader.firmwareDownload

        @property
        def command_buf(self):
            return self.firmwareDownloadHeader

        @property
        def data_buf(self):
            return self.ImageBuffer

        @property
        def data_len(self):
            return len(self.data_buf)

        @property
        def metadata_buf(self):
            return None

        @property
        def result(self):
            return None

        def dump_element(self):
            return {}
    return IOCTL_MINIPORT_FIRMWARE_DOWNLOAD_WITH_BUFFER


class SCSI_MINIPORT_FIRMWARE_ACTIVE(Structure):
    _fields_ = [
        ('srbIoCtrl', SRB_IO_CONTROL),
        ("firmwareRequest", FIRMWARE_REQUEST_BLOCK),
        ("firmwareActivate", STORAGE_FIRMWARE_ACTIVATE),
    ]
    _pack_ = 1
    def __init__(self):
        pass

    @property
    def command_buf(self):
        return self

    @property
    def data_buf(self):
        return None

    @property
    def data_len(self):
        return 0

    @property
    def metadata_buf(self):
        return None

    @property
    def result(self):
        return

    def dump_element(self):
        return {}
