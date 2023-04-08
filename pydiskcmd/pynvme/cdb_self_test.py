# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmd.system.os_tool import os_type
from pydiskcmd.exceptions import CommandNotSupport

#####
CmdOPCode = 0x14
#####

if os_type == "Linux":
    from pydiskcmd.pynvme.nvme_command import LinCommand,build_int_by_bitmap
    ## linux command
    IOCTL_REQ = LinCommand.linux_req.get("NVME_IOCTL_ADMIN_CMD")
    class SelfTest(LinCommand):
        def __init__(self, 
                     stc,
                     ns_id=0xFFFFFFFF):
            raise CommandNotSupport("SelfTest Not Support")
            ### build command
            cdw10 = build_int_by_bitmap({"stc": (0x0F, 0, stc),})
            ##   
            super(SelfTest, self).__init__(IOCTL_REQ)
            self.build_command(opcode=CmdOPCode,
                               nsid=ns_id,
                               cdw10=cdw10,)

elif os_type == "Windows":
    from pydiskcmd.pynvme.nvme_command import WinCommand,build_int_by_bitmap
    from pydiskcmd.pynvme.win_nvme_command import (
        StorageProtocolCommand,
        STORAGE_PROTOCOL_COMMAND_FLAG_ADAPTER_REQUEST,
        STORAGE_PROTOCOL_SPECIFIC_NVME_COMMAND,
        STORAGE_PROTOCOL_STRUCTURE_VERSION,
        )
    ##
    IOCTL_REQ = WinCommand.win_req.get("IOCTL_STORAGE_PROTOCOL_COMMAND")
    class SelfTest(WinCommand):
        def __init__(self,
                     stc,
                     ns_id=0xFFFFFFFF):
            ##
            cdw10 = build_int_by_bitmap({"stc": (0x0F, 0, stc),})
            super(SelfTest, self).__init__(IOCTL_REQ)
            self.build_command(h_version=STORAGE_PROTOCOL_STRUCTURE_VERSION,    
                               h_flags=STORAGE_PROTOCOL_COMMAND_FLAG_ADAPTER_REQUEST,   
                               h_error_info_length=0,   
                               h_d2d_transfer_length=0,
                               h_dfd_transfer_length=0,   
                               h_timeout=10,
                               h_error_info_offset=0,
                               h_d2d_buffer_offset=0,
                               h_dfd_buffer_offset=0,
                               h_command_spec=STORAGE_PROTOCOL_SPECIFIC_NVME_COMMAND.ADMIN.value,
                               opcode=CmdOPCode,
                               nsid=ns_id,
                               cdw10=cdw10,
                               )

        def build_command(self, **kwargs):
            self.cdb = StorageProtocolCommand(**kwargs)
            return self.cdb

else:
    raise NotImplementedError("%s not support" % os_type)
