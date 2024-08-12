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

class TransferDirection(Enum):
    NonData = 0
    Host2Device = 0
    Device2Host = 1

#  T_LENGTH field
#  Code             Description
#  00b              No data is transferred
#  01b              The transfer length is an unsigned integer specified in the FEATURES (7:0) field and, 
#                   for the ATA PASS-THROUGH (16) command and the ATA PASS-THROUGH (32) 
#                   command, the FEATURES (15:8) field.
#  10b              The transfer length is an unsigned integer specified in the COUNT (7:0) field and, for 
#                   the ATA PASS-THROUGH(16) command and the ATA PASS-THROUGH (32) 
#                   command, the COUNT(15:8) field.
#  11b              The transfer length is an unsigned integer specified in the TPSIU.
# 
# 
# Mapping of BYTE_BLOCK bit, T_TYPE bit, and T_LENGTH field
#  BYTE_BLOCK  T_TYPE  T_LENGTH    Transfer length
#  1b          0b      non-zero    The number of 512 byte blocks to be transferred
#  1b          1b      non-zero    The number of ATA logical sector size blocks to be transferred
#  0b          all     non-zero    The number of bytes to be transferred
#  all         all     zero        No data to be transferred
# 


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

    def _decode_sense(self):
        if self.raw_sense_data:
            return ATACheckReturnDescriptorCondition(self.raw_sense_data)

    @property
    def ata_status_return_descriptor(self):
        decode_sense = self._decode_sense()
        if decode_sense:
            return decode_sense.ata_pass_thr_return_descriptor

    def get_ata_status_return(self):
        decode_sense = self._decode_sense()
        # This will include ata_pass_thr_return_descriptor and ata_pass_thr_fixed_format
        if decode_sense:
            return decode_sense.ata_pass_thr_return_descriptor or decode_sense.ata_pass_thr_fixed_format

    def check_return_status(self, success_hint=False, fail_hint=True, raise_if_fail=True) -> bool:
        ##
        _success = True
        decode_sense = self._decode_sense()
        ata_status_return = self.get_ata_status_return()
        # TODO, usually get true here for now.
        # Linux usually return sense_key = 0x01, asc/ascq = 0/29
        if decode_sense and decode_sense.data.get("sense_key") in (0x01,  # Recovered Error
                                                                   0x02,  # Not Ready
                                                                   0x03,  #
                                                                   0x04,
                                                                   0x05,
                                                                   0x07,
                                                                   0x0A,
                                                                   0x0B,
                                                                   0x0E,
                                                                 ):
            _success = False
            if decode_sense.data.get("sense_key") == 1 and decode_sense.asc == 0 and decode_sense.ascq == 29:
                _success = True
            else:
                _success = True
        if ata_status_return and (ata_status_return.get("status") & 0x01 != 0 or ata_status_return.get("status") & 0x20 != 0):
            _success = False
        #
        if _success:
            if success_hint:
                print ("Command Success")
                print ('')
        else:
            if fail_hint:
                print ("Command failed, and details bellow.")
                print ("- SCSI Status:")
                format_string = "  %-12s%-7s%s"
                print (format_string % ("Sense Key", "ASC", "ASCQ"))
                print (format_string % (decode_sense.data.get("sense_key"),
                                        decode_sense.data.get("additional_sense_code"),
                                        decode_sense.data.get("additional_sense_code_qualifier"),
                                        )
                )
                print ('')
                print ("- ATA Status:")
                format_string = "  %-12s%-19s%s"
                print (format_string % ("Error Bit", "DEVICE FAULT Bit", "Error Field"))
                print (format_string % (ata_status_return.get("status") & 0x01, 
                                        1 if (ata_status_return.get("status") & 0x20) else 0, 
                                        "%#x" % ata_status_return.get("error"),
                                        )
                )
            print ('')
            if raise_if_fail:
                raise CommandReturnStatusError("ATA Return Status Check Error: SCSI Sense Key(%#x), Error Bit(%d), device fault bit(%d)" % (decode_sense.data.get("sense_key"),
                                                                                                                                            ata_status_return.get("status") & 0x01,
                                                                                                                                            1 if (ata_status_return.get("status") & 0x20) else 0,
                                                                                                                                            ))
        return _success


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

    def _decode_sense(self):
        if self.raw_sense_data:
            return ATACheckReturnDescriptorCondition(self.raw_sense_data)

    @property
    def ata_status_return_descriptor(self):
        decode_sense = self._decode_sense()
        if decode_sense:
            return decode_sense.ata_pass_thr_return_descriptor

    def get_ata_status_return(self):
        decode_sense = self._decode_sense()
        # This will include ata_pass_thr_return_descriptor and ata_pass_thr_fixed_format
        if decode_sense:
            return decode_sense.ata_pass_thr_return_descriptor or decode_sense.ata_pass_thr_fixed_format

    def check_return_status(self, success_hint=False, fail_hint=True, raise_if_fail=True) -> bool:
        ##
        _success = True
        decode_sense = self._decode_sense()
        ata_status_return = self.get_ata_status_return()
        # TODO, usually get true here for now.
        # Linux usually return sense_key = 0x01, asc/ascq = 0/29
        if decode_sense and decode_sense.data.get("sense_key") in (0x01,  # Recovered Error
                                                                   0x02,  # Not Ready
                                                                   0x03,  #
                                                                   0x04,
                                                                   0x05,
                                                                   0x07,
                                                                   0x0A,
                                                                   0x0B,
                                                                   0x0E,
                                                                 ):
            _success = False
            if decode_sense.data.get("sense_key") == 1 and decode_sense.asc == 0 and decode_sense.ascq == 29:
                _success = True
            else:
                _success = True
        if ata_status_return and (ata_status_return.get("status") & 0x01 != 0 or ata_status_return.get("status") & 0x20 != 0):
            _success = False
        #
        if _success:
            if success_hint:
                print ("Command Success")
                print ('')
        else:
            if fail_hint:
                print ("Command failed, and details bellow.")
                print ("- SCSI Status:")
                format_string = "  %-12s%-7s%s"
                print (format_string % ("Sense Key", "ASC", "ASCQ"))
                print (format_string % (decode_sense.data.get("sense_key"),
                                        decode_sense.data.get("additional_sense_code"),
                                        decode_sense.data.get("additional_sense_code_qualifier"),
                                        )
                )
                print ('')
                print ("- ATA Status:")
                format_string = "  %-12s%-19s%s"
                print (format_string % ("Error Bit", "DEVICE FAULT Bit", "Error Field"))
                print (format_string % (ata_status_return.get("status") & 0x01, 
                                        1 if (ata_status_return.get("status") & 0x20) else 0, 
                                        "%#x" % ata_status_return.get("error"),
                                        )
                )
            print ('')
            if raise_if_fail:
                raise CommandReturnStatusError("ATA Return Status Check Error: SCSI Sense Key(%#x), Error Bit(%d), device fault bit(%d)" % (decode_sense.data.get("sense_key"),
                                                                                                                                            ata_status_return.get("status") & 0x01,
                                                                                                                                            1 if (ata_status_return.get("status") & 0x20) else 0,
                                                                                                                                            ))
        return _success
