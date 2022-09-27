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


nvme_id_ctrl_bit_mask = {}


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
                    if (31 < data[offset+i] < 127):
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
