# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later 
from pydiskcmdlib import os_type
from pyscsi.pyscsi.scsi_command import SCSICommand as _SCSICommand
from pydiskcmdlib.os import lin_ioctl_request,win_ioctl_request
from pydiskcmdlib.device.win_device import ctypes
from pydiskcmdlib.pyscsi.win_scsi_structures import SCSIPassThroughDirect,SCSIPassThroughDirectWithBuffer
from pydiskcmdlib.exceptions import *
from pyscsi.pyscsi.scsi_sense import SCSICheckCondition

def _check_return_status(self: _SCSICommand, success_hint: bool=False, fail_hint: bool = True, raise_if_fail: bool=True) -> bool:
    _status  = False
    _fail_hint = ''
    sense_data = None
    if self.sense:
        sense_data = self.sense
    elif self.raw_sense_data:
        sense_data = self.raw_sense_data
    else:
        _status = True
    ##
    if sense_data:
        sense = SCSICheckCondition(sense_data)
        if sense.valid:
            if sense.data:
                if sense.data["sense_key"] == 0 and sense._ascq == 0:
                    _status = True   
                else:
                    _fail_hint = str(sense)
                    if fail_hint:
                        _hint = """Command failed, and details bellow.
- SCSI Status:
  %-12s%-19s%s
  %-12s%-19s%s
            """ % ("Sense Key", "ASC", "ASCQ", 
                   "0x%X" % sense.data.get("sense_key"), "0x%X" % sense.asc, "0x%X" % sense.ascq,
                   )
                        print (_hint)
            else:
                _fail_hint = "Invalid sense data format"
        else:
            _fail_hint = "Invalid sense data"
    if _status:
        if success_hint:
            print ("Command Success")
            print ('')
    else:
        if fail_hint:
            print (_fail_hint)
        if raise_if_fail:
            raise CommandReturnStatusError(_fail_hint)
    return _status

_SCSICommand.check_return_status = _check_return_status


class SCSICommand(_SCSICommand):
    def __init__(self, *args, **kwargs):
        _SCSICommand.__init__(self, *args, **kwargs)
        ##
        # in general, Do Not need specify the _req_id
        ##
        self._init_request_id()

    def _init_request_id(self):
        if os_type == 'Linux':
            self._req_id = lin_ioctl_request.IOCTLRequest.SG_IO_IOCTL.value
        elif os_type == 'Windows':
            self._req_id = win_ioctl_request.IOCTLRequest.IOCTL_SCSI_PASS_THROUGH_DIRECT.value
        else:
            self._req_id = 0

    @property
    def req_id(self):
        """
        getter method of the req_id property

        :return: a int
        """

        return self._req_id

    def build_cdb(self, **kwargs):
        raw_cdb = _SCSICommand.build_cdb(**kwargs)
        if os_type == 'Windows':
            ## create SCSIPassThroughDirect Or SCSIPassThroughDirectWithBuffer
            # will transfer SCSICommand to windows mode
            cdb = (ctypes.c_ubyte * 16).from_buffer_copy(
                raw_cdb.ljust(16, b'\x00')  # noqa
            )

            if self.datain:
                direction = 1     ## read from device
                data_transfer_length = len(self.datain)
                data_buffer = ctypes.create_string_buffer(data_transfer_length)
            elif self.dataout:
                direction = 0     ## write to device
                data_transfer_length = len(self.dataout)
                data_buffer = ctypes.create_string_buffer(bytes(self.dataout), data_transfer_length)
            else:
                direction = 0
                data_transfer_length = 0
                data_buffer = ctypes.create_string_buffer(b'', 0)
            timeout = 18000
            ## create SCSIPassThroughDirect
            header_sptd = SCSIPassThroughDirect(
                length=ctypes.sizeof(SCSIPassThroughDirect),
                data_in=direction,
                data_transfer_length=data_transfer_length,
                data_buffer=ctypes.addressof(data_buffer),
                cdb_length=len(raw_cdb),
                cdb=cdb,
                timeout_value=timeout,
                sense_info_length=(
                    SCSIPassThroughDirectWithBuffer.sense.size
                ),
                sense_info_offset=(
                    SCSIPassThroughDirectWithBuffer.sense.offset
                )
            )
            # create SCSIPassThroughDirectWithBuffer
            raw_cdb = SCSIPassThroughDirectWithBuffer(sptd=header_sptd)
        elif os_type == 'Linux':
            pass
        else:
            raise BuildNVMeCommandError("%s Do Not Support this command" % os_type)
        return raw_cdb
        
