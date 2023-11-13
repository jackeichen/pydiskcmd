# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from ctypes import *
from pydiskcmd.exceptions import *
from pydiskcmd.utils.converter import scsi_int_to_ba
from pydiskcmd.utils.number_h import build_int_by_bitmap


class CmdStructure(LittleEndianStructure):
    _fields_ = [
        ("opcode", c_uint8),
        ("flags", c_uint8),
        ("rsvd1", c_uint16),
        ("nsid", c_uint32),
        ("cdw2", c_uint32),
        ("cdw3", c_uint32),
        ("metadata", c_uint64),
        ("addr", c_uint64),
        ("metadata_len", c_uint32),
        ("data_len", c_uint32),
        ("cdw10", c_uint32),
        ("cdw11", c_uint32),
        ("cdw12", c_uint32),
        ("cdw13", c_uint32),
        ("cdw14", c_uint32),
        ("cdw15", c_uint32),
        ("timeout_ms", c_uint32),
        ("result", c_uint32),  ## spec 2.0 will be 2 DWs, total length 64 bytes
    ]
    _pack_ = 1

    def __init__(
        self,
        opcode=0,  ## opcode
        flags=0,   ## Fused Operation
        rsvd1=0,   ## Reserved
        nsid=0,    ## Namespace Identifier
        cdw2=0,    ## Reserved
        cdw3=0,    ## Reserved
        metadata=None,  ## Metadata Pointer
        addr=None,      ## Data Pointer
        metadata_len=0, ## Metadata length
        data_len=0,     ## used to create data buffer
        data_in=None,   ## used to init data_buf
        cdw10=0,   ## cdw10
        cdw11=0,   ## cdw11
        cdw12=0,   ## cdw12
        cdw13=0,   ## cdw13
        cdw14=0,   ## cdw14
        cdw15=0,   ## cdw15
        timeout_ms=0, ## timeout in millisecond
        result=0,  ## result
    ):
        self.opcode = c_uint8(opcode)
        self.flags = c_uint8(flags)
        self.rsvd1 = c_uint16(rsvd1)
        self.nsid = c_uint32(nsid)
        self.cdw2 = c_uint32(cdw2)
        self.cdw3 = c_uint32(cdw3)
        self.cdw10 = c_uint32(cdw10)
        self.cdw11 = c_uint32(cdw11)
        self.cdw12 = c_uint32(cdw12)
        self.cdw13 = c_uint32(cdw13)
        self.cdw14 = c_uint32(cdw14)
        self.cdw15 = c_uint32(cdw15)
        self.timeout_ms = c_uint32(timeout_ms)
        self.result = c_uint32(result)

        if addr is None:
            if data_len > 0:
                # Keep a reference alive in pure python.
                if data_in is None:
                    self._data_buf = create_string_buffer(data_len)
                else:
                    self._data_buf = create_string_buffer(data_in, data_len)
                self.addr = c_uint64(addressof(self._data_buf))
            else:
                self._data_buf = None
                self.addr = 0
        else:
            self._data_buf = None
            self.addr = addr
        self.data_len = data_len

        if metadata is None:
            if metadata_len > 0:
                # Keep a reference alive in pure python.
                self._metadata_buf = create_string_buffer(metadata_len)
                self.metadata = c_uint64(addressof(self._metadata_buf))
            else:
                self._metadata_buf = None
                self.metadata = 0
        else:
            self._metadata_buf = None
            self.metadata = metadata
        self.metadata_len = metadata_len

    def dump_element(self):
        info = {}
        # check by _fields_
        for k, v in self._fields_:
            av = getattr(self, k)
            if type(v) == type(Structure):
                av = av.dump_dict()
            elif type(v) == type(Array):
                av = cast(av, c_char_p).value.decode()
            else:
                pass
            info[k] = av
        return info


class DataBuffer(LittleEndianStructure):
    def __init__(self, length):
        self.__len = length
        ## init
        self._data_buf = create_string_buffer(length)
        self.addr = c_uint64(addressof(self._data_buf))

    @property
    def data_buffer(self):
        return self._data_buf

    @property
    def data_length(self):
        return self.__len

    @data_buffer.setter
    def data_buffer(self, value):
        if isinstance(value, bytes):
            self._data_buf.value = value
        else:
            raise RuntimeError("Need bytes object")


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
