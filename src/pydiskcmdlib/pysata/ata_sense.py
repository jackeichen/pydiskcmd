# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import platform
from pydiskcmdlib.utils.enum import Enum
from pydiskcmdlib.utils.converter import scsi_int_to_ba
from pydiskcmdlib.exceptions import ExecuteCmdErr,SenseDataCheckErr
from pydiskcmdlib import os_type
##
from pyscsi.pyscsi.scsi_sense import (
    SCSICheckCondition,
    decode_bits,
    SENSE_FORMAT_CURRENT_DESCRIPTOR,
    SENSE_FORMAT_CURRENT_FIXED,
)


def GetLinuxKernelVer():
    # it usually like '5.14.0-430.el9.x86_64'
    """
    Retrieve the major and minor version numbers of the Linux kernel.
    
    This function extracts the major and minor version numbers from the kernel release string.
    The release string typically follows the format 'x.y.z-...', where 'x' is the major version
    and 'y' is the minor version.
    
    Returns:
        tuple: A tuple containing the major and minor version numbers as integers, or None if
               the system is not Linux or the version string does not contain enough parts.
    """
    if os_type == 'Linux':
        kernel_ver = platform.release().split(".")
        if len(kernel_ver) > 2:
            return int(kernel_ver[0]), int(kernel_ver[1])


class ATACheckReturnDescriptorCondition(SCSICheckCondition):
    _extend_ata_status_return_descriptor=         {'descriptor_code': [0xff, 0],
                                                   'additional_descriptor_length': [0xff, 1],
                                                   'extend': [0x01, 2],
                                                   'error': [0xff, 3],
                                                   'sector_count_rsvd': [0xff, 4], # Sector Count (8:15)
                                                   'sector_count': [0xff, 5],      # Sector Count (0:7)
                                                   'lba_low_rsvd': [0xff, 6],      # LBA (31:24)
                                                   'lba_low': [0xff, 7],           # LBA (7:0)
                                                   'lba_mid_rsvd': [0xff, 8],      # LBA (39:32)
                                                   'lba_mid': [0xff, 9],           # LBA (15:8)
                                                   'lba_high_rsvd': [0xff, 10],    # LBA (47:40)
                                                   'lba_high': [0xff, 11],         # LBA (23:16)
                                                   'device': [0xff, 12],
                                                   'status': [0xff, 13], }        

    _fixed_format_sense_information = {'error': [0xff, 0],
                                       'status': [0xff, 1],
                                       'device': [0xff, 2],
                                       'sector_count': [0xff, 3],
                                       }
    _fixed_format_sense_cmd_spec = {'log_index': [0x0f, 0],
                                    'rsvd': [0x10, 0],
                                    'lba_upper_nonzero': [0x20, 0],
                                    'count_upper_nonzero': [0x40, 0],
                                    'extend': [0x80, 0],
                                    'lba_low': [0xff, 1],
                                    'lba_mid': [0xff, 2],
                                    'lba_high': [0xff, 3],
                                    }

    def __init__(self,
                 sense,
                 print_data=False):
        super(ATACheckReturnDescriptorCondition, self).__init__(sense, print_data=print_data)
        ##
        if self.data:  # sense data is valid
            if self.asc == 0 and self.ascq == 29: ## ATA PASS THROUGH INFORMATION AVAILABLE, success to handle
                if self.response_code == SENSE_FORMAT_CURRENT_DESCRIPTOR:
                    self.data['ata_pass_thr_return_descriptor'] = self.unmarshall_extend_ata_status_return_descriptor_data(sense[8:])
                elif self.response_code == SENSE_FORMAT_CURRENT_FIXED:
                    self.data['ata_pass_thr_fixed_format'] = self.unmarshall_ata_fixed_format_sense_data(scsi_int_to_ba(self.data["information"]), 
                                                                                                         scsi_int_to_ba(self.data["command_specific_information"]))
                else:
                    raise SenseDataCheckErr("Not support decode response code %#x" % self.response_code)
            # it is from https://github.com/torvalds/linux/blob/v5.15/drivers/ata/libata-scsi.c/#L854-#L937
            # try to decode the fixed format sense data
            elif os_type == "Linux" and self.response_code == SENSE_FORMAT_CURRENT_FIXED:
                kernel_ver = GetLinuxKernelVer()
                if kernel_ver and kernel_ver < (6, 11):
                    self.data['ata_pass_thr_fixed_format'] = self.unmarshall_ata_fixed_format_sense_data(sense[8:12],
                                                                                                         sense[16:20])
                else:
                    # TODO: check the sense data in Linux kernel 6.11 or newer
                    # do nothing for now
                    pass
            elif self.response_code == SENSE_FORMAT_CURRENT_DESCRIPTOR and os_type == "Windows": # TODO
                self.data['ata_pass_thr_return_descriptor'] = self.unmarshall_extend_ata_status_return_descriptor_data(sense[8:])
            else:
                raise ExecuteCmdErr(str(SCSICheckCondition.__str__(self)))
            # check the ATA sense data
            if self.response_code == SENSE_FORMAT_CURRENT_DESCRIPTOR:
                if self.ata_pass_thr_return_descriptor["descriptor_code"] != 0x09:
                    raise SenseDataCheckErr("ATA Sense Data check error, descriptor_code should be 0x09 but get %#X" % self.ata_pass_thr_return_descriptor["descriptor_code"])
                if self.ata_pass_thr_return_descriptor["additional_descriptor_length"] != 0x0C:
                    raise SenseDataCheckErr("ATA Sense Data check error, additional_descriptor_length should be 0x0C but get %#X" % self.ata_pass_thr_return_descriptor["additional_descriptor_length"])

    def _print_data(self, data: dict, indent: int) -> None:
        for k, v in data.items():
            if isinstance(v, dict):
                print("%s%s :" % (" " * indent, k))
                self._print_data(v, indent+4)
            else:
                print("%s%s : 0x%02X" % (" " * indent, k, v))

    def print_data(self) -> None:
        self._print_data(self.data, 0)

    @property
    def ata_pass_thr_return_descriptor(self):
        return self.data.get("ata_pass_thr_return_descriptor")

    @property
    def ata_pass_thr_fixed_format(self):
        return self.data.get("ata_pass_thr_fixed_format")

    @staticmethod
    def unmarshall_extend_ata_status_return_descriptor_data(data):
        result = {}
        decode_bits(data,
                    ATACheckReturnDescriptorCondition._extend_ata_status_return_descriptor,
                    result)
        return result

    @staticmethod
    def unmarshall_ata_fixed_format_sense_data(info, cmd_spec) -> dict:
        result = {}
        decode_bits(info,
                    ATACheckReturnDescriptorCondition._fixed_format_sense_information,
                    result)
        decode_bits(cmd_spec,
                    ATACheckReturnDescriptorCondition._fixed_format_sense_cmd_spec,
                    result)
        return result


__all_ = ['NormalOutputs', 'ErrorOutputs', 'OPCodeDict', 'ErrType',
          'SenseData',]

NormalOutputs = {"CheckPowerModeNormalOutput": {},
                }


ErrorOutputs = {"UnsupportedCommandError": {"status_bit_map": {"ERROR_bit": 0x01, "SENSE_DATA_AVAILABLE_bit": 0x02, "Transport_Dependent": 0xC0, "NA": 0x3C},
                                            "device_bit_map": {"Reserved": 0x0F, "NA": 0xF0},
                                            "error_bit_map":  {"NA": 0xFB, "ABORT_bit": 0x04},
                                            },
                "CheckPowerModeAbortError": {},
                }

OPCodeDict = {0xE5:(("CheckPowerModeNormalOutput", "CheckPowerModeAbortError"),),
              0x78: (("GETNATIVEMAXADDRESSEXTNormalOutput", "GenericAbortwoICRCError"), ("GenericExtendedNormalOutput", "SETACCESSIBLEMAXADDRESSEXTError"), ("GenericExtendedNormalOutput", "GenericAbortwoICRCError")),
             }


ErrType = Enum(COMMAND_COMPLETION_TIME_OUT=1, ILLEGAL_LENGTH_INDICATOR=2, Obsolete=3, Abort=4, ID_NOT_FOUND=5, UNCORRECTABLE_ERROR=6, INTERFACE_CRC=7, END_OF_MEDIA=8, Sense_Key=9)


class BitMapMethodBase(object):
    def __init__(self, data, bit_map):
        self._data = data
        self._bit_map = bit_map
        self.__data_struc = []
    
    def __str__(self):
        return self.__class__.__name__ 
    
    @property
    def value(self):
        return self._data
    
    @property
    def value2int(self):
        return int.from_bytes(self._data, byteorder='big', signed=False)
    
    @property
    def bit_map(self):
        return self._bit_map
    
    def append_data_struc(self, element):
        if element not in self.__data_struc:
            self.__data_struc.append(element)
    
    def show_data_struc(self):
        for i in self.__data_struc:
            print (i)

class BitMapMethod1(BitMapMethodBase):
    def __init__(self, data, bit_map):
        super(BitMapMethod1, self).__init__(data, bit_map)
        ##
        for k,v in self.bit_map.items():
            if k == "NA" or k == "Reserved":
                continue
            locate,child = v
            offset = locate[0]
            end = offset + locate[1]
            ret = data[offset:end]
            if child:
                func = child(ret) # pre execute and get the name
                ret = "%s(%s)" % (func, ret)
                func = None
            exec("self.%s=%s" % (k, ret))
            self.append_data_struc(k)

class BitMapMethod2(BitMapMethodBase):
    def __init__(self, data, bit_map):
        super(BitMapMethod2, self).__init__(data, bit_map)
        ##
        self.handle_bit_map()
    
    def handle_bit_map(self):
        for k,v in self.bit_map.items():
            if k == "NA" or k == "Reserved":
                continue
            for i in range(8):
                if (v >> i) & (0x01):
                    break
            ret = (self.value2int & v) >> i
            exec("self.%s=%s" % (k, ret))
            self.append_data_struc(k)
    
    def update_bit_map(self, bit_map):
        self.bit_map.update(bit_map)
        self.handle_bit_map()


class DescriptorExtendByte(BitMapMethod2):
    __extendByte_bit_map = {"Extend": 0x01, "Reserved": 0xFE}

    def __init__(self, data):
        super(DescriptorExtendByte, self).__init__(data, self.__extendByte_bit_map)


class DescriptorError(BitMapMethod2):
    __error_bit_map = {"NA": 0xFF}
    
    def __init__(self, data):
        super(DescriptorError, self).__init__(data, self.__error_bit_map)


class DescriptorSectorCount(BitMapMethod2):
    __count_bit_map = {"NA": 0xFFFF}
    
    def __init__(self, data):
        super(DescriptorSectorCount, self).__init__(data, self.__count_bit_map)
        
        
class DescriptorLBA(BitMapMethod2):
    __lba_bit_map = {"NA": 0xFFFFFFFFFFFF}
    
    def __init__(self, data):
        super(DescriptorLBA, self).__init__(data, self.__lba_bit_map)


class DescriptorDevice(BitMapMethod2):
    __device_bit_map = {"NA": 0xFF}
    
    def __init__(self, data):
        super(DescriptorDevice, self).__init__(data, self.__device_bit_map)


class DescriptorStatus(BitMapMethod2):
    __status_bit_map = {"ERROR_bit": 0x01, "SENSE_DATA_AVAILABLE_bit": 0x02, "NA": 0xFC}
    
    def __init__(self, data):
        super(DescriptorStatus, self).__init__(data, self.__status_bit_map)


class ATAStatusReturnDescriptor(BitMapMethod1):
    __ATA_Status_Return_Descriptor_dict = {"DESCRIPTORCODE":[(0, 1), None], 
                                           "AdditionalDescriptorLength":[(1, 1), None], 
                                           "ExtendByte":[(2, 1), DescriptorExtendByte], 
                                           "Error":[(3, 1), DescriptorError],
                                           "SectorCount":[(4, 2), DescriptorSectorCount],
                                           "LBA":[(6, 6), DescriptorLBA],
                                           "Device":[(12, 1), DescriptorDevice],
                                           "Status":[(13, 1), DescriptorStatus]}
    
    def __init__(self, data):
        super(ATAStatusReturnDescriptor, self).__init__(data, self.__ATA_Status_Return_Descriptor_dict)


class SenseData(BitMapMethod1):
    __Sense_Data_dict = {"ATAStatusReturnDescriptor": [(8, 14), ATAStatusReturnDescriptor]}
    
    def __init__(self, data):
        super(SenseData, self).__init__(data, self.__Sense_Data_dict)
    
    def process_ATAStatusReturnDescriptor(self, opcode, features=0):
        '''
        features = N/A or features = 0
        
        function not verify! do not use now.
        '''
        key = OPCodeDict[opcode]
        if self.ATAStatusReturnDescriptor.Status.ERROR_bit:  # error occur
            bit_map_new = ErrorOutputs[key][features]
        else:
            bit_map_new = NormalOutputs[key][features]
        ## handle here
        if "status_bit_map" in bit_map_new:
            self.ATAStatusReturnDescriptor.Status.update_bit_map(bit_map_new["status_bit_map"])
        if "device_bit_map" in bit_map_new:
            self.ATAStatusReturnDescriptor.Device.update_bit_map(bit_map_new["device_bit_map"])
        if "lba_bit_map" in bit_map_new:
            self.ATAStatusReturnDescriptor.LBA.update_bit_map(bit_map_new["lba_bit_map"])
        if "count_bit_map" in bit_map_new:
            self.ATAStatusReturnDescriptor.SectorCount.update_bit_map(bit_map_new["count_bit_map"])
        if "error_bit_map" in bit_map_new:
            self.ATAStatusReturnDescriptor.Error.update_bit_map(bit_map_new["error_bit_map"])
    
    def simple_check_error(self):
        if self.ATAStatusReturnDescriptor.Status.ERROR_bit:
            return True
        return False
    
    def check_error(self, error_type):
        '''
        error_type: 'AbortError', 
        
        function not verify! do not use now.
        '''
        if not isinstance(error_type, ErrType):
            raise RuntimeError("Error type error!")
        if self.ATAStatusReturnDescriptor.Status.ERROR_bit:
            try:
                if error_type == ErrType.Abort:
                    if self.ATAStatusReturnDescriptor.Error.ABORT_bit:
                        return True
                elif error_type == ErrType.Obsolete:
                    if self.ATAStatusReturnDescriptor.Error.Obsolete:
                        return True
                elif error_type == ErrType.ID_NOT_FOUND:
                    if self.ATAStatusReturnDescriptor.Error.ID_NOT_FOUND_bit:
                        return True
                else:
                    raise RuntimeError("Error type error!")
            except NameError:
                pass
        return False
