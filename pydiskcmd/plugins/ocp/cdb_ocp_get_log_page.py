# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmd.system.os_tool import os_type
from pydiskcmd.exceptions import CommandNotSupport
#####
CmdOPCode = 0x02
admin_timeout_ms = 10000
#####

if os_type == "Linux":
    from pydiskcmd.pynvme.nvme_command import LinCommand,build_int_by_bitmap
    ## linux command
    IOCTL_REQ = LinCommand.linux_req.get("NVME_IOCTL_ADMIN_CMD")
    ##
    class SmartExtendedLog(LinCommand):
        def __init__(self, uuid_index=0, data_buffer=None):
            ###
            data_addr = None
            if data_buffer:
                data_addr = data_buffer.addr
                ## need check data_buffer is multiple of 4 kib
                if data_buffer.data_length < 512:
                    print ("data buffer for persistent_event_log need >= 512 bytes")
                    return 7
            ### build command
            numdl = int(512 / 4) - 1
            cdw10 = build_int_by_bitmap({"lid": (0xFF, 0, 0xC0),      # log id
                                         "numdl": (0x0FFF, 2, numdl),})
            cdw14 = build_int_by_bitmap({"UUID Index": (0x7F, 0, uuid_index),      # log id
                                        })
            ##     
            super(SmartExtendedLog, self).__init__(IOCTL_REQ)
            self.build_command(opcode=CmdOPCode,
                               nsid=0,
                               addr=data_addr,
                               data_len=512,
                               cdw10=cdw10,
                               cdw14=cdw14,
                               timeout_ms=admin_timeout_ms)

    class ErrorRecoveryLog(LinCommand):
        def __init__(self, uuid_index=0, data_buffer=None):
            ###
            data_addr = None
            if data_buffer:
                data_addr = data_buffer.addr
                ## need check data_buffer is multiple of 4 kib
                if data_buffer.data_length < 512:
                    print ("data buffer for persistent_event_log need >= 512 bytes")
                    return 7
            ### build command
            numdl = int(512 / 4) - 1
            cdw10 = build_int_by_bitmap({"lid": (0xFF, 0, 0xC1),      # log id
                                         "numdl": (0x0FFF, 2, numdl),})
            cdw14 = build_int_by_bitmap({"UUID Index": (0x7F, 0, uuid_index),      # log id
                                        })
            ##     
            super(ErrorRecoveryLog, self).__init__(IOCTL_REQ)
            self.build_command(opcode=CmdOPCode,
                               nsid=0,
                               addr=data_addr,
                               data_len=512,
                               cdw10=cdw10,
                               cdw14=cdw14,
                               timeout_ms=admin_timeout_ms)

elif os_type == "Windows":
    from pydiskcmd.pynvme.nvme_command import WinCommand,build_int_by_bitmap
    from pydiskcmd.pynvme.win_nvme_command import (
        NVMeStorageQueryPropertyWithBuffer512,
        NVMeStorageQueryPropertyWithBuffer564,
        NVMeStorageQueryPropertyWithBuffer4096,
        get_NVMeStorageQueryPropertyWithBuffer,
    )
    IOCTL_REQ = WinCommand.win_req.get("IOCTL_STORAGE_QUERY_PROPERTY")
    ##
    class SmartExtendedLog(WinCommand):
        def __init__(self, *args, **kwargs):
            super(SmartExtendedLog, self).__init__(IOCTL_REQ)
            self.build_command(PropertyId=50,    # StorageDeviceProtocolSpecificProperty
                               DataType=2,       # NVMeDataTypeLogPage
                               RequestValue=0xC0,   # log id
                               RequestSubValue=0, # lower 32-bit value of the offset within a log page from which to start returning data.
                               ProtocolDataLength=512,    # data len
                               )

        def build_command(self, **kwargs):
            self.cdb = NVMeStorageQueryPropertyWithBuffer512(**kwargs)
            return self.cdb

    class ErrorRecoveryLog(WinCommand):
        def __init__(self, *args, **kwargs):
            super(ErrorRecoveryLog, self).__init__(IOCTL_REQ)
            self.build_command(PropertyId=50,    # StorageDeviceProtocolSpecificProperty
                               DataType=2,       # NVMeDataTypeLogPage
                               RequestValue=0xC1,   # log id
                               RequestSubValue=0, # lower 32-bit value of the offset within a log page from which to start returning data.
                               ProtocolDataLength=512,    # data len
                               )

        def build_command(self, **kwargs):
            self.cdb = NVMeStorageQueryPropertyWithBuffer512(**kwargs)
            return self.cdb

else:
    raise NotImplementedError("%s not support" % os_type)
