# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from .rst_command import RSTCommand
from pydiskcmdlib.os.win_ioctl_utils import (
    INTELNVM_SIGNATURE,
    CSMI_Control_Code,
    CSMISignature,
)


class CSMI_SAS_GET_DRIVER_INFO(RSTCommand):
    _cdb_bits = {"HeaderLength": [0xFFFFFFFF, 0],  
                 "Signature": ['b', 4, 8],
                 "Timeout": [0xFFFFFFFF, 12],
                 "ControlCode": [0xFFFFFFFF, 16],
                 "ReturnCode":  [0xFFFFFFFF, 20],  #
                 "Length": [0xFFFFFFFF, 24], # 
                }

    def __init__(self):
        RSTCommand.__init__(self)
        self.build_command(Signature=CSMISignature.CSMI_ALL_SIGNATURE.value,
                           ControlCode=CSMI_Control_Code.CC_CSMI_SAS_GET_DRIVER_INFO.value,
                           )
