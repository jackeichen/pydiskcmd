# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmd.system.os_tool import os_type
from pydiskcmd.pynvme.nvme_command import Command,build_command

#####
CmdOPCode = 0x02
#####

if os_type == "Linux":
    ## linux command
    IOCTL_REQ = Command.linux_req.get("NVME_IOCTL_ADMIN_CMD")
    ##
    class FWSlotInfo(Command):
        def __init__(self):
            ### build command
            numdl = int(512 / 4) - 1
            cdw10 = build_command({"lid": (0xFF, 0, 0x03),
                                   "numdl": (0x0FFF, 2, numdl),})  
            ##     
            super(FWSlotInfo, self).__init__(IOCTL_REQ,
                                             opcode=CmdOPCode,
                                             data_len=512,
                                             cdw10=cdw10,)

    class ErrorLog(Command):
        def __init__(self, max_entry):
            ## get the max number log entries
            numbet_dw = max_entry * 16 ## 16 = 64 / 4
            numd = numbet_dw - 1
            ## the numbet_dw <= 256*16= 4096,
            #  so 0x0FFF is enough for numd
            numdl = numd & 0x0FFF
            ### build command
            cdw10 = build_command({"lid": (0xFF, 0, 0x01),      # log id
                                   "numdl": (0x0FFF, 2, numdl),})
            ##     
            super(ErrorLog, self).__init__(IOCTL_REQ,
                                           opcode=CmdOPCode,
                                           data_len=numbet_dw*4,
                                           cdw10=cdw10,)

    class SmartLog(Command):
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
            cdw10 = build_command({"lid": (0xFF, 0, 0x02),      # log id
                                   "numdl": (0x0FFF, 2, numdl),})
            ##     
            super(SmartLog, self).__init__(IOCTL_REQ,
                                           opcode=CmdOPCode,
                                           nsid=0xFFFFFFFF,
                                           addr=data_addr,
                                           data_len=512,
                                           cdw10=cdw10,)

    class SelfTestLog(Command):
        def __init__(self):
            ### build command
            numdl = int(564 / 4) - 1
            cdw10 = build_command({"lid": (0xFF, 0, 0x06),      # log id
                                   "numdl": (0x0FFF, 2, numdl),})
            ##     
            super(SelfTestLog, self).__init__(IOCTL_REQ,
                                              opcode=CmdOPCode,
                                              data_len=564,
                                              cdw10=cdw10)

    class PersistentEventLog(Command):
        def __init__(self,
                     lsp,
                     numdl,
                     lpol=0,
                     lpou=0,
                     data_addr=None):
            cdw10 = build_command({"lid": (0xFF, 0, 0x0D),
                                   "lsp": (0x0F, 1, lsp),   # Read Log Data
                                   "rae": (0x80, 1, 0),
                                   "numdl": (0x0FFF, 2, numdl),})
            cdw12 = build_command({"lpol": (0xFFFF, 0, lpol)})
            cdw13 = build_command({"lpou": (0xFFFF, 0, lpou)})
            ##     
            super(PersistentEventLog, self).__init__(IOCTL_REQ,
                                                     opcode=CmdOPCode,
                                                     addr=data_addr,
                                                     data_len=(numdl+1)*4,
                                                     cdw10=cdw10,
                                                     cdw12=cdw12,
                                                     cdw13=cdw13,)


    class CommandsSupportedAndEffectsLog(Command):
        def __init__(self):
            numdl = int(4096 / 4) - 1
            cdw10 = build_command({"lid": (0xFF, 0, 0x05),      # log id
                                   "numdl": (0x0FFF, 2, numdl),})
            ##     
            super(CommandsSupportedAndEffectsLog, self).__init__(IOCTL_REQ,
                                                                 opcode=CmdOPCode,
                                                                 data_len=4096,
                                                                 cdw10=cdw10)
elif os_type == "Windows":
    class FWSlotInfo(object):
        pass

    class ErrorLog(object):
        pass

    class SmartLog(object):
        pass

    class SelfTestLog(object):
        pass

    class PersistentEventLog(object):
        pass

    class CommandsSupportedAndEffectsLog(object):
        pass
else:
    raise NotImplementedError("%s not support" % os_type)
