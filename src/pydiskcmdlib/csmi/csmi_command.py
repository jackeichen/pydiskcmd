# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmdlib import os_type
from pydiskcmdlib.os import win_ioctl_request
from pydiskcmdlib.exceptions import *
from pydiskcmdlib.command_utils import CommandWrapper
from .win_ioctl_utils import CSMI_SAS_STATUS

class CSMICommand(CommandWrapper):
    '''
    This Class define the function that must be implemented by CommandWapper function.

    Command success or fail:
        process the result of the IOCTL using:
        success:          success = DeviceIoControl(*args, **kwargs)
        GetLastError():   it should be checked by device.win_device, will raise when error happens.
        info->ReturnCode: checked by check_return_status
        bytesReturned:    it should be checked by check_return_status
        IOCTL content:
    '''
    _req_id: int = win_ioctl_request.IOCTLRequest.IOCTL_SCSI_MINIPORT.value

    def __init__(self, cdb_raw_struc):
        """
        """
        if os_type != "Windows":
            raise NotImplementedError("%s Do Not Support this command" % os_type)
        CommandWrapper.__init__(self, cdb_raw_struc, bytes_aligned=4)  # should be DW aligned

    def command_spec_check(self, fail_hint=True, raise_if_fail=False):
        '''
        Check the return status of a specific command
        '''
        return 0

    def check_return_status(self, success_hint=False, fail_hint=True, raise_if_fail=False):
        '''
        Override this function in child class.
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
        if self.bytes_returned is not None:
            pass
        if self.cdb is not None and hasattr(self.cdb, 'IoctlHeader'):
            if self.cdb.IoctlHeader.ReturnCode != CSMI_SAS_STATUS.CSMI_SAS_STATUS_SUCCESS.value:
                ret = 3
                if fail_hint:
                    print ("CSMI Command ReturnCode: %s" % self.cdb.IoctlHeader.ReturnCode)
                if raise_if_fail:
                    raise CommandReturnStatusError("CSMI Command ReturnCode: %s" % self.cdb.IoctlHeader.ReturnCode)
        ret = self.command_spec_check(fail_hint, raise_if_fail)
        if ret == 0 and success_hint:
            print ("CSMI Command Success")
        return ret
