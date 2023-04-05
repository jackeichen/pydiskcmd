# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmd.system.os_tool import os_type
from pydiskcmd.exceptions import CommandNotSupport

#####
CmdOPCode = 0x15
#####

if os_type == "Linux":
    from pydiskcmd.pynvme.nvme_command import LinCommand,build_int_by_bitmap,encode_data_buffer,DataBuffer
    ## linux command
    IOCTL_REQ = LinCommand.linux_req.get("NVME_IOCTL_ADMIN_CMD")
    class NSAttachment(LinCommand):
        def __init__(self, ns_id, sel, ctrl_id_list):
            ### build command
            cdw10 = build_int_by_bitmap({"SEL": (0x0F, 0, sel),      # Select (SEL):  This field selects the type of attachment to perform.
                                        })
            ##
            id_num = len(ctrl_id_list)
            # id_num = min(len(ctrl_id_list), self.__ctrl_identify_info[338]+(self.__ctrl_identify_info[339] << 8))
            data_dict = {"id_number": id_num,}
            check_dict = {"id_number": (0xFFFF, 0),}
            for i in range(id_num):
                data_dict["id_%s" % i] = ctrl_id_list[i]
                check_dict["id_%s" % i] = (0xFFFF, 2+i*2)
            #
            d = DataBuffer(4096)
            encode_data_buffer(data_dict, check_dict, d.data_buffer)
            ##   
            super(NSAttachment, self).__init__(IOCTL_REQ)
            self.build_command(opcode=CmdOPCode,
                               nsid=ns_id,
                               data_len=4096,
                               addr=d.addr,
                               cdw10=cdw10,)

elif os_type == "Windows":
    from pydiskcmd.pynvme.nvme_command import WinCommand
    class NSAttachment(WinCommand):
        def __init__(self, *args, **kwargs):
            raise CommandNotSupport("NSAttachment Not Support")

else:
    raise NotImplementedError("%s not support" % os_type)
