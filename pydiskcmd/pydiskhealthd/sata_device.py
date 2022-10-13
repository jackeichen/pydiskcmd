# SPDX-FileCopyrightText: 2014 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import time
from pydiskcmd.pysata.sata import SATA
from pydiskcmd.utils import init_device
from pydiskcmd.utils.converter import bytearray2string,translocate_bytearray
from pydiskcmd.pysata.sata_spec import decode_bits,SMART_KEY,decode_smart_info,decode_smart_thresh,decode_smart_flag


class SmartInfo(object):
    def __init__(self, vs_value, time_t):
        self.raw_vs_value = vs_value
        self.time_t = time_t
        ##
        self.smart_info = decode_smart_info(self.raw_vs_value)

    def get_attr_by_id(self, _id):
        return self.smart_info.get(_id)


class SmartCalculatedValue(object):
    def __init__(self):
        self.value_int_min = 0
        self.value_int_max = 0
        self.value_int_avg = 0
        self.worst_int_min = 0
        self.worst_int_max = 0
        self.worst_int_avg = 0
        self.raw_value_int_min = 0
        self.raw_value_int_max = 0
        self.raw_value_int_avg = 0


class SmartTrace(object):
    def __init__(self, thresh_value):
        ## set the smart threshold
        self.thresh_value = thresh_value
        self.thresh_info = decode_smart_thresh(self.thresh_value[2:362])
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
        smart_all = {}
        decode_bits(raw_data, SMART_KEY, smart_all)
        smart = SmartInfo(smart_all.get("smartInfo"), time_t)
        ## current value handle
        if self.__current_value:
            ## first update vs_smart_calculated_value
            for _id,smart_attr in self.__current_value.smart_info.items():
                if self.__vs_smart_calculated_value.get(_id):
                    if smart_attr.value > self.__vs_smart_calculated_value[_id].value_int_max:
                        self.__vs_smart_calculated_value[_id].value_int_max = smart_attr.value
                    elif smart_attr.value < self.__vs_smart_calculated_value[_id].value_int_min:
                        self.__vs_smart_calculated_value[_id].value_int_min = smart_attr.value
                    if smart_attr.worst > self.__vs_smart_calculated_value[_id].worst_int_max:
                        self.__vs_smart_calculated_value[_id].worst_int_max = smart_attr.worst
                    elif smart_attr.worst < self.__vs_smart_calculated_value[_id].worst_int_min:
                        self.__vs_smart_calculated_value[_id].worst_int_min = smart_attr.worst
                    if smart_attr.raw_value_int > self.__vs_smart_calculated_value[_id].raw_value_int_max:
                        self.__vs_smart_calculated_value[_id].raw_value_int_max = smart_attr.raw_value_int
                    elif smart_attr.raw_value_int < self.__vs_smart_calculated_value[_id].raw_value_int_min:
                        self.__vs_smart_calculated_value[_id].raw_value_int_min = smart_attr.raw_value_int
                else:
                    temp = SmartCalculatedValue()
                    temp.value_int_min = smart_attr.value
                    temp.value_int_max = smart_attr.value
                    temp.value_int_avg = smart_attr.value
                    temp.worst_int_min = smart_attr.worst
                    temp.worst_int_max = smart_attr.worst
                    temp.worst_int_avg = smart_attr.worst
                    temp.raw_value_int_min = smart_attr.raw_value_int
                    temp.raw_value_int_max = smart_attr.raw_value_int
                    temp.raw_value_int_avg = smart_attr.raw_value_int
                    ##
                    self.__vs_smart_calculated_value[_id] = temp
            ## store the current value to cache
            index = self.get_smart_cache_index()
            self.__smart_cache[index] = self.__current_value
            self.__smart_cache_index += 1
        # set current the new value 
        self.__current_value = smart


class ATADevice(object):
    """
    dev_path: the nvme controller device path(ex. /dev/nvme0)
    
    
    """
    def __init__(self, dev_path):
        self.__device_type = 'ata'
        self.dev_path = dev_path
        # init smart trace
        with SATA(init_device(self.dev_path, open_t="ata"), blocksize=512) as d:
            cmd_thresh = d.smart_read_thresh()
            raw_data_thresh = cmd_thresh.datain
        self.__smart_trace = SmartTrace(raw_data_thresh)
        ## init device
        self.__device_id = None
        with SATA(init_device(self.dev_path, open_t="ata"), blocksize=512) as d:
            cmd = d.identify()
            result = cmd.result
        self.__device_id = bytearray2string(translocate_bytearray(result.get("SerialNumber")))

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

    @property
    def smart_trace(self):
        return self.__smart_trace

    def get_smart_once(self):
        with SATA(init_device(self.dev_path, open_t="ata"), blocksize=512) as d:  
            general_smart = d.smart_read_data().result
            vs_smart = general_smart.pop('smartInfo')
        #
        self.__smart_trace.set_smart(vs_smart, int(time.time()))
        return self.__smart_trace
