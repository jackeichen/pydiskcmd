# SPDX-FileCopyrightText: 2014 The python-scsi Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import time
from pydiskcmd.pynvme.nvme import NVMe
from pydiskcmd.utils import init_device
from pydiskcmd.pynvme.nvme_spec import nvme_smart_decode

###
PCIeMappingPath = "/sys/class/nvme/%s/address"
###

class AttrValue(object):
    def __init__(self):
        self.value_list = []
        self.max_value = 0
        self.min_value = 0
        self.avg_value = 0
        ##
        self.__value_number = 0

    @property
    def current_value(self):
        return self.value_list[-1]

    def set_value(self, value, detail=''):
        self.value_list.append((int(time.time()), value, detail))
        self.max_value = max(self.max_value, value)
        self.min_value = min(self.min_value, value)
        self.avg_value = ((self.avg_value * self.__value_number) + value)
        self.__value_number += 1
        self.avg_value = (self.avg_value / self.__value_number)


class SmartKeyAttr(object):
    def __init__(self, name):
        self.__name = name
        self.__value = []

    def set_value(self, value):
        self.__value.append((int(time.time()), value))



class NVMeDevice(object):
    """
    dev_path: the nvme controller device path(ex. /dev/nvme0)
    
    
    """
    def __init__(self, dev_path):
        self.dev_path = dev_path
        self.bus_address = self._get_bus_addr_by_controller(dev_path)
        ## init device
        self.nvme_device = None
        self._init_device()

    def __del__(self):
        ## close device when exit
        if self.nvme_device:
            self.nvme_device.close()

    def _init_device(self):
        self.nvme_device = NVMe(init_device(self.dev_path))
        ## 
        return

    def _get_bus_addr_by_controller(self, ctrl):
        path = PCIeMappingPath % ctrl
        addr = None
        if os.path.exists(path):
            with open(path, 'r') as f:
                addr = f.read()
            addr = addr.strip()
        return addr

    def get_smart_once(self):
        cmd = self.nvme_device.smart_log()
        return nvme_smart_decode(cmd.data)

    def check_smart(self):
        ## check smart "Critical Warning"
        smart_info = self.get_smart_once()
        if smart_info.get("Critical Warning"):
            cw = smart_info.get("Critical Warning")
            pass
        if smart_info.get("Available Spare") and smart_info.get("Available Spare Threshold"):
            pass

    def check_pcie(self):
        pass
