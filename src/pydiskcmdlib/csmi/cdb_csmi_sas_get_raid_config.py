# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from .csmi_command import CSMICommand
from .win_ioctl_structures import (
    SRB_IO_CONTROL_LEN,
    GET_CSMI_SAS_RAID_CONFIG_BUFFER,
)
from .win_ioctl_utils import (
    CSMI_Control_Code,
    CSMISignature,
    CSMI_TIMEOUT,
)


class CSMI_SAS_GET_RAID_CONFIG(CSMICommand):
    # _cdb_bits = {"HeaderLength": [0xFFFFFFFF, 0],  
    #              "Signature": ['b', 4, 8],
    #              "Timeout": [0xFFFFFFFF, 12],
    #              "ControlCode": [0xFFFFFFFF, 16],
    #              "ReturnCode":  [0xFFFFFFFF, 20],  #
    #              "Length": [0xFFFFFFFF, 24], # 
    #              "RaidSetIndex": [0xFFFFFFFF, 28]
    #             }

    def __init__(self, raid_set_index, uMaxDrivesPerSet, timeout=CSMI_TIMEOUT.CSMI_RAID_TIMEOUT.value):
        CSMICommand.__init__(self, GET_CSMI_SAS_RAID_CONFIG_BUFFER(uMaxDrivesPerSet))
        self.build_command(HeaderLength=SRB_IO_CONTROL_LEN,
                           Signature=CSMISignature.CSMI_RAID_SIGNATURE.value,
                           Timeout=timeout,
                           ControlCode=CSMI_Control_Code.CC_CSMI_SAS_GET_RAID_CONFIG.value,
                           ReturnCode=0,
                           Length=self.cdb_raw_struc_len-SRB_IO_CONTROL_LEN,
                           uRaidSetIndex=raid_set_index
                           )
