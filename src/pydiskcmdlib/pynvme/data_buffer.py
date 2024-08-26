# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from ctypes import create_string_buffer,addressof,c_uint64
from pydiskcmdlib.utils.converter import scsi_int_to_ba

class DataBuffer(object):
    def __init__(self, length):
        """
        Initializes a new instance of the Format class.

        Parameters:
            length (int): The length of the data buffer to be created.
        """
        self.__len = length
        ## init
        self._data_buf = create_string_buffer(length)
        # self.addr = c_uint64(addressof(self._data_buf))

    @property
    def data_buffer(self):
        """ 
        This function is a method of the DataBuffer class and is used to return a data buffer
        
        Returns:
            The returned value is a data buffer, which can be used to store formatted data
        """
        return self._data_buf

    @property
    def addr(self):
        """
        This function is a method of the DataBuffer class and is used to return the address of the data buffer
        If the length of the data buffer is greater than 0, the function returns the address of the data buffer, otherwise it returns 0

        Returns:
            The returned value is an integer, representing the address of the data buffer
        """
        if self.__len > 0:
            return (addressof(self._data_buf))
        return 0

    @property
    def data_length(self):
        return self.__len

    @data_buffer.setter
    def data_buffer(self, value: bytes):
        """
        This method is used to set the value of the data buffer for the Format object.

        Parameters:
            value (bytes): The value that the data buffer will be set to. This must be a bytes object.

        Returns:
            None
        """
        self._data_buf.value = bytes(value)

    def get_data_buffer(self):
        """
        This method is used to return the data buffer.

        Parameters:
            None

        Returns:
            bytes: The data buffer.
        """
        return self._data_buf


def encode_data_buffer(data_dict,
                       check_dict,
                       result):
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

            v = scsi_int_to_ba(value, _num, 'little')
            for i in range(len(v)):
                result[bytepos + i] = (ord(result[bytepos + i]) + v[i])
        else:
            pass
