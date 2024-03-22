# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from enum import Enum

class IOCTLRequest(Enum):
    RESERVED_REQUEST_ID     = 0x00      # This is a reserved request ID for pydiskcmd.
    SG_IO_IOCTL             = 0x2285
    NVME_IOCTL_RESET        = 0x4E44
    NVME_IOCTL_SUBSYS_RESET = 0x4E45
    NVME_IOCTL_ADMIN_CMD    = 0xC0484E41
    NVME_IOCTL_IO_CMD       = 0xC0484E43
