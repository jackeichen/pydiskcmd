# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from ctypes import *

##
NVMeStorageQueryPropertyID = 50          # StorageDeviceProtocolSpecificProperty
NVMeStorageQueryPropertyQueryType = 0    # PropertyStandardQuery
NVMeStorageQueryPropertyProtocolType = 3 # ProtocolTypeNvme
NVMeStorageQueryPropertyDataType = 2     # NVMeDataTypeLogPage

##
# https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddstor/ne-ntddstor-_storage_protocol_nvme_data_type
##

class NVMeStorageQueryPropertyHeader(Structure):
    _fields_ = [
        ("PropertyId", c_uint32),
        ("QueryType", c_uint32),
        ("ProtocolType", c_uint32),
        ("DataType", c_uint32),
        ("ProtocolDataRequestValue", c_uint32),
        ("ProtocolDataRequestSubValue", c_uint32),
        ("ProtocolDataOffset", c_uint32),
        ("ProtocolDataLength", c_uint32),
        ("FixedProtocolReturnData", c_uint32),
        ("ProtocolDataRequestSubValue2", c_uint32),
        ("ProtocolDataRequestSubValue3", c_uint32),
        ("ProtocolDataRequestSubValue4", c_uint32),
        ##c_ubyte * 4
        #("CSEDataAdmin", c_ubyte*1024),
        #("CSEDataIO", c_ubyte*1024),
        #("Reserved1", c_ubyte*2048),
    ]
    _pack_ = 1

    def __init__(
        self,
        PropertyId=0,
        QueryType=0,
        ProtocolType=3,
        DataType=0,
        RequestValue=0,
        RequestSubValue=0,
        ProtocolDataOffset=40,
        ProtocolDataLength=0,
        RequestSubValue2=0,
        RequestSubValue3=0,
        RequestSubValue4=0,
    ):
        self.PropertyId = PropertyId
        self.QueryType = QueryType
        self.ProtocolType = ProtocolType
        self.DataType = DataType
        self.ProtocolDataRequestValue = RequestValue
        self.ProtocolDataRequestSubValue = RequestSubValue
        self.ProtocolDataOffset = ProtocolDataOffset
        self.ProtocolDataLength = ProtocolDataLength
        self.FixedProtocolReturnData = 0
        self.ProtocolDataRequestSubValue2 = RequestSubValue2
        self.ProtocolDataRequestSubValue3 = RequestSubValue3
        self.ProtocolDataRequestSubValue4 = RequestSubValue4


class NVMeStorageQueryPropertyWithoutBuffer(Structure):
    _fields_ = [
        ('nsqp', NVMeStorageQueryPropertyHeader),
    ]

    _pack_ = 1

    def __init__(self, **kwargs):
        self.nsqp = NVMeStorageQueryPropertyHeader(**kwargs)

    @property
    def _data_buf(self):
        return None
    
    @property
    def _metadata_buf(self):
        return None

    @property
    def result(self):
        return self.nsqp.FixedProtocolReturnData


def get_NVMeStorageQueryPropertyWithBuffer(data_len):
    class NVMeStorageQueryPropertyWithBuffer(Structure):
        _fields_ = [
            ('nsqp', NVMeStorageQueryPropertyHeader),
            ('raw_data', c_ubyte * data_len)
        ]
        _pack_ = 1

        def __init__(self, **kwargs):
            self.nsqp = NVMeStorageQueryPropertyHeader(**kwargs)

        @property
        def _data_buf(self):
            return self.raw_data
        
        @property
        def _metadata_buf(self):
            return None

        @property
        def result(self):
            return self.nsqp.FixedProtocolReturnData
    return NVMeStorageQueryPropertyWithBuffer


class NVMeStorageQueryPropertyWithBuffer512(Structure):
    _fields_ = [
        ('nsqp', NVMeStorageQueryPropertyHeader),
        ('raw_data', c_ubyte * 512)
    ]

    _pack_ = 1

    def __init__(self, **kwargs):
        self.nsqp = NVMeStorageQueryPropertyHeader(**kwargs)

    @property
    def _data_buf(self):
        return self.raw_data
    
    @property
    def _metadata_buf(self):
        return None

    @property
    def result(self):
        return self.nsqp.FixedProtocolReturnData


class NVMeStorageQueryPropertyWithBuffer564(Structure):
    _fields_ = [
        ('nsqp', NVMeStorageQueryPropertyHeader),
        ('raw_data', c_ubyte * 564)
    ]

    _pack_ = 1

    def __init__(self, **kwargs):
        self.nsqp = NVMeStorageQueryPropertyHeader(**kwargs)

    @property
    def _data_buf(self):
        return self.raw_data

    @property
    def _metadata_buf(self):
        return None

    @property
    def result(self):
        return self.nsqp.FixedProtocolReturnData


class NVMeStorageQueryPropertyWithBuffer4096(Structure):
    _fields_ = [
        ('nsqp', NVMeStorageQueryPropertyHeader),
        ('raw_data', c_ubyte * 4096)
    ]

    _pack_ = 1

    def __init__(self, **kwargs):
        self.nsqp = NVMeStorageQueryPropertyHeader(**kwargs)

    @property
    def _data_buf(self):
        return self.raw_data

    @property
    def _metadata_buf(self):
        return None

    @property
    def result(self):
        return self.nsqp.FixedProtocolReturnData
