# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmdlib import os_type
from pydiskcmdlib.pynvme.data_buffer import encode_data_buffer
from pydiskcmdlib.pynvme.nvme_command import NVMeCommand,AdminCommandOpcode,CommandTimeout
from pydiskcmdlib.pynvme import linux_nvme_command,win_nvme_command
#####
CmdOPCode = AdminCommandOpcode.NamespaceManagement.value
#####
class NSManagement(NVMeCommand):
    if os_type == "Linux":
        _req_id = linux_nvme_command.IOCTLRequest.NVME_IOCTL_ADMIN_CMD.value
        _cdb_bits = {"opcode": [0xFF, 0],
                     "flags": [0xFF, 1],
                     "rsvd1": [0xFFFF, 2],
                     "nsid":[0xFFFFFFFF, 4],
                     "cdw2":[0xFFFFFFFF, 8],
                     "cdw3":[0xFFFFFFFF, 12],
                     "metadata":[0xFFFFFFFFFFFFFFFF, 16],
                     "addr":[0xFFFFFFFFFFFFFFFF, 24],
                     "metadata_len":[0xFFFFFFFF, 32],
                     "data_len":[0xFFFFFFFF, 36],
                     #"cdw10":[0xFFFFFFFF, 40],
                     "sel": [0x0F, 40],
                     "cdw11":[0xFFFFFFFF, 44],
                     "cdw12":[0xFFFFFFFF, 48],
                     "cdw13":[0xFFFFFFFF, 52],
                     "cdw14":[0xFFFFFFFF, 56],
                     "cdw15":[0xFFFFFFFF, 60],
                     "timeout_ms":[0xFFFFFFFF, 64],
                     "result":[0xFFFFFFFF, 68],
                     }
        _data_check_dict = {"ns_size": (0xFFFFFFFFFFFFFFFF, 0),
                            "ns_cap": (0xFFFFFFFFFFFFFFFF, 8),
                            "flbas": (0xFF, 26),
                            "dps": (0xFF, 29),
                            "nmic": (0xFF, 30),
                            "anagrp_id": (0xFFFFFFFF, 92),
                            "nvmeset_id": (0xFFFF, 100),
                           }
    elif os_type == "Windows":
        _req_id = win_nvme_command.IOCTLRequest.RESERVED_REQUEST_ID.value
        _cdb_bits = {}
        _data_check_dict = {}

    def __init__(self,
                 nsid,
                 sel,
                 timeout=CommandTimeout.admin.value,
                 **data_dict, # this will used to: Namespace Management – Host Software Specified Fields
                 ):
        '''
        Some ways to set Data buffer, the priority is:
        1. Set the data_buffer/metadata_buffer, DataBuffer of the target data;
        2. If set the data_out/metadata_out, data_length/metadata_length is need;
        3. Set the data_length/metadata_length, then a 0 based buffer is created

        Bellow key name is valid for data_dict:
          ns_size, 
          ns_cap, 
          flbas, 
          dps, 
          nmic, 
          anagrp_id, 
          nvmeset_id, 
          csi=0,
          vendor_spec_data=b''
        '''
        ##
        super(NSManagement, self).__init__()
        if os_type == "Linux":
            ## init data buffer
            data_buffer = self.init_data_buffer(data_length=4096)
            if NSManagement._data_check_dict:
                temp = data_buffer.get_data_buffer()
                encode_data_buffer(data_dict, NSManagement._data_check_dict, temp)
                #
                vendor_spec_data = data_dict.get("vendor_spec_data")
                if vendor_spec_data:
                    cycles = min(len(vendor_spec_data), 3072)
                    for i in range(cycles):
                        temp[1024+i] = vendor_spec_data[i]
            ##
            self.build_command(opcode=CmdOPCode,
                               nsid=nsid,
                               addr=data_buffer.addr,
                               data_len=data_buffer.data_length,
                               sel=sel,
                               timeout_ms=timeout)
        elif os_type == "Windows":
            self.build_command()
        else:
            raise NotImplementedError("%s Not support command %s" % (os_type, self.__class__.__name__))


class NSCreate(NSManagement):
    def __init__(self,
                 **data_dict,
                 ):
        NSManagement.__init__(self, 0, 0, **data_dict)


class NSDelete(NSManagement):
    def __init__(self, nsid):
        NSManagement.__init__(self, nsid, 1)
