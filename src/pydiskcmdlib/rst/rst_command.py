# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmdlib import os_type
from pydiskcmdlib.command_utils import CommandWrapper
from pydiskcmdlib.os import win_ioctl_request
from pydiskcmdlib.exceptions import *
from pydiskcmdlib.os.win_ioctl_utils import SRBStatusCode

class RSTCommand(CommandWrapper):
    '''
    This Class define the function that must be implemented by CommandWapper function.
    '''
    _req_id: int = win_ioctl_request.IOCTLRequest.IOCTL_SCSI_MINIPORT.value

    def __init__(self, cdb_raw_struc):
        """
        Initialize the RSTCommand class.

        :param cdb_raw_struc: The raw structure of the CDB (Command Descriptor Block).
        """
        if os_type != "Windows":
            raise NotImplementedError("%s Do Not Support this command" % os_type)
        CommandWrapper.__init__(self, cdb_raw_struc)

    def command_spec_check(self, fail_hint=True, raise_if_fail=False):
        '''
        Check the return status of a specific command

        :param fail_hint: Whether to print a hint message when the command fails.
        :param raise_if_fail: Whether to raise an exception when the command fails.
        :return: 0 if the command is successful, otherwise an error code.
        '''
        return 0

    def check_return_status(self, success_hint=False, fail_hint=True, raise_if_fail=False):
        '''
        3 levels to check the command status after command's execution:
          Level 1: Returned status of DeviceIoControl API,
                   This can be checked in pydiskcmdlib.device.win_device.WinIOCTLDevice.execute()
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
        if self.bytes_returned is not None:
            pass
        if self.cdb is not None and hasattr(self.cdb, 'IoctlHeader'):
            if self.cdb.IoctlHeader.ReturnCode not in (SRBStatusCode.SRB_STATUS_SUCCESS.value,
                                                        SRBStatusCode.SRB_STATUS_PENDING.value):
                ret = 3
                if fail_hint:
                    print ("CSMI Command ReturnCode: %s" % self.cdb.IoctlHeader.ReturnCode)
                if raise_if_fail:
                    raise CommandReturnStatusError("CSMI Command ReturnCode: %s" % self.cdb.IoctlHeader.ReturnCode)
        ret = self.command_spec_check(fail_hint, raise_if_fail)
        if ret == 0 and success_hint:
            print ("CSMI Command Success")
        return ret
