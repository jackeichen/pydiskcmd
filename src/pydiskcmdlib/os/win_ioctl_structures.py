# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from ctypes import (Structure,
                    c_uint8,
                    c_uint16,
                    c_uint32,
                    c_uint64,
                    c_ubyte,
                    sizeof,
                    c_ulonglong,
                    )


#   typedef struct _SRB_IO_CONTROL {
#     ULONG HeaderLength;
#     UCHAR Signature[8];
#     ULONG Timeout;
#     ULONG ControlCode;
#     ULONG ReturnCode;
#     ULONG Length;
#   } SRB_IO_CONTROL,*PSRB_IO_CONTROL;
class SRB_IO_CONTROL(Structure):
    # Total length 28 Bytes
    _fields_ = [
        ('HeaderLength', c_uint32),
        ('Signature', c_ubyte * 8),
        ('Timeout', c_uint32),
        ('ControlCode', c_uint32),
        ('ReturnCode', c_uint32),
        ('Length', c_uint32),
    ]
    _pack_ = 1
