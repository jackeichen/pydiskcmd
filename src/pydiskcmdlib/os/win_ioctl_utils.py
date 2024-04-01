# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from enum import Enum
### DeviceType start ###
NVME_STORPORT_DRIVER = 0xE000
### DeviceType end #####

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
