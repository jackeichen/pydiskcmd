# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from typing import Optional
from pydiskcmdlib.pyscsi.scsi_cdb_writebuffer import WriteBuffer
from pyscsi.pyscsi.scsi_enum_command import mmc, sbc, smc, spc, ssc
#####
CmdOPCode = spc.WRITE_BUFFER
#####

class NVMeWriteBuffer(WriteBuffer):
    def __init__(self, 
                 mode: int,               # action
                 buffer_id: int,          # Shall translate to Firmware Slot (FS) field of Firmware Activate command
                 buffer_offset: int,      # Shall translate to Offset (OFST) field of Firmware Image Download command.
                 para_list_length: int,   # Shall translate to Number of Dwords (NUMD) field of Firmware Image Download command.
                 data: Optional[bytes] = None, # data in bytes or None    
                 control: int = 0):
        if mode not in (0x05, 0x07, 0x0E, 0x0F):
            raise
        WriteBuffer.__init__(self, 
                             CmdOPCode, 
                             mode, 
                             0,
                             buffer_id,
                             buffer_offset, 
                             para_list_length,
                             data=data,
                             control=control
                             )
