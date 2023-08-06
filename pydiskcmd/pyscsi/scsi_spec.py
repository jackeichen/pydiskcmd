# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmd.utils.converter import decode_bits,scsi_ba_to_int


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
                (0x0D,0x00): LogPageAttr(0x0D, 0x00, 'Utilization'),
                "Unkonwn": LogPageAttr(None, None, 'Unkonwn Log Page'),
            }
