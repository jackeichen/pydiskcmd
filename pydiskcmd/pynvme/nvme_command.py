# SPDX-FileCopyrightText: 2014 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later

class BuildNVMeCommandError(Exception):
    pass


def build_command(bitmap):
    '''
    bitmap: {name_0: bitmap_struc_0,
             name_1: bitmap_struc_1, 
             ..., 
             name_n: bitmap_struc_n} 
        name:         is not a valid parameters, just a identifier
        bitmap_struc: [bit_mask, byte_offset, value], example: [0xFFF, 0, 10]
    
    return: int
    '''
    target_value = 0
    for name,struc in bitmap.items():
        bit_mask,byte_offset,value = struc
        ## first check value
        if value > bit_mask:
            raise BuildNVMeCommandError("Value to big to set: %s" % str(struc))
        ## find bit offset
        suboffset = 0
        while True:
            if ((bit_mask >> suboffset) & 0x01):
                break
            suboffset += 1
        ##
        target_value += (value << (byte_offset*8+suboffset))
    return target_value
