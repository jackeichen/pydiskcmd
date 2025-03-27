# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import ctypes
from enum import Enum

#define DXFER_NONE        0
#define DXFER_FROM_DEVICE 1
#define DXFER_TO_DEVICE   2
class SCSI_DXFER(Enum):
    DXFER_NONE = 0
    DXFER_FROM_DEVICE = 1
    DXFER_TO_DEVICE = 2
