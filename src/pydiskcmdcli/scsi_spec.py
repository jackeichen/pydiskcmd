# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmdlib.pyscsi.scsi import SCSI
from pydiskcmdlib.utils.converter import decode_bits,scsi_ba_to_int
from collections import namedtuple


log_page_format_head_bit_map = {"page_code": [0x3F, 0],
                                "spf": [0x40, 0],
                                "ds": [0x80, 0],
                                "subpage_code": [0xFF, 1],
                                "page_length": ('b', 2, 2, 'int_b'),
                                }
log_parameter_format_head_bit_map = {"parameter_code": ('b', 0, 2, 'int_b'),
                                     "ctrl_bit": ('b', 2, 1, 'int_b'),
                                     "parameter_length": ('b', 3, 1, 'int_b'),
                                     }

def decode_logpageformat(value):
    result = {"log_parameters":[]}
    decode_bits(value[0:4], log_page_format_head_bit_map, result)
    ##
    offset = 4
    max_page_len = 4 + result["page_length"]
    while (offset < max_page_len):
        ## first get parameter_length
        log_parameter = {}
        decode_bits(value[offset:offset+4], log_parameter_format_head_bit_map, log_parameter)
        offset += 4
        log_parameter["parameter_value"] = value[offset:offset+log_parameter["parameter_length"]]
        offset += log_parameter["parameter_length"]
        result["log_parameters"].append(log_parameter)
    return result

def decode_logpageformat_supportlogpage(value):
    result = {"log_parameters":[]}
    decode_bits(value[0:4], log_page_format_head_bit_map, result)
    ##
    for i in value[4:4+result["page_length"]]:
        result["log_parameters"].append(i)
    return result

def decode_logpageformat_supportsublogpage(value):
    result = {"log_parameters":[]}
    decode_bits(value[0:4], log_page_format_head_bit_map, result)
    ##
    for i in range(0, result["page_length"], 2):
        result["log_parameters"].append((value[4+i]&0x3F, value[5+i]))
    return result

class LogPageAttr(object):
    def __init__(self, page_code, subpage_code, name, decode_func=decode_logpageformat):
        self.__page_code = page_code
        self.__subpage_code = subpage_code
        self.__name = name
        self.__decode_func = decode_func

    @property
    def log_page_name(self):
        return self.__name

    @property
    def log_page_code(self):
        return self.__page_code

    @property
    def log_subpage_code(self):
        return self.__subpage_code

    def decode_value(self, value):
        return self.__decode_func(value)

LogSenseAttr = {(0x0F,0x00): LogPageAttr(0x0F, 0x00, 'Application Client'),
                (0x15,0x00): LogPageAttr(0x15, 0x00, 'Background Scan'),
                (0x15,0x02): LogPageAttr(0x15, 0x02, 'Background Operation'),
                (0x37,0x00): LogPageAttr(0x37, 0x00, 'Cache Statistics'),
                (0x0D,0x02): LogPageAttr(0x0D, 0x02, 'Environmental Limits'),
                (0x0D,0x01): LogPageAttr(0x0D, 0x01, 'Environmental Reporting'),
                (0x03,0x00): LogPageAttr(0x03, 0x00, 'Read Error Counter'),
                (0x05,0x00): LogPageAttr(0x05, 0x00, 'Verify Error Counter'),
                (0x02,0x00): LogPageAttr(0x02, 0x00, 'Write Error Counter'),
                (0x3E,0x00): LogPageAttr(0x3E, 0x00, 'Factory Log'),
                (0x08,0x00): LogPageAttr(0x08, 0x00, 'Format Status'),
                (0x2F,0x00): LogPageAttr(0x2F, 0x00, 'Informational Exceptions'),
                (0x0C,0x00): LogPageAttr(0x0C, 0x00, 'Logical Block Provisioning'),
                (0x06,0x00): LogPageAttr(0x06, 0x00, 'Non-Medium Error'),
                (0x15,0x01): LogPageAttr(0x15, 0x01, 'Pending Defects'),
                (0x1A,0x00): LogPageAttr(0x1A, 0x00, 'Power Condition Transitions'),
                (0x18,0x00): LogPageAttr(0x18, 0x00, 'Protocol Specific Port'),
                (0x10,0x00): LogPageAttr(0x10, 0x00, 'Self-Test Results'),
                (0x11,0x00): LogPageAttr(0x11, 0x00, 'Solid State Media'),
                (0x0E,0x00): LogPageAttr(0x0E, 0x00, 'Start-Stop Cycle Counter'),
                (0x00,0x00): LogPageAttr(0x00, 0x00, 'Supported Log Pages', decode_logpageformat_supportlogpage),
                (0x00,0xFF): LogPageAttr(0x00, 0xFF, 'Supported Log Pages and Subpages', decode_logpageformat_supportsublogpage),
                (0x0D,0x00): LogPageAttr(0x0D, 0x00, 'Temperature'),
                (0x0E,0x01): LogPageAttr(0x0E, 0x01, 'Utilization'),
                "Unkonwn": LogPageAttr(None, None, 'Unkonwn Log Page'),
            }


def get_smart_simulate(device: SCSI) -> dict:
    smart_table = {}
    smart_table_attr = namedtuple("smart_attr", ['AttributeName', 'LogPage', 'Value', 'Threshold'])
    # Get temperature
    cmd = device.logsense(0x0D, sub_page_code=0x00, sp=0, pc=1, parameter=0, alloclen=16, control=0)
    result = decode_logpageformat(cmd.datain)
    temperature = None
    reference_temperature = None
    for i in result["log_parameters"]:
        if i["parameter_code"] == 0 and i["parameter_length"] > 0:
            temperature = i["parameter_value"][1]
        if i["parameter_code"] == 1 and i["parameter_length"] > 0:
            reference_temperature = i["parameter_value"][1]
    if temperature is not None:
        temp = smart_table_attr(AttributeName="Temperature", LogPage=(0x0D, 0x00), Value=temperature, Threshold=reference_temperature)
        smart_table[temp.AttributeName] = temp
    # Get Power cycle Count
    cmd = device.logsense(0x0E, sub_page_code=0x00, sp=0, pc=1, parameter=0, alloclen=56, control=0)
    result = decode_logpageformat(cmd.datain)
    start_stop_cyle = None
    start_stop_cyle_thred = None
    load_unload_cycle = None
    load_unload_cycle_thred = None
    for i in result["log_parameters"]:
        if i["parameter_code"] == 3 and i["parameter_length"] > 0:
            start_stop_cyle_thred = scsi_ba_to_int(i["parameter_value"][0:4])
        elif i["parameter_code"] == 4 and i["parameter_length"] > 0:
            start_stop_cyle = scsi_ba_to_int(i["parameter_value"][0:4])
        elif i["parameter_code"] == 5 and i["parameter_length"] > 0:
            load_unload_cycle_thred = scsi_ba_to_int(i["parameter_value"][0:4])
        elif i["parameter_code"] == 6 and i["parameter_length"] > 0:
            load_unload_cycle = scsi_ba_to_int(i["parameter_value"][0:4])
    if start_stop_cyle is not None:
        temp = smart_table_attr(AttributeName="Power Cycle Count", LogPage=(0x0E, 0x00), Value=start_stop_cyle, Threshold=start_stop_cyle_thred)
        smart_table[temp.AttributeName] = temp
    if load_unload_cycle is not None:
        temp = smart_table_attr(AttributeName="Load Cycle Count", LogPage=(0x0E, 0x00), Value=load_unload_cycle, Threshold=load_unload_cycle_thred)
        smart_table[temp.AttributeName] = temp
    # Get Power On Time
    cmd = device.logsense(0x15, sub_page_code=0x00, sp=0, pc=1, parameter=0, alloclen=96, control=0)
    result = decode_logpageformat(cmd.datain)
    POH = None
    for i in result["log_parameters"]:
        if i["parameter_code"] == 0 and i["parameter_length"] > 0:
            POH = scsi_ba_to_int(i["parameter_value"][0:4])
    if POH is not None:
        temp = smart_table_attr(AttributeName="Power On Minutes", LogPage=(0x15, 0x00), Value=POH, Threshold=None)
        smart_table[temp.AttributeName] = temp
    # Get Percentage Used
    cmd = device.logsense(0x11, sub_page_code=0x00, sp=0, pc=1, parameter=0, alloclen=96, control=0)
    result = decode_logpageformat(cmd.datain)
    used = None
    for i in result["log_parameters"]:
        if i["parameter_code"] == 1 and i["parameter_length"] > 0:
            used = i["parameter_value"][3]
            break
    if used is not None:
        temp = smart_table_attr(AttributeName="Percentage Used", LogPage=(0x11, 0x00), Value=used, Threshold=100)
        smart_table[temp.AttributeName] = temp
    # Get Logical Block Provisioning
    cmd = device.logsense(0x0C, sub_page_code=0x00, sp=0, pc=1, parameter=0, alloclen=4, control=0)
    result = decode_logpageformat(cmd.datain)
    cmd = device.logsense(0x0C, sub_page_code=0x01, sp=0, pc=1, parameter=0, alloclen=result["page_length"]+4, control=0)
    result = decode_logpageformat(cmd.datain)
    available_spare = None
    for i in result["log_parameters"]:
        if i["parameter_code"] == 3 and i["parameter_length"] > 0:
            available_spare = scsi_ba_to_int(i["parameter_value"][0:2])
    if available_spare is not None:
        temp = smart_table_attr(AttributeName="Available Spare", LogPage=(0x0C, 0x00), Value=available_spare, Threshold=100)
        smart_table[temp.AttributeName] = temp
    # Get Workload Utilization
    cmd = device.logsense(0x0E, sub_page_code=0x01, sp=0, pc=1, parameter=0, alloclen=4, control=0)
    result = decode_logpageformat(cmd.datain)
    cmd = device.logsense(0x0E, sub_page_code=0x01, sp=0, pc=1, parameter=0, alloclen=result["page_length"]+4, control=0)
    result = decode_logpageformat(cmd.datain)
    workload_utilization = None
    for i in result["log_parameters"]:
        if i["parameter_code"] == 0 and i["parameter_length"] > 0:
            workload_utilization = scsi_ba_to_int(i["parameter_value"])
    if workload_utilization is not None:
        temp = smart_table_attr(AttributeName="Workload Utilization", LogPage=(0x0E, 0x01), Value=workload_utilization, Threshold=None)
        smart_table[temp.AttributeName] = temp
    # Get Total Write Data processed
    cmd = device.logsense(0x02, sub_page_code=0x00, sp=0, pc=1, parameter=0, alloclen=4, control=0)
    result = decode_logpageformat(cmd.datain)
    cmd = device.logsense(0x02, sub_page_code=0x00, sp=0, pc=1, parameter=0, alloclen=result["page_length"]+4, control=0)
    result = decode_logpageformat(cmd.datain)
    total_write = None
    total_corrected_errors = None
    total_uncorrected_errors = None
    for i in result["log_parameters"]:
        if i["parameter_code"] == 5 and i["parameter_length"] > 0:
            total_write = scsi_ba_to_int(i["parameter_value"])
        elif i["parameter_code"] == 3 and i["parameter_length"] > 0:
            total_corrected_errors = scsi_ba_to_int(i["parameter_value"])
        elif i["parameter_code"] == 6 and i["parameter_length"] > 0:
            total_uncorrected_errors = scsi_ba_to_int(i["parameter_value"])
    if total_write is not None:
        temp = smart_table_attr(AttributeName="Total Write", LogPage=(0x02, 0x00), Value=total_write, Threshold=None)
        smart_table[temp.AttributeName] = temp
    # Get Total Read
    cmd = device.logsense(0x03, sub_page_code=0x00, sp=0, pc=1, parameter=0, alloclen=4, control=0)
    result = decode_logpageformat(cmd.datain)
    cmd = device.logsense(0x03, sub_page_code=0x00, sp=0, pc=1, parameter=0, alloclen=result["page_length"]+4, control=0)
    result = decode_logpageformat(cmd.datain)
    total_read = None
    for i in result["log_parameters"]:
        if i["parameter_code"] == 5 and i["parameter_length"] > 0:
            total_read = scsi_ba_to_int(i["parameter_value"])
        elif i["parameter_code"] == 3 and i["parameter_length"] > 0:
            if total_corrected_errors is not None:
                total_corrected_errors += scsi_ba_to_int(i["parameter_value"])
            else:
                total_corrected_errors = scsi_ba_to_int(i["parameter_value"])
        elif i["parameter_code"] == 6 and i["parameter_length"] > 0:
            if total_uncorrected_errors is not None:
                total_uncorrected_errors += scsi_ba_to_int(i["parameter_value"])
            else:
                total_uncorrected_errors = scsi_ba_to_int(i["parameter_value"])
    if total_read is not None:
        temp = smart_table_attr(AttributeName="Total Read", LogPage=(0x03, 0x00), Value=total_read, Threshold=None)
        smart_table[temp.AttributeName] = temp
    # Get verify information
    cmd = device.logsense(0x05, sub_page_code=0x00, sp=0, pc=1, parameter=0, alloclen=4, control=0)
    result = decode_logpageformat(cmd.datain)
    cmd = device.logsense(0x05, sub_page_code=0x00, sp=0, pc=1, parameter=0, alloclen=result["page_length"]+4, control=0)
    result = decode_logpageformat(cmd.datain)
    for i in result["log_parameters"]:
        if i["parameter_code"] == 3 and i["parameter_length"] > 0:
            if total_corrected_errors is not None:
                total_corrected_errors += scsi_ba_to_int(i["parameter_value"])
            else:
                total_corrected_errors = scsi_ba_to_int(i["parameter_value"])
        elif i["parameter_code"] == 6 and i["parameter_length"] > 0:
            if total_uncorrected_errors is not None:
                total_uncorrected_errors += scsi_ba_to_int(i["parameter_value"])
            else:
                total_uncorrected_errors = scsi_ba_to_int(i["parameter_value"])
    # get total corrected errors
    if total_corrected_errors is not None:
        temp = smart_table_attr(AttributeName="Corrected Errors", LogPage=(), Value=total_corrected_errors, Threshold=None)
        smart_table[temp.AttributeName] = temp
    # get total uncorrected errors
    if total_uncorrected_errors is not None:
        temp = smart_table_attr(AttributeName="Reported Uncorrect", LogPage=(), Value=total_uncorrected_errors, Threshold=None)
        smart_table[temp.AttributeName] = temp
    # Get Non media error count
    cmd = device.logsense(0x06, sub_page_code=0x00, sp=0, pc=1, parameter=0, alloclen=4, control=0)
    result = decode_logpageformat(cmd.datain)
    cmd = device.logsense(0x06, sub_page_code=0x00, sp=0, pc=1, parameter=0, alloclen=result["page_length"]+4, control=0)
    result = decode_logpageformat(cmd.datain)
    error_count = None
    for i in result["log_parameters"]:
        if i["parameter_code"] == 0 and i["parameter_length"] > 0:
            error_count = scsi_ba_to_int(i["parameter_value"])
    if error_count is not None:
        temp = smart_table_attr(AttributeName="Non-Media Error", LogPage=(0x06, 0x00), Value=error_count, Threshold=None)
        smart_table[temp.AttributeName] = temp
    # Get Pending Defect Count
    cmd = device.logsense(0x15, sub_page_code=0x01, sp=0, pc=1, parameter=0, alloclen=4, control=0)
    result = decode_logpageformat(cmd.datain)
    cmd = device.logsense(0x06, sub_page_code=0x00, sp=0, pc=1, parameter=0, alloclen=result["page_length"]+4, control=0)
    result = decode_logpageformat(cmd.datain)
    pending_defect_count = None
    for i in result["log_parameters"]:
        if i["parameter_code"] == 0 and i["parameter_length"] > 0:
            pending_defect_count = scsi_ba_to_int(i["parameter_value"])
    if pending_defect_count is not None:
        temp = smart_table_attr(AttributeName="Pending Defect Count", LogPage=(0x15, 0x01), Value=pending_defect_count, Threshold=None)
        smart_table[temp.AttributeName] = temp
    return smart_table
