# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from enum import Enum
from .csmi_command import CSMICommand
from .win_ioctl_structures import (
    SRB_IO_CONTROL_LEN,
    CSMI_SAS_CNTLR_STATUS_BUFFER,
)
from .win_ioctl_utils import (
    CSMI_Control_Code,
    CSMISignature,
    CSMI_TIMEOUT,
)

class CSMI_SAS_CNTLR_STATUS(Enum):
    GOOD = 1
    FAILED = 2
    OFFLINE = 3
    POWEROFF = 4


class CSMI_SAS_OFFLINE_REASON(Enum):
    NO_REASON = 0
    INITIALIZING = 1
    BACKSIDE_BUS_DEGRADED = 2
    BACKSIDE_BUS_FAILURE = 3


class CSMI_SAS_GET_CNTLR_STATUS(CSMICommand):
    """
    Initialize the CSMICommand for retrieving the SAS controller status buffer.

    This constructor sets up the CSMICommand with the appropriate parameters to retrieve
    the SAS controller status buffer. It does not take any additional arguments.

    Attributes:
        CSMICommand (class): The base class for CSMI commands.
        CSMI_SAS_CNTLR_STATUS_BUFFER (function): A function to get the CSMI command for retrieving the SAS controller status buffer.
        SRB_IO_CONTROL_LEN (int): The length of the SRB_IO_CONTROL structure.
        CSMISignature (class): A class containing CSMI signatures.
        CSMI_SAS_TIMEOUT (class): A class containing CSMI SAS timeout values.
        CSMI_Control_Code (class): A class containing CSMI control codes.
        cdb_raw_struc_len (int): The length of the raw CDB structure.

    Note:
        This constructor is responsible for initializing the CSMICommand object with the necessary
        parameters to retrieve the SAS controller status buffer. It does not perform the actual
        retrieval operation.
    """
    # _cdb_bits = {"HeaderLength": [0xFFFFFFFF, 0],  
    #              "Signature": ['b', 4, 8],
    #              "Timeout": [0xFFFFFFFF, 12],
    #              "ControlCode": [0xFFFFFFFF, 16],
    #              "ReturnCode":  [0xFFFFFFFF, 20],  #
    #              "Length": [0xFFFFFFFF, 24], # 
    #             }
    def __init__(self, timeout=CSMI_TIMEOUT.CSMI_ALL_TIMEOUT.value):
        CSMICommand.__init__(self, CSMI_SAS_CNTLR_STATUS_BUFFER)
        self.build_command(HeaderLength=SRB_IO_CONTROL_LEN,
                           Signature=CSMISignature.CSMI_ALL_SIGNATURE.value,
                           Timeout=timeout,
                           ControlCode=CSMI_Control_Code.CC_CSMI_SAS_GET_CNTLR_STATUS.value,
                           ReturnCode=0,
                           Length=self.cdb_raw_struc_len-SRB_IO_CONTROL_LEN,
                           )

    def get_status_desp(self):
        return CSMI_SAS_CNTLR_STATUS(self.cdb.Status.uStatus).name
    
    def get_offline_reason(self):
        return CSMI_SAS_OFFLINE_REASON(self.cdb.Status.uOfflineReason).name
