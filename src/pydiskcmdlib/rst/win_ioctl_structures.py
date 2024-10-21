# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from ctypes import (Structure,
                    c_uint8,
                    c_int8,
                    c_uint16,
                    c_uint32,
                    c_uint64,
                    c_ubyte,
                    sizeof,
                    c_ulonglong,
                    )
from pydiskcmdlib.os.win_ioctl_structures import SRB_IO_CONTROL,roundupdw,GENERIC_COMMAND,SRB_IO_CONTROL_LEN

##
class COMPLETION_QUEUE_ENTRY(Structure):
    _fields_ = [
        ('CommandSpecific', c_uint32),
        ('cReserved', c_uint32),
        ('SQHeadPointer', c_uint16),
        ('SQIdentifier', c_uint16),
        ('CommandIdentifier', c_uint16),
        ('P', c_uint16, 1),
        ('StatusField', c_uint16, 15),
        # ('StatusCode', c_uint16, 8),
        # ('StatusCodeType', c_uint16, 3),
        # ('SF_Reserved', c_uint16, 2),
        # ('More', c_uint16, 1),
        # ('DoNotRetry', c_uint16, 1),
    ]
    _pack_ = 1

# struct NVME_PASS_THROUGH_PARAMETERS {
#  GENERIC_COMMAND Command;
#  BOOLEAN IsIOCommandSet;
#  COMPLETION_QUEUE_ENTRY Completion; 
#  ULONG DataBufferOffset;
#  ULONG DataBufferLength;
#  ULONG Reserved[10];
# };
class NVME_PASS_THROUGH_PARAMETERS(Structure):
    _fields_ = [
        ('Command', GENERIC_COMMAND),
        ('IsIOCommandSet', c_uint8),
        ('Completion', COMPLETION_QUEUE_ENTRY),
        ('Reserved1', c_ubyte * 3),  # Keep the NVME_IOCTL_PASS_THROUGH DW aligned
        ('DataBufferOffset', c_uint32),
        ('DataBufferLength', c_uint32),
        ('Reserved', c_uint32 * 10),
    ]
    _pack_ = 1

# struct NVME_IOCTL_PASS_THROUGH {
#  SRB_IO_CONTROL Header;
#  UCHAR Version;
#  UCHAR PathID;
#  UCHAR TargetID;
#  UCHAR Lun;
#  NVME_PASS_THROUGH_PARAMETERS Parameters;
# };
class NVME_IOCTL_PASS_THROUGH(Structure):
    # Total Length: 28 + 4 + (64 + 1 + 16 + 8 + 40) = 161 bytes
    _fields_ = [
        ('IoctlHeader', SRB_IO_CONTROL),
        ('Version', c_uint8),
        ('PathID', c_uint8),
        ('TargetID', c_uint8),
        ('Lun', c_uint8),
        ('Parameters', NVME_PASS_THROUGH_PARAMETERS),
    ]
    _pack_ = 1

    @property
    def command_buf(self):
        return bytes(self)[0:sizeof(NVME_IOCTL_PASS_THROUGH)]

    @property
    def data_buf(self):
        return

    def data(self):
        return

NVME_IOCTL_PASS_THROUGH_LEN = sizeof(NVME_IOCTL_PASS_THROUGH)
# NVME_IOCTL_PASS_THROUGH_LEN_ALIGNED = roundupdw(NVME_IOCTL_PASS_THROUGH_LEN)

def Get_NVME_IOCTL_PASS_THROUGH_ALIGNED_WITH_BUFFER(buffer_length):
    class NVME_IOCTL_PASS_THROUGH_WITH_BUFFER(Structure):
        _fields_ = [
            ('NVME_IOCTL_PASS_THROUGH', NVME_IOCTL_PASS_THROUGH),
            ("Padding", c_uint8 * (roundupdw(buffer_length) - buffer_length)),  # keep DW aligned
            ('DataBuffer', c_ubyte* buffer_length),  # DW
        ]
        _pack_ = 1

        @property
        def IoctlHeader(self):
            return self.NVME_IOCTL_PASS_THROUGH.IoctlHeader

        @property
        def Version(self):
            return self.NVME_IOCTL_PASS_THROUGH.Version

        @property
        def PathID(self):
            return self.NVME_IOCTL_PASS_THROUGH.PathID

        @property
        def TargetID(self):
            return self.NVME_IOCTL_PASS_THROUGH.TargetID

        @property
        def Lun(self):
            return self.NVME_IOCTL_PASS_THROUGH.Lun

        @property
        def Parameters(self):
            return self.NVME_IOCTL_PASS_THROUGH.Parameters

        @property
        def command_buf(self):
            return bytes(self.NVME_IOCTL_PASS_THROUGH)

        @property
        def data_buf(self):
            return self.DataBuffer

    return NVME_IOCTL_PASS_THROUGH_WITH_BUFFER
