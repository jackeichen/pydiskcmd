# SPDX-FileCopyrightText: 2014 The python-scsi Authors
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
###

class SmartKeyAttr(object):
    def __init__(self, name):
        self.__name = name
        ##
        self.__value_list_max = 100
        self.value_list = [None,] * self.__value_list_max
        self.__value_list_head = 0
        ##
        self.max_value = 0
        self.min_value = 0
        self.avg_value = 0
        ##
        self.__value_number = 0

    @property
    def name(self):
        return self.__name

    @property
    def value_list_head(self):
        if self.__value_list_head >= self.__value_list_max:
            self.__value_list_head = 0
        return self.__value_list_head

    @property
    def current_value(self):
        return self.value_list[self.value_list_head-1]

    @property
    def initd_value(self):
        return (self.value_list[self.value_list_head] or self.value_list[0])

    def set_value(self, value, detail=''):
        self.value_list[self.value_list_head] = (int(time.time()), value, detail)
        self.__value_list_head += 1
        ##
        self.max_value = max(self.max_value, value)
        self.min_value = min(self.min_value, value)
        self.avg_value = ((self.avg_value * self.__value_number) + value)
        self.__value_number += 1
        self.avg_value = (self.avg_value / self.__value_number)


class PCIeReport(object): 
    """
    'RxErr', 'BadTLP', 'BadDLLP', 'Rollover', 'Timeout', 'NonFatalErr', 'CorrIntErr', 'HeaderOF', 'TOTAL_ERR_COR'
    
    'Undefined', 'DLP', 'SDES', 'TLP', 'FCP', 'CmpltTO', 'CmpltAbrt', 'UnxCmplt', 'RxOF', 'MalfTLP', 'ECRC', 'UnsupReq', 
    'ACSViol', 'UncorrIntErr', 'BlockedTLP', 'AtomicOpBlocked', 'TLPBlockedErr', 'PoisonTLPBlocked', 'TOTAL_ERR_FATAL'
    """
    def __init__(self):
        ## link status
        self.link_report_times = {"speed": 0,
                                  "width": 0}
        self.last_link_status = {"speed": '',
                                 "width": 0}
        ## AER
        self.aer_ce_report_times = {'RxErr': 0, 
                                    'BadTLP': 0, 
                                    'BadDLLP': 0, 
                                    'Rollover': 0, 
                                    'Timeout': 0, 
                                    'NonFatalErr': 0, 
                                    'CorrIntErr': 0, 
                                    'HeaderOF': 0, 
                                    'TOTAL_ERR_COR': 0}
        self.aer_fatal_report_times = {'Undefined': 0, 
                                       'DLP': 0, 
                                       'SDES': 0, 
                                       'TLP': 0, 
                                       'FCP': 0, 
                                       'CmpltTO': 0, 
                                       'CmpltAbrt': 0, 
                                       'UnxCmplt': 0, 
                                       'RxOF': 0, 
                                       'MalfTLP': 0, 
                                       'ECRC': 0, 
                                       'UnsupReq': 0, 
                                       'ACSViol': 0, 
                                       'UncorrIntErr': 0, 
                                       'BlockedTLP': 0, 
                                       'AtomicOpBlocked': 0, 
                                       'TLPBlockedErr': 0, 
                                       'PoisonTLPBlocked': 0, 
                                       'TOTAL_ERR_FATAL': 0}
        self.aer_nonfatal_report_times = {'Undefined': 0, 
                                          'DLP': 0, 
                                          'SDES': 0, 
                                          'TLP': 0, 
                                          'FCP': 0, 
                                          'CmpltTO': 0, 
                                          'CmpltAbrt': 0, 
                                          'UnxCmplt': 0, 
                                          'RxOF': 0, 
                                          'MalfTLP': 0, 
                                          'ECRC': 0, 
                                          'UnsupReq': 0, 
                                          'ACSViol': 0, 
                                          'UncorrIntErr': 0, 
                                          'BlockedTLP': 0, 
                                          'AtomicOpBlocked': 0, 
                                          'TLPBlockedErr': 0, 
                                          'PoisonTLPBlocked': 0, 
                                          'TOTAL_ERR_NONFATAL': 0}

    def set_aer_report_time(self, aer_type, error):
        if aer_type == "aer_dev_correctable" and error in self.aer_ce_report_times:
            self.aer_ce_report_times[error] += 1
        elif aer_type == "aer_dev_fatal" and error in self.aer_fatal_report_times:
            self.aer_fatal_report_times[error] += 1
        elif aer_type == "aer_dev_nonfatal" and error in self.aer_nonfatal_report_times:
            self.aer_nonfatal_report_times[error] += 1
        else:
            pass


class NVMeDevice(object):
    """
    dev_path: the nvme controller device path(ex. /dev/nvme0)
    
    
    """
    def __init__(self, dev_path):
        self.__device_type = 'nvme'
        self.dev_path = dev_path
        bus_address = self._get_bus_addr_by_controller(dev_path)
        self.pcie_context = map_pci_device(bus_address)
        self.pcie_report = PCIeReport()  ## class used by pydiskhealthd
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
