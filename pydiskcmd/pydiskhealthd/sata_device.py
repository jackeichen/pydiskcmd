# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import time
from pydiskcmd.pysata.sata import SATA
from pydiskcmd.pyscsi.scsi import SCSI
from pydiskcmd.utils import init_device
from pydiskcmd.utils.converter import bytearray2string,translocate_bytearray
from pydiskcmd.pysata.sata_spec import decode_bits,SMART_KEY,decode_smart_info,decode_smart_thresh,decode_smart_flag
from pydiskcmd.pydiskhealthd.DB import disk_trace_pool
from pydiskcmd.pydiskhealthd.disk_health_calculation import get_ata_diskhealth
from pyscsi.pyscsi import scsi_enum_inquiry as INQUIRY


class SmartInfo(object):
    def __init__(self, vs_value, time_t, thresh_info):
        self.raw_vs_value = vs_value
        self.time_t = time_t
        ##
        self.smart_info = decode_smart_info(self.raw_vs_value)
        ##
        self.disk_health = get_ata_diskhealth(self.smart_info, thresh_info)

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
        self.__smart_cache_depth = 5
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
        ## decode the smart info
        smart_all = {}
        decode_bits(raw_data, SMART_KEY, smart_all)
        smart = SmartInfo(smart_all.get("smartInfo"), time_t, self.thresh_info)
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


def get_dev_id(dev_path):
    ## get device ID
    device_id = None
    with SATA(init_device(dev_path, open_t="ata"), blocksize=512) as d:
        cmd = d.identify()
        result = cmd.result
    device_id = bytearray2string(translocate_bytearray(result.get("SerialNumber")))
    return device_id.strip()


class ATADeviceBase(object):
    """
    dev_path: the nvme controller device path(ex. /dev/nvme0)
    
    
    """
    def __init__(self, dev_path):
        self.__device_type = 'ata'
        self.dev_path = dev_path
        ##
        self.__model = None
        self.__serial = None
        self._id_info = b''
        with SATA(init_device(self.dev_path, open_t="ata"), blocksize=512) as d:
            self._id_info = d.identify_raw
            cmd_identify = d.identify()
            identify_info = cmd_identify.result
        ##
        self.__model = bytearray2string(translocate_bytearray(identify_info.get("ModelNumber")))
        self.__serial = bytearray2string(translocate_bytearray(identify_info.get("SerialNumber")))

    @property
    def device_id(self):
        return self.__serial.strip().replace("-", "_")

    @property
    def device_type(self):
        return self.__device_type

    @property
    def Model(self):
        return self.__model

    @property
    def Serial(self):
        return self.__serial

    @property
    def id_info(self):
        return self._id_info


class ATAFeatureStatus(object):
    def __init__(self):
        self.smart = False


class ATADevice(ATADeviceBase):
    """
    dev_path: the nvme controller device path(ex. /dev/nvme0)
    
    
    """
    def __init__(self, dev_path, init_db=False):
        super(ATADevice, self).__init__(dev_path)
        self.ata_feature_status = ATAFeatureStatus()
        if (self.id_info[164] & 0x01) and (self.id_info[170] & 0x01):
            self.ata_feature_status.smart = True
        self.check_feature_support ={"smart": self.ata_feature_status.smart,}
        # init smart trace,
        # the smart_read_thresh is persistent, so init it at first
        with SATA(init_device(self.dev_path, open_t="ata"), blocksize=512) as d:
            ##
            cmd_thresh = d.smart_read_thresh()
            raw_data_thresh = cmd_thresh.datain
        self.__smart_trace = SmartTrace(raw_data_thresh)
        #
        with SCSI(init_device(self.dev_path, open_t="scsi"), blocksize=512) as d:
            cmd = d.inquiry(evpd=1, page_code=INQUIRY.VPD.BLOCK_DEVICE_CHARACTERISTICS)
            i = cmd.result
        self.__media_type = None
        if i.get("medium_rotation_rate") == 1:
            self.__media_type = "SSD"
        elif i.get("medium_rotation_rate") > 1:
            self.__media_type = "HDD"
        ##
        self.__device_info_db = None
        if init_db:
            self.init_db()

    def __del__(self):
        ## close device when exit
        self._close()

    def _close(self):
        pass

    def init_db(self):
        if disk_trace_pool:
            self.__device_info_db = disk_trace_pool.get_table_by_id(self.device_id)
            ##
            res = self.__device_info_db.get_dev_current_info()
            if res:
                timestamp,smart,last_persistent = res
                if smart:
                    self.__smart_trace.set_smart(smart, timestamp)
                    #print ("Init sata smart: ")
                    #print (smart)

    @property
    def smart_trace(self):
        return self.__smart_trace

    @property
    def MediaType(self):
        return self.__media_type

    @property
    def smart_enable(self):
        return self.check_feature_support.get("smart")

    def get_smart_once(self):
        current_t = float(time.time())
        with SATA(init_device(self.dev_path, open_t="ata"), blocksize=512) as d:
            raw_data = d.smart_read_data().datain
        #
        self.__smart_trace.set_smart(raw_data, current_t)
        ## store to db,
        if self.__device_info_db:
            self.__device_info_db.update_dev_info(current_t, raw_data)
        return self.__smart_trace
