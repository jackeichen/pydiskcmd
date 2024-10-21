# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import sys
from typing import Optional
from abc import ABCMeta, abstractmethod
from pydiskcmdlib import os_type
from pydiskcmdlib.data_buffer import DataBuffer
from pydiskcmdlib.utils.converter import encode_dict,decode_bits,CheckDict
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
        # Windows
        self._bytes_returned = None

    @property
    def ioctl_result(self):
        return self._ioctl_result

    @property
    def bytes_returned(self):
        return self._bytes_returned

    def init_cdb_bitmap(self):
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
    def cdb_raw_struc_len(self):
        return sizeof(self.cdb_raw_struc)

    @property
    def req_id(self):
        """
        getter method of the req_id property

        :return: a int
        """
        return self._req_id

    def marshall_cdb(self, cdb, cdb_len: int):
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
        data_buffer = None
        if data_out:
            _data_len = data_length if data_length > 0 else len(data_out)
            data_buffer = DataBuffer(_data_len)
            data_buffer.data_buffer = data_out
        else:
            data_buffer = DataBuffer(data_length)
        return data_buffer

    def init_data_buffer(self, data_length=0, data_out=None, data_buffer=None):
        if isinstance(data_buffer, DataBuffer):
            self._data_buffer = data_buffer
        else:
            self._data_buffer = self._init_data_buffer(data_length=data_length, data_out=data_out)
        return self._data_buffer

    def init_metadata_buffer(self, data_length=0, data_out=None, data_buffer=None):
        if isinstance(data_buffer, DataBuffer):
            self._metadata_buffer = data_buffer
        else:
            self._metadata_buffer = self._init_data_buffer(data_length=data_length, data_out=data_out)
        return self._metadata_buffer

    def build_command(self, **kwargs):
        """
        Build the command in different OS:
          1. The Linux define a fixed-length ctypes.structure;
          2. The Windows define a bariable-length ctypes.structure.
            * Windows init the cdb bufffer with StorageQueryWithoutBuffer
            * Windows cannot set a data buffer in building

        :param kwargs: the parameters to build command

        :return: the built command
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
