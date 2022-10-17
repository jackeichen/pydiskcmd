# SPDX-FileCopyrightText: 2014 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import os
import time
from pydiskcmd.pynvme.nvme import NVMe
from pydiskcmd.pypci.pci_lib import map_pci_device
from pydiskcmd.utils import init_device
from pydiskcmd.pynvme.nvme_spec import nvme_smart_decode,nvme_id_ctrl_decode
from pydiskcmd.utils.converter import scsi_ba_to_int,ba_to_ascii_string

###
PCIeMappingPath = "/sys/class/nvme/%s/address"
SMARTTracePath = "/var/log/pydiskcmd/smart_trace/"
###


class SmartInfo(object):
    def __init__(self, raw_value, time_t):
        self.raw_value = raw_value
        self.time_t = time_t
        ##
        self.smart_info = nvme_smart_decode(self.raw_value)
        for _id in self.smart_info.keys():
            self.smart_info[_id] = scsi_ba_to_int(self.smart_info[_id], 'little')

    def get_attr_by_id(self, _id):
        return self.smart_info.get(_id)


class SmartCalculatedValue(object):
    def __init__(self):
        self.value_int_min = 0
        self.value_int_max = 0
        self.value_int_avg = 0
        self.time_t = 0


class SmartTrace(object):
    def __init__(self):
        ## define smart cache, it usually store the decode smart here
        self.__smart_cache_depth = 100
        self.__smart_cache = [None,] * self.__smart_cache_depth
        self.__smart_cache_index = 0
        self.__smart_cache_index_rollover_cycle = 0
        ## current value is decode smart, setted by function set_smart()
        #  after the next set_smart(), the current is stored to smart_cache 
        self.__current_value = None
        ## need trace the max,min,avg value in vs_smart_info per attribute
        # key: the smart id, int type
        # value: SmartCalculatedValue object
        # the current value DO Not included in this calculated_value
        self.__vs_smart_calculated_value = {}

    @property
    def current_value(self):
        return self.__current_value

    @property
    def smart_cache(self):
        return self.__smart_cache

    @property
    def vs_smart_calculated_value(self):
        return self.__vs_smart_calculated_value

    @property
    def vs_smart_calculated_initd(self):
        return (not self.__vs_smart_calculated_value)

    def if_cached_smart(self):
        if self.__smart_cache_index or self.__smart_cache_index_rollover_cycle:
            return True
        return False

    def get_cache_last_value(self):
        return self.__smart_cache[self.get_smart_cache_index() - 1]

    def get_smart_cache_index(self):
        if self.__smart_cache_index < self.__smart_cache_depth:
            return self.__smart_cache_index
        else:
            self.__smart_cache_index_rollover_cycle += 1
            self.__smart_cache_index = 0
            return self.__smart_cache_index

    def set_smart(self, raw_data, time_t):
        ## TODO: store the raw value to file 
        ## decode the smart info
        smart = SmartInfo(raw_data, time_t)
        ## current value handle
        if self.__current_value:
            ## first update vs_smart_calculated_value
            for _id,value_int in self.__current_value.smart_info.items():
                if self.__vs_smart_calculated_value.get(_id):
                    if value_int > self.__vs_smart_calculated_value[_id].value_int_max:
                        self.__vs_smart_calculated_value[_id].value_int_max = value_int
                        self.__vs_smart_calculated_value[_id].time_t = self.__current_value.time_t
                    elif value_int < self.__vs_smart_calculated_value[_id].value_int_min:
                        self.__vs_smart_calculated_value[_id].value_int_min = value_int
                        self.__vs_smart_calculated_value[_id].time_t = self.__current_value.time_t
                else:
                    temp = SmartCalculatedValue()
                    temp.value_int_min = value_int
                    temp.value_int_max = value_int
                    temp.value_int_avg = value_int
                    temp.time_t = time_t
                    ##
                    self.__vs_smart_calculated_value[_id] = temp
            ## store the current value to cache
            index = self.get_smart_cache_index()
            self.__smart_cache[index] = self.__current_value
            self.__smart_cache_index += 1
        # set current the new value 
        self.__current_value = smart


class PCIeTrace(object):
    def __init__(self):
        self.pcie_link_status = None
        self.pcie_aer_status = {}


class NVMeDevice(object):
    """
    dev_path: the nvme controller device path(ex. /dev/nvme0)
    
    
    """
    def __init__(self, dev_path):
        self.__device_type = 'nvme'
        self.dev_path = dev_path
        bus_address = self._get_bus_addr_by_controller(dev_path)
        self.pcie_context = map_pci_device(bus_address)
        self.__pcie_trace = PCIeTrace()
        # init smart attr
        self.__smart_trace = SmartTrace()
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
        return self.__device_id.strip()

    @property
    def smart_trace(self):
        return self.__smart_trace

    @property
    def pcie_trace(self):
        return self.__pcie_trace

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
        self.__smart_trace.set_smart(cmd.data, int(time.time()))
        return self.__smart_trace

    def update_pcie_trace(self):
        self.__pcie_trace.pcie_link_status = self.pcie_context.express_link
        self.__pcie_trace.pcie_aer_status = self.pcie_context.express_aer
