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
