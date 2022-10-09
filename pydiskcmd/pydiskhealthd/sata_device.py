# SPDX-FileCopyrightText: 2014 The python-scsi Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmd.pysata.sata import SATA
from pydiskcmd.utils import init_device
from pydiskcmd.utils.converter import bytearray2string,translocate_bytearray


class ATADevice(object):
    """
    dev_path: the nvme controller device path(ex. /dev/nvme0)
    
    
    """
    def __init__(self, dev_path):
        self.__device_type = 'ata'
        self.dev_path = dev_path
        # init smart attr
        self.__smart_attr = {}
        ## init device
        self.ata_device = None
        self._init_device()

    def __del__(self):
        ## close device when exit
        self._close()

    def _init_device(self):
        self.ata_device = SATA(init_device(self.dev_path, open_t="ata"))
        ## 
        return

    def _close(self):
        if self.ata_device:
            self.ata_device.device.close()
            self.ata_device = None

    @property
    def device_type(self):
        return self.__device_type

    @property
    def device_id(self):
        cmd = self.ata_device.identify()
        result = cmd.result
        return bytearray2string(translocate_bytearray(result.get("SerialNumber")))

    @property
    def smart_attr(self):
        return self.__smart_attr

    def get_smart_once(self):
        ## 
        cmd = self.ata_device.smart()
        smart = cmd.result
        ## 
        return smart

