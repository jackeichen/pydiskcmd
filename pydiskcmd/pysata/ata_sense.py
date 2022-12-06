# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmd.utils.enum import Enum
from pydiskcmd.exceptions import DeviceTypeError,ExecuteCmdErr
from pydiskcmd.system.os_tool import os_type
##
from pyscsi.pyscsi.scsi_sense import SCSICheckCondition,decode_bits,SENSE_FORMAT_CURRENT_DESCRIPTOR


class ATACheckReturnDescriptorCondition(SCSICheckCondition):
    _extend_ata_status_return_descriptor=         {'descriptor_code': [0xff, 0],
                                                   'additional_descriptor_length': [0xff, 1],
                                                   'extend': [0x01, 2],
                                                   'error': [0xff, 3],
                                                   'sector_count_rsvd': [0xff, 4],
                                                   'sector_count': [0xff, 5],
                                                   'lba_low_rsvd': [0xff, 6],
                                                   'lba_low': [0xff, 7],
                                                   'lba_mid_rsvd': [0xff, 8],
                                                   'lba_mid': [0xff, 9],
                                                   'lba_high_rsvd': [0xff, 10],
                                                   'lba_high': [0xff, 11],
                                                   'device': [0xff, 12],
                                                   'status': [0xff, 13], }        

    def __init__(self,
                 sense,
                 print_data=False):
        super(ATACheckReturnDescriptorCondition, self).__init__(sense, print_data=print_data)
        ##
        if self.asc == 0 and self.ascq == 29: ## ATA PASS THROUGH INFORMATION AVAILABLE, success to handle
            self.data['ata_pass_thr_return_descriptor'] = self.unmarshall_extend_ata_status_return_descriptor_data(sense[8:])
        elif self.response_code == SENSE_FORMAT_CURRENT_DESCRIPTOR and os_type == "Windows":
            self.data['ata_pass_thr_return_descriptor'] = self.unmarshall_extend_ata_status_return_descriptor_data(sense[8:])
        else:
            hint = str(SCSICheckCondition.__str__(self))
            raise ExecuteCmdErr(hint)

    @property
    def ata_pass_thr_return_descriptor(self):
        return self.data.get("ata_pass_thr_return_descriptor")

    @staticmethod
    def unmarshall_extend_ata_status_return_descriptor_data(data):
        result = {}
        decode_bits(data,
                    ATACheckReturnDescriptorCondition._extend_ata_status_return_descriptor,
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
