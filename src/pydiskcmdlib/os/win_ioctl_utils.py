# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later

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
