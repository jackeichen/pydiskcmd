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

def roundupdw(number: int) -> int:
    """
    Round up the number to the next multiple of 4.
    """
    return (number + 3) & ~3

class NVME_COMMAND_DWORD0(Structure):
    _fields_ = [
        ('OPC', c_uint32, 8),
        ('FUSE', c_uint32, 2),
        ('Reserved', c_uint32, 4),
        ('PSDT', c_uint32, 2),
        ('CID', c_uint32, 16),
    ]
    _pack_ = 1

class GENERIC_COMMAND(Structure):
    '''
    Total 64 Bytes command
    '''
    _fields_ = [
        ('CDW0', NVME_COMMAND_DWORD0),
        ('NSID', c_uint32),
        ('Reserved0', c_uint32 * 2),
        ('MPTR', c_uint64),
        ('PRP1', c_uint64),
        ('PRP2', c_uint64),
        ('CDW10', c_uint32),
        ('CDW11', c_uint32),
        ('CDW12', c_uint32),
        ('CDW13', c_uint32),
        ('CDW14', c_uint32),
        ('CDW15', c_uint32),
    ]
    _pack_ = 1

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
SRB_IO_CONTROL_LEN = sizeof(SRB_IO_CONTROL)

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

# typedef struct _CSMI_SAS_DRIVER_INFO
# {
#     BYTE                            szName[81];
#     BYTE                            szDescription[81];
#     WORD                            usMajorRevision;
#     WORD                            usMinorRevision;
#     WORD                            usBuildRevision;
#     WORD                            usReleaseRevision;
#     WORD                            usCSMIMajorRevision;
#     WORD                            usCSMIMinorRevision;

# } CSMI_SAS_DRIVER_INFO, *PCSMI_SAS_DRIVER_INFO;
class CSMI_SAS_DRIVER_INFO(Structure):
    _fields_ = [
        ('szName', c_ubyte * 81),
        ('szDescription', c_ubyte * 81),
        ('usMajorRevision', c_uint16),
        ('usMinorRevision', c_uint16),
        ('usBuildRevision', c_uint16),
        ('usReleaseRevision', c_uint16),
        ('usCSMIMajorRevision', c_uint16),
        ('usCSMIMinorRevision', c_uint16),
    ]
    _pack_ = 1

# typedef struct _CSMI_SAS_DRIVER_INFO_BUFFER
# {
#     IOCTL_HEADER                    IoctlHeader;
#     CSMI_SAS_DRIVER_INFO            Information;

# } CSMI_SAS_DRIVER_INFO_BUFFER, *PCSMI_SAS_DRIVER_INFO_BUFFER;
class CSMI_SAS_DRIVER_INFO_BUFFER(Structure):
    _fields_ = [
        ('IoctlHeader', SRB_IO_CONTROL),
        ('Information', CSMI_SAS_DRIVER_INFO),
    ]
    _pack_ = 1

CSMI_SAS_DRIVER_INFO_BUFFER_LEN = sizeof(CSMI_SAS_DRIVER_INFO_BUFFER)
# typedef struct _CSMI_SAS_RAID_INFO
# {
#     DWORD                           uNumRaidSets;
#     DWORD                           uMaxDrivesPerSet;
#     BYTE                            bReserved[92];

# } CSMI_SAS_RAID_INFO, *PCSMI_SAS_RAID_INFO;
class CSMI_SAS_RAID_INFO(Structure):
    _fields_ = [
        ('uNumRaidSets', c_uint32),
        ('uMaxDrivesPerSet', c_uint32),
        ('bReserved', c_ubyte * 92),
    ]
    _pack_ = 1

# typedef struct _CSMI_SAS_RAID_INFO_BUFFER
# {
#     IOCTL_HEADER                    IoctlHeader;
#     CSMI_SAS_RAID_INFO              Information;

# } CSMI_SAS_RAID_INFO_BUFFER, *PCSMI_SAS_RAID_INFO_BUFFER;
class CSMI_SAS_RAID_INFO_BUFFER(Structure):
    _fields_ = [
        ('IoctlHeader', SRB_IO_CONTROL),
        ('Information', CSMI_SAS_RAID_INFO),
    ]
    _pack_ = 1

# typedef struct _CSMI_SAS_RAID_DRIVES
# {
#     BYTE                            bModel[40];
#     BYTE                            bFirmware[8];
#     BYTE                            bSerialNumber[40];
#     BYTE                            bSASAddress[8];
#     BYTE                            bSASLun[8];
#     BYTE                            bDriveStatus;
#     BYTE                            bDriveUsage;
#     BYTE                            bReserved[30];

# } CSMI_SAS_RAID_DRIVES, *PCSMI_SAS_RAID_DRIVES;
class CSMI_SAS_RAID_DRIVES(Structure):
    _fields_ = [
        ('bModel', c_ubyte * 40),
        ('bFirmware', c_ubyte * 8),
        ('bSerialNumber', c_ubyte * 40),
        ('bSASAddress', c_ubyte * 8),
        ('bSASLun', c_ubyte * 8),
        ('bDriveStatus', c_ubyte),
        ('bDriveUsage', c_ubyte),
        ('bReserved', c_ubyte * 30),
    ]
    _pack_ = 1

# typedef struct _CSMI_SAS_RAID_CONFIG
# {
#     DWORD                           uRaidSetIndex;
#     DWORD                           uCapacity;
#     DWORD                           uStripeSize;
#     BYTE                            bRaidType;
#     BYTE                            bStatus;
#     BYTE                            bInformation;
#     BYTE                            bDriveCount;
#     BYTE                            bReserved[20];
#     CSMI_SAS_RAID_DRIVES            Drives[1];

# } CSMI_SAS_RAID_CONFIG, *PCSMI_SAS_RAID_CONFIG;
class CSMI_SAS_RAID_CONFIG(Structure):
    _fields_ = [
        ('uRaidSetIndex', c_uint32),
        ('uCapacity', c_uint32),
        ('uStripeSize', c_uint32),
        ('bRaidType', c_uint8),
        ('bStatus', c_uint8),
        ('bInformation', c_uint8),
        ('bDriveCount', c_uint8),
        ('bReserved', c_ubyte * 20),
        ('Drives', CSMI_SAS_RAID_DRIVES * 1),
    ]
    _pack_ = 1

# typedef struct _CSMI_SAS_RAID_CONFIG_BUFFER
# {
#     IOCTL_HEADER                    IoctlHeader;
#     CSMI_SAS_RAID_CONFIG            Configuration;

# } CSMI_SAS_RAID_CONFIG_BUFFER, *PCSMI_SAS_RAID_CONFIG_BUFFER;
class CSMI_SAS_RAID_CONFIG_BUFFER(Structure):
    _fields_ = [
        ('IoctlHeader', SRB_IO_CONTROL),
        ('Configuration', CSMI_SAS_RAID_CONFIG),
    ]
    _pack_ = 1

# typedef struct _CSMI_SAS_STP_PASSTHRU
# {
#     BYTE                            bPhyIdentifier;
#     BYTE                            bPortIdentifier;
#     BYTE                            bConnectionRate;
#     BYTE                            bReserved;
#     BYTE                            bDestinationSASAddress[8];
#     BYTE                            bReserved2[4];
#     BYTE                            bCommandFIS[20];
#     DWORD                           uFlags;
#     DWORD                           uDataLength;

# } CSMI_SAS_STP_PASSTHRU, *PCSMI_SAS_STP_PASSTHRU;
class CSMI_SAS_STP_PASSTHRU(Structure):
    _fields_ = [
        ('bPhyIdentifier', c_uint8),
        ('bPortIdentifier', c_uint8),
        ('bConnectionRate', c_uint8),
        ('bReserved', c_uint8),
        ('bDestinationSASAddress', c_uint8 * 8),
        ('bReserved2', c_uint8 * 4),
        ('bCommandFIS', c_uint8 * 20),
        ('uFlags', c_uint32),
        ('uDataLength', c_uint32),
    ]
    _pack_ = 1

# typedef struct _CSMI_SAS_STP_PASSTHRU_STATUS
# {
#     BYTE                            bConnectionStatus;
#     BYTE                            bReserved[3];
#     BYTE                            bStatusFIS[20];
#     DWORD                           uSCR[16];
#     DWORD                           uDataBytes;

# } CSMI_SAS_STP_PASSTHRU_STATUS, *PCSMI_SAS_STP_PASSTHRU_STATUS;
class CSMI_SAS_STP_PASSTHRU_STATUS(Structure):
    _fields_ = [
        ('bConnectionStatus', c_uint8),
        ('bReserved', c_uint8 * 3),
        ('bStatusFIS', c_uint8 * 20),
        ('uSCR', c_uint32 * 16),
        ('uDataBytes', c_uint32),
    ]
    _pack_ = 1

# typedef struct _CSMI_SAS_STP_PASSTHRU_BUFFER
# {
#     IOCTL_HEADER                    IoctlHeader;
#     CSMI_SAS_STP_PASSTHRU           Parameters;
#     CSMI_SAS_STP_PASSTHRU_STATUS    Status;
#     BYTE                            bDataBuffer[1];

# } CSMI_SAS_STP_PASSTHRU_BUFFER, *PCSMI_SAS_STP_PASSTHRU_BUFFER;
class CSMI_SAS_STP_PASSTHRU_BUFFER(Structure):
    _fields_ = [
        ('IoctlHeader', SRB_IO_CONTROL),
        ('Parameters', CSMI_SAS_STP_PASSTHRU),
        ('Status', CSMI_SAS_STP_PASSTHRU_STATUS),
        ('bDataBuffer', c_ubyte * 1),
    ]
    _pack_ = 1

##
class COMPLETION_QUEUE_ENTRY(Structure):
    _fields_ = [
        ('CommandSpecific', c_uint32),
        ('Reserved', c_uint32),
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
NVME_IOCTL_PASS_THROUGH_LEN_ALIGNED = roundupdw(NVME_IOCTL_PASS_THROUGH_LEN)

def Get_NVME_IOCTL_PASS_THROUGH_ALIGNED_WITH_BUFFER(buffer_length):
    class NVME_IOCTL_PASS_THROUGH_WITH_BUFFER(Structure):
        _fields_ = [
            ('NVME_IOCTL_PASS_THROUGH', NVME_IOCTL_PASS_THROUGH),
            ("Padding", c_uint8 * (NVME_IOCTL_PASS_THROUGH_LEN_ALIGNED - NVME_IOCTL_PASS_THROUGH_LEN)),  # keep DW aligned
            ('DataBuffer', c_ubyte*roundupdw(buffer_length)),  # DW
        ]

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
            return bytes(self)[0:sizeof(NVME_IOCTL_PASS_THROUGH)]

        @property
        def data_buf(self):
            return self.DataBuffer

        def data(self):
            if NVME_IOCTL_PASS_THROUGH_LEN_ALIGNED != NVME_IOCTL_PASS_THROUGH_LEN:
                return bytes(self.DataBuffer)[0:(NVME_IOCTL_PASS_THROUGH_LEN-NVME_IOCTL_PASS_THROUGH_LEN_ALIGNED)]
            else:
                return bytes(self.DataBuffer)
    return NVME_IOCTL_PASS_THROUGH_WITH_BUFFER
