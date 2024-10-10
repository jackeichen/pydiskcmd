# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from .rst_command import RSTCommand
from pydiskcmdlib.os.win_ioctl_utils import (
    INTELNVM_SIGNATURE,
    IOCTL_NVME_PASS_THROUGH
)


class RSTNVMePass(RSTCommand):
    _cdb_bits = {"HeaderLength": [0xFFFFFFFF, 0],  
                 "Signature": ['b', 4, 8],
                 "Timeout": [0xFFFFFFFF, 12],
                 "ControlCode": [0xFFFFFFFF, 16],
                 "ReturnCode":  [0xFFFFFFFF, 20], 
                 "Length": [0xFFFFFFFF, 24], # 28
                 "Version": [0xFF, 28],
                 "PathID": [0xFF, 29],
                 "TargetID": [0xFF, 30], 
                 "LUN": [0xFF, 31],          # 32               
                 "OPC": [0xFF, 32],
                 "MIDV": [0xFF, 33],
                 "CID": [0xFFFF, 34],
                 "NSID": [0xFFFFFFFF, 36],
                 # "Reserved0": [0xFFFFFFFFFFFFFFFF, 40],
                 # "MPTR": [0xFFFFFFFFFFFFFFFF, 48],
                 # "PRP1": [0xFFFFFFFFFFFFFFFF, 56],
                 # "PRP2": [0xFFFFFFFFFFFFFFFF, 64],
                 "CDW10": [0xFFFFFFFF, 72],
                 "CDW11": [0xFFFFFFFF, 76],
                 "CDW12": [0xFFFFFFFF, 80],
                 "CDW13": [0xFFFFFFFF, 84],
                 "CDW14": [0xFFFFFFFF, 88],
                 "CDW15": [0xFFFFFFFF, 92],       # 96
                 "IsIOCommandSet": [0xFF, 96],    # 97
                 # "Completion": [], # 97 - 113   # 16
                 "DataBufferOffset": [0xFFFFFFFF, 113], 
                 "DataBufferLength": [0xFFFFFFFF, 117], # 8
                 # "Reserved": [], # 121 - 161    # 40
                }

    def __init__(self, 
                 PathID, # Port number from Windows (non-RAID) or CSMI port number (GET_RAID_INFO and GET_RAID_CONFIG)
                 opcode,
                 nsid,
                 cdw10,
                 cdw11,
                 cdw12,
                 cdw13,
                 cdw14,
                 cdw15,
                 command_type,    # 0 for admincommand
                 data_buffer_len, # data length
                 metadata_len=0,  # TODO, Not support now
                 ):
        RSTCommand.__init__(self)
        self.build_command(Signature=INTELNVM_SIGNATURE,
                           ControlCode=IOCTL_NVME_PASS_THROUGH,
                           PathID=PathID,
                           OPC=opcode,
                           NSID=nsid,
                           CDW10=cdw10,
                           CDW11=cdw11,
                           CDW12=cdw12,
                           CDW13=cdw13,
                           CDW14=cdw14,
                           CDW15=cdw15,
                           IsIOCommandSet=command_type,
                           DataBufferLength=data_buffer_len,
                           )
