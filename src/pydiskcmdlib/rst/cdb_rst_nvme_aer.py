from pydiskcmdlib.command_utils import CommandWrapperPro
from pydiskcmdlib.os import win_ioctl_request
from pydiskcmdlib import os_type
from pydiskcmdlib.os.win_ioctl_structures import SRB_IO_CONTROL_LEN
from .win_ioctl_structures import NVME_IOCTL_REGISTER_AER
from .win_ioctl_utils import (
    IOCTL_NVME_REGISTER_AER,
    INTELNVM_SIGNATURE,
)

class RegisterAER(CommandWrapperPro):
    _req_id: int = win_ioctl_request.IOCTLRequest.IOCTL_SCSI_MINIPORT.value
    def __init__(self, 
                 path_id, # Port number from Windows (non-RAID) or CSMI port number (GET_RAID_INFO and GET_RAID_CONFIG)
                 target_id,
                 lun,
                 eventName,
                 eventMask,
                 timeout=10
                 ):
        if os_type != "Windows":
            raise NotImplementedError("%s Do Not Support this command" % os_type)
        return_code = (path_id << 16) + (target_id << 8) + lun
        CommandWrapperPro.__init__(self, NVME_IOCTL_REGISTER_AER)
        self.build_command(Header={'HeaderLength': SRB_IO_CONTROL_LEN,
                                   'Signature': INTELNVM_SIGNATURE,
                                   'Timeout': timeout,
                                   'ControlCode': IOCTL_NVME_REGISTER_AER,
                                   'ReturnCode': return_code,
                                   'Length': self.cdb_raw_struc_len-SRB_IO_CONTROL_LEN,
                                   },
                            EventData={
                                    'eventMask': eventMask,
                                    'eventName': eventName,
                                   },
                            )

    def check_return_status(self, success_hint=False, fail_hint=True, raise_if_fail=False):
        '''
        3 levels to check the command status after command's execution:
          Level 1: Returned status of DeviceIoControl API,
          Level 2: ReturnCode of SRB_IO_CONTROL structure
          Level 3: Check the returned completion queue entry of NVMe Command

        Note: Do Not Check it before command execute, it may failed in level 2.

        :param success_hint: Whether to print a success message when the command is successful.
        :param fail_hint: Whether to print a failure message when the command fails.
        :param raise_if_fail: Whether to raise an exception when the command fails.
        :return: 0 if the command is successful, otherwise an error code.
        '''
        ret = 0
        if self.ioctl_result is not None:
            if self.ioctl_result == 0:
                ret = 1
                import ctypes # noqa: F401
                if fail_hint:
                    print (str(ctypes.WinError(ctypes.get_last_error())))
                if raise_if_fail:
                    raise ctypes.WinError(ctypes.get_last_error())
        if ret == 0 and success_hint:
            print ("RegisterAER Command Success")
        return ret
