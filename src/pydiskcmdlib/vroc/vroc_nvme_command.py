# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import sys
from pydiskcmdlib import os_type
from pydiskcmdlib.utils.converter import encode_dict,decode_bits,CheckDict
from pydiskcmdlib.os import win_ioctl_request
from pydiskcmdlib.exceptions import *
from pydiskcmdlib.vroc import win_ioctl

class VROCNVMeCommand(object):
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
                _cdb = self.marshall_cdb(kwargs, 256)  # Give a big enough data to marshall cdb: 256
                _cdb = win_ioctl.SRB_IO_CONTROL.from_buffer(_cdb[0:win_ioctl.SRB_IO_CONTROL_LEN])
                if _cdb.ControlCode == win_ioctl.NVME_PASS_THROUGH_SRB_IO_CODE:
                    ## When set NVME_PASS_THROUGH_SRB_IO_CODE command,you must specify the DataBufferLen field
                    _cdb = self.marshall_cdb(kwargs, win_ioctl.sizeof(win_ioctl.NVME_RAID_PASS_THROUGH_IOCTL))
                    self._cdb = win_ioctl.NVME_RAID_PASS_THROUGH_IOCTL.from_buffer(_cdb)
                    if self._cdb.DataBufferLen > 0:
                        _cdb = self.marshall_cdb(kwargs, win_ioctl.sizeof(win_ioctl.NVME_RAID_PASS_THROUGH_IOCTL)+self._cdb.DataBufferLen)
                        self._cdb = win_ioctl.GetNVMeRaidPassThroughIOCTLWithBuffer(self._cdb.DataBufferLen).from_buffer(_cdb)
                        # check the direction
                        if self._cdb.Direction == win_ioctl.NVME_NO_DATA_TX:
                            raise BuildNVMeCommandError("Set data buffer, but Direction is NVME_NO_DATA_TX")
                    # fix the Command structures
                    if self._cdb.ReturnBufferLen == 0:
                        self._cdb.ReturnBufferLen = win_ioctl.sizeof(self._cdb)
                elif _cdb.ControlCode in (win_ioctl.NVME_GET_NUMBER_OF_RAID_VOLUMES,
                                          win_ioctl.NVME_GET_NUMBER_OF_SPARE_DISKS,
                                          win_ioctl.NVME_GET_NUMBER_OF_PASSTHROUGH_DISKS,
                                          win_ioctl.NVME_GET_NUMBER_OF_JOURNALING_DRIVES,
                                          ):
                    _cdb = self.marshall_cdb(kwargs, win_ioctl.sizeof(win_ioctl.NVME_GET_NUMBER_OF_DEVCICES))
                    self._cdb = win_ioctl.NVME_GET_NUMBER_OF_DEVCICES.from_buffer(_cdb)
                elif _cdb.ControlCode == win_ioctl.NVME_GET_RAID_INFORMATION:
                    _cdb = self.marshall_cdb(kwargs, win_ioctl.sizeof(win_ioctl.NVME_GET_RAID_INFORMATION_IOCTL))
                    self._cdb = win_ioctl.NVME_GET_RAID_INFORMATION_IOCTL.from_buffer(_cdb)
                elif _cdb.ControlCode == win_ioctl.NVME_GET_RAID_CONFIGURATION:
                    # This shall be a command with buffer
                    _cdb = self.marshall_cdb(kwargs, win_ioctl.sizeof(win_ioctl.NVME_GET_RAID_CONFIGURATION_IOCTL))
                    _cdb = win_ioctl.NVME_GET_RAID_CONFIGURATION_IOCTL.from_buffer(_cdb)
                    temp_length = _cdb.ReturnBufferLen
                    _cdb = self.marshall_cdb(kwargs, win_ioctl.sizeof(win_ioctl.NVME_GET_RAID_CONFIGURATION_IOCTL)+temp_length)
                    self._cdb = win_ioctl.GetNVMeGetRaidConfigurationIOCTLWithBuffer(temp_length).from_buffer(_cdb)
                elif _cdb.ControlCode in (win_ioctl.NVME_GET_SPARE_DISKS_INFORMATION,
                                          win_ioctl.NVME_GET_PASSTHROUGH_DISKS_INFORMATION,
                                          win_ioctl.NVME_GET_JOURNALING_DRIVES_INFORMATION,
                                          ):
                    _cdb = self.marshall_cdb(kwargs, win_ioctl.sizeof(win_ioctl.NVME_GET_DRIVES_INFORMATION))
                    _cdb = win_ioctl.NVME_GET_DRIVES_INFORMATION.from_buffer(_cdb)
                    temp_length = _cdb.ReturnBufferLen
                    _cdb = self.marshall_cdb(kwargs, win_ioctl.sizeof(win_ioctl.NVME_GET_DRIVES_INFORMATION)+temp_length)
                    self._cdb = win_ioctl.GetNVMeGetDrivesInformationWithBuffer(temp_length).from_buffer(_cdb)
                else: # This is a passthrough command
                    ## When set passthrough command,you must specify the SrbIoCtrl->Length field
                    if _cdb.Length == 0:
                        raise BuildNVMeCommandError("SrbIoCtrl->Length should not be zero")
                    vs_data_length = _cdb.Length
                    _cdb = self.marshall_cdb(kwargs, win_ioctl.SRB_IO_CONTROL_LEN+vs_data_length)
                    self._cdb = win_ioctl.GetVendorSpecIOCTL(vs_data_length).from_buffer(_cdb)
                    #raise BuildNVMeCommandError("Failed to build command, Do Not Support Request %#x" % _cdb.SrbIoCtrl.ControlCode)
                # check and fix the SrbIoCtrl structures
                if self._cdb.SrbIoCtrl.HeaderLength == 0:
                    self._cdb.SrbIoCtrl.HeaderLength = win_ioctl.SRB_IO_CONTROL_LEN
                if self._cdb.SrbIoCtrl.Timeout == 0:
                    self._cdb.SrbIoCtrl.Timeout = win_ioctl.NVME_PT_TIMEOUT
                if self._cdb.SrbIoCtrl.Length == 0:
                    self._cdb.SrbIoCtrl.Length = win_ioctl.sizeof(self._cdb) - win_ioctl.SRB_IO_CONTROL_LEN
                # if bytes(self._cdb.SrbIoCtrl.Signature) == b'\x00\x00\x00\x00\x00\x00\x00\x00':
                #     for i in range(win_ioctl.NVME_RAID_SIG_STR_LEN):
                #         self._cdb.SrbIoCtrl.Signature[i] = ord(win_ioctl.NVME_RAID_SIG_STR[i])
            else:
                raise BuildNVMeCommandError("Failed to build command, Do Not Support SrbIoCtrl->ControlCode %#x" % self._req_id)
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
