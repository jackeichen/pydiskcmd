# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from enum import Enum
### DeviceType start ###
NVME_STORPORT_DRIVER = 0xE000
### DeviceType end #####

### STORAGE_PROTOCOL_STATUS start ###
class StorageProtocolStatus(Enum):
    STORAGE_PROTOCOL_STATUS_PENDING                = 0 
    STORAGE_PROTOCOL_STATUS_SUCCESS                = 1
    STORAGE_PROTOCOL_STATUS_ERROR                  = 2
    STORAGE_PROTOCOL_STATUS_INVALID_REQUEST        = 3
    STORAGE_PROTOCOL_STATUS_NO_DEVICE              = 4
    STORAGE_PROTOCOL_STATUS_BUSY                   = 5
    STORAGE_PROTOCOL_STATUS_DATA_OVERRUN           = 6
    STORAGE_PROTOCOL_STATUS_INSUFFICIENT_RESOURCES = 7
    STORAGE_PROTOCOL_STATUS_THROTTLED_REQUEST      = 8
    STORAGE_PROTOCOL_STATUS_NOT_SUPPORTED          = 255
### STORAGE_PROTOCOL_STATUS end #####

### Method start ###
METHOD_BUFFERED   = 0x00
METHOD_IN_DIRECT  = 0x01
METHOD_OUT_DIRECT = 0x02
METHOD_NEITHER    = 0x03
### Method end #####

### Access start ###
FILE_ANY_ACCESS     = 0
FILE_READ_ACCESS    = 0x0001 
FILE_WRITE_ACCESS   = 0x0002
### Access end #####

def CTL_CODE(DeviceType, Function, Method, Access):
    return (DeviceType << 16) | (Access << 14) | (Function << 2) | Method

#define FIRMWARE_FUNCTION_GET_INFO                          0x01
#define FIRMWARE_FUNCTION_DOWNLOAD                          0x02
#define FIRMWARE_FUNCTION_ACTIVATE                          0x03
class FIRMWARE_FUNCTION(Enum):
    GET_INFO = 0x01
    DOWNLOAD = 0x02
    ACTIVATE = 0x03

### IOCTL_MINIPORT_SIGNATURE start ###
IOCTL_MINIPORT_SIGNATURE_FIRMWARE = 'FIRMWARE'
### IOCTL_MINIPORT_SIGNATURE end #####
FIRMWARE_REQUEST_BLOCK_STRUCTURE_VERSION = 1  # uint32
FIRMWARE_REQUEST_FLAG_CONTROLLER = 1          # uint32
FIRMWARE_REQUEST_FLAG_LAST_SEGMENT = 2        # uint32
FIRMWARE_REQUEST_FLAG_FIRST_SEGMENT = 4       # uint32
FIRMWARE_REQUEST_FLAG_REPLACE_EXISTING_IMAGE = 1073741824   # uint32
FIRMWARE_REQUEST_FLAG_SWITCH_TO_EXISTING_FIRMWARE = 2147483648  # uint32
### srbControl ControlCode start ###
FILE_DEVICE_SCSI = 0x0000001b 
##
IOCTL_SCSI_MINIPORT_FIRMWARE = ((FILE_DEVICE_SCSI << 16) + 0x0780)
### srbControl ControlCode end #####
### FIRMWARE_STATUS start ###
class FIRMWARE_STATUS(Enum):
    COMMAND_ABORT = 133
    FIRMWARE_STATUS_CONTROLLER_ERROR = 16
    FIRMWARE_STATUS_DEVICE_ERROR = 64
    FIRMWARE_STATUS_END_OF_MEDIA = 134
    FIRMWARE_STATUS_ERROR = 1
    FIRMWARE_STATUS_ID_NOT_FOUND = 131
    FIRMWARE_STATUS_ILLEGAL_LENGTH = 135
    FIRMWARE_STATUS_ILLEGAL_REQUEST = 2
    FIRMWARE_STATUS_INPUT_BUFFER_TOO_BIG = 4
    FIRMWARE_STATUS_INTERFACE_CRC_ERROR = 128
    FIRMWARE_STATUS_INVALID_IMAGE = 7
    FIRMWARE_STATUS_INVALID_PARAMETER = 3
    FIRMWARE_STATUS_INVALID_SLOT = 6
    FIRMWARE_STATUS_MEDIA_CHANGE = 130
    FIRMWARE_STATUS_MEDIA_CHANGE_REQUEST = 132
    FIRMWARE_STATUS_OUTPUT_BUFFER_TOO_SMALL = 5
    FIRMWARE_STATUS_POWER_CYCLE_REQUIRED = 32
    FIRMWARE_STATUS_SUCCESS = 0
    FIRMWARE_STATUS_UNCORRECTABLE_DATA_ERROR = 129
### FIRMWARE_STATUS end ###
class CSMI_Control_Code(Enum):
    CC_CSMI_SAS_GET_DRIVER_INFO = 1
    CC_CSMI_SAS_GET_RAID_INFO = 10
    CC_CSMI_SAS_GET_RAID_CONFIG = 11
    CC_CSMI_SAS_STP_PASSTHRU = 25

class CSMI_Return_Code(Enum):
    CSMI_SAS_STATUS_SUCCESS = 0
    CSMI_SAS_STATUS_FAILED = 1
    CSMI_SAS_STATUS_BAD_CNTL_CODE = 2
    CSMI_SAS_STATUS_INVALID_PARAMETER = 3
    CSMI_SAS_STATUS_WRITE_ATTEMPTED = 4

class CSMISignature(Enum):
    CSMI_SAS_SIGNATURE = "CSMISAS"
    CSMI_ALL_SIGNATURE = "CSMIALL"
    CSMI_RAID_SIGNATURE = "CSMIARY"

class CSMI_SAS_TIMEOUT(Enum):
    default = 60

### INTEL RST SIGNATURE ###
INTELNVM_SIGNATURE = "IntelNvm"
IOCTL_NVME_PASS_THROUGH = CTL_CODE(0xF000, 0xA02, METHOD_BUFFERED, FILE_ANY_ACCESS)
class RST_NVME_PASS_THROUGH_VERSION(Enum):
    default = 1
