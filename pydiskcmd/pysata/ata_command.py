# SPDX-FileCopyrightText: 2014 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pyscsi.pyscsi.scsi_enum_command import sbc_opcodes
from pyscsi.pyscsi.scsi_cdb_atapassthrough12 import ATAPassThrough12
from pyscsi.pyscsi.scsi_cdb_atapassthrough16 import ATAPassThrough16
from pydiskcmd.pysata.ata_sense import ATACheckReturnDescriptorCondition
###
OPCode12 = sbc_opcodes.get("ATA_PASS_THROUGH_12")
OPCode16 = sbc_opcodes.get("ATA_PASS_THROUGH_16")
###
ProtocalMap = {"Non-Data": 0x03,
               "PIO Data-In": 0x04,
               "PIO Data-Out": 0x05,
               "DMA": 0x06,
               "Execute Device Diagnostic": 0x08}


class ATACommand12(ATAPassThrough12):
    """
    A class of ATA command by ATAPassThrough12
    """
    def __init__(self,
                 feature,    # ATA command field start
                 count,
                 lba,
                 device,
                 command,
                 protocal,   # ATA command field end 
                 t_length,   # data transfer filed start
                 t_dir,
                 byte_block=1,
                 t_type=0,
                 blocksize=0,
                 extra_tl=None,
                 data=None,  # data transfer filed start
                 off_line=0,
                 control=0,
                 ck_cond=1,
                 ):
        ATAPassThrough12.__init__(self,
                                  OPCode12,            # opcode of ata-passthrough
                                  protocal,            # protocal
                                  t_length,            # t_length 
                                  byte_block,          # byte_block
                                  t_dir,               # t_dir
                                  t_type,              # t_type
                                  off_line,            # off_line
                                  feature,             # fetures
                                  count,               # count
                                  lba,                 # lba
                                  command,             # command
                                  blocksize=blocksize,
                                  extra_tl=extra_tl,
                                  ck_cond=ck_cond,
                                  device=device,
                                  control=control,
                                  data=data)

    @property
    def ata_status_return_descriptor(self):
        if self.raw_sense_data:
            decode_sense = ATACheckReturnDescriptorCondition(self.raw_sense_data)
            return decode_sense.ata_pass_thr_return_descriptor


class ATACommand16(ATAPassThrough16):
    """
    A class of ATA command by ATAPassThrough12
    """
    def __init__(self,
                 feature,    # ATA command field start
                 count,
                 lba,
                 device,
                 command,
                 protocal,   # ATA command field end 
                 t_length,   # data transfer filed start
                 t_dir,
                 byte_block=1,
                 t_type=0,
                 blocksize=0,
                 extra_tl=None,
                 data=None,  # data transfer filed start
                 off_line=0,
                 control=0,
                 ck_cond=1,
                 extend=1,
                 ):
        ATAPassThrough16.__init__(self,
                                  OPCode16,            # opcode of ata-passthrough
                                  protocal,            # protocal
                                  t_length,            # t_length 
                                  byte_block,          # byte_block
                                  t_dir,               # t_dir
                                  t_type,              # t_type
                                  off_line,            # off_line
                                  feature,             # fetures
                                  count,               # count
                                  lba,                 # lba
                                  command,             # command
                                  blocksize=blocksize,
                                  extra_tl=extra_tl,
                                  ck_cond=ck_cond,
                                  device=device,
                                  control=control,
                                  data=data,
                                  extend=extend)

    @property
    def ata_status_return_descriptor(self):
        if self.raw_sense_data:
            decode_sense = ATACheckReturnDescriptorCondition(self.raw_sense_data)
            return decode_sense.ata_pass_thr_return_descriptor
