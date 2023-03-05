# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmd.system.os_tool import os_type
from pydiskcmd.pynvme.nvme_command import Command,build_command

#####
CmdOPCode = 0x06
#####

if os_type == "Linux":
    ## linux command
    IOCTL_REQ = Command.linux_req.get("NVME_IOCTL_ADMIN_CMD")
    class IDCtrl(Command):
        def __init__(self):
            cdw10 = build_command({"CNS": (0xFF, 0, 0x01)})
            super(IDCtrl, self).__init__(IOCTL_REQ,
                                         opcode=CmdOPCode,
                                         data_len=4096,
                                         cdw10=cdw10,)


    class IDNS(Command):
        def __init__(self, ns_id):
            cdw10 = build_command({"CNS": (0xFF, 0, 0x00)})
            super(IDNS, self).__init__(IOCTL_REQ,
                                       opcode=CmdOPCode,
                                       nsid=ns_id,
                                       data_len=4096,
                                       cdw10=cdw10,)


    class IDActiveNS(Command):
        def __init__(self, 
                     ns_id,
                     uuid_index=0):
            ## build command
            cdw10 = build_command({"CNS": (0xFF, 0, 0x02)})
            cdw14 = build_command({"UUID": (0x7F, 0, uuid_index),})
            super(IDActiveNS, self).__init__(IOCTL_REQ, 
                                             opcode=CmdOPCode,
                                             nsid=ns_id,
                                             data_len=4096,
                                             cdw10=cdw10,
                                             cdw14=cdw14)


    class IDAllocatedNS(Command):
        def __init__(self, ns_id):
            ## build command
            cdw10 = build_command({"CNS": (0xFF, 0, 0x10)})
            super(IDAllocatedNS, self).__init__(IOCTL_REQ,
                                                opcode=CmdOPCode,
                                                nsid=ns_id,
                                                data_len=4096,
                                                cdw10=cdw10)


    class IDCtrlListInSubsystem(Command):
        def __init__(self, cnt_id):
            ## build command
            cdw10 = build_command({"CNS": (0xFF, 0, 0x13),
                                   "CNTID": (0xFFFF, 2, cnt_id)})
            super(IDCtrlListInSubsystem, self).__init__(IOCTL_REQ,
                                                        opcode=CmdOPCode,
                                                        data_len=4096,
                                                        cdw10=cdw10)


    class IDCtrlListAttachedToNS(Command):
        def __init__(self, 
                     ns_id,
                     cnt_id):
            ## build command
            cdw10 = build_command({"CNS": (0xFF, 0, 0x12),
                                   "CNTID": (0xFFFF, 2, cnt_id)})
            super(IDCtrlListAttachedToNS, self).__init__(IOCTL_REQ,
                                                         opcode=CmdOPCode,
                                                         nsid=ns_id,
                                                         data_len=4096,
                                                         cdw10=cdw10)
elif os_type == "Windows":
    class IDCtrl(object):
        pass

    class IDNS(object):
        pass

    class IDActiveNS(object):
        pass

    class IDAllocatedNS(object):
        pass

    class IDCtrlListInSubsystem(object):
        pass

    class IDCtrlListAttachedToNS(object):
        pass
else:
    raise NotImplementedError("%s not support" % os_type)
