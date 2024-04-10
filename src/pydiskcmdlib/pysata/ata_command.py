# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from enum import Enum
from pyscsi.pyscsi.scsi_enum_command import sbc_opcodes
from pyscsi.pyscsi.scsi_cdb_atapassthrough12 import ATAPassThrough12
from pyscsi.pyscsi.scsi_cdb_atapassthrough16 import ATAPassThrough16
from pydiskcmdlib.pysata.ata_sense import ATACheckReturnDescriptorCondition
from pydiskcmdlib.exceptions import CommandReturnStatusError
###
OPCode12 = sbc_opcodes.get("ATA_PASS_THROUGH_12")
OPCode16 = sbc_opcodes.get("ATA_PASS_THROUGH_16")
###
class ProtocalMap(Enum):
    DMATAHardReset            = 0x00
    DMSoftReset               = 0x01
    NonData                   = 0x03
    PIODataIn                 = 0x04
    PIODataOut                = 0x05
    DMA                       = 0x06
    ExecuteDeviceDiagnostic   = 0x08
    DeviceReset               = 0x09
    UDMADataIn                = 0x0A
    UDMADataOut               = 0x0B
    NCQ                       = 0x0C
    ReturnResponseInformation = 0x0F


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

    def check_return_status(self, success_hint=False, fail_hint=True, raise_if_fail=True):
        if self.ata_status_return_descriptor:
            if (self.ata_status_return_descriptor.get("status") & 0x01) == 0 and (self.ata_status_return_descriptor.get("status") & 0x20) == 0:
                if success_hint:
                    print ("Command Success")
                    print ('')
            else:
                if fail_hint:
                    print ("Command failed, and details bellow.")
                    format_string = "%-10s%-17s%s"
                    print (format_string % ("Error Bit", "DEVICE FAULT Bit", "Error Field"))
                    print (format_string % (self.ata_status_return_descriptor.get("status") & 0x01, 
                                            1 if (self.ata_status_return_descriptor.get("status") & 0x20) else 0, 
                                            "%#x" % self.ata_status_return_descriptor.get("error"),
                                            )
                        )
                    print ('')
                if raise_if_fail:
                    raise CommandReturnStatusError("ATA Return Status Check Error: Error Bit(%d), device fault bit(%d)" % (self.ata_status_return_descriptor.get("status") & 0x01,
                                                                                                                            1 if (self.ata_status_return_descriptor.get("status") & 0x20) else 0,
                                                                                                                            ))
            return self.ata_status_return_descriptor.get("error")
        return 0


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

    def check_return_status(self, success_hint=False, fail_hint=True, raise_if_fail=True):
        if self.ata_status_return_descriptor:
            if (self.ata_status_return_descriptor.get("status") & 0x01) == 0 and (self.ata_status_return_descriptor.get("status") & 0x20) == 0:
                if success_hint:
                    print ("Command Success")
                    print ('')
            else:
                if fail_hint:
                    print ("Command failed, and details bellow.")
                    format_string = "%-10s%-17s%s"
                    print (format_string % ("Error Bit", "DEVICE FAULT Bit", "Error Field"))
                    print (format_string % (self.ata_status_return_descriptor.get("status") & 0x01, 
                                            1 if (self.ata_status_return_descriptor.get("status") & 0x20) else 0, 
                                            "%#x" % self.ata_status_return_descriptor.get("error"),
                                            )
                        )
                    print ('')
                if raise_if_fail:
                    raise CommandReturnStatusError("ATA Return Status Check Error: Error Bit(%d), device fault bit(%d)" % (self.ata_status_return_descriptor.get("status") & 0x01,
                                                                                                                            1 if (self.ata_status_return_descriptor.get("status") & 0x20) else 0,
                                                                                                                            ))
            return self.ata_status_return_descriptor.get("error")
        return 0
