# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from .csmi_command import CSMICommand
from .win_ioctl_structures import (
    SRB_IO_CONTROL_LEN,
    CSMI_SAS_SMP_PASSTHRU_BUFFER,
)
from .win_ioctl_utils import (
    CSMI_Control_Code,
    CSMISignature,
    CSMI_TIMEOUT,
)

class CSMI_SAS_SMP_PASSTHRU(CSMICommand):
    """
    Initialize the CSMICommand for the SAS SMP Pass-Through Buffer.

    This constructor sets up the CSMICommand with the appropriate parameters for a SAS SMP Pass-Through operation.
    It takes several arguments related to the SAS device, connection, and request details.

    Args:
        phy_id (int): The physical identifier of the SAS device.
        port_id (int): The port identifier of the SAS device.
        connection_rate (int): The connection rate of the SAS device.
        sas_addr (int): The SAS address of the destination device.
        request_length (int): The length of the request in bytes.
        request_frame_type (int): The type of the request frame.
        request_function (int): The function code of the request.
        request_add_request_bytes (int): Additional bytes for the request.

    Attributes:
        CSMICommand (class): The base class for CSMI commands.
        CSMI_SAS_SMP_PASSTHRU_BUFFER (function): A function to get the CSMI command for the SAS SMP Pass-Through Buffer.
        SRB_IO_CONTROL_LEN (int): The length of the SRB_IO_CONTROL structure.
        CSMISignature (class): A class containing CSMI signatures.
        CSMI_SAS_TIMEOUT (class): A class containing CSMI SAS timeout values.
        CSMI_Control_Code (class): A class containing CSMI control codes.
        cdb_raw_struc_len (int): The length of the raw CDB structure.

    Note:
        This constructor is responsible for initializing the CSMICommand object with the necessary
        parameters for a SAS SMP Pass-Through operation. It does not perform the actual
        pass-through operation.
    """
    def __init__(self, phy_id, port_id, connection_rate, sas_addr, request_length,
                 request_frame_type, request_function, request_add_request_bytes,
                 timeout=CSMI_TIMEOUT.CSMI_SAS_TIMEOUT.value,):
        CSMICommand.__init__(self, CSMI_SAS_SMP_PASSTHRU_BUFFER)
        self.build_command(HeaderLength=SRB_IO_CONTROL_LEN,
                           Signature=CSMISignature.CSMI_SAS_SIGNATURE.value,
                           Timeout=timeout,
                           ControlCode=CSMI_Control_Code.CC_CSMI_SAS_SMP_PASSTHRU.value,
                           ReturnCode=0,
                           Length=self.cdb_raw_struc_len-SRB_IO_CONTROL_LEN,
                           bPhyIdentifier=phy_id,
                           bPortIdentifier=port_id,
                           bConnectionRate=connection_rate,
                           bDestinationSASAddress=sas_addr,
                           uRequestLength=request_length,
                           bFrameType=request_frame_type,
                           bFunction=request_function,
                           bAdditionalResponseBytes=request_add_request_bytes,
                           )
