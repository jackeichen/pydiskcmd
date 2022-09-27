# coding: utf-8

# Copyright:
#  Copyright (C) 2014 by Ronnie Sahlberg<ronniesahlberg@gmail.com>
#  Copyright (C) 2015 by Markus Rosjat<markus.rosjat@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 2.1 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
from __future__ import print_function
from pydiskcmd.utils.converter import decode_bits

int_to_hex_map = {0: '0', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7',
                  8: '8', 9: '9', 10: 'a', 11: 'b', 12: 'c', 13: 'd', 14: 'e', 15: 'f'}

nvme_smart_bit_mask = {"Critical Warning": ('b', 0, 1),
                       "Composite Temperature": ('b', 1, 2),
                       "Available Spare": ('b', 3, 1),
                       "Available Spare Threshold": ('b', 4, 1),
                       "Percentage Used": ('b', 5, 1),
                       "Endurance Group Critical Warning Summary": ('b', 6, 1),
                       "Data Units Read": ('b', 32, 16),
                       "Data Units Written": ('b', 48, 16),
                       "Host Read Commands": ('b', 64, 16),
                       "Host Write Commands": ('b', 80, 16),
                       "Controller Busy Time": ('b', 96, 16),
                       "Power Cycles": ('b', 112, 16),
                       "Power On Hours": ('b', 128, 16),
                       "Unsafe Shutdowns": ('b', 144, 16),
                       "Media and Data Integrity Errors": ('b', 160, 16),
                       "Number of Error Information Log Entries": ('b', 176, 16),
                       "Warning Composite Temperature Time": ('b', 192, 4),
                       "Critical Composite Temperature Time": ('b', 196, 4),
                       }


nvme_id_ctrl_bit_mask = {"VID": ('b', 0, 2),
                         "SSVID": ('b', 2, 2),
                         "SN": ('b', 4, 20),
                         "MN": ('b', 24, 40),
                         "FR": ('b', 64, 8),
                         "RAB": ('b', 72, 1),
                         "IEEE": ('b', 73, 3),
                         "CMIC": ('b', 76, 1),
                         "MDTS": ('b', 77, 1),
                         "CNTLID": ('b', 78, 2),
                         "VER": ('b', 80, 4),
                         "RTD3R": ('b', 84, 4),
                         "RTD3E": ('b', 88, 4),
                         "OAES": ('b', 92, 4),
                         "CTRATT": ('b', 96, 4),
                         "RRLS": ('b', 100, 2),
                         "CNTRLTYPE": ('b', 111, 1),
                         "FGUID": ('b', 112, 16),
                         "CRDT1": ('b', 128, 2),
                         "CRDT2": ('b', 130, 2),
                         "CRDT3": ('b', 132, 2),
                         "OACS": ('b', 256, 2),           ## Optional Admin Command Support
                         "ACL": ('b', 258, 1),            ## Abort Command Limit
                         "AERL": ('b', 259, 1),           ## Asynchronous Event Request Limit
                         "FRMW": ('b', 260, 1),           ## Firmware Updates
                         "LPA": ('b', 261, 1),            ## Log Page Attributes
                         "ELPE": ('b', 262, 1),           ## Error Log Page Entries
                         "NPSS": ('b', 263, 1),           ## Number of Power States Support
                         "AVSCC": ('b', 264, 1),          ## Admin Vendor Specific Command Configuration
                         "APSTA": ('b', 265, 1),          ## Autonomous Power State Transition Attributes
                         "WCTEMP": ('b', 266, 2),         ## Warning Composite Temperature Threshold
                         "CCTEMP": ('b', 268, 2),         ## Critical Composite Temperature Threshold
                         "MTFA": ('b', 270, 2),           ## Maximum Time for Firmware Activation
                         "HMPRE": ('b', 272, 4),          ## Host Memory Buffer Preferred Size
                         "HMMIN": ('b', 276, 4),          ## Host Memory Buffer Minimum Size
                         "TNVMCAP": ('b', 280, 16),       ## Total NVM Capacity
                         "UNVMCAP": ('b', 296, 16),       ## Unallocated NVM Capacity
                         "RPMBS": ('b', 312, 4),          ## Replay Protected Memory Block Support
                         "EDSTT": ('b', 316, 2),          ## Extended Device Self-test Time
                         "DSTO": ('b', 318, 1),           ## Device Self-test Options
                         "FWUG": ('b', 319, 1),           ## Firmware Update Granularity
                         "KAS": ('b', 320, 2),            ## Keep Alive Support
                         "HCTMA": ('b', 322, 2),          ## Host Controlled Thermal Management Attributes
                         "MNTMT": ('b', 324, 2),          ## Minimum Thermal Management Temperature
                         "MXTMT": ('b', 326, 2),          ## Maximum Thermal Management Temperature
                         "SANICAP": ('b', 328, 4),        ## Sanitize Capabilities
                         "HMMINDS": ('b', 332, 4),        ## Host Memory Buffer Minimum Descriptor Entry Size
                         "HMMAXD": ('b', 336, 2),         ## Host Memory Maximum Descriptors Entries
                         "NSETIDMAX": ('b', 338, 2),      ## NVM Set Identifier Maximum
                         "ENDGIDMAX": ('b', 340, 2),      ## Endurance Group Identifier Maximum
                         "ANATT": ('b', 342, 1),          ## ANA Transition Time
                         "ANACAP": ('b', 343, 1),         ## Asymmetric Namespace Access Capabilities
                         "ANAGRPMAX": ('b', 344, 4),      ## ANA Group Identifier Maximum
                         "NANAGRPID": ('b', 348, 4),      ## Number of ANA Group Identifiers
                         "PELS": ('b', 352, 4),           ## Persistent Event Log Size
                         "SQES": ('b', 512, 1),           ## Submission Queue Entry Size
                         "CQES": ('b', 513, 1),           ## Completion Queue Entry Size
                         "MAXCMD": ('b', 514, 2),         ## Maximum Outstanding Commands
                         "NN": ('b', 516, 4),             ## Number of Namespaces
                         "ONCS": ('b', 520, 2),           ## Optional NVM Command Support
                         "FUSES": ('b', 522, 2),          ## Fused Operation Support
                         "FNA": ('b', 524, 1),            ## Format NVM Attributes
                         "VWC": ('b', 525, 1),            ## Volatile Write Cache
                         "AWUN": ('b', 526, 2),           ## Atomic Write Unit Normal
                         "AWUPF": ('b', 528, 2),          ## Atomic Write Unit Power Fail
                         "NVSCC": ('b', 530, 1),          ## NVM Vendor Specific Command Configuration
                         "NWPC": ('b', 531, 1),           ## Namespace Write Protection Capabilities
                         "ACWU": ('b', 532, 2),           ## Atomic Compare & Write Unit
                         "SGLS": ('b', 536, 4),           ## SGL Support
                         "MNAN": ('b', 540, 4),           ## Maximum Number of Allowed Namespaces
                         "SUBNQN": ('b', 768, 256),       ## NVM Subsystem NVMe Qualified Name
                       }

nvme_id_ctrl_ps_bit_mask = {"MP": ('b', 0, 2),            ## Maximum Power
                            "MXPS": [0x01, 3],            ## Max Power Scale
                            "NOPS": [0x02, 3],            ## Non-Operational State
                            "ENLAT": ('b', 4, 4),         ## Entry Latency
                            "EXLAT": ('b', 8, 4),         ## Exit Latency
                            "RRT": [0x1F, 12],            ## Relative Read Throughput
                            "RRL": [0x1F, 13],            ## Relative Read Latency
                            "RWT": [0x1F, 14],            ## Relative Write Throughput
                            "RWL": [0x1F, 15],            ## Relative Write Latency
                            "IDLP": ('b', 16, 2),         ## Idle Power
                            "IPS": [0xC0, 18],            ## Idle Power Scale
                            "ACTP": ('b', 20, 2),         ## Active Power
                            "APW": [0x07, 22],            ## Active Power Workload
                            "APS": [0xC0, 22],            ## Active Power Scale
                           }



def format_dump_bytes(data, offset=0, end=None, ascii_str=True):
    def my_func(d0, d1):
        t = ''
        if isinstance(d1, int):
            t += int_to_hex_map[(d1 >> 4) & 0x0F]
            t += int_to_hex_map[d1 & 0x0F]
        else:
            t += d1
        if isinstance(d0, int):
            t += int_to_hex_map[(d0 >> 4) & 0x0F]
            t += int_to_hex_map[d0 & 0x0F]
        else:
            t += d0
        return t
    def get_data(data, index):
        if index < len(data):
            return data[index]
        else:
            return "**"

    if end is None:
        end = len(data) - 1
    format_str = "%-10s" + "%-6s" * 8 + "     %s"
    ##
    show_ascii_string = ""
    if ascii_str:
        show_ascii_string = "ASCII String"
    #
    print (format_str % ("offset", "0x00", "0x02", "0x04", "0x06", "0x08", "0x0A", "0x0C", "0x0E", show_ascii_string))
    print ('')
    while True:
        if offset < end:
            index = ''
            index_offset = 0
            for i in range(6):
                index = int_to_hex_map[((offset >> index_offset) & 0x0F)] + index
                index_offset += 4
            temp_ascii_string = ""
            if ascii_str:
                for i in range(16):
                    if (offset+i) < len(data) and (31 < data[offset+i] < 127):
                        temp_ascii_string += chr(data[offset+i])
                    else:
                        temp_ascii_string +="." 
            print (format_str % (index, 
                                 my_func(get_data(data, offset), get_data(data, offset+1)), 
                                 my_func(get_data(data, offset+2), get_data(data, offset+3)), 
                                 my_func(get_data(data, offset+4), get_data(data, offset+5)), 
                                 my_func(get_data(data, offset+6), get_data(data, offset+7)), 
                                 my_func(get_data(data, offset+8), get_data(data, offset+9)), 
                                 my_func(get_data(data, offset+10), get_data(data, offset+11)), 
                                 my_func(get_data(data, offset+12), get_data(data, offset+13)), 
                                 my_func(get_data(data, offset+14), get_data(data, offset+15)),
                                 temp_ascii_string))
            offset += 16
        else:
            break

def nvme_smart_decode(data):
    result = {}
    decode_bits(data, nvme_smart_bit_mask, result)
    return result

def nvme_id_ctrl_decode(data):
    result = {}
    decode_bits(data, nvme_id_ctrl_bit_mask, result)
    ## power state
    for i in range(32):
        key = "PSD%s" % i
        _offset = 2048 + 32*i
        _data = data[_offset:(_offset+32)]
        power_state = {}
        decode_bits(_data, nvme_id_ctrl_ps_bit_mask, power_state)
        if power_state.get("MP") != b'\x00\x00':
            result[key] = power_state
    return result

