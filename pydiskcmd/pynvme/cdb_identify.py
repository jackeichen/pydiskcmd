# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmd.system.os_tool import os_type
from pydiskcmd.exceptions import CommandNotSupport

#####
CmdOPCode = 0x06
#####

if os_type == "Linux":
    from pydiskcmd.pynvme.nvme_command import LinCommand,build_int_by_bitmap
    ## linux command
    IOCTL_REQ = LinCommand.linux_req.get("NVME_IOCTL_ADMIN_CMD")
    class IDCtrl(LinCommand):
        def __init__(self):
            cdw10 = build_int_by_bitmap({"CNS": (0xFF, 0, 0x01)})
            super(IDCtrl, self).__init__(IOCTL_REQ)
            self.build_command(opcode=CmdOPCode,
                               data_len=4096,
                               cdw10=cdw10,)


    class IDNS(LinCommand):
        def __init__(self, ns_id):
            cdw10 = build_int_by_bitmap({"CNS": (0xFF, 0, 0x00)})
            super(IDNS, self).__init__(IOCTL_REQ)
            self.build_command(opcode=CmdOPCode,
                               nsid=ns_id,
                               data_len=4096,
                               cdw10=cdw10,)


    class IDActiveNS(LinCommand):
        def __init__(self, 
                     ns_id,
                     uuid_index=0):
            ## build command
            cdw10 = build_int_by_bitmap({"CNS": (0xFF, 0, 0x02)})
            cdw14 = build_int_by_bitmap({"UUID": (0x7F, 0, uuid_index),})
            super(IDActiveNS, self).__init__(IOCTL_REQ)
            self.build_command(opcode=CmdOPCode,
                               nsid=ns_id,
                               data_len=4096,
                               cdw10=cdw10,
                               cdw14=cdw14)


    class IDAllocatedNS(LinCommand):
        def __init__(self, ns_id):
            ## build command
            cdw10 = build_int_by_bitmap({"CNS": (0xFF, 0, 0x10)})
            super(IDAllocatedNS, self).__init__(IOCTL_REQ)
            self.build_command(opcode=CmdOPCode,
                               nsid=ns_id,
                               data_len=4096,
                               cdw10=cdw10)


    class IDCtrlListInSubsystem(LinCommand):
        def __init__(self, cnt_id):
            ## build command
            cdw10 = build_int_by_bitmap({"CNS": (0xFF, 0, 0x13),
                                         "CNTID": (0xFFFF, 2, cnt_id)})
            super(IDCtrlListInSubsystem, self).__init__(IOCTL_REQ)
            self.build_command(opcode=CmdOPCode,
                               data_len=4096,
                               cdw10=cdw10)


    class IDCtrlListAttachedToNS(LinCommand):
        def __init__(self, 
                     ns_id,
                     cnt_id):
            ## build command
            cdw10 = build_int_by_bitmap({"CNS": (0xFF, 0, 0x12),
                                         "CNTID": (0xFFFF, 2, cnt_id)})
            super(IDCtrlListAttachedToNS, self).__init__(IOCTL_REQ)
            self.build_command(opcode=CmdOPCode,
                               nsid=ns_id,
                               data_len=4096,
                               cdw10=cdw10)
elif os_type == "Windows":
    from pydiskcmd.pynvme.nvme_command import WinCommand,build_int_by_bitmap
    from pydiskcmd.pynvme.win_nvme_command import NVMeStorageQueryPropertyWithBuffer4096
    #
    IOCTL_REQ = WinCommand.win_req.get("IOCTL_STORAGE_QUERY_PROPERTY")
    ##
    class IDCtrl(WinCommand):
        def __init__(self):
            super(IDCtrl, self).__init__(IOCTL_REQ)
            self.build_command(PropertyId=49,    # StorageDeviceProtocolSpecificProperty
                               DataType=1,       # NVMeDataTypeIdentify
                               RequestValue=1,   # 
                               ProtocolDataLength=4096,    # data len
                               )

        def build_command(self, **kwargs):
            self.cdb = NVMeStorageQueryPropertyWithBuffer4096(**kwargs)
            return self.cdb

    class IDNS(WinCommand):
        def __init__(self, ns_id):
            super(IDNS, self).__init__(IOCTL_REQ)
            ##
            # NSID Always =1 Now!
            if ns_id != 1:
                raise CommandNotSupport("ns_id will be always 1 in windows now!")
            dwNSID = build_int_by_bitmap({"NSID": (0xFFFFFFFF, 0, ns_id)})
            #
            self.build_command(PropertyId=49,    # StorageDeviceProtocolSpecificProperty
                               DataType=1,       # NVMeDataTypeIdentify
                               RequestValue=0,   # CNS
                               RequestSubValue=dwNSID,
                               ProtocolDataLength=4096,    # data len
                               )

        def build_command(self, **kwargs):
            self.cdb = NVMeStorageQueryPropertyWithBuffer4096(**kwargs)
            return self.cdb

    class IDActiveNS(WinCommand):
        def __init__(self, *args, **kwargs):
            raise CommandNotSupport("IDActiveNS Not Support")

    class IDAllocatedNS(WinCommand):
        def __init__(self, *args, **kwargs):
            raise CommandNotSupport("IDAllocatedNS Not Support")

    class IDCtrlListInSubsystem(WinCommand):
        def __init__(self, *args, **kwargs):
            raise CommandNotSupport("IDCtrlListInSubsystem Not Support")

    class IDCtrlListAttachedToNS(WinCommand):
        def __init__(self, *args, **kwargs):
            raise CommandNotSupport("IDCtrlListAttachedToNS Not Support")
else:
    raise NotImplementedError("%s not support" % os_type)
