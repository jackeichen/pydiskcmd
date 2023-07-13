# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmd.system.os_tool import os_type
from pydiskcmd.exceptions import CommandNotSupport

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
        def __init__(self, max_entry, loge_page_offset=0):
            ## get the max number log entries
            numbet_dw = max_entry * 16 ## 16 = 64 / 4
            numd = numbet_dw - 1
            ## Identify controller Byte 262, so the numbet_dw <= 256*16= 4096,
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
            cdw12 = build_int_by_bitmap({"lpol": (0xFFFFFFFF, 0, lpol)})
            cdw13 = build_int_by_bitmap({"lpou": (0xFFFFFFFF, 0, lpou)})
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


    class TelemetryHostInitiatedLog(LinCommand):
        def __init__(self,
                     create_telemetry,
                     numdl,
                     lpol=0,
                     lpou=0,
                     data_addr=None):
            cdw10 = build_int_by_bitmap({"lid": (0xFF, 0, 0x07),
                                         "create_telemetry": (0x01, 1, create_telemetry),   # Read Log Data
                                         "rae": (0x80, 1, 0),
                                         "numdl": (0x0FFF, 2, numdl),})
            cdw12 = build_int_by_bitmap({"lpol": (0xFFFFFFFF, 0, lpol)})
            cdw13 = build_int_by_bitmap({"lpou": (0xFFFFFFFF, 0, lpou)})
            ##     
            super(TelemetryHostInitiatedLog, self).__init__(IOCTL_REQ)
            self.build_command(opcode=CmdOPCode,
                               addr=data_addr,
                               data_len=(numdl+1)*4,
                               cdw10=cdw10,
                               cdw12=cdw12,
                               cdw13=cdw13,)


    class TelemetryControllerInitiatedLog(LinCommand):
        def __init__(self,
                     numdl,
                     lpol=0,
                     lpou=0,
                     data_addr=None):
            cdw10 = build_int_by_bitmap({"lid": (0xFF, 0, 0x08),
                                         "lsp": (0x0F, 1, 0),   # Read Log Data
                                         "rae": (0x80, 1, 0),
                                         "numdl": (0x0FFF, 2, numdl),})
            cdw12 = build_int_by_bitmap({"lpol": (0xFFFFFFFF, 0, lpol)})
            cdw13 = build_int_by_bitmap({"lpou": (0xFFFFFFFF, 0, lpou)})
            ##     
            super(TelemetryControllerInitiatedLog, self).__init__(IOCTL_REQ)
            self.build_command(opcode=CmdOPCode,
                               addr=data_addr,
                               data_len=(numdl+1)*4,
                               cdw10=cdw10,
                               cdw12=cdw12,
                               cdw13=cdw13,)
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
    class FWSlotInfo(WinCommand):
        def __init__(self, *args, **kwargs):
            super(FWSlotInfo, self).__init__(IOCTL_REQ)
            self.build_command(PropertyId=50,    # StorageDeviceProtocolSpecificProperty
                               DataType=2,       # NVMeDataTypeLogPage
                               RequestValue=3,   # log id
                               RequestSubValue=0, #  lower 32-bit value of the offset within a log page from which to start returning data.
                               ProtocolDataLength=512,    # data len
                               )

        def build_command(self, **kwargs):
            self.cdb = NVMeStorageQueryPropertyWithBuffer512(**kwargs)
            return self.cdb

    class ErrorLog(WinCommand):
        def __init__(self, max_entry, loge_page_offset=0, **kwargs):
            self.__data_len = max_entry * 64
            ##
            super(ErrorLog, self).__init__(IOCTL_REQ)
            self.build_command(PropertyId=50,    # StorageDeviceProtocolSpecificProperty
                               DataType=2,       # NVMeDataTypeLogPage
                               RequestValue=1,   # log id
                               RequestSubValue=loge_page_offset&0xFF, #  lower 32-bit value of the offset within a log page from which to start returning data.
                               RequestSubValue2=(loge_page_offset>>32)&0xFF, # the upper 32-bit value of the offset within a log page from which to start returning data.
                               ProtocolDataLength=self.__data_len,    # data len
                               )

        def build_command(self, **kwargs):
            temp = get_NVMeStorageQueryPropertyWithBuffer(self.__data_len)
            self.cdb = temp(**kwargs)
            return self.cdb

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
        def __init__(self, *args, **kwargs):
            super(SelfTestLog, self).__init__(IOCTL_REQ)
            self.build_command(PropertyId=50,    # StorageDeviceProtocolSpecificProperty
                               DataType=2,       # NVMeDataTypeLogPage
                               RequestValue=0x06,   # log id
                               RequestSubValue=0, #  lower 32-bit value of the offset within a log page from which to start returning data.
                               ProtocolDataLength=564,    # data len
                               )

        def build_command(self, **kwargs):
            self.cdb = NVMeStorageQueryPropertyWithBuffer564(**kwargs)
            return self.cdb

    class PersistentEventLog(WinCommand):
        def __init__(self,
                     lsp,
                     numdl,
                     lpol=0,
                     lpou=0,
                     data_addr=None):
            # raise CommandNotSupport("PersistentEventLog Not Support")
            ##
            self.__data_len = (numdl + 1) * 4
            request_sub_value4 = build_int_by_bitmap({"RetainAsynEvent": [0x01, 0, 0],
                                                      "LogSpecificField": [0x1E, 0, lsp],
                                                      #"Reserved": [0xFFFFFFE0, 0, 0],
                                                      }
                                                    )
            ##
            super(PersistentEventLog, self).__init__(IOCTL_REQ)
            # https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddstor/ne-ntddstor-_storage_protocol_nvme_data_type
            self.build_command(PropertyId=50,    # StorageDeviceProtocolSpecificProperty
                               DataType=2,       # NVMeDataTypeLogPage
                               RequestValue=0x0D,   # log id
                               RequestSubValue=lpol, #  lower 32-bit value of the offset within a log page from which to start returning data.
                               RequestSubValue2=lpou, # the upper 32-bit value of the offset within a log page from which to start returning data.
                               RequestSubValue4=request_sub_value4,  # https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddstor/ns-ntddstor-storage_protocol_data_subvalue_get_log_page
                               ProtocolDataLength=self.__data_len,    # data len
                               )

        def build_command(self, **kwargs):
            temp = get_NVMeStorageQueryPropertyWithBuffer(self.__data_len)
            self.cdb = temp(**kwargs)
            return self.cdb

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


    class TelemetryHostInitiatedLog(WinCommand):
        def __init__(self,
                     lsp,
                     numdl,
                     lpol=0,
                     lpou=0,
                     data_addr=None):
            raise CommandNotSupport("TelemetryHostInitiatedLog Not Support")


    class TelemetryControllerInitiatedLog(WinCommand):
        def __init__(self,
                     lsp,
                     numdl,
                     lpol=0,
                     lpou=0,
                     data_addr=None):
            raise CommandNotSupport("TelemetryControllerInitiatedLog Not Support")
else:
    raise NotImplementedError("%s not support" % os_type)
