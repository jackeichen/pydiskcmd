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
from pydiskcmdlib.os.win_ioctl_structures import SRB_IO_CONTROL,SRB_IO_CONTROL_LEN

#################################
# Important: The Structure should be DW aligned
# 
#################################
BytesAligned = 4
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
        ('Padding', c_ubyte * 2),
    ]
    _pack_ = 1

CSMI_SAS_DRIVER_INFO_BUFFER_LEN = sizeof(CSMI_SAS_DRIVER_INFO_BUFFER)

##
# typedef struct _CSMI_SAS_PCI_BUS_ADDRESS {
#  __u8 bBusNumber; 
#  __u8 bDeviceNumber; 
#  __u8 bFunctionNumber; 
#  __u8 bReserved; 
# } CSMI_SAS_PCI_BUS_ADDRESS,
class CSMI_SAS_PCI_BUS_ADDRESS(Structure):
    _fields_ = [
        ('bBusNumber', c_uint8),
        ('bDeviceNumber', c_uint8),
        ('bFunctionNumber', c_uint8),
        ('bReserved', c_uint8),
    ]
    _pack_ = 1

# typedef union _CSMI_SAS_IO_BUS_ADDRESS {
#  CSMI_SAS_PCI_BUS_ADDRESS PciAddress; 
#  __u8 bReserved[32]; 
# } CSMI_SAS_IO_BUS_ADDRESS,
class CSMI_SAS_IO_BUS_ADDRESS(Structure):
    _fields_ = [
        ('PciAddress', CSMI_SAS_PCI_BUS_ADDRESS),
        ('bReserved', c_uint8 * 32),
    ]
    _pack_ = 1

# typedef struct _CSMI_SAS_CNTLR_CONFIG {
#  __u32 uBaseIoAddress; 
#  struct {
#  __u32 uLowPart; 
#  __u32 uHighPart; 
#  } BaseMemoryAddress; 
#  __u32 uBoardID; 
#  __u16 usSlotNumber; 
#  __u8 bControllerClass; 
#  __u8 bIoBusType; 
#  CSMI_SAS_IO_BUS_ADDRESS BusAddress; 
#  __u8 szSerialNumber[81]; 
#  __u16 usMajorRevision; 
#  __u16 usMinorRevision; 
#  __u16 usBuildRevision; 
#  __u16 usReleaseRevision; 
#  __u16 usBIOSMajorRevision; 
#  __u16 usBIOSMinorRevision; 
#  __u16 usBIOSBuildRevision; 
#  __u16 usBIOSReleaseRevision; 
#  __u32 uControllerFlags; 
#  __u16 usRromMajorRevision; 
#  __u16 usRromMinorRevision; 
#  __u16 usRromBuildRevision; 
#  __u16 usRromReleaseRevision; 
#  __u16 usRromBIOSMajorRevision; 
#  __u16 usRromBIOSMinorRevision; 
#  __u16 usRromBIOSBuildRevision; 
#  __u16 usRromBIOSReleaseRevision; 
#  __u8 bReserved[7]; 
# } CSMI_SAS_CNTLR_CONFIG,
class BaseMemoryAddress(Structure):
    _fields_ = [
        ('uLowPart', c_uint32),
        ('uHighPart', c_uint32),
    ]
    _pack_ = 1

class CSMI_SAS_CNTLR_CONFIG(Structure):
    _fields_ = [
        ('uBaseIoAddress', c_uint32),
        ('BaseMemoryAddress', BaseMemoryAddress),
        ('uBoardID', c_uint32),
        ('usSlotNumber', c_uint16),
        ('bControllerClass', c_uint8),
        ('bIoBusType', c_uint8),
        ('BusAddress', CSMI_SAS_IO_BUS_ADDRESS),
        ('szSerialNumber', c_ubyte * 81),
        ('usMajorRevision', c_uint16),
        ('usMinorRevision', c_uint16),
        ('usBuildRevision', c_uint16),
        ('usReleaseRevision', c_uint16),
        ('usBIOSMajorRevision', c_uint16),
        ('usBIOSMinorRevision', c_uint16),
        ('usBIOSBuildRevision', c_uint16),
        ('usBIOSReleaseRevision', c_uint16),
        ('uControllerFlags', c_uint32),
        ('usRromMajorRevision', c_uint16),
        ('usRromMinorRevision', c_uint16),
        ('usRromBuildRevision', c_uint16),
        ('usRromReleaseRevision', c_uint16),
        ('usRromBIOSMajorRevision', c_uint16),
        ('usRromBIOSMinorRevision', c_uint16),
        ('usRromBIOSBuildRevision', c_uint16),
        ('usRromBIOSReleaseRevision', c_uint16),
        ('bReserved', c_uint8 * 7),
    ]
    _pack_ = 1

# typedef struct _CSMI_SAS_CNTLR_CONFIG_BUFFER {
#  IOCTL_HEADER IoctlHeader; 
#  CSMI_SAS_CNTLR_CONFIG Configuration; 
# } CSMI_SAS_CNTLR_CONFIG_BUFFER, 
#  *PCSMI_SAS_CNTLR_CONFIG_BUFFER;
class CSMI_SAS_CNTLR_CONFIG_BUFFER(Structure):
    _fields_ = [
        ('IoctlHeader', SRB_IO_CONTROL),
        ('Configuration', CSMI_SAS_CNTLR_CONFIG),
    ]
    _pack_ = 1
##
# typedef struct _CSMI_SAS_CNTLR_STATUS {
#  __u32 uStatus; 
#  __u32 uOfflineReason; 
#  __u8 bReserved[28]; 
# } CSMI_SAS_CNTLR_STATUS, 
#  *PCSMI_SAS_CNTLR_STATUS;
class CSMI_SAS_CNTLR_STATUS(Structure):
    _fields_ = [
        ('uStatus', c_uint32),
        ('uOfflineReason', c_uint32),
        ('bReserved', c_uint8 * 28),
    ]
    _pack_ = 1

# typedef struct _CSMI_SAS_CNTLR_STATUS_BUFFER {
#  IOCTL_HEADER IoctlHeader; 
#  CSMI_SAS_CNTLR_STATUS Status; 
# } CSMI_SAS_CNTLR_STATUS_BUFFER, 
#  *PCSMI_SAS_CNTLR_STATUS_BUFFER;
class CSMI_SAS_CNTLR_STATUS_BUFFER(Structure):
    _fields_ = [
        ('IoctlHeader', SRB_IO_CONTROL),
        ('Status', CSMI_SAS_CNTLR_STATUS),
    ]
    _pack_ = 1

##
# typedef struct _CSMI_SAS_FIRMWARE_DOWNLOAD {
#  __u32 uBufferLength; 
#  __u32 uDownloadFlags; 
#  __u8 bReserved[32]; 
#  __u16 usStatus; 
#  __u16 usSeverity; 
# } CSMI_SAS_FIRMWARE_DOWNLOAD, 
#  *PCSMI_SAS_FIRMWARE_DOWNLOAD;
class CSMI_SAS_FIRMWARE_DOWNLOAD(Structure):
    _fields_ = [
        ('uBufferLength', c_uint32),
        ('uDownloadFlags', c_uint32),
        ('bReserved', c_uint8 * 32),
        ('usStatus', c_uint16),
        ('usSeverity', c_uint16),
    ]
    _pack_ = 1

# typedef struct _CSMI_SAS_FIRMWARE_DOWNLOAD_BUFFER {
#  IOCTL_HEADER IoctlHeader; 
#  CSMI_SAS_FIRMWARE_DOWNLOAD Information; 
#  __u8 bDataBuffer[1]; 
# } CSMI_SAS_FIRMWARE_DOWNLOAD_BUFFER, 
#  *PCSMI_SAS_FIRMWARE_DOWNLOAD_BUFFER;
class CSMI_SAS_FIRMWARE_DOWNLOAD_BUFFER(Structure):
    _fields_ = [
        ('IoctlHeader', SRB_IO_CONTROL),
        ('Information', CSMI_SAS_FIRMWARE_DOWNLOAD),
        ('bDataBuffer', c_ubyte * 1),
    ]
    _pack_ = 1

def GET_CSMI_SAS_FIRMWARE_DOWNLOAD_BUFFER(data_len):
    padding_num = BytesAligned - ((SRB_IO_CONTROL_LEN + sizeof(CSMI_SAS_FIRMWARE_DOWNLOAD) + data_len) % BytesAligned)
    class CSMI_SAS_FIRMWARE_DOWNLOAD_BUFFER(Structure):
        _fields_ = [
            ('IoctlHeader', SRB_IO_CONTROL),
            ('Information', CSMI_SAS_FIRMWARE_DOWNLOAD),
            ('bDataBuffer', c_ubyte * data_len),
            ('Padding', c_ubyte * padding_num),
        ]
        _pack_ = 1
    return CSMI_SAS_FIRMWARE_DOWNLOAD_BUFFER
##
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

##
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

def GET_CSMI_SAS_RAID_CONFIG(drives_number):
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
            ('Drives', CSMI_SAS_RAID_DRIVES * drives_number),
        ]
        _pack_ = 1
    return CSMI_SAS_RAID_CONFIG
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

def GET_CSMI_SAS_RAID_CONFIG_BUFFER(drives_number):
    padding_num = BytesAligned - ((SRB_IO_CONTROL_LEN + sizeof(GET_CSMI_SAS_RAID_CONFIG(drives_number))) % BytesAligned)
    class CSMI_SAS_RAID_CONFIG_BUFFER(Structure):
        _fields_ = [
            ('IoctlHeader', SRB_IO_CONTROL),
            ('Configuration', GET_CSMI_SAS_RAID_CONFIG(drives_number)),
            ('Padding', c_ubyte * padding_num),
        ]
        _pack_ = 1
    return CSMI_SAS_RAID_CONFIG_BUFFER
##
# typedef struct _CSMI_SAS_IDENTIFY {
#  __u8 bDeviceType; 
#  __u8 bRestricted; 
#  __u8 bInitiatorPortProtocol; 
#  __u8 bTargetPortProtocol; 
#  __u8 bRestricted2[8]; 
#  __u8 bSASAddress[8]; 
#  __u8 bPhyIdentifier; 
#  __u8 bSignalClass;
#  __u8 bReserved[6]; 
# } CSMI_SAS_IDENTIFY, 
#  *PCSMI_SAS_IDENTIFY;
class CSMI_SAS_IDENTIFY(Structure):
    _fields_ = [
        ('bDeviceType', c_uint8),
        ('bRestricted', c_uint8),
        ('bInitiatorPortProtocol', c_uint8),
        ('bTargetPortProtocol', c_uint8),
        ('bRestricted2', c_uint8 * 8),
        ('bSASAddress', c_uint8 * 8),
        ('bPhyIdentifier', c_uint8),
        ('bSignalClass', c_uint8),
        ('bReserved', c_uint8 * 6),
    ]
    _pack_ = 1
# typedef struct _CSMI_SAS_PHY_ENTITY {
#  CSMI_SAS_IDENTIFY Identify; 
#  __u8 bPortIdentifier; 
#  __u8 bNegotiatedLinkRate; 
#  __u8 bMinimumLinkRate; 
#  __u8 bMaximumLinkRate; 
#  __u8 bPhyChangeCount; 
#  __u8 bAutoDiscover; 
#  __u8 bReserved[2];
#  CSMI_SAS_IDENTIFY Attached; 
# } CSMI_SAS_PHY_ENTITY, 
#  *PCSMI_SAS_PHY_ENTITY;
class CSMI_SAS_PHY_ENTITY(Structure):
    _fields_ = [
        ('Identify', CSMI_SAS_IDENTIFY),
        ('bPortIdentifier', c_uint8),
        ('bNegotiatedLinkRate', c_uint8),
        ('bMinimumLinkRate', c_uint8),
        ('bMaximumLinkRate', c_uint8),
        ('bPhyChangeCount', c_uint8),
        ('bAutoDiscover', c_uint8),
        ('bReserved', c_uint8 * 2),
        ('Attached', CSMI_SAS_IDENTIFY),
    ]
    _pack_ = 1

# typedef struct _CSMI_SAS_PHY_INFO {
#  __u8 bNumberOfPhys; 
#  __u8 bReserved[3]; 
#  CSMI_SAS_PHY_ENTITY Phy[32]; 
# } CSMI_SAS_PHY_INFO, 
#  *PCSMI_SAS_PHY_INFO;
class CSMI_SAS_PHY_INFO(Structure):
    _fields_ = [
        ('bNumberOfPhys', c_uint8),
        ('bReserved', c_uint8 * 3),
        ('Phy', CSMI_SAS_PHY_ENTITY * 32),
    ]
    _pack_ = 1

# typedef struct _CSMI_SAS_PHY_INFO_BUFFER {
#  IOCTL_HEADER IoctlHeader; 
#  CSMI_SAS_PHY_INFO Information; 
# } CSMI_SAS_PHY_INFO_BUFFER, 
#  *PCSMI_SAS_PHY_INFO_BUFFER;
class CSMI_SAS_PHY_INFO_BUFFER(Structure):
    _fields_ = [
        ('IoctlHeader', SRB_IO_CONTROL),
        ('Information', CSMI_SAS_PHY_INFO),
    ]
    _pack_ = 1
##
# typedef struct _CSMI_SAS_SET_PHY_INFO {
#  __u8 bPhyIdentifier; 
#  __u8 bNegotiatedLinkRate; 
#  __u8 bProgrammedMinimumLinkRate; 
#  __u8 bProgrammedMaximumLinkRate; 
#  __u8 bSignalClass;
#  __u8 bReserved[3]; 
# } CSMI_SAS_SET_PHY_INFO, 
#  *PCSMI_SAS_SET_PHY_INFO;
class CSMI_SAS_SET_PHY_INFO(Structure):
    _fields_ = [
        ('bPhyIdentifier', c_uint8),
        ('bNegotiatedLinkRate', c_uint8),
        ('bProgrammedMinimumLinkRate', c_uint8),
        ('bProgrammedMaximumLinkRate', c_uint8),
        ('bSignalClass', c_uint8),
        ('bReserved', c_uint8 * 3),
    ]
    _pack_ = 1

# typedef struct _CSMI_SAS_SET_PHY_INFO_BUFFER {
#  IOCTL_HEADER IoctlHeader; 
#  CSMI_SAS_SET_PHY_INFO Information; 
# } CSMI_SAS_SET_PHY_INFO_BUFFER, 
#  *PCSMI_SAS_SET_PHY_INFO_BUFFER;
class CSMI_SAS_SET_PHY_INFO_BUFFER(Structure):
    _fields_ = [
        ('IoctlHeader', SRB_IO_CONTROL),
        ('Information', CSMI_SAS_SET_PHY_INFO),
    ]
    _pack_ = 1

##
# typedef struct _CSMI_SAS_LINK_ERRORS {
#  __u8 bPhyIdentifier; 
#  __u8 bResetCounts; 
#  __u8 bReserved[2]; 
#  __u32 uInvalidDwordCount; 
#  __u32 uRunningDisparityErrorCount; 
#  __u32 uLossOfDwordSyncCount; 
#  __u32 uPhyResetProblemCount; 
# } CSMI_SAS_LINK_ERRORS, 
#  *PCSMI_SAS_LINK_ERRORS;
class CSMI_SAS_LINK_ERRORS(Structure):
    _fields_ = [
        ('bPhyIdentifier', c_uint8),
        ('bResetCounts', c_uint8),
        ('bReserved', c_uint8 * 2),
        ('uInvalidDwordCount', c_uint32),
        ('uRunningDisparityErrorCount', c_uint32),
        ('uLossOfDwordSyncCount', c_uint32),
        ('uPhyResetProblemCount', c_uint32),
    ]
    _pack_ = 1

# typedef struct _CSMI_SAS_LINK_ERRORS_BUFFER {
#  IOCTL_HEADER IoctlHeader; 
#  CSMI_SAS_LINK_ERRORS Information; 
# } CSMI_SAS_LINK_ERRORS_BUFFER, 
#  *PCSMI_SAS_LINK_ERRORS_BUFFER;
class CSMI_SAS_LINK_ERRORS_BUFFER(Structure):
    _fields_ = [
        ('IoctlHeader', SRB_IO_CONTROL),
        ('Information', CSMI_SAS_LINK_ERRORS),
    ]
    _pack_ = 1

##
# typedef struct _CSMI_SAS_SMP_REQUEST {
#  __u8 bFrameType; 
#  __u8 bFunction; 
#  __u8 bReserved[2]; 
#  __u8 bAdditionalRequestBytes[1016];
#  } CSMI_SAS_SMP_REQUEST, 
#  *PCSMI_SAS_SMP_REQUEST;
class CSMI_SAS_SMP_REQUEST(Structure):
    _fields_ = [
        ('bFrameType', c_uint8),
        ('bFunction', c_uint8),
        ('bReserved', c_uint8 * 2),
        ('bAdditionalRequestBytes', c_uint8 * 1016),
    ]
    _pack_ = 1

# typedef struct _CSMI_SAS_SMP_RESPONSE {
#  __u8 bFrameType; 
#  __u8 bFunction; 
#  __u8 bFunctionResult; 
#  __u8 bReserved; 
#  __u8 bAdditionalResponseBytes[1016]; 
# } CSMI_SAS_SMP_RESPONSE, 
#  *PCSMI_SAS_SMP_RESPONSE;
class CSMI_SAS_SMP_RESPONSE(Structure):
    _fields_ = [
        ('bResFrameType', c_uint8),
        ('bResFunction', c_uint8),
        ('bResFunctionResult', c_uint8),
        ('bResReserved', c_uint8),
        ('bResAdditionalResponseBytes', c_uint8 * 1016),
    ]
    _pack_ = 1

# typedef struct _CSMI_SAS_SMP_PASSTHRU {
#  __u8 bPhyIdentifier; 
#  __u8 bPortIdentifier; 
#  __u8 bConnectionRate; 
#  __u8 bReserved; 
#  __u8 bDestinationSASAddress[8]; 
#  __u32 uRequestLength; 
#  CSMI_SAS_SMP_REQUEST Request; 
#  __u8 bConnectionStatus; 
#  __u8 bReserved2[3]; 
#  __u32 uResponseBytes; 
#  CSMI_SAS_SMP_RESPONSE Response; 
# } CSMI_SAS_SMP_PASSTHRU, 
#  *PCSMI_SAS_SMP_PASSTHRU;
class CSMI_SAS_SMP_PASSTHRU(Structure):
    _fields_ = [
        ('bPhyIdentifier', c_uint8),
        ('bPortIdentifier', c_uint8),
        ('bConnectionRate', c_uint8),
        ('bReserved', c_uint8),
        ('bDestinationSASAddress', c_uint8 * 8),
        ('uRequestLength', c_uint32),
        ('Request', CSMI_SAS_SMP_REQUEST),
        ('bConnectionStatus', c_uint8),
        ('bReserved2', c_uint8 * 3),
        ('uResponseBytes', c_uint32),
        ('Response', CSMI_SAS_SMP_RESPONSE),
    ]
    _pack_ = 1

# typedef struct _CSMI_SMP_PASSTHRU_BUFFER {
#  IOCTL_HEADER IoctlHeader; 
#  CSMI_SAS_SMP_PASSTHRU Parameters; 
# } CSMI_SAS_SMP_PASSTHRU_BUFFER, 
#  *PCSMI_SAS_SMP_PASSTHRU_BUFFER;
class CSMI_SAS_SMP_PASSTHRU_BUFFER(Structure):
    _fields_ = [
        ('IoctlHeader', SRB_IO_CONTROL),
        ('Parameters', CSMI_SAS_SMP_PASSTHRU),
    ]
    _pack_ = 1

##
# typedef struct _CSMI_SAS_SSP_PASSTHRU {
#  __u8 bPhyIdentifier; 
#  __u8 bPortIdentifier; 
#  __u8 bConnectionRate; 
#  __u8 bReserved; 
#  __u8 bDestinationSASAddress[8]; 
#  __u8 bLun[8]; 
#  __u8 bCDBLength; 
#  __u8 bAdditionalCDBLength; 
#  __u8 bReserved2[2]; 
#  __u8 bCDB[16]; 
#  __u32 uFlags; 
#  __u8 bAdditionalCDB[24]; 
#  __u32 uDataLength; 
# } CSMI_SAS_SSP_PASSTHRU, 
#  *PCSMI_SAS_SSP_PASSTHRU;
class CSMI_SAS_SSP_PASSTHRU(Structure):
    _fields_ = [
        ('bPhyIdentifier', c_uint8),
        ('bPortIdentifier', c_uint8),
        ('bConnectionRate', c_uint8),
        ('bReserved1', c_uint8),
        ('bDestinationSASAddress', c_uint8 * 8),
        ('bLun', c_uint8 * 8),
        ('bCDBLength', c_uint8),
        ('bAdditionalCDBLength', c_uint8),
        ('bReserved2', c_uint8 * 2),
        ('bCDB', c_uint8 * 16),
        ('uFlags', c_uint32),
        ('bAdditionalCDB', c_uint8 * 24),
        ('uDataLength', c_uint32),
    ]
    _pack_ = 1

# typedef struct _CSMI_SAS_SSP_PASSTHRU_STATUS {
#  __u8 bConnectionStatus; 
#  __u8 bReserved[3]; 
#  __u8 bDataPresent; 
#  __u8 bStatus; 
#  __u8 bReponseLength[2]; 
#  __u8 bResponse[256]; 
#  __u32 uDataBytes; 
# } CSMI_SAS_SSP_PASSTHRU_STATUS, 
#  *PCSMI_SAS_SSP_PASSTHRU_STATUS;
class CSMI_SAS_SSP_PASSTHRU_STATUS(Structure):
    _fields_ = [
        ('bConnectionStatus', c_uint8),
        ('bReserved', c_uint8 * 3),
        ('bDataPresent', c_uint8),
        ('bStatus', c_uint8),
        ('bReponseLength', c_uint8 * 2),
        ('bResponse', c_uint8 * 256),
        ('uDataBytes', c_uint32),
    ]
    _pack_ = 1

# typedef struct _CSMI_SAS_SSP_PASSTHRU_BUFFER {
#  IOCTL_HEADER IoctlHeader; 
#  CSMI_SAS_SSP_PASSTHRU Parameters; 
#  CSMI_SAS_SSP_PASSTHRU_STATUS Status; 
#  __u8 bDataBuffer[1]; 
# } CSMI_SAS_SSP_PASSTHRU_BUFFER, 
#  *PCSMI_SAS_SSP_PASSTHRU_BUFFER;
class CSMI_SAS_SSP_PASSTHRU_BUFFER(Structure):
    _fields_ = [
        ('IoctlHeader', SRB_IO_CONTROL),
        ('Parameters', CSMI_SAS_SSP_PASSTHRU),
        ('Status', CSMI_SAS_SSP_PASSTHRU_STATUS),
        ('bDataBuffer', c_uint8 * 1),
    ]
    _pack_ = 1

def GET_CSMI_SAS_SSP_PASSTHRU_BUFFER(data_len):
    padding_num = BytesAligned - ((SRB_IO_CONTROL_LEN + sizeof(CSMI_SAS_SSP_PASSTHRU) + sizeof(CSMI_SAS_SSP_PASSTHRU_STATUS) + data_len) % BytesAligned)
    class CSMI_SAS_SSP_PASSTHRU_BUFFER(Structure):
        _fields_ = [
            ('IoctlHeader', SRB_IO_CONTROL),
            ('Parameters', CSMI_SAS_SSP_PASSTHRU),
            ('Status', CSMI_SAS_SSP_PASSTHRU_STATUS),
            ('bDataBuffer', c_uint8 * data_len),
            ('Padding', c_ubyte * padding_num),
        ]
        _pack_ = 1
    return CSMI_SAS_SSP_PASSTHRU_BUFFER

##
# typedef struct _CSMI_SAS_STP_PASSTHRU {
#  __u8 bPhyIdentifier; 
#  __u8 bPortIdentifier; 
#  __u8 bConnectionRate; 
#  __u8 bReserved; 
#  __u8 bDestinationSASAddress[8]; 
#  __u8 bReserved2[4]; 
#  __u8 bCommandFIS[20]; 
#  __u32 uFlags; 
#  __u32 uDataLength; 
# } CSMI_SAS_STP_PASSTHRU, 
#  *PCSMI_SAS_STP_PASSTHRU;
class CSMI_SAS_STP_PASSTHRU(Structure):
    _fields_ = [
        ('bPhyIdentifier', c_uint8),
        ('bPortIdentifier', c_uint8),
        ('bConnectionRate', c_uint8),
        ('bReserved1', c_uint8),
        ('bDestinationSASAddress', c_uint8 * 8),
        ('bReserved2', c_uint8 * 4),
        ('bCommandFIS', c_uint8 * 20),
        ('uFlags', c_uint32),
        ('uDataLength', c_uint32),
    ]
    _pack_ = 1

# typedef struct _CSMI_SAS_STP_PASSTHRU_STATUS {
#  __u8 bConnectionStatus; 
#  __u8 bReserved[3]; 
#  __u8 bStatusFIS[20]; 
#  __u32 uSCR[16]; 
#  __u32 uDataBytes; 
# } CSMI_SAS_STP_PASSTHRU_STATUS, 
#  *PCSMI_SAS_STP_PASSTHRU_STATUS;
class CSMI_SAS_STP_PASSTHRU_STATUS(Structure):
    _fields_ = [
        ('bConnectionStatus', c_uint8),
        ('bReserved', c_uint8 * 3),
        ('bStatusFIS', c_uint8 * 20),
        ('uSCR', c_uint32 * 16),
        ('uDataBytes', c_uint32),
    ]
    _pack_ = 1

# typedef struct _CSMI_SAS_STP_PASSTHRU_BUFFER {
#  IOCTL_HEADER IoctlHeader; 
#  CSMI_SAS_STP_PASSTHRU Parameters; 
#  CSMI_SAS_STP_PASSTHRU_STATUS Status; 
#  __u8 bDataBuffer[1]; 
# } CSMI_SAS_STP_PASSTHRU_BUFFER, 
#  *PCSMI_SAS_STP_PASSTHRU_BUFFER;
class CSMI_SAS_STP_PASSTHRU_BUFFER(Structure):
    _fields_ = [
        ('IoctlHeader', SRB_IO_CONTROL),
        ('Parameters', CSMI_SAS_STP_PASSTHRU),
        ('Status', CSMI_SAS_STP_PASSTHRU_STATUS),
        ('bDataBuffer', c_uint8 * 1),
    ]
    _pack_ = 1

def GET_CSMI_SAS_STP_PASSTHRU_BUFFER(data_len):
    padding_num = BytesAligned - ((SRB_IO_CONTROL_LEN + sizeof(CSMI_SAS_STP_PASSTHRU) + sizeof(CSMI_SAS_STP_PASSTHRU_STATUS) + data_len) % BytesAligned)
    class CSMI_SAS_STP_PASSTHRU_BUFFER(Structure):
        _fields_ = [
            ('IoctlHeader', SRB_IO_CONTROL),
            ('Parameters', CSMI_SAS_STP_PASSTHRU),
            ('Status', CSMI_SAS_STP_PASSTHRU_STATUS),
            ('bDataBuffer', c_uint8 * data_len),
            ('Padding', c_ubyte * padding_num),
        ]
        _pack_ = 1
    return CSMI_SAS_STP_PASSTHRU_BUFFER

##
# typedef struct _CSMI_SAS_SATA_SIGNATURE {
#  __u8 bPhyIdentifier; 
#  __u8 bReserved[3]; 
#  __u8 bSignatureFIS[20]; 
# } CSMI_SAS_SATA_SIGNATURE, 
#  *PCSMI_SAS_SATA_SIGNATURE;
class CSMI_SAS_SATA_SIGNATURE(Structure):
    _fields_ = [
        ('bPhyIdentifier', c_uint8),
        ('bReserved', c_uint8 * 3),
        ('bSignatureFIS', c_uint8 * 20),
    ]
    _pack_ = 1

# typedef struct _CSMI_SAS_SATA_SIGNATURE_BUFFER {
#  IOCTL_HEADER IoctlHeader; 
#  CSMI_SAS_SATA_SIGNATURE Signature; 
# } CSMI_SAS_SATA_SIGNATURE_BUFFER, 
#  *PCSMI_SAS_SATA_SIGNATURE_BUFFER;
class CSMI_SAS_SATA_SIGNATURE_BUFFER(Structure):
    _fields_ = [
        ('IoctlHeader', SRB_IO_CONTROL),
        ('Signature', CSMI_SAS_SATA_SIGNATURE),
    ]
    _pack_ = 1

##
# typedef struct _CSMI_SAS_GET_SCSI_ADDRESS_BUFFER {
#  IOCTL_HEADER IoctlHeader; 
#  __u8 bSASAddress[8]; 
#  __u8 bSASLun[8]; 
#  __u8 bHostIndex; 
#  __u8 bPathId; 
#  __u8 bTargetId; 
#  __u8 bLun; 
# } CSMI_SAS_GET_SCSI_ADDRESS_BUFFER, 
#  *PCSMI_SAS_GET_SCSI_ADDRESS_BUFFER;
class CSMI_SAS_GET_SCSI_ADDRESS_BUFFER(Structure):
    _fields_ = [
        ('IoctlHeader', SRB_IO_CONTROL),
        ('bSASAddress', c_uint8 * 8),
        ('bSASLun', c_uint8 * 8),
        ('bHostIndex', c_uint8),
        ('bPathId', c_uint8),
        ('bTargetId', c_uint8),
        ('bLun', c_uint8),
    ]
    _pack_ = 1

##
# typedef struct _CSMI_SAS_GET_DEVICE_ADDRESS_BUFFER {
#  IOCTL_HEADER IoctlHeader; 
#  __u8 bHostIndex; 
#  __u8 bPathId; 
#  __u8 bTargetId; 
#  __u8 bLun; 
#  __u8 bSASAddress[8]; 
#  __u8 bSASLun[8]; 
# } CSMI_SAS_GET_DEVICE_ADDRESS_BUFFER, 
#  *PCSMI_SAS_GET_DEVICE_ADDRESS_BUFFER;
class CSMI_SAS_GET_DEVICE_ADDRESS_BUFFER(Structure):
    _fields_ = [
        ('IoctlHeader', SRB_IO_CONTROL),
        ('bHostIndex', c_uint8),
        ('bPathId', c_uint8),
        ('bTargetId', c_uint8),
        ('bLun', c_uint8),
        ('bSASAddress', c_uint8 * 8),
        ('bSASLun', c_uint8 * 8),
    ]
    _pack_ = 1

##
# typedef struct _CSMI_SAS_SSP_TASK_IU {
#  __u8 bHostIndex; 
#  __u8 bPathId; 
#  __u8 bTargetId; 
#  __u8 bLun; 
#  __u32 uFlags; 
#  __u32 uQueueTag; 
#  __u32 uReserved; 
#  __u8 bTaskManagementFunction; 
#  __u8 bReserved[7]; 
#  __u32 uInformation;
# } CSMI_SAS_SSP_TASK_IU, 
#  *PCSMI_SAS_SSP_TASK_IU
class CSMI_SAS_SSP_TASK_IU(Structure):
    _fields_ = [
        ('bHostIndex', c_uint8),
        ('bPathId', c_uint8),
        ('bTargetId', c_uint8),
        ('bLun', c_uint8),
        ('uFlags', c_uint32),
        ('uQueueTag', c_uint32),
        ('uReserved', c_uint32),
        ('bTaskManagementFunction', c_uint8),
        ('bReserved', c_uint8 * 7),
        ('uInformation', c_uint32),
    ]
    _pack_ = 1

# typedef struct _CSMI_SAS_SSP_TASK_IU_BUFFER {
#  IOCTL_HEADER IoctlHeader; 
#  CSMI_SAS_SSP_TASK_IU Parameters; 
#  CSMI_SAS_SSP_PASSTHRU_STATUS Status; 
# } CSMI_SAS_SSP_TASK_IU_BUFFER, 
#  *PCSMI_SAS_SSP_TASK_IU_BUFFER;
class CSMI_SAS_SSP_TASK_IU_BUFFER(Structure):
    _fields_ = [
        ('IoctlHeader', SRB_IO_CONTROL),
        ('Parameters', CSMI_SAS_SSP_TASK_IU),
        ('Status', CSMI_SAS_SSP_PASSTHRU_STATUS),
    ]
    _pack_ = 1

##
# typedef struct _CSMI_SAS_PHY_CONTROL {
#  __u8 bType; 
#  __u8 bRate;
#   __u8 bReserved[6]; 
#  __u32 uVendorUnique[8]; 
#  __u32 uTransmitterFlags; 
#  __i8 bTransmitAmplitude; 
#  __i8 bTransmitterPreemphasis; 
#  __i8 bTransmitterSlewRate; 
#  __i8 bTransmitterReserved[13]; 
#  __u8 bTransmitterVendorUnique[64]; 
#  __u32 uReceiverFlags; 
#  __i8 bReceiverThreshold; 
#  __i8 bReceiverEqualizationGain; 
#  __i8 bReceiverReserved[14]; 
#  __u8 bReceiverVendorUnique[64]; 
#  __u8 bFixedPattern; 
#  __u8 bUserPatternLength; 
#  __u8 bPatternReserved[6]; 
#  __u8 bUserPattern[32]; 
# } CSMI_SAS_PHY_CONTROL, 
#  *PCSMI_SAS_PHY_CONTROL;
class CSMI_SAS_PHY_CONTROL(Structure):
    _fields_ = [
        ('bType', c_uint8),
        ('bRate', c_uint8),
        ('bReserved', c_uint8 * 6),
        ('uVendorUnique', c_uint32 * 8),
        ('uTransmitterFlags', c_uint32),
        ('bTransmitAmplitude', c_int8),
        ('bTransmitterPreemphasis', c_int8),
        ('bTransmitterSlewRate', c_int8),
        ('bTransmitterReserved', c_int8 * 13),
        ('bTransmitterVendorUnique', c_uint8 * 64),
        ('uReceiverFlags', c_uint32),
        ('bReceiverThreshold', c_int8),
        ('bReceiverEqualizationGain', c_int8),
        ('bReceiverReserved', c_int8 * 14),
        ('bReceiverVendorUnique', c_uint8 * 64),
        ('bFixedPattern', c_uint8),
        ('bUserPatternLength', c_uint8),
        ('bPatternReserved', c_uint8 * 6),
        ('bUserPattern', c_uint8 * 32),
    ]
    _pack_ = 1

# typedef struct _CSMI_SAS_PHY_CONTROL_BUFFER {
#  IOCTL_HEADER IoctlHeader; 
#  __u32 uFunction; 
#  __u8 bPhyIdentifier; 
#  __u16 usLengthOfControls; 
#  __u8 bNumberOfControls; 
#  __u8 bReserved[4]; 
#  __u32 uLinkFlags; 
#  __u8 bSpinupRate; 
#  __u8 bLinkReserved[7];
#  __u32 uVendorUnique[8]; 
#  CSMI_SAS_PHY_CONTROL Control[1]; 
# } CSMI_SAS_PHY_CONTROL_BUFFER, 
#  *PCSMI_SAS_PHY_CONTROL_BUFFER;
class CSMI_SAS_PHY_CONTROL_BUFFER(Structure):
    _fields_ = [
        ('IoctlHeader', SRB_IO_CONTROL),
        ('uFunction', c_uint32),
        ('bPhyIdentifier', c_uint8),
        ('usLengthOfControls', c_uint16),
        ('bNumberOfControls', c_uint8),
        ('bReserved', c_uint8 * 4),
        ('uLinkFlags', c_uint32),
        ('bSpinupRate', c_uint8),
        ('bLinkReserved', c_uint8 * 7),
        ('uVendorUnique', c_uint32 * 8),
        ('Control', CSMI_SAS_PHY_CONTROL * 1),
    ]
    _pack_ = 1

def GET_CSMI_SAS_PHY_CONTROL_BUFFER(phy_control_number):
    padding_num = BytesAligned - ((SRB_IO_CONTROL_LEN + 56 + sizeof(CSMI_SAS_PHY_CONTROL) * phy_control_number) % BytesAligned)
    class CSMI_SAS_PHY_CONTROL_BUFFER(Structure):
        _fields_ = [
            ('IoctlHeader', SRB_IO_CONTROL),
            ('uFunction', c_uint32),
            ('bPhyIdentifier', c_uint8),
            ('usLengthOfControls', c_uint16),
            ('bNumberOfControls', c_uint8),
            ('bReserved', c_uint8 * 4),
            ('uLinkFlags', c_uint32),
            ('bSpinupRate', c_uint8),
            ('bLinkReserved', c_uint8 * 7),
            ('uVendorUnique', c_uint32 * 8),
            ('Control', CSMI_SAS_PHY_CONTROL * phy_control_number),
            ('Padding', c_ubyte * padding_num),
        ]
        _pack_ = 1
    return CSMI_SAS_PHY_CONTROL_BUFFER

##
# typedef struct _CSMI_SAS_GET_CONNECTOR_INFO {
#  __u32 uPinout; 
#  __u8 bConnector[16]; 
#  __u8 bLocation; 
#  __u8 bReserved[15]; 
# } CSMI_SAS_CONNECTOR_INFO, 
#  *PCSMI_SAS_CONNECTOR_INFO;
class CSMI_SAS_GET_CONNECTOR_INFO(Structure):
    _fields_ = [
        ('uPinout', c_uint32),
        ('bConnector', c_uint8 * 16),
        ('bLocation', c_uint8),
        ('bReserved', c_uint8 * 15),
    ]
    _pack_ = 1

# typedef struct _CSMI_SAS_CONNECTOR_INFO_BUFFER {
#  IOCTL_HEADER IoctlHeader; 
#  CSMI_SAS_CONNECTOR_INFO Reference[32]; 
# } CSMI_SAS_CONNECTOR_INFO_BUFFER, 
#  *PCSMI_SAS_CONNECTOR_INFO_BUFFER;
class CSMI_SAS_CONNECTOR_INFO_BUFFER(Structure):
    _fields_ = [
        ('IoctlHeader', SRB_IO_CONTROL),
        ('Reference', CSMI_SAS_GET_CONNECTOR_INFO * 32),
    ]
    _pack_ = 1
