# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from .csmi_command import CSMICommandPro
from .win_ioctl_structures import (
    SRB_IO_CONTROL_LEN,
    CSMI_SAS_SATA_SIGNATURE_BUFFER,
)
from .win_ioctl_utils import (
    CSMI_Control_Code,
    CSMISignature,
    CSMI_TIMEOUT,
)


class CSMI_SAS_GET_SATA_SIGNATURE(CSMICommandPro):
    """
    This CSMI functional behavior provides a method of obtaining the initial SATA signature (the 
    initial Register Device to Host FIS) from a directly attached SATA device. The signature may be 
    used to identify whether a SATA device supports the PACKET command set or whether it is a 
    unique SATA device (like a port multiplier). Any driver that implements this specification and 
    supports directly attached SATA devices must support this behavior; otherwise the driver may 
    respond to this control code with a generic IO error.
    """
    def __init__(self, phy_id, timeout=CSMI_TIMEOUT.CSMI_ALL_TIMEOUT.value):
        CSMICommandPro.__init__(self, CSMI_SAS_SATA_SIGNATURE_BUFFER)  # IoctlHeader, Configuration
        self.build_command(IoctlHeader={"HeaderLength": SRB_IO_CONTROL_LEN,
                                        "Signature":CSMISignature.CSMI_SAS_SIGNATURE.value,
                                        "Timeout":timeout,
                                        "ControlCode":CSMI_Control_Code.CC_CSMI_SAS_GET_SATA_SIGNATURE.value,
                                        "ReturnCode":0,
                                        "Length": self.cdb_raw_struc_len-SRB_IO_CONTROL_LEN,
                                        },
                           Signature={"bPhyIdentifier": phy_id,
                                      },
                           )
