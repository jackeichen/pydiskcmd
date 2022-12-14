# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import os
import time
from pydiskcmd.pynvme.nvme import NVMe
from pydiskcmd.pypci.pci_lib import map_pci_device
from pydiskcmd.utils import init_device
from pydiskcmd.pynvme.nvme_spec import nvme_smart_decode,nvme_id_ctrl_decode
from pydiskcmd.pynvme.nvme_spec import persistent_event_log_header_decode,persistent_event_log_events_decode
from pydiskcmd.utils.converter import scsi_ba_to_int,ba_to_ascii_string
from pydiskcmd.pynvme.nvme_command import DataBuffer
from pydiskcmd.pydiskhealthd.DB import disk_trace_pool
from pydiskcmd.pydiskhealthd.linux_nvme_aer import AERTrace,AERTraceRL
from pydiskcmd.pydiskhealthd.some_path import DiskTracePath
###
PCIeMappingPath = "/sys/class/nvme/%s/address"
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
        ##

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


class PersistentEventTrace(object):
    def __init__(self, device_id):
        ##
        # self.last_trace
        self.last_trace_event_begin = {}
        self.current_trace = []
        ##
        self.__data_buffer = DataBuffer(16384)

    def init_last_trace_event_begin(self, raw_data):
        event_log_events = persistent_event_log_events_decode(raw_data, 1)
        self.last_trace_event_begin = event_log_events[0]

    def set_log(self, persistent_event_log_data):
        event_log_header = persistent_event_log_header_decode(persistent_event_log_data[0:512])
        event_log_events = persistent_event_log_events_decode(persistent_event_log_data[512:], scsi_ba_to_int(event_log_header.get("TNEV"), 'little'))
        if self.current_trace:
            self.last_trace_event_begin = self.current_trace[1][0]
            self.current_trace = [event_log_header, event_log_events]
        else:
            self.current_trace = [event_log_header, event_log_events]

    @property
    def current_trace_timestamp(self):
        if self.current_trace:
            return scsi_ba_to_int(self.current_trace[0].get("Timestamp"), 'little')

    @property
    def data_buffer(self):
        return self.__data_buffer

    def get_current_first_event_offset(self):
        if self.current_trace:
            event_log_event_header = self.current_trace[1][0]["event_log_event_header"]
            #
            ehl_int = scsi_ba_to_int(event_log_event_header.get("EHL"), 'little')
            el_int = scsi_ba_to_int(event_log_event_header.get("EL"), 'little')
            ## offset+ehl_int+el_int+2+1
            return ehl_int+el_int+2+1

    def diff_trace(self):
        if self.last_trace_event_begin and self.current_trace:
            result = []
            for k,v in self.current_trace[1].items():
                if v == self.last_trace_event_begin:
                    break
                result.append(v)
            return result


def get_dev_id(dev_path):
    ## get device ID
    device_id = None
    with NVMe(init_device(dev_path, open_t="nvme")) as d:
        result = nvme_id_ctrl_decode(d.ctrl_identify_info)
    device_id = ba_to_ascii_string(result.get("SN"), "")
    return device_id.strip()


class NVMeDevice(object):
    """
    dev_path: the nvme controller device path(ex. /dev/nvme0)
    """
    def __init__(self, dev_path, init_db=False):
        self.__device_type = 'nvme'
        self.dev_path = dev_path
        bus_address = self._get_bus_addr_by_controller(dev_path)
        ## get device ID
        self.__model = None
        self.__serial = None
        with NVMe(init_device(dev_path, open_t="nvme")) as d:
            result = nvme_id_ctrl_decode(d.ctrl_identify_info)
        self.__serial = ba_to_ascii_string(result.get("SN"), "")
        self.__model = ba_to_ascii_string(result.get("MN"), "")
        self.__media_type = "SSD"
        ##
        self.pcie_context = map_pci_device(bus_address)
        self.__pcie_trace = PCIeTrace()
        # init smart attr
        self.__smart_trace = SmartTrace()
        # init 
        self.__persistent_event_log = PersistentEventTrace(self.device_id)
        ##
        self.__device_info_db = None
        if init_db:
            self.init_db()

    def __del__(self):
        ## close device when exit
        self._close()

    def _close(self):
        '''
        May save the smart to a file, used in next power on
        '''
        pass

    def init_db(self):
        if disk_trace_pool:
            self.__device_info_db = disk_trace_pool.get_table_by_id(self.device_id)
            ## try to initial smart info, stored in last time.
            res = self.__device_info_db.get_dev_current_info()
            if res:
                timestamp,smart,last_persistent = res
                if smart:
                    self.__smart_trace.set_smart(smart, timestamp)
                    #print ("Init nvme  smart: ")
                    #print (smart)
                if last_persistent:
                    self.__persistent_event_log.init_last_trace_event_begin(last_persistent)
                    #print ("Init persistent_event_log begin:")
                    #print (self.__persistent_event_log.last_trace_event_begin)

    @property
    def device_type(self):
        return self.__device_type

    @property
    def device_id(self):
        return self.__serial.strip()

    @property
    def smart_trace(self):
        return self.__smart_trace

    @property
    def pcie_trace(self):
        return self.__pcie_trace

    @property
    def persistent_event_log(self):
        return self.__persistent_event_log

    @property
    def Model(self):
        return self.__model

    @property
    def Serial(self):
        return self.__serial

    @property
    def MediaType(self):
        return self.__media_type

    def _get_bus_addr_by_controller(self, ctrl):
        path = PCIeMappingPath % ctrl.replace("/dev/", "")
        addr = None
        if os.path.exists(path):
            with open(path, 'r') as f:
                addr = f.read()
            addr = addr.strip()
        return addr

    def get_log_once(self):
        smart_data = None
        persistent_event_log_data = None
        ##
        with NVMe(init_device(self.dev_path, open_t="nvme")) as d:
            cmd = d.smart_log()
            smart_data = cmd.data
            ##
            persistent_event_log_status = 0  # the state of persistent_event_log_status
            persistent_event_log_ret = d.get_persistent_event_log(3, data_buffer=self.__persistent_event_log.data_buffer)
            if persistent_event_log_ret == 6:
                ## not support persistent_event_log
                pass
            else:
                if persistent_event_log_ret == 1:
                    ## the persistent_event_log is opened 
                    persistent_event_log_status = 1
                    ## need close it to refresh the log
                    d.get_persistent_event_log(2, data_buffer=self.__persistent_event_log.data_buffer)
                d.get_persistent_event_log(0, data_buffer=self.__persistent_event_log.data_buffer)
                persistent_event_log_data = d.get_persistent_event_log(1, data_buffer=self.__persistent_event_log.data_buffer)
                if persistent_event_log_status == 0: # if not open, then close it.
                    d.get_persistent_event_log(2, data_buffer=self.__persistent_event_log.data_buffer)
        current_t = float(time.time())
        if smart_data:
            self.__smart_trace.set_smart(smart_data, current_t)
        ##
        if persistent_event_log_data:
            self.__persistent_event_log.set_log(persistent_event_log_data)
        ## store it to db
        if self.__device_info_db:
            current_trace_event_begin = None
            offset = self.__persistent_event_log.get_current_first_event_offset()
            if offset is not None:
                current_trace_event_begin = persistent_event_log_data[512:512+offset]
            ##
            self.__device_info_db.update_dev_info(current_t, smart_data, current_trace_event_begin)
        return self.__smart_trace,self.__persistent_event_log

    def update_pcie_trace(self):
        self.__pcie_trace.pcie_link_status = self.pcie_context.express_link
        self.__pcie_trace.pcie_aer_status = self.pcie_context.express_aer
