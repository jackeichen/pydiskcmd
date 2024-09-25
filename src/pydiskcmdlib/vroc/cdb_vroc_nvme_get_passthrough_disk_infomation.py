# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from .vroc_nvme_command import VROCNVMeCommand,win_ioctl


class GetPassthroughDiskInformation(VROCNVMeCommand):
    _cdb_bits = {"HeaderLength": [0xFFFFFFFF, 0],  
                 "Signature": ['b', 4, 8],
                 "Timeout": [0xFFFFFFFF, 12],
                 "ControlCode": [0xFFFFFFFF, 16],
                 "ReturnCode":  [0xFFFFFFFF, 20],  #
                 "Length": [0xFFFFFFFF, 24], # 
                 "ReturnBufferLen": [0xFFFFFFFF, 28], # 
                 "DataBuffer": [0xFFFFFFFF, 128],  # output
                }
    def __init__(self, number_of_passthrough_disks):
        VROCNVMeCommand.__init__(self)
        self.build_command(Signature=win_ioctl.NVME_RAID_SIG_STR,
                           ControlCode=win_ioctl.NVME_GET_PASSTHROUGH_DISKS_INFORMATION,
                           ReturnBufferLen=number_of_passthrough_disks*win_ioctl.sizeof(win_ioctl.NVME_MEMBER_DISK_INFORMATION),
                           )
