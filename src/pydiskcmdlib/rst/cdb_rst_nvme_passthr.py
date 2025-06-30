# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from enum import Enum
from pydiskcmdlib import os_type
from pydiskcmdlib.command_utils import CommandWrapper,CommandWrapperPro
from pydiskcmdlib.os import win_ioctl_request
from pydiskcmdlib.os.win_ioctl_utils import (
    INTELNVM_SIGNATURE,
    IOCTL_NVME_PASS_THROUGH,
    RST_NVME_PASS_THROUGH_VERSION,
    SRBStatusCode,
)
from .win_ioctl_structures import (
    Get_NVME_IOCTL_PASS_THROUGH_ALIGNED_WITH_BUFFER,
    NVME_IOCTL_PASS_THROUGH_LEN_DW_ALIGNED,
    SRB_IO_CONTROL_LEN,
)
from pydiskcmdlib.pynvme.nvme_status_code import StatusCodeDescription
from pydiskcmdlib.exceptions import *


class NVMeCommandType(Enum):
    admincommand = 0
    iocommand = 1


class RSTNVMePass(CommandWrapper):
    # _cdb_bits = {"HeaderLength": [0xFFFFFFFF, 0],  
    #              "Signature": ['b', 4, 8],
    #              "Timeout": [0xFFFFFFFF, 12],
    #              "ControlCode": [0xFFFFFFFF, 16],
    #              "ReturnCode":  [0xFFFFFFFF, 20], 
    #              "Length": [0xFFFFFFFF, 24], # 28
    #              "Version": [0xFF, 28],
    #              "PathID": [0xFF, 29],
    #              "TargetID": [0xFF, 30], 
    #              "LUN": [0xFF, 31],          # 32               
    #              "OPC": [0xFF, 32],
    #              "MIDV": [0xFF, 33],
    #              "CID": [0xFFFF, 34],
    #              "NSID": [0xFFFFFFFF, 36],
    #              # "Reserved0": [0xFFFFFFFFFFFFFFFF, 40],
    #              # "MPTR": [0xFFFFFFFFFFFFFFFF, 48],
    #              # "PRP1": [0xFFFFFFFFFFFFFFFF, 56],
    #              # "PRP2": [0xFFFFFFFFFFFFFFFF, 64],
    #              "CDW10": [0xFFFFFFFF, 72],
    #              "CDW11": [0xFFFFFFFF, 76],
    #              "CDW12": [0xFFFFFFFF, 80],
    #              "CDW13": [0xFFFFFFFF, 84],
    #              "CDW14": [0xFFFFFFFF, 88],
    #              "CDW15": [0xFFFFFFFF, 92],       # 96
    #              "IsIOCommandSet": [0xFF, 96],    # 97
    #              # "Completion": [], # 97 - 113   # 16
    #              "DataBufferOffset": [0xFFFFFFFF, 113], 
    #              "DataBufferLength": [0xFFFFFFFF, 117], # 8
    #              # "Reserved": [], # 121 - 161    # 40
    #             }
    _req_id: int = win_ioctl_request.IOCTLRequest.IOCTL_SCSI_MINIPORT.value
    def __init__(self, 
                 PathID, # Port number from Windows (non-RAID) or CSMI port number (GET_RAID_INFO and GET_RAID_CONFIG)
                 command_type,    # 0 for admincommand, 1 for iocommand
                 opcode,
                 nsid,
                 cdw10,
                 cdw11,
                 cdw12,
                 cdw13,
                 cdw14,
                 cdw15,
                 data_buffer_len,
                 metadata_buffer_len, # TODO, Not support now
                 data=None,
                 metadata=None,       # TODO, Not support now
                 timeout=60,
                 ):
        if os_type != "Windows":
            raise NotImplementedError("%s Do Not Support this command" % os_type)
        if data is not None:
            data_buffer_len = min(len(data), data_buffer_len)
        if metadata_buffer_len or metadata:
            raise BuildSCSICommandError("NVMe Pass Through command metadata is not supported now")
        ##
        CommandWrapper.__init__(self, Get_NVME_IOCTL_PASS_THROUGH_ALIGNED_WITH_BUFFER(data_buffer_len))
        self.build_command(HeaderLength=SRB_IO_CONTROL_LEN,
                           Signature=INTELNVM_SIGNATURE,
                           Timeout=timeout,
                           ControlCode=IOCTL_NVME_PASS_THROUGH,
                           ReturnCode=0,
                           Length=self.cdb_raw_struc_len-SRB_IO_CONTROL_LEN,
                           Version=RST_NVME_PASS_THROUGH_VERSION.default.value,
                           PathID=PathID,
                           TargetID=0,
                           Lun=0,
                           OPC=opcode,
                           NSID=nsid,
                           CDW10=cdw10,
                           CDW11=cdw11,
                           CDW12=cdw12,
                           CDW13=cdw13,
                           CDW14=cdw14,
                           CDW15=cdw15,
                           IsIOCommandSet=command_type,
                           DataBufferOffset=NVME_IOCTL_PASS_THROUGH_LEN_DW_ALIGNED,
                           DataBufferLength=self.cdb_raw_struc_len-NVME_IOCTL_PASS_THROUGH_LEN_DW_ALIGNED,
                           DataBuffer=data,
                           )

    @property
    def cq_status(self):
        '''
        Compeletion Queue DWORD 3
        '''
        if self.cdb:
            return self.cdb.NVME_IOCTL_PASS_THROUGH.Parameters.Completion.StatusField

    @property
    def cq_cmd_spec(self):
        '''
        Compeletion Queue DWORD 1
        '''
        if self.cdb:
            return self.cdb.NVME_IOCTL_PASS_THROUGH.Parameters.Completion.CommandSpecific

    def specific_nvme_command_check(self, fail_hint=True, raise_if_fail=False):
        '''
        Check the return status of a specific nvme command
        '''
        return 0

    def command_spec_check(self, fail_hint=True, raise_if_fail=False):
        '''
        Check the return status of a specific command
        '''
        ret = 0
        SC = (self.cq_status & 0xFF)
        SCT = ((self.cq_status >> 8) & 0x07)
        if SCT != 0 or SC != 0:
            ret = 4
            CRD = ((self.cq_status >> 11) & 0x03)
            More = (self.cq_status >> 13 & 0x01)
            DNR = (self.cq_status >> 14 & 0x01)
            _hint = "NVMe Return Status Check Error: Status Code Type(%#x), Status Code(%#x)" % (SCT, SC)
            if fail_hint:
                print ("Command failed, and details bellow.")
                format_string = "%-15s%-20s%-8s%s"
                print (format_string % ("Status Code", "Status Code Type", "More", "Do Not Retry"))
                print (format_string % (SC, SCT, More, DNR))
                print ('')
                print (StatusCodeDescription.get((SCT,SC)))
                print ('')
            if raise_if_fail:
                raise CommandReturnStatusError(_hint)
        ret = self.specific_nvme_command_check(fail_hint=fail_hint, raise_if_fail=raise_if_fail)
        return ret

    def check_return_status(self, success_hint=False, fail_hint=True, raise_if_fail=False):
        '''
        3 levels to check the command status after command's execution:
          Level 1: Returned status of DeviceIoControl API,
          Level 2: ReturnCode of SRB_IO_CONTROL structure
          Level 3: Check the returned completion queue entry of NVMe Command

        Note: Do Not Check it before command execute, it may failed in level 2.

        :param success_hint: Whether to print a success message when the command is successful.
        :param fail_hint: Whether to print a failure message when the command fails.
        :param raise_if_fail: Whether to raise an exception when the command fails.
        :return: 0 if the command is successful, otherwise an error code.
        '''
        ret = 0
        if self.ioctl_result is not None:
            if self.ioctl_result == 0:
                ret = 1
                import ctypes # noqa: F401
                if fail_hint:
                    print (str(ctypes.WinError(ctypes.get_last_error())))
                if raise_if_fail:
                    raise ctypes.WinError(ctypes.get_last_error())
        if self.bytes_returned is not None:
            pass
        if self.cdb is not None and hasattr(self.cdb, 'IoctlHeader'):
            if self.cdb.IoctlHeader.ReturnCode not in (SRBStatusCode.SRB_STATUS_SUCCESS.value,
                                                       SRBStatusCode.SRB_STATUS_PENDING.value):
                ret = 3
                if fail_hint:
                    print ("CSMI Command ReturnCode: %#x" % self.cdb.IoctlHeader.ReturnCode)
                if raise_if_fail:
                    raise CommandReturnStatusError("CSMI Command ReturnCode: %#x" % self.cdb.IoctlHeader.ReturnCode)
        ret = self.command_spec_check(fail_hint, raise_if_fail)
        if ret == 0 and success_hint:
            print ("CSMI Command Success")
        return ret
