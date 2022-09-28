from ctypes import *


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
        ("result", c_uint32),
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
        metadata_len=0, ##
        data_len=0,     ## used to create data buffer
        data_in=None,    ## used to init data_buf
        cdw10=0,   ## cdw10
        cdw11=0,   ## cdw11
        cdw12=0,   ## cdw12
        cdw13=0,   ## cdw13
        cdw14=0,   ## cdw14
        cdw15=0,   ## cdw15
        timeout_ms=0, ## timeout
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
