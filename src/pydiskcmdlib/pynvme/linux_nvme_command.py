# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from ctypes import *
from enum import Enum
from pydiskcmdlib.pynvme.data_buffer import DataBuffer
from pydiskcmdlib.exceptions import *
from pydiskcmdlib.os.lin_ioctl_request import IOCTLRequest 
##
cdb_bitmap = {IOCTLRequest.NVME_IOCTL_ADMIN_CMD.value: {
                "opcode": [0xFF, 0],
                "flags": [0xFF, 1],
                "rsvd1": [0xFFFF, 2],
                "nsid":[0xFFFFFFFF, 4],
                "cdw2":[0xFFFFFFFF, 8],
                "cdw3":[0xFFFFFFFF, 12],
                "metadata":[0xFFFFFFFFFFFFFFFF, 16],
                "addr":[0xFFFFFFFFFFFFFFFF, 24],
                "metadata_len":[0xFFFFFFFF, 32],
                "data_len":[0xFFFFFFFF, 36],
                "cdw10":[0xFFFFFFFF, 40],
                "cdw11":[0xFFFFFFFF, 44],
                "cdw12":[0xFFFFFFFF, 48],
                "cdw13":[0xFFFFFFFF, 52],
                "cdw14":[0xFFFFFFFF, 56],
                "cdw15":[0xFFFFFFFF, 60],
                "timeout_ms":[0xFFFFFFFF, 64],
                "result":[0xFFFFFFFF, 68],
                },
              IOCTLRequest.NVME_IOCTL_IO_CMD.value: {
                "opcode": [0xFF, 0],
                "flags": [0xFF, 1],
                "rsvd1": [0xFFFF, 2],
                "nsid":[0xFFFFFFFF, 4],
                "cdw2":[0xFFFFFFFF, 8],
                "cdw3":[0xFFFFFFFF, 12],
                "metadata":[0xFFFFFFFFFFFFFFFF, 16],
                "addr":[0xFFFFFFFFFFFFFFFF, 24],
                "metadata_len":[0xFFFFFFFF, 32],
                "data_len":[0xFFFFFFFF, 36],
                "cdw10":[0xFFFFFFFF, 40],
                "cdw11":[0xFFFFFFFF, 44],
                "cdw12":[0xFFFFFFFF, 48],
                "cdw13":[0xFFFFFFFF, 52],
                "cdw14":[0xFFFFFFFF, 56],
                "cdw15":[0xFFFFFFFF, 60],
                "timeout_ms":[0xFFFFFFFF, 64],
                "result":[0xFFFFFFFF, 68],
                },
             }

class CmdStructure(LittleEndianStructure):
    _fields_ = [
        ("opcode", c_uint8),        # OPCode of command  ------------------------|
        ("flags", c_uint8),         # FUSE and PSDT included, usually not used --|-> DWORD 0
        ("rsvd1", c_uint16),        # Command Identifier, used by low-level -----|
        ("nsid", c_uint32),         # Namespace Identifier ------------------------- DWORD 1
        ("cdw2", c_uint32),         # cdw2 ----------------------------------------- DWORD 2
        ("cdw3", c_uint32),         # cdw3 ----------------------------------------- DWORD 3
        ("metadata", c_uint64),     # Metadata Pointer ----------------------------- DWORD 4-5
        ("addr", c_uint64),         # Data Pointer --------------------------------- DWORD 6-7
        ("metadata_len", c_uint32), 
        ("data_len", c_uint32),
        ("cdw10", c_uint32),        # CDW10 
        ("cdw11", c_uint32),        # CDW11
        ("cdw12", c_uint32),        # CDW12
        ("cdw13", c_uint32),        # CDW13
        ("cdw14", c_uint32),        # CDW14
        ("cdw15", c_uint32),        # CDW15
        ("timeout_ms", c_uint32),   # Timeout
        ("result", c_uint32),       # spec 2.0 will be 2 DWs, total length 64 bytes
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
        metadata_buffer=None,  ## Metadata Pointer, structure of DataBuffer
        data_buffer=None,      ## Data Pointer, structure of DataBuffer
        metadata_len=0, ## Metadata length
        data_len=0,     ## used to create data buffer
        data_out=None,  ## used to init data_buf
        cdw10=0,   ## cdw10
        cdw11=0,   ## cdw11
        cdw12=0,   ## cdw12
        cdw13=0,   ## cdw13
        cdw14=0,   ## cdw14
        cdw15=0,   ## cdw15
        timeout_ms=10000, ## timeout in millisecond addr
        result=0,  ## result
        **kwargs,  ## ignore the invalid key-value
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

        if data_buffer is None and data_len > 0: # Need init buffer in other ways
            # Keep a reference alive in pure python.
            if data_out is None:
                self._data_buf = create_string_buffer(data_len)
            else:
                self._data_buf = create_string_buffer(data_out, data_len)
            self.addr = c_uint64(addressof(self._data_buf))
        elif isinstance(data_buffer, DataBuffer):  # init data buffer in DataBuffer
            self._data_buf = data_buffer.data_buffer
            self.addr = data_buffer.addr
            self._active_addr()
            data_len = data_buffer.data_length
        else:  # disable the data buffer in all the other state.
            self._data_buf = None
            self.addr = 0
        self.data_len = data_len

        if metadata_buffer is None and metadata_len < 1:
            self._metadata_buf = None
            self.metadata = 0
        elif metadata_buffer is None and metadata_len > 0:
            # Keep a reference alive in pure python.
            self._metadata_buf = create_string_buffer(metadata_len)
            self.metadata = c_uint64(addressof(self._metadata_buf))
        elif isinstance(metadata_buffer, DataBuffer):  # init data buffer in DataBuffer
            self._metadata_buf = metadata_buffer.data_buffer
            self.metadata = metadata_buffer.addr
            self._active_metadata()
            metadata_len = metadata_buffer.data_length
        else:
            self._metadata_buf = None
            self.metadata = 0
        self.metadata_len = metadata_len

    def _active_addr(self):
        cast(self.addr, POINTER(c_int)) # This will active the memory data

    def _active_metadata(self):
        cast(self.metadata, POINTER(c_int)) # This will active the memory data

    @property
    def command_buf(self):
        return self

    @property
    def data_buf(self):
        # In case of setting CmdStructure in the way of CmdStructure.from_buffer
        if not hasattr(self, '_data_buf'): 
            if self.data_len > 0:
                self._data_buf = cast(self.addr, POINTER(c_char*self.data_len)).contents
            else:
                self._data_buf = None
        return self._data_buf

    @property
    def metadata_buf(self):
        # In case of setting CmdStructure in the way of CmdStructure.from_buffer
        if not hasattr(self, '_metadata_buf'): 
            if self.metadata_len > 0:
                self._metadata_buf = cast(self.metadata, POINTER(c_char*self.metadata_len)).contents
            else:
                self._metadata_buf = None
        return self._metadata_buf

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
