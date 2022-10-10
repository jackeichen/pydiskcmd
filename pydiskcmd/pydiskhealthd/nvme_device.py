# SPDX-FileCopyrightText: 2014 The python-scsi Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import os
import time
from pydiskcmd.pynvme.nvme import NVMe
from pydiskcmd.utils import init_device
from pydiskcmd.pynvme.nvme_spec import nvme_smart_decode,nvme_id_ctrl_decode
from pydiskcmd.utils.converter import scsi_ba_to_int,ba_to_ascii_string

###
PCIeMappingPath = "/sys/class/nvme/%s/address"
###

class AttrValue(object):
    def __init__(self):
        self.value_list_max = 100
        self.value_list = [None,] * self.value_list_max
        self.value_list_head = 0
        ##
        self.max_value = 0
        self.min_value = 0
        self.avg_value = 0
        ##
        self.__value_number = 0

    @property
    def current_value(self):
        return self.value_list[self.value_list_head-1]

    def set_value(self, value, detail=''):
        info = (int(time.time()), value, detail)
        if self.value_list_head < self.value_list_max:
            self.value_list[self.value_list_head] = info
        else:
            self.value_list_head = 0
            self.value_list[self.value_list_head] = info
        self.value_list_head += 1
        ##
        self.max_value = max(self.max_value, value)
        self.min_value = min(self.min_value, value)
        self.avg_value = ((self.avg_value * self.__value_number) + value)
        self.__value_number += 1
        self.avg_value = (self.avg_value / self.__value_number)


class SmartKeyAttr(object):
    def __init__(self, name):
        self.__name = name
        self.__value = AttrValue()

    @property
    def name(self):
        return self.__name

    @property
    def value(self):
        return self.__value

    def set_value(self, value):
        self.__value.set_value(value)


class NVMeDevice(object):
    """
    dev_path: the nvme controller device path(ex. /dev/nvme0)
    
    
    """
    def __init__(self, dev_path):
        self.__device_type = 'nvme'
        self.dev_path = dev_path
        self.bus_address = self._get_bus_addr_by_controller(dev_path)
        # init smart attr
        self.__smart_attr = {"Critical Warning": SmartKeyAttr("Critical Warning"),
                             "Available Spare": SmartKeyAttr("Available Spare"),
                             "Available Spare Threshold": SmartKeyAttr("Available Spare Threshold"),
                             "Percentage Used": SmartKeyAttr("Percentage Used"),
                             "Media and Data Integrity Errors": SmartKeyAttr("Media and Data Integrity Errors"),
                             "Number of Error Information Log Entries": SmartKeyAttr("Number of Error Information Log Entries"),
                             "Warning Composite Temperature Time": SmartKeyAttr("Warning Composite Temperature Time"),
                             "Critical Composite Temperature Time": SmartKeyAttr("Critical Composite Temperature Time "),
                            }
        ## get device ID
        self.__device_id = None
        with NVMe(init_device(self.dev_path, open_t="nvme")) as d:
            result = nvme_id_ctrl_decode(d.ctrl_identify_info)
        self.__device_id = ba_to_ascii_string(result.get("SN"), "")

    def __del__(self):
        ## close device when exit
        self._close()

    def _close(self):
        '''
        May save the smart to a file, used in next power on
        '''
        pass

    @property
    def device_type(self):
        return self.__device_type

    @property
    def device_id(self):
        return self.__device_id

    @property
    def smart_attr(self):
        return self.__smart_attr

    def _get_bus_addr_by_controller(self, ctrl):
        path = PCIeMappingPath % ctrl.replace("/dev/", "")
        addr = None
        if os.path.exists(path):
            with open(path, 'r') as f:
                addr = f.read()
            addr = addr.strip()
        return addr

    def get_smart_once(self):
        with NVMe(init_device(self.dev_path, open_t="nvme")) as d:
            cmd = d.smart_log()
        smart = nvme_smart_decode(cmd.data)
        self.__smart_attr["Critical Warning"].set_value(scsi_ba_to_int(smart.get("Critical Warning"), 'little'))
        self.__smart_attr["Available Spare"].set_value(scsi_ba_to_int(smart.get("Available Spare"), 'little'))
        self.__smart_attr["Available Spare Threshold"].set_value(scsi_ba_to_int(smart.get("Available Spare Threshold"), 'little'))
        self.__smart_attr["Percentage Used"].set_value(scsi_ba_to_int(smart.get("Percentage Used"), 'little'))
        self.__smart_attr["Media and Data Integrity Errors"].set_value(scsi_ba_to_int(smart.get("Media and Data Integrity Errors"), 'little'))
        self.__smart_attr["Number of Error Information Log Entries"].set_value(scsi_ba_to_int(smart.get("Number of Error Information Log Entries"), 'little'))
        self.__smart_attr["Warning Composite Temperature Time"].set_value(scsi_ba_to_int(smart.get("Warning Composite Temperature Time"), 'little'))
        self.__smart_attr["Critical Composite Temperature Time"].set_value(scsi_ba_to_int(smart.get("Critical Composite Temperature Time"), 'little'))
        return smart
