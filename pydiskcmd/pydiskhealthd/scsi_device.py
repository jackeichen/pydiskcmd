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


class SCSIDeviceBase(object):
    """
    dev_path: the nvme controller device path(ex. /dev/nvme0)
    
    """
    def __init__(self, dev_path):
        self.__device_type = 'scsi'
        self.dev_path = dev_path
        ## init device
        self.__model = "dummy value"
        self.__serial = None
        with SCSI(init_device(dev_path, open_t="scsi"), blocksize=512) as d:
            cmd = d.inquiry(evpd=1, page_code=INQUIRY.VPD.UNIT_SERIAL_NUMBER)
            serial_info = cmd.result
        if 'unit_serial_number' in serial_info:
            id_string = bytearray2string(serial_info['unit_serial_number']).strip()
            if id_string:
                self.__serial = id_string
            else:
                for encode_t in ("UTF-8", "GBK", "GB2312"):
                    try:
                        self.__serial = bytes(serial_info['unit_serial_number']).decode(encoding=encode_t)
                    except:
                        pass
                    else:
                        break

    @property
    def device_type(self):
        return self.__device_type

    @property
    def device_id(self):
        return self.__serial.strip()

    @property
    def Model(self):
        return self.__model

    @property
    def Serial(self):
        return self.__serial

    def inquiry(self, page_code):
        with SCSI(init_device(self.dev_path, open_t="scsi"), blocksize=512) as d:
            cmd = d.inquiry(evpd=1, page_code=page_code)
            i = cmd.result
        return i


class SCSIDevice(SCSIDeviceBase):
    """
    dev_path: the nvme controller device path(ex. /dev/nvme0)
    
    """
    def __init__(self, dev_path, init_db=False):
        super(SCSIDevice, self).__init__(dev_path)
        ##
        self.__media_type = None
        blk_dev_char = self.inquiry(INQUIRY.VPD.BLOCK_DEVICE_CHARACTERISTICS)
        if blk_dev_char.get("medium_rotation_rate") == 1:
            self.__media_type = "SSD"
        elif blk_dev_char.get("medium_rotation_rate") > 1:
            self.__media_type = "HDD"
        ##
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
    def MediaType(self):
        return self.__media_type

    @property
    def smart_enable(self):
        return False
