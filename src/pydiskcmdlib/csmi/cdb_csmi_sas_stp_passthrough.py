# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from .csmi_command import CSMICommand
from .win_ioctl_structures import (
    SRB_IO_CONTROL_LEN,
    GET_CSMI_SAS_STP_PASSTHRU_BUFFER,
)
from .win_ioctl_utils import (
    CSMI_Control_Code,
    CSMISignature,
    CSMI_TIMEOUT,
)

class CSMI_SAS_SSP_PASSTHRU(CSMICommand):
    def __init__(self, phy_id, port_id, connection_rate, sas_addr, 
                 command_FIS, flags, data=None, timeout=CSMI_TIMEOUT.CSMI_SAS_TIMEOUT.value,):
        if data is None:
            data_len = 0
        else:
            data_len = len(data)
        CSMICommand.__init__(self, GET_CSMI_SAS_STP_PASSTHRU_BUFFER(data_len))
        self.build_command(HeaderLength=SRB_IO_CONTROL_LEN,
                           Signature=CSMISignature.CSMI_SAS_SIGNATURE.value,
                           Timeout=timeout,
                           ControlCode=CSMI_Control_Code.CC_CSMI_SAS_STP_PASSTHRU.value,
                           ReturnCode=0,
                           Length=self.cdb_raw_struc_len-SRB_IO_CONTROL_LEN,
                           bPhyIdentifier=phy_id,
                           bPortIdentifier=port_id,
                           bConnectionRate=connection_rate,
                           bDestinationSASAddress=sas_addr,
                           bCommandFIS=command_FIS,
                           uFlags=flags,
                           bDataBuffer=data,
                           )
