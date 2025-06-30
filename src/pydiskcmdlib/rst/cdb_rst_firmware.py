from pydiskcmdlib.command_utils import CommandWrapperPro
from pydiskcmdlib.os import win_ioctl_request
from pydiskcmdlib.os.win_ioctl_structures import (
    SRB_IO_CONTROL_LEN,
    FIRMWARE_REQUEST_BLOCK,
    sizeof,
)
from pydiskcmdlib.os.win_ioctl_utils import (
    FIRMWARE_FUNCTION,
    FIRMWARE_REQUEST_FLAG_CONTROLLER,
    FIRMWARE_REQUEST_BLOCK_STRUCTURE_VERSION,
)
from .win_ioctl_structures import (
    DEV_FIRMWARE_INFO_M1,
    DEV_FIRMWARE_INFO_V2_M7,
    RAID_FIRMWARE_REQUEST_BLOCK,
    )
from .win_ioctl_utils import (
    INTEL_RAID_FW_SIGNATURE,
    IOCTL_RAID_FIRMWARE,
    RAID_FIRMWARE_REQUEST_BLOCK_VERSION,
    )
from pydiskcmdlib.exceptions import *


class DeviceGetFirmwareInfo(CommandWrapperPro):
    _req_id: int = win_ioctl_request.IOCTLRequest.IOCTL_SCSI_MINIPORT.value
    def __init__(self, path_id, target_id, lun, timeout=30):
        CommandWrapperPro.__init__(self, DEV_FIRMWARE_INFO_M1)
        header = {'HeaderLength': SRB_IO_CONTROL_LEN,
                  'Signature': INTEL_RAID_FW_SIGNATURE,
                  'Timeout': timeout,
                  'ControlCode': IOCTL_RAID_FIRMWARE,
                  'ReturnCode': 0,
                  'Length': self.cdb_raw_struc_len-SRB_IO_CONTROL_LEN, 
                 }
        #
        firmwareInfoOffset = SRB_IO_CONTROL_LEN+sizeof(RAID_FIRMWARE_REQUEST_BLOCK)+self.cdb_raw_struc.Padding.size
        request = {'Version': RAID_FIRMWARE_REQUEST_BLOCK_VERSION,
                   'PathID': path_id,
                   'TargetID': target_id,
                   'Lun': lun,
                   'FwRequestBlock': {'Version': FIRMWARE_REQUEST_BLOCK_STRUCTURE_VERSION,
                                      'Size': sizeof(FIRMWARE_REQUEST_BLOCK),
                                      'Function': FIRMWARE_FUNCTION.GET_INFO.value,
                                      'Flags': FIRMWARE_REQUEST_FLAG_CONTROLLER,
                                      'DataBufferOffset': firmwareInfoOffset,
                                      'DataBufferLength': self.cdb_raw_struc_len-firmwareInfoOffset,
                                      },
                   }

        self.build_command(Header=header,
                           Request=request,
                           )

    def check_return_status(self, success_hint=False, fail_hint=True, raise_if_fail=True) -> int:
        ret = 0
        ## level 1. Check the IOCTL execute return code
        if self.ioctl_result is not None and self.ioctl_result == 0:
            ret = 1
            import ctypes # noqa: F401
            if fail_hint:
                print (str(ctypes.WinError(ctypes.get_last_error())))
            if raise_if_fail:
                raise ctypes.WinError(ctypes.get_last_error())
        ## Level 2. Check SRB_IO_CONTROL ReturnCode field
        if self.cdb.Header.ReturnCode != 0:
            ret = 2
            rc = self.cdb.Header.ReturnCode
            if fail_hint:
                print ("SrbIoCtrl->ReturnCode is %#x" % rc)
            if raise_if_fail:
                raise CommandReturnStatusError('Command Check Error: %#x' % rc)
        ##
        if ret == 0 and success_hint:
            print ("Command Success")
            print ('')
        return ret


class DeviceGetFirmwareInfoV2(CommandWrapperPro):
    _req_id: int = win_ioctl_request.IOCTLRequest.IOCTL_SCSI_MINIPORT.value
    def __init__(self, path_id, target_id, lun, timeout=30):
        CommandWrapperPro.__init__(self, DEV_FIRMWARE_INFO_V2_M7)
        header = {'HeaderLength': SRB_IO_CONTROL_LEN,
                  'Signature': INTEL_RAID_FW_SIGNATURE,
                  'Timeout': timeout,
                  'ControlCode': IOCTL_RAID_FIRMWARE,
                  'ReturnCode': 0,
                  'Length': self.cdb_raw_struc_len-SRB_IO_CONTROL_LEN, 
                 }
        #
        firmwareInfoOffset = SRB_IO_CONTROL_LEN+sizeof(RAID_FIRMWARE_REQUEST_BLOCK)+self.cdb_raw_struc.Padding.size
        request = {'Version': RAID_FIRMWARE_REQUEST_BLOCK_VERSION,
                   'PathID': path_id,
                   'TargetID': target_id,
                   'Lun': lun,
                   'FwRequestBlock': {'Version': 2,
                                      'Size': sizeof(FIRMWARE_REQUEST_BLOCK),
                                      'Function': FIRMWARE_FUNCTION.GET_INFO.value,
                                      'Flags': FIRMWARE_REQUEST_FLAG_CONTROLLER,
                                      'DataBufferOffset': firmwareInfoOffset,
                                      'DataBufferLength': self.cdb_raw_struc_len-firmwareInfoOffset,
                                      },
                   }

        self.build_command(Header=header,
                           Request=request,
                           )

    def check_return_status(self, success_hint=False, fail_hint=True, raise_if_fail=True) -> int:
        ret = 0
        ## level 1. Check the IOCTL execute return code
        if self.ioctl_result is not None and self.ioctl_result == 0:
            ret = 1
            import ctypes # noqa: F401
            if fail_hint:
                print (str(ctypes.WinError(ctypes.get_last_error())))
            if raise_if_fail:
                raise ctypes.WinError(ctypes.get_last_error())
        ## Level 2. Check SRB_IO_CONTROL ReturnCode field
        if self.cdb.Header.ReturnCode != 0:
            ret = 2
            rc = self.cdb.Header.ReturnCode
            if fail_hint:
                print ("SrbIoCtrl->ReturnCode is %#x" % rc)
            if raise_if_fail:
                raise CommandReturnStatusError('Command Check Error: %#x' % rc)
        ##
        if ret == 0 and success_hint:
            print ("Command Success")
            print ('')
        return ret

