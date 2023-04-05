# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmd.system.os_tool import os_type
from pydiskcmd.exceptions import CommandNotSupport

#####
CmdOPCode = 0x0D
#####

if os_type == "Linux":
    from pydiskcmd.pynvme.nvme_command import LinCommand,build_int_by_bitmap,encode_data_buffer,DataBuffer
    ### linux command
    IOCTL_REQ = LinCommand.linux_req.get("NVME_IOCTL_ADMIN_CMD")
    ###
    class NSCreate(LinCommand):
        def __init__(self, 
                     ns_size, 
                     ns_cap, 
                     flbas, 
                     dps, 
                     nmic, 
                     anagrp_id, 
                     nvmeset_id, 
                     csi=0,
                     vendor_spec_data=b''):
            ### build command
            cdw10 = build_int_by_bitmap({"SEL": (0x0F, 0, 0x00),      # Select (SEL): This field selects the type of management operation to perform
                                        })
            # for nvme spec 2.0
            cdw10 = build_int_by_bitmap({"CSI": (0xFF, 3, csi),       # Select (SEL): This field selects the type of management operation to perform
                                        })
            #
            data_dict = {"ns_size": ns_size,
                         "ns_cap": ns_cap,
                         "flbas": flbas,
                         "dps": dps,
                         "nmic": nmic,
                         "anagrp_id": anagrp_id,
                         "nvmeset_id": nvmeset_id,
                        }
            check_dict = {"ns_size": (0xFFFFFFFFFFFFFFFF, 0),
                          "ns_cap": (0xFFFFFFFFFFFFFFFF, 8),
                          "flbas": (0xFF, 26),
                          "dps": (0xFF, 29),
                          "nmic": (0xFF, 30),
                          "anagrp_id": (0xFFFFFFFF, 92),
                          "nvmeset_id": (0xFFFF, 100),
                         }
            #
            d = DataBuffer(4096)
            encode_data_buffer(data_dict, check_dict, d.data_buffer)
            # set vendor_spec_data
            if vendor_spec_data:
                cycles = min(len(vendor_spec_data), 3072)
                for i in range(cycles):
                    d.data_buffer[1024+i] = vendor_spec_data[i]
            ##   
            super(NSCreate, self).__init__(IOCTL_REQ)
            self.build_command(opcode=CmdOPCode,
                               nsid=0,         ## Create: The NSID field is reserved for this operation; host software clears this field to a value of 0h.
                               data_len=4096,
                               addr=d.addr,
                               cdw10=cdw10,)

    class NSDelete(LinCommand):
        def __init__(self, ns_id):
            ### build command
            cdw10 = build_int_by_bitmap({"SEL": (0x0F, 0, 0x01),      # Select (SEL): This field selects the type of management operation to perform
                                        })
            ##   
            super(NSDelete, self).__init__(IOCTL_REQ)
            self.build_command(opcode=CmdOPCode,
                               nsid=ns_id,
                               cdw10=cdw10,)

elif os_type == "Windows":
    from pydiskcmd.pynvme.nvme_command import WinCommand
    class NSCreate(WinCommand):
        def __init__(self, *args, **kwargs):
            raise CommandNotSupport("NSCreate Not Support")

    class NSDelete(WinCommand):
        def __init__(self, *args, **kwargs):
            raise CommandNotSupport("NSDelete Not Support")

else:
    raise NotImplementedError("%s not support" % os_type)
