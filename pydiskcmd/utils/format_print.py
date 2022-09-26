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

int_to_hex_map = {0: '0', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7',
                  8: '8', 9: '9', 10: 'a', 11: 'b', 12: 'c', 13: 'd', 14: 'e', 15: 'f'}


def format_dump_bytes(data, offset=0, end=None):
    def my_func(d0, d1):
        t = ''
        t += int_to_hex_map[(d1 >> 4) & 0x0F]
        t += int_to_hex_map[d1 & 0x0F]
        t += int_to_hex_map[(d0 >> 4) & 0x0F]
        t += int_to_hex_map[d0 & 0x0F]
        return t
    if end is None:
        end = len(data) - 1
    format_str = "%-10s" + "%-6s" * 8
    ##
    print (format_str % ("offset", "0x00", "0x02", "0x04", "0x06", "0x08", "0x0A", "0x0C", "0x0E"))
    print ('')
    while True:
        if offset < end:
            index = ''
            index_offset = 0
            for i in range(6):
                index = int_to_hex_map[((offset >> index_offset) & 0x0F)] + index
                index_offset += 4
            print (format_str % (index, 
                                 my_func(data[offset], data[offset+1]), 
                                 my_func(data[offset+2], data[offset+3]), 
                                 my_func(data[offset+4], data[offset+5]), 
                                 my_func(data[offset+6], data[offset+7]), 
                                 my_func(data[offset+8], data[offset+9]), 
                                 my_func(data[offset+10], data[offset+11]), 
                                 my_func(data[offset+12], data[offset+13]), 
                                 my_func(data[offset+14], data[offset+15])))
            offset += 16
        else:
            break
