# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmdlib import os_type
from pydiskcmdlib.pynvme.nvme_command import NVMeCommand,AdminCommandOpcode,CommandTimeout

#####
CmdOPCode = AdminCommandOpcode.FirmwareCommit.value
#####
class FWCommit(NVMeCommand):
    _cmd_spec_fail = {0x06: "Invalid Firmware Slot: The firmware slot indicated is invalid or read only. This error is indicated if \
the firmware slot exceeds the number supported.",
                      0x07: "Invalid Firmware Image: The firmware image specified for activation is invalid and not loaded by the controller.",
                      0x0B: "Firmware Activation Requires Conventional Reset: The firmware commit was successful, \
however, activation of the firmware image requires a Conventional Reset. If an FLR or Controller \
Reset occurs prior to a Conventional Reset, the controller shall continue operation with the currently executing firmware image.",
                      0x10: "Firmware Activation Requires NVM Subsystem Reset: The firmware commit was successful, \
however, activation of the firmware image requires an NVM Subsystem Reset. If any other type of \
Controller Level Reset occurs prior to an NVM Subsystem Reset, the controller shall continue \
operation with the currently executing firmware.",
                      0x11: "Firmware Activation Requires Controller Level Reset: The firmware commit was successful; \
however, the image specified does not support being activated without a Controller Level Reset. \
The image shall be activated at the next Controller Level Reset. This status code should be returned \
only if the Commit Action field in the Firmware Commit command is set to 011b (i.e., activate immediately).",
                      0x12: "Firmware Activation Requires Maximum Time Violation: The image specified if activated \
immediately would exceed the Maximum Time for Firmware Activation (MTFA) value reported in \
the Identify Controller data structure (refer to Figure 251). To activate the firmware, the Firmware \
Commit command needs to be re-issued and the image activated using a reset.",
                      0x13: "Firmware Activation Prohibited: The image specified is being prohibited from activation by the \
controller for vendor specific reasons (e.g., controller does not support down revision firmware).",
                      0x14: "Overlapping Range: This error is indicated if the firmware image has overlapping ranges.",
                      0x1E: "Boot Partition Write Prohibited: This error is indicated if a command attempts to modify a Boot Partition while locked.",
                      }
    if os_type == "Linux":
        from pydiskcmdlib.pynvme.linux_nvme_command import IOCTLRequest
        _req_id = IOCTLRequest.NVME_IOCTL_ADMIN_CMD.value
        _cdb_bits = {"opcode": [0xFF, 0],
                     "flags": [0xFF, 1],
                     "rsvd1": [0xFFFF, 2],
                     "nsid":[0xFFFFFFFF, 4],
                     "cdw2":[0xFFFFFFFF, 8],
                     "cdw3":[0xFFFFFFFF, 12],
                     "metadata":[0xFFFFFFFFFFFFFFFF, 16],
                     "addr":[0xFFFFFFFFFFFFFFFF, 24],
                     "metadata_len":[0xFFFFFFFF, 32],
                     "data_len":[0xFFFFFFFF, 36],
                     #"cdw10":[0xFFFFFFFF, 40],
                     "fs": [0x07, 40],
                     "ca": [0x38, 40],
                     "bpid": [0x80, 43],
                     "cdw11":[0xFFFFFFFF, 44],
                     "cdw12":[0xFFFFFFFF, 48],
                     "cdw13":[0xFFFFFFFF, 52],
                     "cdw14":[0xFFFFFFFF, 56],
                     "cdw15":[0xFFFFFFFF, 60],
                     "timeout_ms":[0xFFFFFFFF, 64],
                     "result":[0xFFFFFFFF, 68],
                     }
    elif os_type == "Windows":
        from pydiskcmdlib.pynvme import win_nvme_command
        _req_id = win_nvme_command.IOCTLRequest.IOCTL_SCSI_MINIPORT.value
        _cdb_bits = {"HeaderLength": [0xFFFFFFFF, 0],
                     "Signature": ('b', 4, 8),
                     "Timeout": [0xFFFFFFFF, 12],
                     "ControlCode": [0xFFFFFFFF, 16],
                     "ReturnCode": [0xFFFFFFFF, 20],
                     "Length": [0xFFFFFFFF, 24],       # 
                     "Version": [0xFFFFFFFF, 28],
                     "Size": [0xFFFFFFFF, 32],
                     "Function": [0xFFFFFFFF, 36],
                     "Flags": [0xFFFFFFFF, 40],
                     "DataBufferOffset": [0xFFFFFFFF, 44],
                     "DataBufferLength": [0xFFFFFFFF, 48], # 
                     "faVersion": [0xFFFFFFFF, 52],
                     "faSize": [0xFFFFFFFF, 56],
                     "faSlotToActivate": [0xFF, 60],
                     "faReserved0": [0xFFFFFF, 61],
                     }

    def __init__(self, 
                 fw_slot, 
                 action,
                 bpid=0):
        super(FWCommit, self).__init__()
        if os_type == "Linux":
            self.build_command(opcode=CmdOPCode,
                               fs=fw_slot,
                               ca=action,
                               bpid=bpid,
                               timeout_ms=CommandTimeout.admin.value)
        elif os_type == "Windows":
            self.build_command(ControlCode=FWCommit.win_nvme_command.IOCTL_SCSI_MINIPORT_FIRMWARE,
                               Function=FWCommit.win_nvme_command.FIRMWARE_FUNCTION.ACTIVATE.value,
                               faSlotToActivate=fw_slot,
                               )


from .cdb_scsi2nvme_write_buffer import NVMeWriteBuffer
class SCSI2NVMeFWCommit(NVMeWriteBuffer):
    def __init__(self, 
                 fw_slot, 
                 action,
                 bpid=0):
        NVMeWriteBuffer.__init__(self, 0x0F, fw_slot, 0, 0,)
