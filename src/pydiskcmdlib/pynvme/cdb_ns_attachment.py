# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from typing import List
from pydiskcmdlib import os_type
from pydiskcmdlib.pynvme.data_buffer import encode_data_buffer
from pydiskcmdlib.pynvme.nvme_command import NVMeCommand,AdminCommandOpcode,CommandTimeout
from pydiskcmdlib.pynvme import linux_nvme_command,win_nvme_command
#####
CmdOPCode = AdminCommandOpcode.NamespaceAttachment.value
#####
class NSAttachment(NVMeCommand):
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
    elif os_type == "Windows":
        _req_id = win_nvme_command.IOCTLRequest.RESERVED_REQUEST_ID.value
        _cdb_bits = {}

    def __init__(self,
                 nsid,    # Namespace ID
                 sel,     # CDW10: Select (SEL):  This field selects the type of attachment to perform.
                 ctrl_id_list: List,
                 timeout=CommandTimeout.admin.value,
                 ):
        '''
        Some ways to set Data buffer, the priority is:
        1. Set the data_buffer/metadata_buffer, DataBuffer of the target data;
        2. If set the data_out/metadata_out, data_length/metadata_length is need;
        3. Set the data_length/metadata_length, then a 0 based buffer is created
        '''
        super(NSAttachment, self).__init__()
        if os_type == "Linux":
            ## init data buffer
            id_num = len(ctrl_id_list)
            #
            data_dict = {"id_number": id_num,}
            check_dict = {"id_number": (0xFFFF, 0),}
            for i in range(id_num):
                data_dict["id_%s" % i] = ctrl_id_list[i]
                check_dict["id_%s" % i] = (0xFFFF, 2+i*2)
            #
            data_buffer = self.init_data_buffer(data_length=4096)
            encode_data_buffer(data_dict, check_dict, data_buffer.get_data_buffer())
            ##
            self.build_command(opcode=CmdOPCode,
                               nsid=nsid,
                               addr=data_buffer.addr,
                               data_len=data_buffer.data_length,
                               sel=sel,
                               timeout_ms=timeout)
        elif os_type == "Windows":
            self.build_command()
