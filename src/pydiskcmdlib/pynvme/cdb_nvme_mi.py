# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmdlib import os_type
from pydiskcmdlib.pynvme.nvme_command import NVMeCommand,AdminCommandOpcode,CommandTimeout,build_int_by_bitmap
from pydiskcmdlib.exceptions import BuildNVMeCommandError
#####
#####
class NVMeMISend(NVMeCommand):
    if os_type == "Linux":
        from pydiskcmdlib.pynvme.linux_nvme_command import IOCTLRequest
        _req_id = IOCTLRequest.NVME_IOCTL_ADMIN_CMD.value
        # Use default cdb_bits
    elif os_type == "Windows":
        from pydiskcmdlib.pynvme import win_nvme_command
        _req_id = win_nvme_command.IOCTLRequest.RESERVED_REQUEST_ID.value
        _cdb_bits = {}

    def __init__(self, 
                 opcode,
                 nmd0,
                 nmd1,
                 data=None,):
        super(NVMeMISend, self).__init__()
        #
        if data:
            data_len = len(data)
            if (data_len % 4):
                raise BuildNVMeCommandError("data length should be dword aligned")
            dataout_buffer = self.init_data_buffer(data_length=data_len)
            dataout_buffer.data_buffer = data
            #
            data_addr = dataout_buffer.addr
        else:
            data_addr = 0
            data_len = 0
        #
        cdw10 = build_int_by_bitmap({"MT": (0x7F, 0, 0x04),   # Message Type, set to 4h
                                     "IC": (0x80, 0 , 0),     # The Integrity Check (IC) bit shall be cleared to ‘0’ in all NVMe-MI Messages in the in-band tunneling mechanism, set to 0
                                     "CSI": (0x01, 1, 0),     # Command Slot Identifier, this bit is reserved for NVMe-MI Messages in the in-band tunneling mechanism, set to 0h
                                     "R": (0x06, 1, 0),       # Reserved, set to 0h
                                     "NMIMT": (0x78, 1, 1),   # NVMe-MI Message Type, 0: Control Primitive, 1: NVMe-MI Command, 2: NVMe Admin Command, 4: PCIe Command. Set to 1h
                                     "ROR": (0x80, 1, 0),     # Request or Response, This bit is cleared to ‘0’ for Request Messages. Set to 0 in command init
                                     "MEB": (0x01, 2, 0),     # This bit is only valid for Command Messages sent using the out-of-band mechanism, set to 0h
                                     "CIAP": (0x02, 2, 0),    # Command Initiated Auto Pause, This bit is only valid for Command Messages sent using the out-of-band mechanisms, set to 0h
                                     })  # 
        cdw11 = build_int_by_bitmap({"Opcode": (0xFF, 0, opcode),})
        ##
        if os_type == "Linux":
            self.build_command(opcode=AdminCommandOpcode.NVMeMISend.value,
                               addr=data_addr,
                               data_len=data_len,
                               cdw10=cdw10,
                               cdw11=cdw11,
                               cdw12=nmd0,
                               cdw13=nmd1,
                               timeout_ms=CommandTimeout.admin.value)
        elif os_type == "Windows":
            self.build_command()


class NVMeMIRecv(NVMeCommand):
    if os_type == "Linux":
        from pydiskcmdlib.pynvme.linux_nvme_command import IOCTLRequest
        _req_id = IOCTLRequest.NVME_IOCTL_ADMIN_CMD.value
        # Use default cdb_bits
    elif os_type == "Windows":
        from pydiskcmdlib.pynvme import win_nvme_command
        _req_id = win_nvme_command.IOCTLRequest.RESERVED_REQUEST_ID.value
        _cdb_bits = {}

    def __init__(self, 
                 opcode,
                 nmd0,
                 nmd1,
                 data_len=0,):
        super(NVMeMIRecv, self).__init__()
        #
        if data_len > 0:
            if (data_len % 4):
                raise BuildNVMeCommandError("data length should be dword aligned")
            dataout_buffer = self.init_data_buffer(data_length=data_len)
            #
            data_addr = dataout_buffer.addr
        else:
            data_addr = 0
        cdw10 = build_int_by_bitmap({"MT": (0x7F, 0, 0x04),   # Message Type, set to 4h
                                     "IC": (0x80, 0 , 0),     # The Integrity Check (IC) bit shall be cleared to ‘0’ in all NVMe-MI Messages in the in-band tunneling mechanism, set to 0
                                     "CSI": (0x01, 1, 0),     # Command Slot Identifier, this bit is reserved for NVMe-MI Messages in the in-band tunneling mechanism, set to 0h
                                     "R": (0x06, 1, 0),       # Reserved, set to 0h
                                     "NMIMT": (0x78, 1, 1),   # NVMe-MI Message Type, 0: Control Primitive, 1: NVMe-MI Command, 2: NVMe Admin Command, 4: PCIe Command. Set to 1h
                                     "ROR": (0x80, 1, 0),     # Request or Response, This bit is cleared to ‘0’ for Request Messages. Set to 0 in command init
                                     "MEB": (0x01, 2, 0),     # This bit is only valid for Command Messages sent using the out-of-band mechanism, set to 0h
                                     "CIAP": (0x02, 2, 0),    # Command Initiated Auto Pause, This bit is only valid for Command Messages sent using the out-of-band mechanisms, set to 0h
                                     })  # 
        cdw11 = build_int_by_bitmap({"Opcode": (0xFF, 0, opcode),})
        if os_type == "Linux":
            self.build_command(opcode=AdminCommandOpcode.NVMeMIReceive.value,
                               addr=data_addr,
                               data_len=data_len,
                               cdw10=cdw10,
                               cdw11=cdw11,
                               cdw12=nmd0,
                               cdw13=nmd1,
                               timeout_ms=CommandTimeout.admin.value)
        elif os_type == "Windows":
            self.build_command()
