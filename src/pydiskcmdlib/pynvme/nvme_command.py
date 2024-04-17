# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import sys
from enum import Enum
from pydiskcmdlib import os_type
from pydiskcmdlib.exceptions import *
from pydiskcmdlib.utils.converter import encode_dict,decode_bits,CheckDict
from pydiskcmdlib.pynvme import linux_nvme_command
from pydiskcmdlib.pynvme import win_nvme_command
from pydiskcmdlib.pynvme.data_buffer import DataBuffer
##
class AdminCommandOpcode(Enum):
    DeleteIOSQ               = 0x00
    CreateIOSQ               = 0x01
    GetLogPage               = 0x02
    DeleteIOCQ               = 0x04
    CreateIOCQ               = 0x05
    Identify                 = 0x06
    Abort                    = 0x08
    SetFeature               = 0x09
    GetFeature               = 0x0A
    AsynchronousEventRequest = 0x0C
    NamespaceManagement      = 0x0D
    FirmwareCommit           = 0x10
    FirmwareImageDownload    = 0x11
    DeviceSelftest           = 0x14
    NamespaceAttachment      = 0x15
    KeepAlive                = 0x18
    DirectiveSend            = 0x19
    DirectiveReceive         = 0x1A
    VirtualizationManagement = 0x1C
    NVMeMISend               = 0x1D
    NVMeMIReceive            = 0x1E
    DoorbellBufferConfig     = 0x7C
    # 0x7F, Refer to the NVMe over Fabrics specification
    # C0h to FFh, Vendor specific
    FormatNVM                = 0x80
    SecuritySend             = 0x81
    SecurityReceive          = 0x82
    Sanitize                 = 0x84
    GetLBAStatus             = 0x86

class NVMCommandOpcode(Enum):
    Flush               = 0x00
    Write               = 0x01
    Read                = 0x02
    WriteUncorrectable  = 0x04
    Compare             = 0x05
    WriteZeroes         = 0x08
    DatasetManagement   = 0x09
    Verify              = 0x0C
    ReservationRegister = 0x0D
    ReservationReport   = 0x0E
    ReservationAcquire  = 0x11
    ReservationRelease  = 0x15
    # 80h to FFh, Vendor specific

class CommandTimeout(Enum):
    # in millisecond
    admin = 60000
    nvm   = 60000


def build_int_by_bitmap(bitmap):
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
        ## find bit offset
        suboffset = 0
        while True:
            if ((bit_mask >> suboffset) & 0x01):
                break
            suboffset += 1
        ## check value
        if value > (bit_mask >> suboffset):
            raise RuntimeError("Value to big to set: %s" % str(value))
        ##
        target_value += (value << (byte_offset*8+suboffset))
    return target_value


class NVMeCommand(object):
    '''
    This Class define the function that must be implemented by CommandWapper function.
    '''
    _cdb_bits: CheckDict = {}   # define your self command bitmap
    _req_id: int = 0

    def __init__(self):
        """
        """
        # the _cdb may include command and data_buffer
        self._cdb = None  #  default value: None
        ##
        self._cq_status_field = None
        ##
        self.__data_buffer = None
        self.__metadata_buffer = None
        ## used by build command
        self._byteorder = sys.byteorder
        ## init bitmap
        self.init_cdb_bitmap()

    def print_cdb(self):
        """
        simple helper to print out the cdb as hex values
        """
        if self.cdb_struc:
            for b in self.cdb_struc:
                print("0x%02X " % b)

    def init_cdb_bitmap(self):
        self._cdb_bitmap = self._cdb_bits
        if not self._cdb_bitmap:
            if os_type == "Linux":
                self._cdb_bitmap = linux_nvme_command.cdb_bitmap.get(self.req_id)
            elif os_type == "Windows":
                self._cdb_bitmap = win_nvme_command.cdb_bitmap.get(self.req_id)
            if self._cdb_bitmap is None:
                self._cdb_bitmap = {}

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
            return bytes(self.cdb.command_buf)

    @property
    def req_id(self):
        """
        getter method of the req_id property

        :return: a int
        """
        return self._req_id

    @property
    def data_buffer(self):
        return self.__data_buffer

    @property
    def metadata_buffer(self):
        return self.__metadata_buffer

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
            self.__data_buffer = data_buffer
        else:
            self.__data_buffer = self._init_data_buffer(data_length=data_length, data_out=data_out)
        return self.__data_buffer

    def init_metadata_buffer(self, data_length=0, data_out=None, data_buffer=None):
        if isinstance(data_buffer, DataBuffer):
            self.__metadata_buffer = data_buffer
        else:
            self.__metadata_buffer = self._init_data_buffer(data_length=data_length, data_out=data_out)
        return self.__metadata_buffer

    def build_command(self, **kwargs):
        """
        Build the command in different OS:
          1. The Linux define a fixed-length ctypes.structure;
          2. The Windows define a bariable-length ctypes.structure.
            * Windows init the cdb bufffer with StorageQueryWithoutBuffer
            * Windows cannot set a data buffer in building

        :param kwargs: the parameters to build command
                    For Linux, the key in kwargs should be xxx(like abc)
                    For Windows, the key in kwargs should be Xxx(like Abc)
                the kwargs is to build command.

        :return: the built command
        """
        if os_type == "Linux":
            ## build CDB
            if self._req_id in (linux_nvme_command.IOCTLRequest.NVME_IOCTL_ADMIN_CMD.value, 
                                linux_nvme_command.IOCTLRequest.NVME_IOCTL_IO_CMD.value):
                ## if use default cdb bitmap, check the parametrs and fix
                ## The valid parameters
                # opcode,flags,nsid,cdw2,cdw3,metadata,metadata_len,data_len
                # cdw10,cdw11,cdw12,cdw13,cdw14,cdw15,timeout_ms
                ##
                if not self._cdb_bits:
                    if self.__data_buffer: 
                        if kwargs.get("addr") is None:  # data not set
                            kwargs["addr"] = self.__data_buffer.addr
                        if kwargs.get("data_len") is None:
                            kwargs["data_len"] = self.__data_buffer.data_length
                    if self.__metadata_buffer:
                        if kwargs.get("metadata") is None:  # data not set
                            kwargs["metadata"] = self.__metadata_buffer.addr
                        if kwargs.get("metadata_len") is None:
                            kwargs["metadata_len"] = self.__metadata_buffer.data_length
                ## start to build command
                _cdb = self.marshall_cdb(kwargs, linux_nvme_command.sizeof(linux_nvme_command.CmdStructure))
                # build the command
                self._cdb = linux_nvme_command.CmdStructure.from_buffer(_cdb)
            elif self._req_id in (linux_nvme_command.IOCTLRequest.NVME_IOCTL_RESET.value,
                                  linux_nvme_command.IOCTLRequest.NVME_IOCTL_SUBSYS_RESET.value):
                self._cdb = None
            elif self._req_id == linux_nvme_command.IOCTLRequest.SG_IO_IOCTL.value:
                raise BuildNVMeCommandError("Failed to build command, Do Not Support Request %#x" % self._req_id)
            elif self._req_id == linux_nvme_command.IOCTLRequest.RESERVED_REQUEST_ID.value:
                raise BuildNVMeCommandError("Failed to build command, Command may Not Support(Request ID value %d stands for %s)" % (self._req_id, linux_nvme_command.IOCTLRequest.RESERVED_REQUEST_ID.name))
            else:
                raise BuildNVMeCommandError("Failed to build command, Do Not Support Request %#x" % self._req_id)
        elif os_type == "Windows":
            if self._req_id == win_nvme_command.IOCTLRequest.IOCTL_STORAGE_QUERY_PROPERTY.value:
                ## if use default cdb bitmap, check the parametrs and fix
                ## The valid parameters
                # PropertyId,QueryType,DataType,ProtocolDataLength
                # ProtocolDataRequestValue,ProtocolDataRequestSubValue,ProtocolDataRequestSubValue2,ProtocolDataRequestSubValue3,ProtocolDataRequestSubValue4
                ##
                if not self._cdb_bits:
                    # kwargs["PropertyId"]
                    # kwargs["QueryType"]
                    kwargs["ProtocolType"] = win_nvme_command.StroageProtocolType.ProtocolTypeNvme.value
                    if kwargs["DataType"] >= win_nvme_command.StorageProtocolNVMeDataType.UnusedMaxValue.value:
                        raise BuildNVMeCommandError("DataType should be less than %d" % win_nvme_command.StorageProtocolNVMeDataType.UnusedMaxValue.value)
                    kwargs["ProtocolDataOffset"] = win_nvme_command.sizeof(win_nvme_command.StorageProtocolSpecificData)
                # This will get the data length in StorageQueryWithBuffer.StorageProtocolSpecificData.ProtocolDataLength
                _cdb = self.marshall_cdb(kwargs, win_nvme_command.sizeof(win_nvme_command.StorageQueryWithoutBuffer))
                self._cdb = win_nvme_command.StorageQueryWithoutBuffer.from_buffer(_cdb)
                data_len = self._cdb.protocol_specific.ProtocolDataLength
                if data_len > 0:
                    # Get the StorageQueryWithBuffer with data_len
                    _cdb = self.marshall_cdb(kwargs, win_nvme_command.sizeof(win_nvme_command.StorageQueryWithoutBuffer)+data_len)
                    self._cdb = win_nvme_command.GetStorageQueryWithBuffer(data_len).from_buffer(_cdb)
            # STORAGE_PROTOCOL_COMMAND
            elif self._req_id == win_nvme_command.IOCTLRequest.IOCTL_STORAGE_PROTOCOL_COMMAND.value:
                ## if use default cdb bitmap, check the parametrs and fix
                ## The valid parameters
                # Flags,ErrorInfoLength,TimeOutValue,DataToDeviceTransferLength,DataFromDeviceTransferLength,CommandSpecific
                # CDW0: OPC,FUSE,PSDT,CID
                # NSID,CDW10,CDW11,CDW12,CDW13,CDW14,CDW15
                ##
                if not self._cdb_bits:
                    kwargs["Version"] = win_nvme_command.STORAGE_PROTOCOL_STRUCTURE_VERSION
                    kwargs["Length"] = win_nvme_command.STORAGE_PROTOCOL_COMMAND_LENGTH
                    kwargs["ProtocolType"] = win_nvme_command.StroageProtocolType.ProtocolTypeNvme.value
                    if kwargs.get("Flags") not in (win_nvme_command.STORAGE_PROTOCOL_COMMAND_FLAG_ADAPTER_REQUEST, 0):
                        raise BuildNVMeCommandError("Flags should be %#x|%#x" % (win_nvme_command.STORAGE_PROTOCOL_COMMAND_FLAG_ADAPTER_REQUEST, 0))
                    kwargs["CommandLength"] = win_nvme_command.STORAGE_PROTOCOL_COMMAND_LENGTH_NVME
                    if kwargs.get("ErrorInfoLength") in (None, 0):
                        kwargs["ErrorInfoOffset"] = 0
                        kwargs["ErrorInfoLength"] = 0
                    elif kwargs.get("ErrorInfoLength") == win_nvme_command.sizeof(win_nvme_command.NVME_ERROR_INFO_LOG):
                        kwargs["ErrorInfoOffset"] = win_nvme_command.sizeof(win_nvme_command.STORAGE_PROTOCOL_COMMAND)
                    else:
                        raise BuildNVMeCommandError("ErrorInfoLength should be %#x|%#x" % (win_nvme_command.sizeof(win_nvme_command.NVME_ERROR_INFO_LOG), 0))
                    # kwargs["DataToDeviceTransferLength"]
                    # kwargs["DataFromDeviceTransferLength"]
                    if not kwargs.get("TimeOutValue"):
                        kwargs["TimeOutValue"] = 10
                    #
                    if kwargs.get("DataToDeviceTransferLength") in (None, 0):
                        kwargs["DataToDeviceTransferLength"] = 0
                        kwargs["DataToDeviceBufferOffset"] = 0
                    elif kwargs["DataToDeviceTransferLength"] > 0:
                        kwargs["DataToDeviceBufferOffset"] = win_nvme_command.sizeof(win_nvme_command.STORAGE_PROTOCOL_COMMAND) + kwargs["ErrorInfoLength"]
                        kwargs["DataFromDeviceTransferLength"] = 0  # if set DataToDevice, then disable DataFromDevice
                    if kwargs.get("DataFromDeviceTransferLength") in (None, 0):
                        kwargs["DataFromDeviceTransferLength"] = 0
                        kwargs["DataFromDeviceBufferOffset"] = 0
                    elif kwargs["DataFromDeviceTransferLength"] > 0:
                        kwargs["DataFromDeviceBufferOffset"] = win_nvme_command.sizeof(win_nvme_command.STORAGE_PROTOCOL_COMMAND) + kwargs["ErrorInfoLength"]
                    #
                    if kwargs.get("CommandSpecific") not in (win_nvme_command.STORAGE_PROTOCOL_SPECIFIC_NVME_ADMIN_COMMAND,
                                                             win_nvme_command.STORAGE_PROTOCOL_SPECIFIC_NVME_NVM_COMMAND):
                        raise BuildNVMeCommandError("CommandSpecific should be %#x|%#x" % (win_nvme_command.STORAGE_PROTOCOL_SPECIFIC_NVME_ADMIN_COMMAND, win_nvme_command.STORAGE_PROTOCOL_SPECIFIC_NVME_NVM_COMMAND))
                    ## NVME_COMMAND init start
                    # The valid parameters is CDW0: OPC,FUSE,PSDT,CID
                    #                         NSID,CDW10,CDW11,CDW12,CDW13,CDW14,CDW15
                    ##
                    ## Do Not Check here
                    # if kwargs["CommandSpecific"] == win_nvme_command.STORAGE_PROTOCOL_SPECIFIC_NVME_ADMIN_COMMAND and kwargs["OPC"] < 0xC0:
                    #     raise BuildNVMeCommandError("IOCTL_STORAGE_PROTOCOL_COMMAND should only be used for Vendor Specific Admin Commands (C0h - FFh)")
                    # elif kwargs["CommandSpecific"] == win_nvme_command.STORAGE_PROTOCOL_SPECIFIC_NVME_NVM_COMMAND and kwargs["OPC"] < 0x80:
                    #     raise BuildNVMeCommandError("IOCTL_STORAGE_PROTOCOL_COMMAND should only be used for Vendor Specific NVMe Commands (80h - FFh)")
                # 
                _cdb = self.marshall_cdb(kwargs, win_nvme_command.sizeof(win_nvme_command.STORAGE_PROTOCOL_COMMAND))
                self._cdb = win_nvme_command.STORAGE_PROTOCOL_COMMAND.from_buffer(_cdb)
                data_len = (self._cdb.DataToDeviceTransferLength or self._cdb.DataFromDeviceTransferLength) + self._cdb.ErrorInfoLength
                if data_len > 0:
                    _cdb = self.marshall_cdb(kwargs, win_nvme_command.sizeof(win_nvme_command.StorageQueryWithoutBuffer)+data_len)
                    self._cdb = win_nvme_command.GetStorageProtocolCommandWithBuffer(data_len).from_buffer(_cdb)
            elif self._req_id in (win_nvme_command.IOCTLRequest.FSCTL_LOCK_VOLUME.value,
                                  win_nvme_command.IOCTLRequest.FSCTL_UNLOCK_VOLUME.value,
                                  win_nvme_command.IOCTLRequest.IOCTL_DISK_FLUSH_CACHE.value,
                                  ):
                self._cdb = None
            elif self._req_id == win_nvme_command.IOCTLRequest.RESERVED_REQUEST_ID.value:
                raise BuildNVMeCommandError("Failed to build command, Command may Not Support(Request ID value %d stands for %s)" % (self._req_id, win_nvme_command.IOCTLRequest.RESERVED_REQUEST_ID.name))
            else:
                raise BuildNVMeCommandError("Failed to build command, Do Not Support Request %#x" % self._req_id)
        else:
            raise BuildNVMeCommandError("%s Do Not Support this command" % os_type)
        return self._cdb

    @property
    def cq_status(self):
        '''
        Compeletion Queue DWORD 3
        '''
        return self._cq_status_field

    @cq_status.setter
    def cq_status(self, value):
        '''
        To set Compeletion Queue DWORD 3
        '''
        self._cq_status_field = value

    @property
    def cq_cmd_spec(self):
        '''
        Compeletion Queue DWORD 1
        '''
        if self.cdb:
            return self.cdb.result

    @property
    def data(self):
        if self.cdb and self.cdb.data_buf:
            return bytes(self.cdb.data_buf)

    @property
    def metadata(self):
        if self.cdb and self.cdb.metadata_buf:
            return bytes(self.cdb.metadata_buf)

    def _win_execute_check(self):
        if self._req_id == win_nvme_command.IOCTLRequest.IOCTL_STORAGE_QUERY_PROPERTY.value:
            if self._cdb:
                temp = win_nvme_command.STORAGE_PROTOCOL_DATA_DESCRIPTOR.from_buffer_copy(self.cdb_raw)
                # Validate the returned data.
                if temp.Version != win_nvme_command.sizeof(win_nvme_command.STORAGE_PROTOCOL_DATA_DESCRIPTOR) or temp.Size != win_nvme_command.sizeof(win_nvme_command.STORAGE_PROTOCOL_DATA_DESCRIPTOR):
                    raise CommandReturnDataError("DeviceNVMeQueryProtocolData: data descriptor header not valid.")

    def check_return_status(self, success_hint=False, fail_hint=True, raise_if_fail=False):
        SC = (self.cq_status & 0xFF)
        SCT = ((self.cq_status >> 8) & 0x07)
        CRD = ((self.cq_status >> 11) & 0x03)
        More = (self.cq_status >> 13 & 0x01)
        DNR = (self.cq_status >> 14 & 0x01)
        if SCT == 0 and SC == 0:
            if success_hint:
                print ("Command Success")
                print ('')
        else:
            if fail_hint:
                print ("Command failed, and details bellow.")
                format_string = "%-15s%-20s%-8s%s"
                print (format_string % ("Status Code", "Status Code Type", "More", "Do Not Retry"))
                print (format_string % (SC, SCT, More, DNR))
                print ('')
            if raise_if_fail:
                raise CommandReturnStatusError("NVMe Return Status Check Error: Status Code Type(%#x), Status Code(%#x)" % (SCT, SC))
        return SC,SCT
