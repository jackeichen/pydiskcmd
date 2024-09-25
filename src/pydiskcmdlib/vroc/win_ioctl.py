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
from pydiskcmdlib.os.win_ioctl_structures import SRB_IO_CONTROL
from pydiskcmdlib.os.win_ioctl_utils import (
    CTL_CODE,
    NVME_STORPORT_DRIVER,
    METHOD_BUFFERED,
    FILE_ANY_ACCESS
)
from pydiskcmdlib.pynvme.win_nvme_command import NVME_COMMAND

SRB_IO_CONTROL_LEN = sizeof(SRB_IO_CONTROL)
#########
NVME_NO_DATA_TX       = 0 # No data transfer involved
NVME_FROM_HOST_TO_DEV = 1 # Transfer data from host to device
NVME_FROM_DEV_TO_HOST = 2 # Transfer data from device to host 

NVME_RAID_SIG_STR = "NvmeRAID"
NVME_RAID_SIG_STR_LEN = 8
NVME_STORPORT_DRIVER = 0xE000
NVME_PT_TIMEOUT = 40

NVME_GET_NUMBER_OF_RAID_VOLUMES = CTL_CODE(NVME_STORPORT_DRIVER, 0x805, METHOD_BUFFERED, FILE_ANY_ACCESS)
NVME_GET_RAID_INFORMATION = CTL_CODE(NVME_STORPORT_DRIVER, 0x806, METHOD_BUFFERED, FILE_ANY_ACCESS)
NVME_GET_RAID_CONFIGURATION = CTL_CODE(NVME_STORPORT_DRIVER, 0x807, METHOD_BUFFERED, FILE_ANY_ACCESS)
NVME_PASS_THROUGH_SRB_IO_CODE = CTL_CODE(NVME_STORPORT_DRIVER, 0x800, METHOD_BUFFERED, FILE_ANY_ACCESS)
NVME_GET_NUMBER_OF_SPARE_DISKS = CTL_CODE(NVME_STORPORT_DRIVER, 0x808, METHOD_BUFFERED, FILE_ANY_ACCESS)
NVME_GET_SPARE_DISKS_INFORMATION = CTL_CODE(NVME_STORPORT_DRIVER, 0x809, METHOD_BUFFERED, FILE_ANY_ACCESS)
NVME_GET_NUMBER_OF_PASSTHROUGH_DISKS = CTL_CODE(NVME_STORPORT_DRIVER, 0x80A, METHOD_BUFFERED, FILE_ANY_ACCESS)
NVME_GET_PASSTHROUGH_DISKS_INFORMATION = CTL_CODE(NVME_STORPORT_DRIVER, 0x80B, METHOD_BUFFERED, FILE_ANY_ACCESS)
NVME_GET_NUMBER_OF_JOURNALING_DRIVES = CTL_CODE(NVME_STORPORT_DRIVER, 0x80C, METHOD_BUFFERED, FILE_ANY_ACCESS)
NVME_GET_JOURNALING_DRIVES_INFORMATION = CTL_CODE(NVME_STORPORT_DRIVER, 0x80D, METHOD_BUFFERED, FILE_ANY_ACCESS)
#########
class NVME_GET_NUMBER_OF_DEVCICES(Structure):
    _fields_ = [
        ('SrbIoCtrl', SRB_IO_CONTROL),
        ('numberOfDevices', c_uint32),  # it may RaidVolumes Or SpareDisks Or PASSTHROUGH_DISKS Or JOURNALING_DRIVES
    ]
    _pack_ = 1

    @property
    def command_buf(self):
        return self

    @property
    def data_buf(self):
        return None


class NVME_GET_DRIVES_INFORMATION(Structure):
    _fields_ = [
        ('SrbIoCtrl', SRB_IO_CONTROL),
        ('ReturnBufferLen', c_uint32),
        ('DataBuffer', c_ubyte),
    ]
    _pack_ = 1

    @property
    def command_buf(self):
        return self

    @property
    def data_buf(self):
        return None


class NVME_RAID_PASS_THROUGH_IOCTL(Structure):
    _fields_ = [
        ('SrbIoCtrl', SRB_IO_CONTROL),
        ('VendorSpecific', c_uint32 * 6),
        ('NVMeCmd', NVME_COMMAND),
        ('CplEntry', c_uint32 * 4),
        ('Direction', c_uint32),
        ('QueueId', c_uint32),
        ('DataBufferLen', c_uint32),
        ('MetaDataLen', c_uint32),
        ('ReturnBufferLen', c_uint32),
        ('DataBuffer', c_ubyte),
    ]
    _pack_ = 1 

    @property
    def command_buf(self):
        return self

    @property
    def data_buf(self):
        return None

# typedef struct _NVME_GET_RAID_CONFIGURATION_IOCTL {
#  SRB_IO_CONTROL SrbIoCtrl;
#  ULONG indexOfRaidVolume;
#  ULONG ReturnBufferLen;
#  UCHAR DataBuffer[1];
# } NVME_GET_RAID_CONFIGURATION_IOCTL, *PNVME_GET_RAID_CONFIGURATION_IOCTL;
class NVME_GET_RAID_CONFIGURATION_IOCTL(Structure):
    _fields_ = [
        ('SrbIoCtrl', SRB_IO_CONTROL),
        ('indexOfRaidVolume', c_uint32),
        ('ReturnBufferLen', c_uint32),
        ('DataBuffer', c_ubyte),
    ]
    _pack_ = 1

    @property
    def command_buf(self):
        return self

    @property
    def data_buf(self):
        return None


class NVME_GET_RAID_INFORMATION_IOCTL(Structure):
    _fields_ = [
        ('SrbIoCtrl', SRB_IO_CONTROL),
        ('indexOfRaidVolume', c_uint32),
        ('raidType', c_ubyte * 8),
        ('model', c_ubyte * 40),
        ('firmwareVersion', c_ubyte * 8),
        ('serialNumber', c_ubyte * 40),
        ('numberOfMemberDisks', c_uint32),
    ]
    _pack_ = 1 

    @property
    def command_buf(self):
        return self

    @property
    def data_buf(self):
        return None


class NVME_MEMBER_DISK_INFORMATION(Structure):
    _fields_ = [
        ('vrocDiskID', c_uint32),
        ('diskModel', c_ubyte * 40),
        ('firmwareVersion', c_ubyte * 8),
        ('serialNumber', c_ubyte * 40),
        ('socketNumber', c_uint32),
        ('vmdControllerNumber', c_uint32),
        ('rootPortOffset', c_uint32),
        ('slotNumber', c_uint32),
    ]
    _pack_ = 1 

    @property
    def command_buf(self):
        return self

    @property
    def data_buf(self):
        return None


def GetVendorSpecIOCTL(data_len: int):
    class VENDOR_SPEC_IOCTL(Structure):
        _fields_ = [
            ('SrbIoCtrl', SRB_IO_CONTROL),
            ('VendorSpecData', c_uint8*data_len),
        ]

        @property
        def command_buf(self):
            return None

        @property
        def data_buf(self):
            return self.VendorSpecData
    return VENDOR_SPEC_IOCTL

def GetNVMeRaidPassThroughIOCTLWithBuffer(buffer_length: int):
    class NVME_RAID_PASS_THROUGH_IOCTL_WITH_BUFFER(Structure):
        _fields_ = [
            ('SrbIoCtrl', SRB_IO_CONTROL),
            ('VendorSpecific', c_uint32 * 6),
            ('NVMeCmd', NVME_COMMAND),
            ('CplEntry', c_uint32 * 4),
            ('Direction', c_uint32),
            ('QueueId', c_uint32),
            ('DataBufferLen', c_uint32),
            ('MetaDataLen', c_uint32),
            ('ReturnBufferLen', c_uint32),
            ('DataBuffer', c_ubyte*(buffer_length+1)),
        ]
        _pack_ = 1

        @property
        def command_buf(self):
            return bytes(self)[0:sizeof(NVME_RAID_PASS_THROUGH_IOCTL)]

        @property
        def data_buf(self):
            return self.DataBuffer
    return NVME_RAID_PASS_THROUGH_IOCTL_WITH_BUFFER

def GetNVMeGetRaidConfigurationIOCTLWithBuffer(buffer_length: int):
    class NVME_GET_RAID_CONFIGURATION_IOCTL_WITH_BUFFER(Structure):
        _fields_ = [
            ('SrbIoCtrl', SRB_IO_CONTROL),
            ('indexOfRaidVolume', c_uint32),
            ('ReturnBufferLen', c_uint32),
            ('DataBuffer', c_ubyte*(buffer_length+1)),
        ]
        _pack_ = 1

        @property
        def command_buf(self):
            return bytes(self)[0:sizeof(NVME_GET_RAID_CONFIGURATION_IOCTL)]

        @property
        def data_buf(self):
            return self.DataBuffer
    return NVME_GET_RAID_CONFIGURATION_IOCTL_WITH_BUFFER


def GetNVMeGetDrivesInformationWithBuffer(buffer_length: int):
    class NVME_GET_DRIVES_INFORMATION_WITH_BUFFER(Structure):
        _fields_ = [
            ('SrbIoCtrl', SRB_IO_CONTROL),
            ('ReturnBufferLen', c_uint32),
            ('DataBuffer', c_ubyte*(buffer_length+1)),
        ]
        _pack_ = 1

        @property
        def command_buf(self):
            return bytes(self)[0:sizeof(NVME_GET_DRIVES_INFORMATION)]

        @property
        def data_buf(self):
            return self.DataBuffer
    return NVME_GET_DRIVES_INFORMATION_WITH_BUFFER
