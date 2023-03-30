# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmd.system.os_tool import os_type

#####
CmdOPCode = 0x02
#####

if os_type == "Linux":
    from pydiskcmd.pynvme.nvme_command import LinCommand,build_int_by_bitmap
    ## linux command
    IOCTL_REQ = LinCommand.linux_req.get("NVME_IOCTL_ADMIN_CMD")
    ##
    class FWSlotInfo(LinCommand):
        def __init__(self):
            ### build command
            numdl = int(512 / 4) - 1
            cdw10 = build_int_by_bitmap({"lid": (0xFF, 0, 0x03),
                                         "numdl": (0x0FFF, 2, numdl),})  
            ##     
            super(FWSlotInfo, self).__init__(IOCTL_REQ)
            self.build_command(opcode=CmdOPCode,
                                data_len=512,
                                cdw10=cdw10,)

    class ErrorLog(LinCommand):
        def __init__(self, max_entry):
            ## get the max number log entries
            numbet_dw = max_entry * 16 ## 16 = 64 / 4
            numd = numbet_dw - 1
            ## the numbet_dw <= 256*16= 4096,
            #  so 0x0FFF is enough for numd
            numdl = numd & 0x0FFF
            ### build command
            cdw10 = build_int_by_bitmap({"lid": (0xFF, 0, 0x01),      # log id
                                         "numdl": (0x0FFF, 2, numdl),})
            ##     
            super(ErrorLog, self).__init__(IOCTL_REQ)
            self.build_command(opcode=CmdOPCode,
                               data_len=numbet_dw*4,
                               cdw10=cdw10,)

    class SmartLog(LinCommand):
        def __init__(self, data_buffer=None):
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
            cdw10 = build_int_by_bitmap({"lid": (0xFF, 0, 0x02),      # log id
                                         "numdl": (0x0FFF, 2, numdl),})
            ##     
            super(SmartLog, self).__init__(IOCTL_REQ)
            self.build_command(opcode=CmdOPCode,
                               nsid=0xFFFFFFFF,
                               addr=data_addr,
                               data_len=512,
                               cdw10=cdw10,)

    class SelfTestLog(LinCommand):
        def __init__(self):
            ### build command
            numdl = int(564 / 4) - 1
            cdw10 = build_int_by_bitmap({"lid": (0xFF, 0, 0x06),      # log id
                                         "numdl": (0x0FFF, 2, numdl),})
            ##     
            super(SelfTestLog, self).__init__(IOCTL_REQ)
            self.build_command(opcode=CmdOPCode,
                               data_len=564,
                               cdw10=cdw10)

    class PersistentEventLog(LinCommand):
        def __init__(self,
                     lsp,
                     numdl,
                     lpol=0,
                     lpou=0,
                     data_addr=None):
            cdw10 = build_int_by_bitmap({"lid": (0xFF, 0, 0x0D),
                                         "lsp": (0x0F, 1, lsp),   # Read Log Data
                                         "rae": (0x80, 1, 0),
                                         "numdl": (0x0FFF, 2, numdl),})
            cdw12 = build_int_by_bitmap({"lpol": (0xFFFF, 0, lpol)})
            cdw13 = build_int_by_bitmap({"lpou": (0xFFFF, 0, lpou)})
            ##     
            super(PersistentEventLog, self).__init__(IOCTL_REQ)
            self.build_command(opcode=CmdOPCode,
                               addr=data_addr,
                               data_len=(numdl+1)*4,
                               cdw10=cdw10,
                               cdw12=cdw12,
                               cdw13=cdw13,)


    class CommandsSupportedAndEffectsLog(LinCommand):
        def __init__(self):
            numdl = int(4096 / 4) - 1
            cdw10 = build_int_by_bitmap({"lid": (0xFF, 0, 0x05),      # log id
                                         "numdl": (0x0FFF, 2, numdl),})
            ##     
            super(CommandsSupportedAndEffectsLog, self).__init__(IOCTL_REQ)
            self.build_command(opcode=CmdOPCode,
                               data_len=4096,
                               cdw10=cdw10)
elif os_type == "Windows":
    from pydiskcmd.pynvme.nvme_command import WinCommand
    from pydiskcmd.pynvme.win_nvme_command import NVMeStorageQueryPropertyWithBuffer512,NVMeStorageQueryPropertyWithBuffer4096
    IOCTL_REQ = WinCommand.win_req.get("IOCTL_STORAGE_QUERY_PROPERTY")
    ##
    class FWSlotInfo(WinCommand):
        pass

    class ErrorLog(WinCommand):
        pass

    class SmartLog(WinCommand):
        def __init__(self, *args, **kwargs):
            super(SmartLog, self).__init__(IOCTL_REQ)
            self.build_command(PropertyId=50,    # StorageDeviceProtocolSpecificProperty
                               DataType=2,       # NVMeDataTypeLogPage
                               RequestValue=2,   # log id
                               RequestSubValue=0, #  lower 32-bit value of the offset within a log page from which to start returning data.
                               ProtocolDataLength=512,    # data len
                               )

        def build_command(self, **kwargs):
            self.cdb = NVMeStorageQueryPropertyWithBuffer512(**kwargs)
            return self.cdb

    class SelfTestLog(WinCommand):
        pass

    class PersistentEventLog(WinCommand):
        pass

    class CommandsSupportedAndEffectsLog(WinCommand):
        def __init__(self):
            super(CommandsSupportedAndEffectsLog, self).__init__(IOCTL_REQ)
            self.build_command(PropertyId=50,    # StorageDeviceProtocolSpecificProperty
                               DataType=2,       # NVMeDataTypeLogPage
                               RequestValue=5,   # log id
                               RequestSubValue=0, #  lower 32-bit value of the offset within a log page from which to start returning data.
                               ProtocolDataLength=4096,    # data len
                               )

        def build_command(self, **kwargs):
            self.cdb = NVMeStorageQueryPropertyWithBuffer4096(**kwargs)
            return self.cdb

else:
    raise NotImplementedError("%s not support" % os_type)
