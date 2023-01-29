# coding: utf-8

# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later

from __future__ import print_function


int_to_hex_map = {0: '0', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7',
                  8: '8', 9: '9', 10: 'a', 11: 'b', 12: 'c', 13: 'd', 14: 'e', 15: 'f'}


def format_dump_bytes(data, offset=0, end=None, byteorder='reversed', ascii_str=True, ascii_str_mask='.'):
    def my_func(d0, d1):
        t = ''
        if byteorder == 'reversed':
            data = (d1, d0)
        elif byteorder == 'obverse':
            data = (d0, d1)
        else:
            raise RuntimeError("byteorder should be one of reversed|obverse")
        for d in data:
            if isinstance(d, int):
                t += int_to_hex_map[(d >> 4) & 0x0F]
                t += int_to_hex_map[d & 0x0F]
            else:
                t += d
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
    print ('Start: %s' % offset)
    print ('End: %s' % end)
    print ('Byte Order: %s' % byteorder)
    print ('')
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
                for i in range(0, 16, 2):
                    if byteorder == 'reversed':
                        _offset = (i+1, i)
                    else:
                        _offset = (i, i+1)
                    for k in _offset:
                        if (offset+k) < len(data) and (31 < data[offset+k] < 127):
                            temp_ascii_string += chr(data[offset+k])
                        else:
                            temp_ascii_string += ascii_str_mask
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

def human_read_capacity(size_b, kb_base=1000):
    """
    size_b: the total size in byte
    kb_base: 1000 or 1024
    
    return
      string: "size"+ " unit", example-> "3.84 TB"
    """
    unit = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    for u in unit:
        size_b = size_b / kb_base
        if int(size_b) < 1:
            break
    size_b = "%.2f" % (size_b*kb_base)
    return "%s %s" % (size_b, u)
