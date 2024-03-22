# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import os
###
KernelTraceEventPath = "/sys/kernel/debug/tracing/events"
KernelNVMeAEREnable = "/sys/kernel/debug/tracing/events/nvme/nvme_async_event/enable"
KernelNVMeAERTraceFile = "/sys/kernel/debug/tracing/trace"
KernelNVMeAERTracePIPEFile = "/sys/kernel/debug/tracing/trace_pipe"
###

def check_aer_support():
    return os.path.isfile(KernelNVMeAEREnable)

def if_other_event_enabled():
    '''
    check all the trace event(excluded nvme_async_event) enabled or disabled
    '''
    with open("/sys/kernel/debug/tracing/events/enable", 'r') as f:
        content = f.read()
    return content.strip() != '0'

class NVMeAER(object):
    '''
    NVMe Asynchronous Event Check
    '''
    def __init__(self):
        self.__aer_enable_file = KernelNVMeAEREnable
        self.__trace_log_file = KernelNVMeAERTraceFile
        if (not os.path.isfile(self.__aer_enable_file)) or (not os.path.isfile(self.__trace_log_file)):
            raise RuntimeError("No Trace fucntion!")
        if not self.check_aer_status():
            self.enable_aer()
        ##

    @property
    def trace_log_file(self):
        return self.__trace_log_file

    def enable_aer(self):
        with open(self.__aer_enable_file, "w") as f:
            f.write("1")

    def disable_aer(self):
        with open(self.__aer_enable_file, "w") as f:
            f.write("0")

    def check_aer_status(self):
        with open(self.__aer_enable_file, "r") as f:
            status = f.read()
        return int(status)

    def _decode_trace_by_line(self, content):
        description = None
        ## skip annotation
        if not content.startswith("#"):
            ## check if nvme_async_event
            if "nvme_async_event:" in content:
                description = {}
                ##
                content = content.strip()
                temp_list = content.split(' ')
                ## remove "''"
                while '' in temp_list:
                    temp_list.remove('')
                ## strip ":"
                for i in range(len(temp_list)):
                    if temp_list[i].endswith(":"):
                        temp_list[i] = temp_list[i].rstrip(":")
                ##
                description["TASK-PID"] = temp_list[0]
                description["CPU#"] = temp_list[1]
                description["setting"] = temp_list[2]
                description["TIMESTAMP"] = float(temp_list[3])
                description["DEV"] = temp_list[5]
                description["NVME_AEN"] = int(temp_list[6].strip("NVME_AEN="), base=16)
                description["AER_TYPE"] = temp_list[7]
        return description

    def check_trace_once(self):
        '''
        description = {"TASK-PID": '',
                       "CPU#": '',
                       "setting": '',
                       "TIMESTAMP": 0,
                       "DEV": '',
                       "NVME_AEN": '',
                       "AER_TYPE": }
        '''
        nvme_aer = []
        ##
        with open(self.__trace_log_file, 'r') as f:
            while True:
                content = f.readline()
                if not content:
                    break
                description = self._decode_trace_by_line(content)
                if description:
                    nvme_aer.append(description)
        return nvme_aer
