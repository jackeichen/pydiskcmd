# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from .csmi_command import CSMICommand
from .win_ioctl_structures import (
    SRB_IO_CONTROL_LEN,
    CSMI_SAS_PHY_INFO_BUFFER,
)
from .win_ioctl_utils import (
    CSMI_Control_Code,
    CSMISignature,
    CSMI_TIMEOUT,
)

class CSMI_SAS_GET_PHY_INFO(CSMICommand):
    def __init__(self, timeout=CSMI_TIMEOUT.CSMI_SAS_TIMEOUT.value):
        CSMICommand.__init__(self, CSMI_SAS_PHY_INFO_BUFFER)
        self.build_command(HeaderLength=SRB_IO_CONTROL_LEN,
                           Signature=CSMISignature.CSMI_SAS_SIGNATURE.value,
                           Timeout=timeout,
                           ControlCode=CSMI_Control_Code.CC_CSMI_SAS_GET_PHY_INFO.value,
                           ReturnCode=0,
                           Length=self.cdb_raw_struc_len-SRB_IO_CONTROL_LEN,
                           )
