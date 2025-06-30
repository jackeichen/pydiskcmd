# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import sys
from typing import Optional
from abc import ABCMeta, abstractmethod
from pydiskcmdlib import os_type
from pydiskcmdlib.data_buffer import DataBuffer
from pydiskcmdlib.utils.converter import encode_dict,decode_bits,CheckDict,scsi_int_to_ba,scsi_ba_to_int,ba_to_ascii_string
from pydiskcmdlib.device.win_device import BytesReturnedStruc
from pydiskcmdlib.exceptions import *
from pydiskcmdlib.os.win_ioctl_structures import (
    Structure,
    sizeof,
)


class BitStrucInfo():
    def __init__(self):
        self.name = None
        self.c_type = None
        self.bit_length = 0
        self.bit_offset = 0

class StructureContext():
    def __init__(self):
        self.bit_struc_info = BitStrucInfo()
        self.byte_offset = 0

    def get_bit_map(self, obj: tuple) -> list:
        if len(obj) == 2:
            #
            field_name,filed_type = obj
            #
            if self.bit_struc_info.name is not None:
                self.byte_offset += sizeof(self.bit_struc_info.c_type)
                # then clear it
                self.bit_struc_info.name = None
                self.bit_struc_info.c_type = None
                self.bit_struc_info.bit_length = 0
                self.bit_struc_info.bit_offset = 0
            #
            if str(type(filed_type)) != "<class '_ctypes.PyCArrayType'>":
                result = [2**(sizeof(filed_type) * 8)-1, self.byte_offset]
                # then add the bytes_offset
                self.byte_offset += sizeof(filed_type)
            else:
                result = ['b', self.byte_offset, sizeof(filed_type)]
                #
                self.byte_offset += sizeof(filed_type)
        elif len(obj) == 3:
            field_name,filed_type,filed_length = obj
            # 
            # if field_name == self.bit_struc_info.name:
            #     # it is the same bit_struc_info
            #     result = [(2**filed_length-1) << self.bit_struc_info.bit_offset, self.byte_offset]
            #     #
            #     self.bit_struc_info.bit_offset += filed_length
            # else:
            if self.bit_struc_info.name is None:
                self.bit_struc_info.name = field_name
                self.bit_struc_info.c_type = filed_type
                self.bit_struc_info.bit_length = sizeof(filed_type) * 8
                self.bit_struc_info.bit_offset = 0
                #
                result = [2**filed_length-1, self.byte_offset]
                #
                self.bit_struc_info.bit_offset += filed_length
            else:
                # 1. they all in one c_type
                if filed_type == self.bit_struc_info.c_type and (filed_length + self.bit_struc_info.bit_offset) <= self.bit_struc_info.bit_length:
                    # 1. they all in one c_type
                    result = [(2**filed_length-1) << self.bit_struc_info.bit_offset, self.byte_offset]
                    self.bit_struc_info.name = field_name
                    self.bit_struc_info.bit_offset += filed_length
                else:
                    # 2. they are in different c_type
                    # add byte_offset
                    self.byte_offset += sizeof(self.bit_struc_info.c_type)
                    #
                    result = [2**filed_length-1, self.byte_offset]
                    # init
                    self.bit_struc_info.name = field_name
                    self.bit_struc_info.c_type = filed_type
                    self.bit_struc_info.bit_length = sizeof(filed_type) * 8
                    self.bit_struc_info.bit_offset = filed_length
        else:
            raise Exception("_field_ %s has wrong format" % str(obj))
        return field_name,result


def generate_cdb_bits_by_structure(structure: Structure, context=None):
    if context is None:
        context=StructureContext()
    cdb_bits = {}
    for i in structure._fields_:
        field_name = i[0]
        filed_type = i[1]
        if hasattr(filed_type, '_fields_'):
            _cdb_bits = generate_cdb_bits_by_structure(filed_type, context=context)
            cdb_bits.update(_cdb_bits)
        else:
            field_name,result = context.get_bit_map(i)
            cdb_bits[field_name] = result
    return cdb_bits


class CommandWrapper(object):
    '''
    This Class define the function that must be implemented by CommandWapper function.
    '''
    _cdb_bits: CheckDict = {}
    _cdb_bitmap_pool: dict = {}
    _req_id: int = 0

    def __init__(self, 
                 cdb_raw_struc: Structure,
                 bytes_aligned: int = 1):
        """
        """
        self._cdb_raw_struc = cdb_raw_struc
        self.__bytes_aligned = bytes_aligned
        ## init bitmap
        self.init_cdb_bitmap()
        ## the _cdb may include command and data_buffer
        self._cdb = None  #  default value: None, command data used by ioctl
        self._cdb_bytearray = None #  default value: None, command data that
        #
        self._data_buffer = None
        self._metadata_buffer = None
        ## used by build command
        self._byteorder = sys.byteorder
        ## some variables used by OS
        self._ioctl_result = None
        # Linux
        # Windows IOCTL parameters
        self._bytes_returned = BytesReturnedStruc(0) if os_type == "Windows" else None
        self._over_lapped = None  # Not used now

    @property
    def ioctl_result(self):
        """
        Get the result of the IOCTL operation.

        This method returns the value of the `_ioctl_result` attribute, which represents the result of the IOCTL operation.

        :return: The result of the IOCTL operation.
        """
        return self._ioctl_result

    @ioctl_result.setter
    def ioctl_result(self, value: int):
        """
        Set the result of the IOCTL operation.

        This method sets the value of the `_ioctl_result` attribute, which represents the result of the IOCTL operation.

        :param value: The value to be set as the result of the IOCTL operation.
        """
        self._ioctl_result = value

    @property
    def bytes_returned(self):
        """
        Return the IOCTL bytes returned.

        This method returns the value of the `_bytes_returned` attribute, which represents IOCTL bytes returned

        :return: IOCTL bytes returned.
        """
        return self._bytes_returned

    @property
    def over_lapped(self):
        """
        Return the IOCTL over lapped.

        This method returns the value of the `_over_lapped` attribute, which represents IOCTL over lapped.

        :return: IOCTL over lapped.
        """
        return self._over_lapped

    def init_cdb_bitmap(self):
        """
        Initialize the CDB (Command Descriptor Block) bitmap.

        This method initializes the CDB bitmap, which is a dictionary used to store the
        bit positions and their corresponding values in the CDB. The method first checks
        if the `_cdb_bits` attribute is present, and if so, it assigns it to the `_cdb_bitmap`.
        If `_cdb_bits` is not present, it checks if the `_cdb_raw_struc` attribute is present,
        and if so, it generates the CDB bitmap using the `generate_cdb_bits_by_structure`
        function. If neither `_cdb_bits` nor `_cdb_raw_struc` is present, it checks if the
        `_cdb_bitmap_pool` attribute is present, and if so, it retrieves the CDB bitmap
        from the pool using the `req_id` as the key.
        """
        self._cdb_bitmap = {}
        if self._cdb_bits:
            self._cdb_bitmap = self._cdb_bits
        elif self._cdb_raw_struc:
            self._cdb_bitmap = generate_cdb_bits_by_structure(self._cdb_raw_struc)
        elif self._cdb_bitmap_pool:
            self._cdb_bitmap = self._cdb_bitmap_pool.get(self.req_id)

    def print_cdb(self):
        """
        simple helper to print out the cdb as hex values
        """
        if self.cdb_struc:
            for b in self.cdb_struc:
                print("0x%02X " % b)

    @property
    def cdb(self):
        """
        getter method of the cdb property

        :return: a byte array
        """
        return self._cdb

    @property
    def cdb_struc(self):
        if self.cdb:
            return bytes(self._cdb_bytearray)

    @property
    def cdb_raw_struc(self):
        return self._cdb_raw_struc

    @property
    def cdb_raw_struc_len(self) -> int:
        return sizeof(self.cdb_raw_struc)

    @property
    def req_id(self) -> int:
        """
        getter method of the req_id property

        :return: a int
        """
        return self._req_id

    def marshall_cdb(self, cdb, cdb_len: int) -> bytearray:
        """
        Marshall a Command cdb

        :param cdb: a dict with key:value pairs representing a code descriptor block
        :param cdb_len: the total length of build command
        :return result: a byte array representing a code descriptor block
        """
        result = bytearray(cdb_len) # The command initial value is all 0
        encode_dict(cdb, self._cdb_bitmap, result, byteorder=self._byteorder)
        return result

    def unmarshall_cdb(self):
        """
        Unmarshall an SCSICommand cdb

        :param cdb: a byte array representing a code descriptor block
        :return result: a dict
        """
        result = {}
        decode_bits(self.cdb_struc, self._cdb_bitmap, result, byteorder=self._byteorder)
        return result

    @property
    def data_buffer(self):
        return self._data_buffer

    @property
    def metadata_buffer(self):
        return self._metadata_buffer

    @staticmethod
    def _init_data_buffer(data_length=0, data_out=None):
        """
        Initialize a data buffer with the specified length and optional data.

        This method creates a new `DataBuffer` object with the given `data_length`. If `data_out` is provided,
        it will be copied into the data buffer. If `data_length` is not specified or is 0, the length of `data_out`
        will be used.

        :param data_length: The length of the data buffer to be initialized. If not provided, defaults to 0.
        :param data_out: Optional data to be pre-populated into the data buffer. If not provided, defaults to None.
        :return: The initialized data buffer or None.
        """
        data_buffer = None
        if data_out:
            _data_len = data_length if data_length > 0 else len(data_out)
            data_buffer = DataBuffer(_data_len)
            data_buffer.data_buffer = data_out
        else:
            data_buffer = DataBuffer(data_length)
        return data_buffer

    def init_data_buffer(self, data_length=0, data_out=None, data_buffer=None):
        """
        Initialize or assign a data buffer.

        This method can be used to initialize a data buffer with a specified length and optional data output,
        or it can be used to assign an existing data buffer to the current object.

        :param data_length: The length of the data buffer to be initialized. If not provided, defaults to 0.
        :param data_out: Optional data to be pre-populated into the data buffer. If not provided, defaults to None.
        :param data_buffer: An existing data buffer to be assigned to the current object. If provided, it will
                            override the `data_length` and `data_out` parameters.
        :return: The initialized or assigned data buffer.
        """
        if isinstance(data_buffer, DataBuffer):
            self._data_buffer = data_buffer
        else:
            self._data_buffer = self._init_data_buffer(data_length=data_length, data_out=data_out)
        return self._data_buffer

    def init_metadata_buffer(self, data_length=0, data_out=None, data_buffer=None):
        """
        Initialize or assign a metadata buffer.

        Same as init_data_buffer, but for metadata buffer.
        """
        if isinstance(data_buffer, DataBuffer):
            self._metadata_buffer = data_buffer
        else:
            self._metadata_buffer = self._init_data_buffer(data_length=data_length, data_out=data_out)
        return self._metadata_buffer

    def build_command(self, **kwargs):
        """
        Build a command based on the provided keyword arguments and the raw command structure.

        This method takes keyword arguments, marshals them into a byte array based on the raw command structure,
        and then creates a command object from this byte array. The built command is returned.

        :param kwargs: Keyword arguments containing the values to be included in the command.
        :return: The built command as a byte array.
        :raises CommandDataStrucError: If the raw command structure is not initialized or if the length of the command structure
                                       is not a multiple of the specified byte alignment.
        """
        if not self._cdb_raw_struc:
            raise CommandDataStrucError("Need init cdb_raw_struc")
        if self.cdb_raw_struc_len % self.__bytes_aligned > 0:
            raise CommandDataStrucError("The length of command strcture is %d, it must be multiple of %d" % (self.cdb_raw_struc_len, self.__bytes_aligned))
        #
        self._cdb_bytearray = self.marshall_cdb(kwargs, sizeof(self._cdb_raw_struc))
        self._cdb = self._cdb_raw_struc.from_buffer(self._cdb_bytearray)
        return self._cdb

    @abstractmethod
    def check_return_status(self, success_hint=False, fail_hint=True, raise_if_fail=False):
        '''
        Check the return status of command
        '''

def generate_cdb_bits_by_structure_pro(structure: Structure, context=None):
    if context is None:
        context=StructureContext()
    cdb_bits = {}
    for i in structure._fields_:
        field_name = i[0]
        filed_type = i[1]
        if hasattr(filed_type, '_fields_'):
            cdb_bits[field_name] = generate_cdb_bits_by_structure_pro(filed_type, context=context)
        else:
            field_name,result = context.get_bit_map(i)
            cdb_bits[field_name] = result
    return cdb_bits


def encode_dict_pro(data_dict,
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
        if value is None:
            continue

        val = check_dict[key]
        if isinstance(value, dict) and isinstance(val, dict):
            encode_dict_pro(value, val, result, byteorder=byteorder)
        elif isinstance(value, dict) or isinstance(val, dict):
            raise CommandDataStrucError("The data_dict of %s is dict, but the check_dict is not dict" % key)
        else:
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

def decode_bits_pro(data,
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
        if isinstance(val, dict):
            result_dict[key] = {}
            decode_bits_pro(data, val, result_dict[key], byteorder=byteorder)
        else:
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


class CommandWrapperPro(CommandWrapper):
    def init_cdb_bitmap(self):
        """
        Initialize the CDB (Command Descriptor Block) bitmap.

        This method initializes the CDB bitmap, which is a dictionary used to store the
        bit positions and their corresponding values in the CDB. The method first checks
        if the `_cdb_bits` attribute is present, and if so, it assigns it to the `_cdb_bitmap`.
        If `_cdb_bits` is not present, it checks if the `_cdb_raw_struc` attribute is present,
        and if so, it generates the CDB bitmap using the `generate_cdb_bits_by_structure`
        function. If neither `_cdb_bits` nor `_cdb_raw_struc` is present, it checks if the
        `_cdb_bitmap_pool` attribute is present, and if so, it retrieves the CDB bitmap
        from the pool using the `req_id` as the key.
        """
        self._cdb_bitmap = {}
        if self._cdb_bits:
            self._cdb_bitmap = self._cdb_bits
        elif self._cdb_raw_struc:
            self._cdb_bitmap = generate_cdb_bits_by_structure_pro(self._cdb_raw_struc)
        elif self._cdb_bitmap_pool:
            self._cdb_bitmap = self._cdb_bitmap_pool.get(self.req_id)

    def marshall_cdb(self, cdb, cdb_len: int) -> bytearray:
        """
        Marshall a Command cdb

        :param cdb: a dict with key:value pairs representing a code descriptor block
        :param cdb_len: the total length of build command
        :return result: a byte array representing a code descriptor block
        """
        result = bytearray(cdb_len) # The command initial value is all 0
        encode_dict_pro(cdb, self._cdb_bitmap, result, byteorder=self._byteorder)
        return result

    def unmarshall_cdb(self):
        """
        Unmarshall an SCSICommand cdb

        :param cdb: a byte array representing a code descriptor block
        :return result: a dict
        """
        result = {}
        decode_bits_pro(self.cdb_struc, self._cdb_bitmap, result, byteorder=self._byteorder)
        return result
