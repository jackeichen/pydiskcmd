# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import time
from pydiskcmd.pyscsi.scsi import SCSI
from pydiskcmd.utils import init_device
from pydiskcmd.utils.converter import bytearray2string,translocate_bytearray
##
from pyscsi.pyscsi import scsi_enum_inquiry as INQUIRY

def get_dev_id(dev_path):
    ## get device ID
    device_id = None
    ##
    with SCSI(init_device(dev_path, open_t="scsi"), blocksize=512) as d:
        cmd = d.inquiry(evpd=1, page_code=INQUIRY.VPD.UNIT_SERIAL_NUMBER)
        i = cmd.result
    if 'unit_serial_number' in i:
        id_string = bytearray2string(i['unit_serial_number'])
        if id_string:
            device_id = id_string
        else:
            device_id = bytes(i['unit_serial_number'])
    return device_id


class SCSIDevice(object):
    """
    dev_path: the nvme controller device path(ex. /dev/nvme0)
    
    """
    def __init__(self, dev_path, init_db=False):
        self.__device_type = 'scsi'
        self.dev_path = dev_path
        ## init device
        self.__device_id = get_dev_id(self.dev_path)
        if init_db:
            self.init_db()

    def __del__(self):
        ## close device when exit
        self._close()

    def _close(self):
        pass

    def init_db(self):
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
