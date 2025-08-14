# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from ctypes import (Structure,
                    c_int,
                    c_uint8,
                    c_int8,
                    c_uint16,
                    c_uint32,
                    c_uint64,
                    c_ubyte,
                    sizeof,
                    c_ulonglong,
                    Union,
                    )
from pydiskcmdlib.os.win_ioctl_structures import (SRB_IO_CONTROL,
                                                  roundupdw,
                                                  GENERIC_COMMAND,
                                                  SRB_IO_CONTROL_LEN,
                                                  FIRMWARE_REQUEST_BLOCK,
                                                  STORAGE_FIRMWARE_INFO_V2,
                                                  Get_STORAGE_FIRMWARE_INFO_V2,
                                                  Get_STORAGE_FIRMWARE_INFO,
)
from .win_ioctl_utils import AEN_MAX_EVENT_NAME_LENGTH,NVME_GET_AER_DATA_MAX_COMPLETIONS

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
NVME_IOCTL_PASS_THROUGH_LEN_DW_ALIGNED = roundupdw(NVME_IOCTL_PASS_THROUGH_LEN)

def Get_NVME_IOCTL_PASS_THROUGH_ALIGNED_WITH_BUFFER(buffer_length):
    class NVME_IOCTL_PASS_THROUGH_WITH_BUFFER(Structure):
        _fields_ = [
            ('NVME_IOCTL_PASS_THROUGH', NVME_IOCTL_PASS_THROUGH),
            ("Padding", c_uint8 * (NVME_IOCTL_PASS_THROUGH_LEN_DW_ALIGNED - NVME_IOCTL_PASS_THROUGH_LEN)),  # keep DW aligned of NVME_IOCTL_PASS_THROUGH
            ('DataBuffer', c_ubyte* buffer_length),  # DW
            ('PaddingDataBuffer', c_uint8 * (roundupdw(buffer_length) - buffer_length)),  # keep DW aligned of DataBuffer
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

# struct RAID_FIRMWARE_REQUEST_BLOCK {
#  UCHAR Version;
#  UCHAR PathID;
#  UCHAR TargetID;
#  UCHAR Lun;
#  FIRMWARE_REQUEST_BLOCK FwRequestBlock; // from ntddscsi.h
# };
class RAID_FIRMWARE_REQUEST_BLOCK(Structure):
    _fields_ = [
        ('Version', c_uint8),
        ('PathID', c_uint8),
        ('TargetID', c_uint8),
        ('Lun', c_uint8),
        ('FwRequestBlock', FIRMWARE_REQUEST_BLOCK),
    ]
    _pack_ = 1

# struct IOCTL_RAID_FIRMWARE_BUFFER {
#  SRB_IO_CONTROL Header; // from ntddscsi.h
#  RAID_FIRMWARE_REQUEST_BLOCK Request;
# };
class IOCTL_RAID_FIRMWARE_BUFFER(Structure):
    _fields_ = [
        ('Header', SRB_IO_CONTROL),
        ('Request', RAID_FIRMWARE_REQUEST_BLOCK),
    ]
    _pack_ = 1


class DEV_FIRMWARE_INFO_M1(Structure):
    from pydiskcmdlib.os.win_ioctl_structures import PVOID
    temp = (SRB_IO_CONTROL_LEN+sizeof(RAID_FIRMWARE_REQUEST_BLOCK)) % sizeof(PVOID)
    padding = 0 if temp == 0 else (sizeof(PVOID) - temp)
    # Set max 7 firmware info here
    _fields_ = [
        ('Header', SRB_IO_CONTROL),
        ('Request', RAID_FIRMWARE_REQUEST_BLOCK),
        ('Padding', c_uint8 * padding),
        ('FirmwareInfo', Get_STORAGE_FIRMWARE_INFO(1)),
    ]
    _pack_ = 1


class DEV_FIRMWARE_INFO_V2_M7(Structure):
    from pydiskcmdlib.os.win_ioctl_structures import PVOID
    temp = (SRB_IO_CONTROL_LEN+sizeof(RAID_FIRMWARE_REQUEST_BLOCK)) % sizeof(PVOID)
    padding = 0 if temp == 0 else (sizeof(PVOID) - temp)
    # Set max 7 firmware info here
    _fields_ = [
        ('Header', SRB_IO_CONTROL),
        ('Request', RAID_FIRMWARE_REQUEST_BLOCK),
        ('Padding', c_uint8 * padding),
        ('FirmwareInfo', Get_STORAGE_FIRMWARE_INFO_V2(7)),
    ]
    _pack_ = 1

# typedef struct _RAIDPORT_REGISTER_SHARED_EVENT {
#  U8 eventName[AEN_MAX_EVENT_NAME_LENGTH];
#  U8 reserved;
#  U64 eventMask;
# } RAIDPORT_REGISTER_SHARED_EVENT;
class RAIDPORT_REGISTER_SHARED_EVENT(Structure):
    _fields_ = [
        ('eventName', c_uint8 * AEN_MAX_EVENT_NAME_LENGTH),
        ('reserved', c_uint8),
        ('eventMask', c_uint64),
    ]
    _pack_ = 1

# struct NVME_IOCTL_REGISTER_AER {
#  SRB_IO_CONTROL Header;
#  RAIDPORT_REGISTER_SHARED_EVENT EventData;
# };
# Main Structures
class NVME_IOCTL_REGISTER_AER(Structure):
    _fields_ = [
        ('Header', SRB_IO_CONTROL),
        ('EventData', RAIDPORT_REGISTER_SHARED_EVENT),
    ]
    _pack_ = 1

# struct ADMIN_ASYNCHRONOUS_EVENT_REQUEST_COMPLETION_DW0 {
#  union {
#  struct {
#  U32 AsynchronousEventType : 3;
#  U32 Reserved1 : 5;
#  U32 AsynchronousEventInformation : 8;
#  U32 AssociatedLogPage : 8;
#  U32 Reserved2 : 8;
#  };
#  U32 Raw;
#  };
# };
class ADMIN_ASYNCHRONOUS_EVENT_REQUEST_COMPLETION_DW0_INFO(Structure):
    _fields_ = [
        ('AsynchronousEventType', c_uint32, 3),
        ('Reserved1', c_uint32, 5),
        ('AsynchronousEventInformation', c_uint32, 8),
        ('AssociatedLogPage', c_uint32, 8),
        ('Reserved2', c_uint32, 8),
    ]

class ADMIN_ASYNCHRONOUS_EVENT_REQUEST_COMPLETION_DW0(Union):
    _fields_ = [
        ('Info', ADMIN_ASYNCHRONOUS_EVENT_REQUEST_COMPLETION_DW0_INFO),
        ('Raw', c_uint32),
    ]
    _pack_ = 1

# struct NVME_AER_DATA {
#  U8 eventName[AEN_MAX_EVENT_NAME_LENGTH];
#  U8 reserved;
#  ADMIN_ASYNCHRONOUS_EVENT_REQUEST_COMPLETION_DW0
# Completions[NVME_GET_AER_DATA_MAX_COMPLETIONS];
#  UINT32 CompletionsCount;
# };
class NVME_AER_DATA(Structure):
    _fields_ = [
        ('eventName', c_uint8 * AEN_MAX_EVENT_NAME_LENGTH),
        ('reserved', c_uint8),
        ('Completions', ADMIN_ASYNCHRONOUS_EVENT_REQUEST_COMPLETION_DW0 * NVME_GET_AER_DATA_MAX_COMPLETIONS),
        ('CompletionsCount', c_uint32),
    ]
    _pack_ = 1

# struct NVME_IOCTL_GET_AER_DATA {
#  SRB_IO_CONTROL Header;
#  NVME_AER_DATA Data;
# };
# Main Structures
class NVME_IOCTL_GET_AER_DATA(Structure):
    _fields_ = [
        ('Header', SRB_IO_CONTROL),
        ('Data', NVME_AER_DATA),
    ]
    _pack_ = 1

# struct REMAPPORT_LOCATION_PCI_BDF
# {
# UCHAR Bus;
# UCHAR Device : 5;
# UCHAR Function : 3;
# } REMAPPORT_LOCATION_PCI_BDF;
class REMAPPORT_LOCATION_PCI_BDF(Structure):
    _fields_ = [
        ('Bus', c_uint8),
        ('Device', c_uint8, 5),
        ('Function', c_uint8, 3),
    ]
    _pack_ = 1

# struct REMAPPORT_LOCATION_SATA
# {
# UCHAR PortNumber;
# };
# struct REMAPPORT_LOCATION_CR
# {
# UCHAR CycleRouterNumber;
# };
# struct REMAPPORT_LOCATION_SW_REMAP
# {
# REMAPPORT_LOCATION_PCI_BDF PciAddress;
# };
class REMAPPORT_LOCATION_SATA(Structure):
    _fields_ = [
        ('PortNumber', c_uint8),
    ]
    _pack_ = 1

class REMAPPORT_LOCATION_CR(Structure):
    _fields_ = [
        ('CycleRouterNumber', c_uint8),
    ]
    _pack_ = 1

class REMAPPORT_LOCATION_SW_REMAP(Structure):
    _fields_ = [
        ('PciAddress', REMAPPORT_LOCATION_PCI_BDF),
    ]
    _pack_ = 1

# struct REMAPPORT_LOCATION_VMD
# {
# USHORT SocketNumber;
# USHORT ControllerNumber;
# // Device's root port Bus/Device/Function
# REMAPPORT_LOCATION_PCI_BDF RootPortAddress;
# // Physical slot number from SLCAP.PSN field in
# // devices root port's PCI Express Capability
# USHORT PhysicalSlotNumber;
# };
class REMAPPORT_LOCATION_VMD(Structure):
    _fields_ = [
        ('SocketNumber', c_uint16),
        ('ControllerNumber', c_uint16),
        ('RootPortAddress', REMAPPORT_LOCATION_PCI_BDF),
        ('PhysicalSlotNumber', c_uint16),
    ]
    _pack_ = 1

# struct REMAPPORT_IOCTL_GET_DEVICE_LOCATION
# {
# SRB_IO_CONTROL srbIoControl;
# UCHAR Version; // version 1
# UCHAR Size; // sizeof this struct
# UCHAR PathId;
# UCHAR TargetId;
# UCHAR Lun;
# REMAPPORT_LOCATION_TYPE LocationType;
# union {
# REMAPPORT_LOCATION_SATA Sata;
# REMAPPORT_LOCATION_CR CR;
# REMAPPORT_LOCATION_SW_REMAP SwRemap;
# REMAPPORT_LOCATION_VMD Vmd;
# } Location;
# };
# #pragma pack(pop, remapport_ioctl)
class Location_UNION(Union):
    _fields_ = [
        ('Sata', REMAPPORT_LOCATION_SATA),
        ('CR', REMAPPORT_LOCATION_CR),
        ('SwRemap', REMAPPORT_LOCATION_SW_REMAP),
        ('Vmd', REMAPPORT_LOCATION_VMD),
    ]
    _pack_ = 1

class REMAPPORT_IOCTL_GET_DEVICE_LOCATION(Structure):
    _fields_ = [
        ('srbIoControl', SRB_IO_CONTROL),
        ('Version', c_uint8),
        ('Size', c_uint8),
        ('PathId', c_uint8),
        ('TargetId', c_uint8),
        ('Lun', c_uint8),
        ('LocationType', c_int),
        ('Location', Location_UNION),
    ]
    _pack_ = 1

