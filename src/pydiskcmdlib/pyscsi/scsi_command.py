# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later 
from pydiskcmdlib import os_type
from pyscsi.pyscsi.scsi_command import SCSICommand as _SCSICommand
from pydiskcmdlib.os import lin_ioctl_request,win_ioctl_request
from pydiskcmdlib.device.win_device import ctypes
from pydiskcmdlib.pyscsi.win_scsi_structures import SCSIPassThroughDirect,SCSIPassThroughDirectWithBuffer
from pydiskcmdlib.exceptions import *


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
        
