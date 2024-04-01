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

# typedef struct _FIRMWARE_REQUEST_BLOCK {
#     ULONG   Version;            // FIRMWARE_REQUEST_BLOCK_STRUCTURE_VERSION
#     ULONG   Size;               // Size of the data structure.
#     ULONG   Function;           // Function code
#     ULONG   Flags;

#     ULONG   DataBufferOffset;   // the offset is from the beginning of buffer. e.g. from beginning of SRB_IO_CONTROL. The value should be multiple of sizeof(PVOID); Value 0 means that there is no data buffer.
#     ULONG   DataBufferLength;   // length of the buffer
# } FIRMWARE_REQUEST_BLOCK, *PFIRMWARE_REQUEST_BLOCK;
class FIRMWARE_REQUEST_BLOCK(Structure):
    # Total length 24 Bytes
    _fields_ = [
        ('Version', c_uint32),
        ('Size', c_uint32),
        ('Function', c_uint32),
        ('Flags', c_uint32),
        ('DataBufferOffset', c_uint32),
        ('DataBufferLength', c_uint32),
    ]
    _pack_ = 1

# typedef struct _STORAGE_FIRMWARE_DOWNLOAD {

#     ULONG       Version;            // STORAGE_FIRMWARE_DOWNLOAD_STRUCTURE_VERSION
#     ULONG       Size;               // sizeof(STORAGE_FIRMWARE_DOWNLOAD)

#     ULONGLONG   Offset;             // image file offset, should be aligned to value of "ImagePayloadAlignment" from STORAGE_FIRMWARE_INFO.
#     ULONGLONG   BufferSize;         // should be multiple of value of "ImagePayloadAlignment" from STORAGE_FIRMWARE_INFO

#     UCHAR       ImageBuffer[0];     // firmware image file. 

# } STORAGE_FIRMWARE_DOWNLOAD, *PSTORAGE_FIRMWARE_DOWNLOAD; 
class STORAGE_FIRMWARE_DOWNLOAD(Structure):
    _fields_ = [
        ('Version', c_uint32),
        ('Size', c_uint32),
        ('Offset', c_ulonglong),
        ('BufferSize', c_ulonglong),
        ('ImageBuffer', c_uint32 * 0),
    ]
    _pack_ = 1

# typedef struct _STORAGE_FIRMWARE_ACTIVATE {

#     ULONG   Version;
#     ULONG   Size;

#     UCHAR   SlotToActivate;
#     UCHAR   Reserved0[3];

# } STORAGE_FIRMWARE_ACTIVATE, *PSTORAGE_FIRMWARE_ACTIVATE;
class STORAGE_FIRMWARE_ACTIVATE(Structure):
    _fields_ = [
        ('Version', c_uint32),
        ('Size', c_uint32),
        ('SlotToActivate', c_uint8),
        ('Reserved0', c_ubyte * 3),
    ]
    _pack_ = 1
