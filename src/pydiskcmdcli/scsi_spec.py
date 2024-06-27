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


class SimulateSmartMember(object):
    def __init__(self, 
                 page,
                 subpage,
                 sp=0,
                 pc=1,
                 parameter=0):
        self.page = page
        self.subpage = subpage
        self.sp = sp
        self.pc = pc
        self.parameter = parameter

    def get_value(self, device: SCSI, *args):
        ## send command
        cmd = device.logsense(self.page, sub_page_code=self.subpage, sp=self.sp, pc=self.pc, parameter=self.parameter, alloclen=4, control=0)
        decode_data = decode_logpageformat(cmd.datain)
        cmd = device.logsense(self.page, sub_page_code=self.subpage, sp=self.sp, pc=self.pc, parameter=self.parameter, alloclen=decode_data["page_length"]+4, control=0)
        decode_data = decode_logpageformat(cmd.datain)
        ##
        result = []
        for parameter_code,offset,length in args:
            for i in decode_data["log_parameters"]:
                if i["parameter_code"] == parameter_code and i["parameter_length"] > 0:
                    if length is None:
                        length = i["parameter_length"]
                    result.append(scsi_ba_to_int(i["parameter_value"][offset:offset+length]))
                    break
            else:
                result.append(None)
        return result

def get_smart_simulate(device: SCSI) -> dict:
    smart_table = {}
    smart_table_attr = namedtuple("smart_attr", ['AttributeName', 'LogPage', 'Value', 'Threshold'])
    # Get support log page
    cmd = device.logsense(0)
    support_log_page = decode_logpageformat_supportlogpage(cmd.datain)['log_parameters']
    cmd = device.logsense(0, sub_page_code=0xFF)
    support_log_page_subpage = decode_logpageformat_supportsublogpage(cmd.datain)['log_parameters']
    def check_log_page_support(member):
        if member.page in support_log_page:
            if member.subpage == 0:
                return True
            elif (member.page, member.subpage) in support_log_page_subpage:
                return True
        return False
    # Get temperature
    member = SimulateSmartMember(0x0D, 0x00)
    if check_log_page_support(member):
        temperature,reference_temperature = member.get_value(device,
                                                            (0, 1, 1),  # temperature
                                                            (1, 1, 1))   # reference temperature
        if temperature is not None:
            temp = smart_table_attr(AttributeName="Temperature", LogPage=(member.page, member.subpage), Value=temperature, Threshold=reference_temperature)
            smart_table[temp.AttributeName] = temp
    # Get Power cycle Count
    member = SimulateSmartMember(0x0E, 0x00)
    if check_log_page_support(member):
        start_stop_cyle_thred,start_stop_cyle,load_unload_cycle_thred,load_unload_cycle = member.get_value(device,
                                                                                                        (3, 0, 4),
                                                                                                        (4, 0, 4),
                                                                                                        (5, 0, 4),
                                                                                                        (6, 0, 4))
        if start_stop_cyle is not None:
            temp = smart_table_attr(AttributeName="Power Cycle Count", LogPage=(member.page, member.subpage), Value=start_stop_cyle, Threshold=start_stop_cyle_thred)
            smart_table[temp.AttributeName] = temp
        if load_unload_cycle is not None:
            temp = smart_table_attr(AttributeName="Load Cycle Count", LogPage=(member.page, member.subpage), Value=load_unload_cycle, Threshold=load_unload_cycle_thred)
            smart_table[temp.AttributeName] = temp
    # Get Power On Time
    member = SimulateSmartMember(0x15, 0x00)
    if check_log_page_support(member):
        POH = member.get_value(device,
                            (0, 0, 4))[0]
        if POH is not None:
            temp = smart_table_attr(AttributeName="Power On Minutes", LogPage=(member.page, member.subpage), Value=POH, Threshold=None)
            smart_table[temp.AttributeName] = temp
    # Get Percentage Used
    member = SimulateSmartMember(0x11, 0x00)
    if check_log_page_support(member):
        used = member.get_value(device,
                                (1, 3, 1))[0]
        if used is not None:
            temp = smart_table_attr(AttributeName="Percentage Used", LogPage=(member.page, member.subpage), Value=used, Threshold=100)
            smart_table[temp.AttributeName] = temp
    # Get Logical Block Provisioning
    member = SimulateSmartMember(0x0C, 0x00)
    if check_log_page_support(member):
        available_spare = member.get_value(device,
                                        (3, 0, 2))[0]
        if available_spare is not None:
            temp = smart_table_attr(AttributeName="Available Spare", LogPage=(member.page, member.subpage), Value=available_spare, Threshold=100)
            smart_table[temp.AttributeName] = temp
    # Get Workload Utilization
    member = SimulateSmartMember(0x0E, 0x01)
    if check_log_page_support(member):
        workload_utilization = member.get_value(device,
                                                (0, 0, 2))[0]
        if workload_utilization is not None:
            temp = smart_table_attr(AttributeName="Workload Utilization", LogPage=(member.page, member.subpage), Value=workload_utilization, Threshold=None)
            smart_table[temp.AttributeName] = temp
    # init total_corrected_errors,total_uncorrected_errors
    total_corrected_errors = None
    total_uncorrected_errors = None
    # Get Total Write Data processed
    member = SimulateSmartMember(0x02, 0x00)
    if check_log_page_support(member):
        total_corrected_errors,total_write,total_uncorrected_errors = member.get_value(device,
                                                                                    (3, 0, None), # total_corrected_errors
                                                                                    (5, 0, None), # total_write
                                                                                    (6, 0 ,None))
        if total_write is not None:
            temp = smart_table_attr(AttributeName="Total Write", LogPage=(member.page, member.subpage), Value=total_write, Threshold=None)
            smart_table[temp.AttributeName] = temp
    # Get Total Read
    member = SimulateSmartMember(0x03, 0x00)
    if check_log_page_support(member):
        v_0,total_read,v_1 = member.get_value(device,
                                            (3, 0, None),   # total_corrected_errors
                                            (5, 0 , None),  # total_read
                                            (6, 0 , None))  # total_uncorrected_errors
        if total_corrected_errors is None:
            total_corrected_errors = v_0
        elif v_0 is not None:
            total_corrected_errors += v_0
        if total_uncorrected_errors is None:
            total_uncorrected_errors = v_1
        elif v_1 is not None:
            total_uncorrected_errors += v_1
        if total_read is not None:
            temp = smart_table_attr(AttributeName="Total Read", LogPage=(member.page, member.subpage), Value=total_read, Threshold=None)
            smart_table[temp.AttributeName] = temp
    # Get verify information
    member = SimulateSmartMember(0x05, 0x00)
    if check_log_page_support(member):
        v_0,v_1 = member.get_value(device,
                                (3, 0, None),   # total_corrected_errors
                                (6, 0 , None))  # total_uncorrected_errors
        if total_corrected_errors is None:
            total_corrected_errors = v_0
        elif v_0 is not None:
            total_corrected_errors += v_0
        if total_uncorrected_errors is None:
            total_uncorrected_errors = v_1
        elif v_1 is not None:
            total_uncorrected_errors += v_1
    # get total corrected errors
    if total_corrected_errors is not None:
        temp = smart_table_attr(AttributeName="Corrected Errors", LogPage=(), Value=total_corrected_errors, Threshold=None)
        smart_table[temp.AttributeName] = temp
    # get total uncorrected errors
    if total_uncorrected_errors is not None:
        temp = smart_table_attr(AttributeName="Reported Uncorrect", LogPage=(), Value=total_uncorrected_errors, Threshold=None)
        smart_table[temp.AttributeName] = temp
    # Get Non media error count
    member = SimulateSmartMember(0x06, 0x00)
    if check_log_page_support(member):
        error_count = member.get_value(device,
                                    (0, 0, None))[0]
        if error_count is not None:
            temp = smart_table_attr(AttributeName="Non-Media Error", LogPage=(member.page, member.subpage), Value=error_count, Threshold=None)
            smart_table[temp.AttributeName] = temp
    # Get Pending Defect Count
    member = SimulateSmartMember(0x15, 0x01)
    if check_log_page_support(member):
        pending_defect_count = member.get_value(device,
                                                (0, 0, None))[0]
        if pending_defect_count is not None:
            temp = smart_table_attr(AttributeName="Pending Defect Count", LogPage=(member.page, member.subpage), Value=pending_defect_count, Threshold=None)
            smart_table[temp.AttributeName] = temp
    return smart_table
