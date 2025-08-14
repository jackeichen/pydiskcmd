from enum import Enum
import uuid
import ctypes
from pydiskcmdlib.os.win_ioctl_utils import (
    CTL_CODE,
    METHOD_BUFFERED,
    FILE_ANY_ACCESS,

)
from pydiskcmdlib.os.win_utils import WinEvent,getUniqueName


INTEL_RAID_FW_SIGNATURE = "IntelFw "
IOCTL_RAID_FIRMWARE = CTL_CODE(0xF000, 0x010, METHOD_BUFFERED, FILE_ANY_ACCESS)
RAID_FIRMWARE_REQUEST_BLOCK_VERSION = 1
#
INTELNVM_SIGNATURE = "IntelNvm"
IOCTL_NVME_REGISTER_AER = CTL_CODE(0xF000, 0xC00, METHOD_BUFFERED, FILE_ANY_ACCESS)
IOCTL_NVME_GET_AER_DATA = CTL_CODE(0xF000, 0xE00, METHOD_BUFFERED, FILE_ANY_ACCESS)
AEN_MAX_EVENT_NAME_LENGTH = 32
NVME_GET_AER_DATA_MAX_COMPLETIONS = 10
#
INTELRMP_SIGNATURE = "IntelRmp"
IOCTL_REMAPPORT_GET_DEVICE_LOCATION = 0x80000D05
REMAPPORT_IOCTL_GET_DEVICE_LOCATION_VERSION = 1

class AER_COMPLETION_EVENT_TYPES(Enum):
    AE_TYPE_ERROR_STATUS = 0
    AE_TYPE_SMART_HEALTH_STATUS = 1
    AE_TYPE_NOTICE = 2
    AE_TYPE_IO_CMD_SET_SPECIFIC_STATUS = 6
    AE_TYPE_VENDOR_SPECIFIC = 7

class REMAPPORT_LOCATION_TYPE(Enum):
    RemapPortLocationTypeSata = 0
    RemapPortLocationTypeCR = 1
    RemapPortLocationTypeSwRemap = 2
    RemapPortLocationTypeVmd = 3

class REMAPPORT_GET_DEVICE_LOCATION_STATUS(Enum):
    GetLocationSuccess = 1
    ErrorNoPciDevice = 2
    ErrorNoBridgeDevice = 3
    ErrorNoBridgeCapabilities = 4

def CreateEventForAER(eventName: str):
    eventNameWithPrefix = "Global\\" + eventName
    event = WinEvent(None,
                     True,
                     False,
                     eventNameWithPrefix,
                     )
    return event
