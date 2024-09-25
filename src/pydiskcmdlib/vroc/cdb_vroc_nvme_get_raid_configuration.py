# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from .vroc_nvme_command import VROCNVMeCommand,win_ioctl


class GetRaidConfiguration(VROCNVMeCommand):
    _cdb_bits = {"HeaderLength": [0xFFFFFFFF, 0],  
                 "Signature": ['b', 4, 8],
                 "Timeout": [0xFFFFFFFF, 12],
                 "ControlCode": [0xFFFFFFFF, 16],
                 "ReturnCode":  [0xFFFFFFFF, 20],  #
                 "Length": [0xFFFFFFFF, 24], # 
                 "indexOfRaidVolume": [0xFFFFFFFF, 28], # 
                 "ReturnBufferLen": [0xFFFFFFFF, 32], # 
                 "DataBuffer": [0xFF, 36], #  Should not set it
                }
    def __init__(self, raid_volume_index, disk_number):
        VROCNVMeCommand.__init__(self)
        self.build_command(Signature=win_ioctl.NVME_RAID_SIG_STR,
                           ControlCode=win_ioctl.NVME_GET_RAID_CONFIGURATION,
                           indexOfRaidVolume=raid_volume_index,
                           ReturnBufferLen=disk_number*win_ioctl.sizeof(win_ioctl.NVME_MEMBER_DISK_INFORMATION),
                           )
