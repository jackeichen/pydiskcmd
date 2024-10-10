# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import sys
from pydiskcmdlib import os_type
from pydiskcmdlib.utils.converter import encode_dict,decode_bits,CheckDict
from pydiskcmdlib.os import win_ioctl_request
from pydiskcmdlib.exceptions import *
from pydiskcmdlib.os.win_ioctl_structures import (
    SRB_IO_CONTROL,
    SRB_IO_CONTROL_LEN,
    CSMI_SAS_DRIVER_INFO_BUFFER,
    CSMI_SAS_DRIVER_INFO_BUFFER_LEN,
    sizeof,
    NVME_IOCTL_PASS_THROUGH,
    NVME_IOCTL_PASS_THROUGH_LEN,
    Get_NVME_IOCTL_PASS_THROUGH_ALIGNED_WITH_BUFFER,
)
from pydiskcmdlib.os.win_ioctl_utils import (
    CSMI_Control_Code,
    CSMI_SAS_TIMEOUT,
    INTELNVM_SIGNATURE,
    IOCTL_NVME_PASS_THROUGH,
    RST_NVME_PASS_THROUGH_VERSION,
)


class RSTCommand(object):
    '''
    This Class define the function that must be implemented by CommandWapper function.
    '''
    _cdb_bits: CheckDict = {}   # define your self command bitmap
    _req_id: int = win_ioctl_request.IOCTLRequest.IOCTL_SCSI_MINIPORT.value

    def __init__(self):
        """
        """
        # the _cdb may include command and data_buffer
        self._cdb = None  #  default value: None
        ## used by build command
        self._byteorder = sys.byteorder
        ## init bitmap
        self.init_cdb_bitmap()

    def init_cdb_bitmap(self):
        '''Only do a copy'''
        self._cdb_bitmap = self._cdb_bits

    def print_cdb(self):
        """
        simple helper to print out the cdb as hex values
        """
        if self.cdb_struc:
            for b in self.cdb_struc:
                print("0x%02X " % b)

    @property
    def cdb(self):
        """
        getter method of the cdb property

        :return: a byte array
        """
        return self._cdb

    @property
    def cdb_struc(self):
        if self.cdb:
            return bytes(self.cdb.command_buf)

    @property
    def req_id(self):
        """
        getter method of the req_id property

        :return: a int
        """
        return self._req_id

    def marshall_cdb(self, cdb, cdb_len: int):
        """
        Marshall a Command cdb

        :param cdb: a dict with key:value pairs representing a code descriptor block
        :param cdb_len: the total length of build command
        :return result: a byte array representing a code descriptor block
        """
        result = bytearray(cdb_len) # The command initial value is all 0
        encode_dict(cdb, self._cdb_bitmap, result, byteorder=self._byteorder)
        return result

    def unmarshall_cdb(self):
        """
        Unmarshall an SCSICommand cdb

        :param cdb: a byte array representing a code descriptor block
        :return result: a dict
        """
        result = {}
        decode_bits(self.cdb_struc, self._cdb_bitmap, result, byteorder=self._byteorder)
        return result

    def build_command(self, **kwargs):
        """
        Build the command in different OS:
          1. The Linux define a fixed-length ctypes.structure;
          2. The Windows define a bariable-length ctypes.structure.
            * Windows init the cdb bufffer with StorageQueryWithoutBuffer
            * Windows cannot set a data buffer in building

        :param kwargs: the parameters to build command
                    For Linux, the key in kwargs should be xxx(like abc)
                    For Windows, the key in kwargs should be Xxx(like Abc)
                the kwargs is to build command.

        :return: the built command
        """
        if os_type == "Windows":
            # IOCTL_SCSI_MINIPORT
            if self._req_id == win_ioctl_request.IOCTLRequest.IOCTL_SCSI_MINIPORT.value:
                ## first check the SrbIoCtrl->ControlCode
                # Get an any-length dummy command
                _cdb = self.marshall_cdb(kwargs, 512)  # Give a big enough data to marshall cdb: 512
                _cdb = SRB_IO_CONTROL.from_buffer(_cdb[0:SRB_IO_CONTROL_LEN])
                if _cdb.ControlCode == CSMI_Control_Code.CC_CSMI_SAS_GET_DRIVER_INFO.value:
                    _cdb = self.marshall_cdb(kwargs, CSMI_SAS_DRIVER_INFO_BUFFER_LEN)
                    self._cdb = CSMI_SAS_DRIVER_INFO_BUFFER.from_buffer(_cdb)
                    if self._cdb.IoctlHeader.Timeout == 0:
                        self._cdb.IoctlHeader.Timeout = CSMI_SAS_TIMEOUT.default.value
                elif _cdb.ControlCode == IOCTL_NVME_PASS_THROUGH:
                    _cdb = self.marshall_cdb(kwargs, NVME_IOCTL_PASS_THROUGH_LEN)
                    self._cdb = NVME_IOCTL_PASS_THROUGH.from_buffer(_cdb)
                    data_buffer_len = self._cdb.Parameters.DataBufferLength
                    if data_buffer_len > 0:
                        temp = Get_NVME_IOCTL_PASS_THROUGH_ALIGNED_WITH_BUFFER(data_buffer_len)
                        _cdb = self.marshall_cdb(kwargs, sizeof(temp))
                        self._cdb = temp.from_buffer(_cdb)
                        #
                        if self._cdb.Parameters.DataBufferOffset == 0:
                            self._cdb.Parameters.DataBufferOffset = sizeof(self._cdb) - sizeof(self._cdb.data_buf)
                    else:
                        self._cdb.Parameters.DataBufferOffset = 0 
                    # check and fix the NVME_IOCTL_PASS_THROUGH structures
                    if self._cdb.IoctlHeader.Timeout == 0:
                        self._cdb.IoctlHeader.Timeout = 10  # default timeout
                    if self._cdb.Version == 0:
                        self._cdb.Version = RST_NVME_PASS_THROUGH_VERSION.default.value
                else:
                    raise BuildNVMeCommandError("Failed to build command, Do Not Support ControlCode %#x" % _cdb.ControlCode)
                # check and fix the SrbIoCtrl structures
                if self._cdb.IoctlHeader.HeaderLength == 0:
                    self._cdb.IoctlHeader.HeaderLength = SRB_IO_CONTROL_LEN
                if self._cdb.IoctlHeader.Length == 0:
                    self._cdb.IoctlHeader.Length = sizeof(self._cdb) - SRB_IO_CONTROL_LEN
            else:
                raise BuildNVMeCommandError("Failed to build command, Do Not Support request ID %#x" % self._req_id)
        else:
            raise BuildNVMeCommandError("%s Do Not Support this command" % os_type)
        return self._cdb

    @property
    def data(self):
        if self.cdb and self.cdb.data_buf:
            return bytes(self.cdb.data_buf)

    @property
    def metadata(self):
        return None

    def check_return_status(self, success_hint=False, fail_hint=True, raise_if_fail=False):
        '''
        Do Not Check it before command execute, it may failed in level 2.
        '''
        ## Level 1: Returned status of DeviceIoControl API
        #  This can be checked in pydiskcmdlib.device.win_device.WinIOCTLDevice.execute()
        ## Level 2: ReturnCode of SRB_IO_CONTROL structure
        if self.cdb.SrbIoCtrl.ReturnCode != 0:
            if fail_hint:
                print ("SrbIoCtrl->ReturnCode is %d" % self.cdb.SrbIoCtrl.ReturnCode)
            if raise_if_fail:
                raise CommandReturnStatusError('Command Check Error')
        return self.cdb.SrbIoCtrl.ReturnCode
