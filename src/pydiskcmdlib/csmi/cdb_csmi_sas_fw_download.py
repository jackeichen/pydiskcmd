# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from .csmi_command import CSMICommand
from .win_ioctl_structures import (
    SRB_IO_CONTROL_LEN,
    GET_CSMI_SAS_FIRMWARE_DOWNLOAD_BUFFER,
)
from .win_ioctl_utils import (
    CSMI_Control_Code,
    CSMISignature,
    CSMI_TIMEOUT,
)


class CSMI_SAS_FW_DOWNLOAD(CSMICommand):
    # _cdb_bits = {"HeaderLength": [0xFFFFFFFF, 0],  
    #              "Signature": ['b', 4, 8],
    #              "Timeout": [0xFFFFFFFF, 12],
    #              "ControlCode": [0xFFFFFFFF, 16],
    #              "ReturnCode":  [0xFFFFFFFF, 20],  #
    #              "Length": [0xFFFFFFFF, 24], # 
    #              "BufferLength": [0xFFFFFFFF, 28],
    #              "DownloadFlags": [0xFFFFFFFF, 32],
    #             }

    def __init__(self, data: bytes, download_flags: int, timeout: int = CSMI_TIMEOUT.CSMI_ALL_TIMEOUT.value):
        """
        Initialize the CSMICommand for retrieving the SAS firmware download buffer.

        This constructor sets up the CSMICommand with the appropriate parameters to retrieve
        the SAS firmware download buffer. It takes a byte data and download flags as arguments.

        Args:
            data (bytes): The data to be included in the command.
            download_flags (int): The flags for the download operation.
                0x00000001: CSMI_SAS_FWD_VALIDATE, validate the download image, but do not upgrade 
                            the image. If this operation cannot be supported, then return with 
                            Information.uStatus set to CSMI_SAS_FWD_REJECT.
                0x00000002: CSMI_SAS_FWD_SOFT_RESET, download operation will initiate a soft reset to 
                            the controller after the ROM image has been upgraded. The driver will manage 
                            all I/O until the controller has returned to a ready state. If a soft reset is 
                            insufficient to complete a firmware download operation then Information.uStatus 
                            will return with CSMI_SAS_FWD_REJECT and the upgrade operation will not be 
                            initiated.
                0x00000003: CSMI_SAS_FWD_HARD_RESET, download operation will initiate a hard reset 
                            to the controller after the ROM image has been upgraded. The driver will 
                            suspend all I/O until the controller has returned to a ready state. If a hard reset is 
                            insufficient to complete a firmware download operation then Information.uStatus 
                            will return with CSMI_SAS_FWD_REJECT and the upgrade operation will not be 
                            initiated.

        Attributes:
            CSMICommand (class): The base class for CSMI commands.
            GET_CSMI_SAS_FIRMWARE_DOWNLOAD_BUFFER (function): A function to get the CSMI command for retrieving the SAS firmware download buffer.
            SRB_IO_CONTROL_LEN (int): The length of the SRB_IO_CONTROL structure.
            CSMISignature (class): A class containing CSMI signatures.
            CSMI_SAS_TIMEOUT (class): A class containing CSMI SAS timeout values.
            CSMI_Control_Code (class): A class containing CSMI control codes.
            cdb_raw_struc_len (int): The length of the raw CDB structure.

        Note:
            This constructor is responsible for initializing the CSMICommand object with the necessary
            parameters to retrieve the SAS firmware download buffer. It does not perform the actual
            retrieval operation.
        """
        CSMICommand.__init__(self, GET_CSMI_SAS_FIRMWARE_DOWNLOAD_BUFFER(len(data)))
        self.build_command(HeaderLength=SRB_IO_CONTROL_LEN,
                           Signature=CSMISignature.CSMI_ALL_SIGNATURE.value,
                           Timeout=timeout,
                           ControlCode=CSMI_Control_Code.CC_CSMI_SAS_FIRMWARE_DOWNLOAD.value,
                           ReturnCode=0,
                           Length=self.cdb_raw_struc_len-SRB_IO_CONTROL_LEN,
                           uBufferLength=len(data),
                           uDownloadFlags=download_flags,
                           bDataBuffer=data,
                           )
