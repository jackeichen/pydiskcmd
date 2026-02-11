# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import sys
from enum import Enum
from pydiskcmdlib import os_type
from pydiskcmdlib.exceptions import *
from pydiskcmdlib.utils.converter import (
    encode_dict,
    decode_bits,
    CheckDict,
    get_check_dict_maxsize,
)
from pydiskcmdlib.pynvme import linux_nvme_command
from pydiskcmdlib.pynvme import win_nvme_command
from pydiskcmdlib.pynvme.data_buffer import DataBuffer
from pydiskcmdlib.os.win_ioctl_utils import StorageProtocolStatus
from pydiskcmdlib.utils.common_lib import enum_find
from .nvme_status_code import StatusCodeDescription
#
sizeof = win_nvme_command.sizeof
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
    _cdb_bits: CheckDict = {}   # user defined cdb bitmap
    _req_id: int = 0
    _cmd_spec_fail = {}

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
        ## inner used for check
        self.__command_data_length = 0
        ## used by build command
        self._byteorder = sys.byteorder
        ## init bitmap
        self.init_cdb_bitmap()
        ## ioctl return value
        self._result = None

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

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, value: int):
        self._result = value

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
        We suppose the command is consist of command-descriptor,in-data or out-data.
        Build the command in different OS:
          1. The Linux define a fixed-length ctypes.structure;
             * the command is always 72-bytes;
             * the in-data or out-data in command should be included in command-descriptor as a memory address.
          2. The Windows May define a bariable-length ctypes.structure. So The function will:
            * The function will determine the command type with req_id;
            * the in-data or out-data in command should follow the command-descriptor OR
              should be included in command-descriptor as a memory address(Not enabled for now);
            * For data-in command, the length could be in the command descriptor(like 
              StorageQueryWithoutBuffer.StorageProtocolSpecificData.ProtocolDataLength), and this function will init a 0x00 data buffer;
            * For data-out command, the length could be in the command descriptor, and this function will init a 0x00 data buffer and 
              then set the data buffer with self.__data_buffer. You must call init_data_buffer() before do build_command() when send 
              data-out command.

        :param kwargs: the parameters to build command

        :return: the built command
        """
        ## init command_data_length to zero before build command
        self.__command_data_length = 0
        ##
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
                # allocate memory to use if need
                if data_len > 0:
                    # For an IOCTL_STORAGE_QUERY_PROPERTY that uses a STORAGE_PROPERTY_ID of StorageAdapterProtocolSpecificProperty, 
                    # and whose STORAGE_PROTOCOL_SPECIFIC_DATA or STORAGE_PROTOCOL_SPECIFIC_DATA_EXT structure is set to 
                    # ProtocolType=ProtocolTypeNvme and DataType=NVMeDataTypeLogPage, set the ProtocolDataLength member of that same 
                    # structure to a minimum value of 512 (bytes).
                    if (self._cdb.protocol_specific.DataType == win_nvme_command.StorageProtocolNVMeDataType.NVMeDataTypeLogPage.value
                    and self._cdb.query.PropertyId == win_nvme_command.StoragePropertyID.StorageAdapterProtocolSpecificProperty.value
                    and self._cdb.protocol_specific.ProtocolType == win_nvme_command.StroageProtocolType.ProtocolTypeNvme.value 
                    and data_len < 512):
                        raise BuildNVMeCommandError("ProtocolDataLength shoule be a minimum value of 512 (bytes)")
                    # Callers could use a STORAGE_PROPERTY_ID of StorageAdapterProtocolSpecificProperty, and whose STORAGE_PROTOCOL_SPECIFIC_DATA 
                    # or STORAGE_PROTOCOL_SPECIFIC_DATA_EXT structure is set to ProtocolDataRequestValue=VENDOR_SPECIFIC_LOG_PAGE_IDENTIFIER to 
                    # request 512 byte chunks of vendor specific data.
                    if (self._cdb.protocol_specific.DataType in (win_nvme_command.StorageProtocolNVMeDataType.NVMeDataTypeLogPage.value,
                                                                win_nvme_command.StorageProtocolNVMeDataType.NVMeDataTypeFeature.value,)
                    and (0xBF < self._cdb.protocol_specific.ProtocolDataRequestValue < 0x100)
                    and data_len % 512 != 0):
                        raise BuildNVMeCommandError("Need request 512 byte chunks of vendor specific data")
                    ## Get the StorageQueryWithBuffer with data_len
                    _cdb = self.marshall_cdb(kwargs, win_nvme_command.sizeof(win_nvme_command.StorageQueryWithoutBuffer)+data_len)
                    self._cdb = win_nvme_command.GetStorageQueryWithBuffer(data_len).from_buffer(_cdb)
                    # for delay check
                    self.__command_data_length = data_len
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
                    _cdb = self.marshall_cdb(kwargs, win_nvme_command.sizeof(win_nvme_command.STORAGE_PROTOCOL_COMMAND)+data_len)
                    self._cdb = win_nvme_command.GetStorageProtocolCommandWithBuffer(data_len).from_buffer(_cdb)
            # set feature request, data out command
            elif self._req_id == win_nvme_command.IOCTLRequest.IOCTL_STORAGE_SET_PROPERTY.value:
                if not self._cdb_bits:
                    # kwargs["PropertyId"]
                    # kwargs["QueryType"]
                    kwargs["ProtocolType"] = win_nvme_command.StroageProtocolType.ProtocolTypeNvme.value
                    if kwargs["DataType"] >= win_nvme_command.StorageProtocolNVMeDataType.UnusedMaxValue.value:
                        raise BuildNVMeCommandError("DataType should be less than %d" % win_nvme_command.StorageProtocolNVMeDataType.UnusedMaxValue.value)
                # This will get the data length in StorageQueryWithBuffer.StorageProtocolSpecificData.ProtocolDataLength
                _cdb = self.marshall_cdb(kwargs, sizeof(win_nvme_command.IOCTL_STORAGE_SET_PROPERTY))
                self._cdb = win_nvme_command.IOCTL_STORAGE_SET_PROPERTY.from_buffer(_cdb)
                self.__command_data_length = self._cdb.protocolData.ProtocolDataLength
                # allocate memory to use if need
                if self.__command_data_length > 0:
                    ## Get the StorageQueryWithBuffer with data_len
                    _cdb = self.marshall_cdb(kwargs, sizeof(win_nvme_command.StorageQueryWithoutBuffer)+self.__command_data_length)
                    # set data buffer
                    if self.__data_buffer:
                        _cdb[sizeof(win_nvme_command.IOCTL_STORAGE_SET_PROPERTY):self._cdb.protocolData.ProtocolDataOffset+self.__command_data_length] = bytes(self.__data_buffer.data_buffer)[0:self.__command_data_length]
                    else:
                        raise BuildNVMeCommandError("Building data-out command, but no invalid data in data buffer")
                    ##
                    self._cdb = win_nvme_command.GetIOCTLStorageSetPropertyWithBuffer(self.__command_data_length).from_buffer(_cdb)
                    #
                    if self._cdb.protocolData.ProtocolDataOffset == 0:
                        self._cdb.protocolData.ProtocolDataOffset = sizeof(win_nvme_command.IOCTL_STORAGE_SET_PROPERTY)
            elif self._req_id == win_nvme_command.IOCTLRequest.IOCTL_SCSI_MINIPORT.value:
                ## first check the srbIoCtrl->ControlCode
                # max_size = get_check_dict_maxsize(self._cdb_bitmap)  # obsoleted
                max_size = 0
                _cdb_ba = self.marshall_cdb(kwargs, 256) # give an enough buffer to set cdb
                _cdb = win_nvme_command.SRB_IO_CONTROL.from_buffer(_cdb_ba[0:win_nvme_command.SRB_IO_CONTROL_LEN])
                if _cdb.Length > 0:
                    max_size = _cdb.Length + win_nvme_command.SRB_IO_CONTROL_LEN
                if _cdb.ControlCode == win_nvme_command.IOCTL_SCSI_MINIPORT_FIRMWARE:
                    _cdb = win_nvme_command.SCSI_MINIPORT_FIRMWARE_HEADER.from_buffer(_cdb_ba[0:sizeof(win_nvme_command.SCSI_MINIPORT_FIRMWARE_HEADER)])
                    if _cdb.firmwareRequest.DataBufferLength > 0:
                        max_size = _cdb.firmwareRequest.DataBufferLength + sizeof(win_nvme_command.SCSI_MINIPORT_FIRMWARE_HEADER)
                    if _cdb.firmwareRequest.Function == win_nvme_command.FIRMWARE_FUNCTION.DOWNLOAD.value:
                        _cdb = win_nvme_command.SCSI_MINIPORT_FIRMWARE_DOWNLOAD_HEADER.from_buffer(_cdb_ba[0:sizeof(win_nvme_command.SCSI_MINIPORT_FIRMWARE_DOWNLOAD_HEADER)])
                        if _cdb.firmwareDownload.BufferSize > 0:
                            max_size = _cdb.firmwareDownload.BufferSize + sizeof(win_nvme_command.SCSI_MINIPORT_FIRMWARE_DOWNLOAD_HEADER)
                        self.__command_data_length = max_size - sizeof(win_nvme_command.SCSI_MINIPORT_FIRMWARE_DOWNLOAD_HEADER)
                        if max_size == 0:
                            raise BuildNVMeCommandError("Data Buffer Length Not Set")
                        elif self.__command_data_length > 0:
                            _cdb_ba = self.marshall_cdb(kwargs, max_size)
                            # set data
                            if self.__data_buffer:
                                # Set data to command data
                                _cdb_ba[sizeof(win_nvme_command.SCSI_MINIPORT_FIRMWARE_DOWNLOAD_HEADER):sizeof(win_nvme_command.SCSI_MINIPORT_FIRMWARE_DOWNLOAD_HEADER)+self.__command_data_length] = bytes(self.__data_buffer.data_buffer)[0:self.__command_data_length]
                            else:
                                raise BuildNVMeCommandError("Building data-out command, but no invalid data in data buffer")
                            #
                            self._cdb = win_nvme_command.GetScsiMiniportFirmwareDownload(self.__command_data_length).from_buffer(_cdb_ba)
                        else:
                            raise BuildNVMeCommandError("Data Buffer Length Error")
                        # check parameters
                        if self._cdb.firmwareDownload.Version == 0:
                            self._cdb.firmwareDownload.Version = 1
                        if self._cdb.firmwareDownload.Size == 0:
                            self._cdb.firmwareDownload.Size = sizeof(win_nvme_command.STORAGE_FIRMWARE_DOWNLOAD)
                        if self._cdb.firmwareDownload.BufferSize == 0:
                            self._cdb.firmwareDownload.BufferSize = self.__command_data_length
                    elif _cdb.firmwareRequest.Function == win_nvme_command.FIRMWARE_FUNCTION.ACTIVATE.value:
                        self._cdb = win_nvme_command.SCSI_MINIPORT_FIRMWARE_ACTIVE.from_buffer(_cdb_ba[0:sizeof(win_nvme_command.SCSI_MINIPORT_FIRMWARE_ACTIVE)])
                        # check parameters
                        if self._cdb.firmwareActivate.Version == 0:
                            self._cdb.firmwareActivate.Version = 1
                        if self._cdb.firmwareActivate.Size == 0:
                            self._cdb.firmwareActivate.Size = sizeof(win_nvme_command.STORAGE_FIRMWARE_ACTIVATE)
                    else:
                        raise BuildNVMeCommandError("Unknown Or Non-support Firmware Request Function(%#X)" % _cdb.firmwareRequest.Function)
                    # check invalid parameters
                    if self._cdb.srbIoCtrl.Timeout == 0:
                        self._cdb.srbIoCtrl.Timeout = win_nvme_command.SCSI_FIRMWARE_TIMEOUT
                    if bytes(self._cdb.srbIoCtrl.Signature) == b'\x00\x00\x00\x00\x00\x00\x00\x00':
                        for k,v in enumerate(win_nvme_command.IOCTL_MINIPORT_SIGNATURE_FIRMWARE.encode()):
                            self._cdb.srbIoCtrl.Signature[k] = v
                    if self._cdb.firmwareRequest.Size == 0:
                        self._cdb.firmwareRequest.Size = sizeof(win_nvme_command.FIRMWARE_REQUEST_BLOCK)
                    if self._cdb.firmwareRequest.Version == 0:
                        self._cdb.firmwareRequest.Version = win_nvme_command.FIRMWARE_REQUEST_BLOCK_STRUCTURE_VERSION
                    if self._cdb.firmwareRequest.Flags == 0:
                        self._cdb.firmwareRequest.Flags = win_nvme_command.FIRMWARE_REQUEST_FLAG_CONTROLLER
                    if self._cdb.firmwareRequest.DataBufferOffset == 0:
                        self._cdb.firmwareRequest.DataBufferOffset = sizeof(win_nvme_command.SCSI_MINIPORT_FIRMWARE_HEADER)
                    if self._cdb.firmwareRequest.DataBufferLength == 0:
                        self._cdb.firmwareRequest.DataBufferLength = sizeof(self._cdb) - self._cdb.firmwareRequest.DataBufferOffset
                ##
                # check and fix the SrbIoCtrl structures
                if self._cdb.srbIoCtrl.HeaderLength == 0:
                    self._cdb.srbIoCtrl.HeaderLength = win_nvme_command.SRB_IO_CONTROL_LEN
                if self._cdb.srbIoCtrl.Length == 0:
                    self._cdb.srbIoCtrl.Length = sizeof(self._cdb) - win_nvme_command.SRB_IO_CONTROL_LEN
            elif self._req_id == win_nvme_command.IOCTLRequest.IOCTL_STORAGE_FIRMWARE_ACTIVATE.value:
                # TODO
                raise BuildNVMeCommandError("Failed to build command, Do Not Support Request %#x" % self._req_id)
            elif self._req_id == win_nvme_command.IOCTLRequest.IOCTL_STORAGE_FIRMWARE_DOWNLOAD.value:
                # TODO
                raise BuildNVMeCommandError("Failed to build command, Do Not Support Request %#x" % self._req_id)
            elif self._req_id == win_nvme_command.IOCTLRequest.IOCTL_SCSI_PASS_THROUG.value:
                # TODO
                raise BuildNVMeCommandError("Failed to build command, Do Not Support Request %#x" % self._req_id)
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
        Compeletion Queue DWORD 0
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
        SCT,SC =  0,0
        hint = ''
        if self._req_id == win_nvme_command.IOCTLRequest.IOCTL_STORAGE_QUERY_PROPERTY.value:
            if self.cdb_struc:
                temp = win_nvme_command.STORAGE_PROTOCOL_DATA_DESCRIPTOR.from_buffer_copy(bytearray(self.cdb_struc)) # cdb_struc
                # Validate the returned data.
                if (temp.Version != win_nvme_command.sizeof(win_nvme_command.STORAGE_PROTOCOL_DATA_DESCRIPTOR) 
                 or temp.Size != win_nvme_command.sizeof(win_nvme_command.STORAGE_PROTOCOL_DATA_DESCRIPTOR)):
                    SCT,SC = 16,1
                    hint = 'DeviceNVMeQueryProtocolData: data descriptor header not valid.'
                if self.__command_data_length > 0 and (temp.protocol_specific.ProtocolDataOffset < win_nvme_command.sizeof(win_nvme_command.StorageProtocolSpecificData) or temp.protocol_specific.ProtocolDataLength < self.__command_data_length):
                    SCT,SC = 16,2
                    hint = 'DeviceNVMeQueryProtocolData: ProtocolData Offset/Length not valid.'
        elif self._req_id == win_nvme_command.IOCTLRequest.IOCTL_STORAGE_PROTOCOL_COMMAND.value:
            if self._cdb.ReturnStatus not in (StorageProtocolStatus.STORAGE_PROTOCOL_STATUS_SUCCESS.value, StorageProtocolStatus.STORAGE_PROTOCOL_STATUS_PENDING.value):
                SCT,SC = 16,3
                hint = "Unkown Storage Protocol Status"
                status = enum_find(StorageProtocolStatus, value=self._cdb.ReturnStatus)
                if status:
                    hint = status.name
        elif self._req_id == win_nvme_command.IOCTLRequest.IOCTL_SCSI_MINIPORT.value:
            if self._cdb and self._cdb.firmwareRequest.Function == win_nvme_command.FIRMWARE_FUNCTION.DOWNLOAD.value:
                SCT,SC = 16,4
                if self._cdb.srbIoCtrl.ReturnCode != win_nvme_command.FIRMWARE_STATUS.FIRMWARE_STATUS_SUCCESS.value:
                    hint = "FirmwareUpgrade - firmware download failed. srbControl->ReturnCode %d." % self._cdb.srbIoCtrl.ReturnCode
            elif self._cdb and self._cdb.firmwareRequest.Function == win_nvme_command.FIRMWARE_FUNCTION.ACTIVATE.value:
                if self._cdb.srbIoCtrl.ReturnCode == win_nvme_command.FIRMWARE_STATUS.FIRMWARE_STATUS_SUCCESS.value:
                    hint = "FirmwareUpgrade - firmware activate succeeded."
                elif self._cdb.srbIoCtrl.ReturnCode == win_nvme_command.FIRMWARE_STATUS.FIRMWARE_STATUS_POWER_CYCLE_REQUIRED.value:
                    hint = "FirmwareUpgrade - firmware activate succeeded. PLEASE REBOOT COMPUTER."
                else:
                    SCT,SC = 16,5
                    status = enum_find(win_nvme_command.FIRMWARE_STATUS, value=self._cdb.srbIoCtrl.ReturnCode)
                    if status:
                        hint = "FirmwareUpgrade - firmware activate error. srbControl->ReturnCode %d(%s)." % (status.value, status.name)
                    else:
                        hint = "FirmwareUpgrade - firmware activate error. srbControl->ReturnCode %d(Unkonwn Error)." % self._cdb.srbIoCtrl.ReturnCode
        return SC,SCT,hint

    def check_return_status(self, success_hint=False, fail_hint=True, raise_if_fail=False):
        """
        SCT    Status Code Type
            0-7     For Common: Completion Queue Entry Status Field Definition
            16      For Windows: Windows IOCTL status check error
            17      For Windows: Windows IOCTL Return Value Error
        """
        ## 
        # Step 1. If windows, check the return code.
        if os_type == 'Windows':
            # Step 1.1  check the result form ioctl
            if self.result == 0:
                import ctypes
                SCT,SC = 17,1
                hint = "Windows IOCTL Return Value Error: %s" % ctypes.get_last_error()
                if fail_hint:
                    print (hint)
                if raise_if_fail:
                    raise ctypes.WinError(ctypes.get_last_error())
                return SC,SCT
            # step 1.2  Check the return status from ioctl
            SC,SCT,hint = self._win_execute_check()
            if SCT != 0 or SC != 0:
                if fail_hint:
                    print (hint)
                if raise_if_fail:
                    raise CommandReturnStatusError("Windows IOCTL Check Error: %s" % hint if hint else "Unkonwn Error")
                return SC,SCT
            elif hint and success_hint:
                print (hint)
        # Step 2. Check SQ entry, sometimes do not work for windows 
        SC = (self.cq_status & 0xFF)
        SCT = ((self.cq_status >> 8) & 0x07)
        if SCT != 0 or SC != 0:
            CRD = ((self.cq_status >> 11) & 0x03)
            More = (self.cq_status >> 13 & 0x01)
            DNR = (self.cq_status >> 14 & 0x01)
            _hint = "NVMe Return Status Check Error: Status Code Type(%#x), Status Code(%#x)" % (SCT, SC)
            if fail_hint:
                print ("Command failed, and details bellow.")
                format_string = "%-15s%-20s%-8s%s"
                print (format_string % ("Status Code", "Status Code Type", "More", "Do Not Retry"))
                print (format_string % (SC, SCT, More, DNR))
                print ('')
                print (StatusCodeDescription.get((SCT,SC)))
                print ('')
                # Step 1.2 check Command Specific Status Value. It may not work,
                # just an ideas
                if os_type == 'Linux':
                    if fail_hint and self.cq_cmd_spec in self._cmd_spec_fail:
                        print (self._cmd_spec_fail.get(self.cq_cmd_spec))
                        print ('')
                        _hint = "%s, Command Specific Status Value: %#x" % (_hint, self.cq_cmd_spec)
            if raise_if_fail:
                raise CommandReturnStatusError(_hint)
            return SC,SCT
        # Should always SC,SCT = 0,0 here
        if success_hint:
            print ("Command Success")
            print ('')
        ##
        return SC,SCT
