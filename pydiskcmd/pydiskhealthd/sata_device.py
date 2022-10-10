# SPDX-FileCopyrightText: 2014 The python-scsi Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import time
from pydiskcmd.pysata.sata import SATA
from pydiskcmd.utils import init_device
from pydiskcmd.utils.converter import bytearray2string,translocate_bytearray
from pydiskcmd.pysata.sata_spec import decode_smart_info,decode_smart_thresh,decode_smart_flag


class SmartAttr(object):
    def __init__(self, name, thresh):
        self.__name = name
        self.__thresh = thresh
        ##
        self.__value_list_max = 100
        self.value_list = [None,] * self.__value_list_max
        self.__value_list_head = 0
        ##
        self.__value_max = 0
        self.__value_min = 0
        self.__value_avg = 0
        #
        self.__raw_value_min = 0
        self.__raw_value_max = 0
        self.__raw_value_avg = 0
        ##
        self.__value_number = 0

    @property
    def name(self):
        return self.__name

    @property
    def current_value(self):
        return self.value_list[self.__value_list_head-1]

    def set_value(self, value, detail=''):
        """
        Value is a dict that decode by function->decode_smart_info
        detail: ''
        """
        info = (int(time.time()), value, detail)
        if self.__value_list_head < self.__value_list_max:
            self.value_list[self.__value_list_head] = info
        else:
            self.__value_list_head = 0
            self.value_list[self.__value_list_head] = info
        self.__value_list_head += 1
        self.__value_number += 1

    @property
    def thresh(self):
        return self.__thresh 

    @property
    def value_max(self):
        return self.__value_max

    @property
    def value_min(self):
        return self.__value_min

    @property
    def value_avg(self):
        return self.__value_avg

    @property
    def raw_value_min(self):
        return self.__raw_value_min

    @property
    def raw_value_max(self):
        return self.__raw_value_max

    @property
    def raw_value_avg(self):
        return self.__raw_value_avg


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
        return self.__device_id

    @property
    def smart_attr(self):
        return self.__smart_attr

    def get_smart_once(self):
        with SATA(init_device(self.dev_path, open_t="ata"), blocksize=512) as d:  
            general_smart = d.smart_read_data().result
            vs_smart = general_smart.pop('smartInfo')
        smart = decode_smart_info(vs_smart)
        ## check prefail attribute 
        if self.__smart_attr:  ## check attr changed
            for _id,s in smart.items():
                self.__smart_attr[_id].set_value(s)
        else: ## init smart attr
            with SATA(init_device(self.dev_path, open_t="ata"), blocksize=512) as d:
                ##
                cmd_thresh = d.smart_read_thresh()
                raw_data_thresh = cmd_thresh.datain
            smart_thresh = decode_smart_thresh(raw_data_thresh[2:362])
            ## init smart_attr
            for _id,s in smart.items():
                self.__smart_attr[_id] = SmartAttr(_id, smart_thresh[_id])
                self.__smart_attr[_id].set_value(s)
        return smart
