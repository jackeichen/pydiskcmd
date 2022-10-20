# SPDX-FileCopyrightText: 2014 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import time
from pydiskcmd.pyscsi.scsi import SCSI
from pydiskcmd.pyscsi import scsi_enum_inquiry as INQUIRY
from pydiskcmd.utils import init_device
from pydiskcmd.utils.converter import bytearray2string,translocate_bytearray


class SCSIDevice(object):
    """
    dev_path: the nvme controller device path(ex. /dev/nvme0)
    
    
    """
    def __init__(self, dev_path):
        self.__device_type = 'scsi'
        self.dev_path = dev_path
        ## init device
        self.__device_id = None
        i = self.inquiry(INQUIRY.VPD.UNIT_SERIAL_NUMBER)
        id_string = bytearray2string(i['unit_serial_number'])
        if id_string:
            self.__device_id = id_string
        else:
            self.__device_id = bytes(i['unit_serial_number'])

    def __del__(self):
        ## close device when exit
        self._close()

    def _close(self):
        pass

    @property
    def device_type(self):
        return self.__device_type

    @property
    def device_id(self):
        return self.__device_id.strip()

    def inquiry(self, page_code):
        with SCSI(init_device(self.dev_path, open_t="scsi"), blocksize=512) as d:
            cmd = d.inquiry(evpd=1, page_code=page_code)
            i = cmd.result
        return i
