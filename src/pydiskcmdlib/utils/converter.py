# coding: utf-8

# Copyright (C) 2014 by Ronnie Sahlberg<ronniesahlberg@gmail.com>
# Copyright (C) 2015 by Markus Rosjat<markus.rosjat@gmail.com>
# SPDX-FileCopyrightText: 2014 The python-scsi Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import binascii
from typing import Mapping, Sequence, Tuple, Union

CheckDict = Mapping[
    str, Union[
        Sequence[int],
        Tuple[int, int],
        Tuple[str, int, int]
    ]]

def scsi_int_to_ba(to_convert=0,
                   array_size=4,
                   byteorder="big"):
    """
    This function converts a  integer of (8 *array_size)-bit to a bytearray(array_size) in
    BigEndian Or LittleEndian byte order. Here we use the 32-bit as default.

    example:

        >>scsi_to_ba(34,4)
        bytearray(b'\x00\x00\x00"')

        so we take a 32-bit integer and get a byte array(4)

    :param to_convert: a integer
    :param array_size: a integer defining the size of the byte array
    :param byteorder: a string defining BigEndian Or LittleEndian byte order
    :return: a byte array
    """
    if byteorder == 'big':
        return bytearray((to_convert >> i * 8) & 0xff for i in reversed(range(array_size)))
    else:
        return bytearray((to_convert >> i * 8) & 0xff for i in range(array_size))


def scsi_ba_to_int(ba, byteorder='big'):
    """
    This function converts a bytearray  in BigEndian Or LittleEndian byte order
    to an integer.

    :param ba: a bytearray
    :param byteorder: 'big'|'little'
    :return: an integer
    """
    if byteorder == 'big':
        return sum(ba[i] << ((len(ba) - 1 - i) * 8) for i in range(len(ba)))
    else:
        return sum(ba[i] << (i * 8) for i in range(len(ba)))

def ba_to_ascii_string(ba, dummy_char="."):
    ascii_string = ""
    for v in ba:
        if (31 < v < 127):
            ascii_string += chr(v)
        else:
            ascii_string += dummy_char
    return ascii_string

def decode_bits(data,
                check_dict,
                result_dict,
                byteorder='big'):
    """
    helper method to perform some simple bit operations

    the list in the value of each key:value pair contains 2 values
    - the bit mask
    - the offset byte in the datain byte array

    for now we assume he have to right shift only

    :param data: a buffer containing the bits to decode
    :param check_dict: a dict mapping field-names to notation tuples.
    :param result_dict: a dict mapping field-names to notation tuples.
    """
    for key in check_dict.keys():
        # Notation format:
        #
        # If the length is 2 we have the legacy notation [bitmask, offset]
        # Example: 'sync': [0x10, 7],
        #
        # >2-tuples is the new style of notation.
        # These tuples always consist of at least three elements, where the
        # first element is a string that describes the type of value.
        #
        # 'b': Byte array blobs
        # ----------------
        # ('b', offset, length)
        # Example: 't10_vendor_identification': ('b', 8, 8),
        #

        val = check_dict[key]
        if len(val) == 2:
            bitmask, byte_pos = val
            _num = 1
            _bm = bitmask
            while _bm > 0xff:
                _bm >>= 8
                _num += 1
            value = scsi_ba_to_int(data[byte_pos:byte_pos + _num],byteorder=byteorder)
            while not bitmask & 0x01:
                bitmask >>= 1
                value >>= 1
            value &= bitmask
        elif val[0] == 'b':
            offset, length = val[1:3]
            value = data[offset:offset + length]
        elif val[0] == 'bb':
            bit_offset, bit_length = val[1:3]
            if isinstance(data, bytes):
                _tmp = scsi_ba_to_int(data, 'little')
            value = (_tmp >> bit_offset) & (2**bit_length-1)
        elif val[0] == 'w':
            offset, length = val[1:3]
            value = data[offset:offset + length * 2]
        elif val[0] == 'dw':
            offset, length = val[1:3]
            value = data[offset:offset + length * 4]
        ##
        if len(val) > 3:
            if val[3] == 'int_l':
                value = scsi_ba_to_int(value, 'little')
            elif val[3] == 'int_b':
                value = scsi_ba_to_int(value, 'big')
            elif val[3] == 'str_ascii':
                value = ba_to_ascii_string(value)
        result_dict.update({key: value})


def encode_dict(data_dict,
                check_dict,
                result,
                byteorder='big'):
    """
    helper method to perform some simple bit operations

    the list in the value of each key:value pair contains 2 values
    - the bit mask
    - the offset byte in the datain byte array

    for now we assume he have to right shift only

    :param data_dict:  a dict mapping field-names to notation tuples.
    :param check_dict: a dict mapping field-names to notation tuples.
    :param result: a buffer containing the bits encoded
    """
    for key in data_dict.keys():
        if key not in check_dict:
            continue
        value = data_dict[key]

        val = check_dict[key]
        if len(val) == 2:
            bitmask, bytepos = val

            _num = 1
            _bm = bitmask
            while _bm > 0xff:
                _bm >>= 8
                _num += 1

            _bm = bitmask
            while not _bm & 0x01:
                _bm >>= 1
                value <<= 1

            v = scsi_int_to_ba(value, _num, byteorder=byteorder)
            for i in range(len(v)):
                result[bytepos + i] ^= v[i]
        elif val[0] == 'b' and val[2] > 0:
            offset, length = val[1:]
            fixed_length = min(length, len(value))
            if isinstance(value, str):
                value = value.encode()
            result[offset:offset + fixed_length] = value[0:fixed_length]
        elif val[0] == 'w' and val[2] > 0:
            offset, length = val[1:]
            result[offset:offset + length * 2] = value
        elif val[0] == 'dw' and val[2] > 0:
            offset, length = val[1:]
            result[offset:offset + length * 4] = value


def get_check_dict_maxsize(check_dict) -> int:
    """
    helper method to get check_dict max size in byte

    :param check_dict: a dict mapping field-names to notation tuples.
    """
    max_size = 0
    if check_dict:
        # check the max 
        for val in check_dict.values():
            if len(val) == 2:
                length = 0
                while (val[0] >> 8 * length) > 0:
                    length += 1
                max_size = max(max_size, val[1] + length)
            elif val[0] == 'b':
                max_size = max(max_size, val[1] + val[2])
            elif val[0] == 'w':
                max_size = max(max_size, val[1] + val[2] * 2)
            elif val[0] == 'dw':
                max_size = max(max_size, val[1] + val[2] * 4)
    return max_size


def print_data(data_dict):
    """
    A small method to print out data we generate in this package.

    It's not really a converter but in a way we convert a dict of
    key - value pairs into strings ...

    :param data_dict: a dictionary
    :return: a few strings
    """
    for k, v in data_dict.items():
        if isinstance(v, dict):
            print(k)
            print_data(v)
        else:
            if isinstance(v, str):
                print('%s -> %s' % (k, v))
            elif isinstance(v, float):
                print('%s -> %.02d' % (k, v))
            else:
                print('%s -> 0x%02X' % (k, v))


def get_opcode(enum,
               part):
    """
    A generator that returns an OpCode object from a given
    Enum object.

    :param enum: the Enum of opcodes
    :param part: a string to lookup in the enum keys
    :return: an OpCode object
    """
    for val in enum._enums:
        if val[len(val)-2:] == part:
                yield getattr(enum, val)

#####################################
# Add by gaozh, gaozh3@lenovo.com   #
# Date: 2021/11/02                  #
#####################################
def translocate_bytearray(ba, type=1):
    if type == 1:
        ba_index = [i for i in range(len(ba)) if (i % 2) == 0]
        for index in ba_index:
            ba[index],ba[index+1] = ba[index+1],ba[index]
    elif type == 2:
        ba = ba[::-1]
    return ba

def bytearray2string(ba):
    return ba.decode()

def bytearray2int(ba):
    return int(binascii.hexlify(ba), 16)

