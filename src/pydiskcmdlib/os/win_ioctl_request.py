# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from enum import Enum

class IOCTLRequest(Enum):
    RESERVED_REQUEST_ID                      = 0x00      # This is a reserved request ID for pydiskcmd.
    IOCTL_SCSI_PASS_THROUGH_DIRECT           = 0x4D014
    IOCTL_SCSI_MINIPORT                      = 0x4D008
    IOCTL_SCSI_PASS_THROUGH_DIRECT_EX        = 0x4D048
    IOCTL_DISK_FLUSH_CACHE                   = 0x71C54   # TODO: Not Test.
    FSCTL_LOCK_VOLUME                        = 0x90018
    FSCTL_UNLOCK_VOLUME                      = 0x9001C
    IOCTL_STORAGE_QUERY_PROPERTY             = 0x2D1400
    IOCTL_STORAGE_SET_PROPERTY               = 0x2D93FC
    IOCTL_STORAGE_MANAGE_DATA_SET_ATTRIBUTES = 0x2D9404
    IOCTL_STORAGE_REINITIALIZE_MEDIA         = 0x2D9640
    IOCTL_STORAGE_SET_TEMPERATURE_THRESHOLD  = 0x2DD200
    IOCTL_STORAGE_PROTOCOL_COMMAND           = 0x2DD3C0
    IOCTL_STORAGE_FIRMWARE_DOWNLOAD          = 0x2DDC04
    IOCTL_STORAGE_FIRMWARE_ACTIVATE          = 0x2DDC08
