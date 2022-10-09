# coding: utf-8

# Copyright (C) 2014 by Ronnie Sahlberg<ronniesahlberg@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 2.1 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
from pydiskcmd.pyscsi.scsi_cdb_passthrough16 import PassThrough16
from pydiskcmd.pyscsi.scsi_cdb_passthrough12 import PassThrough12
import pydiskcmd.utils.converter as convert
from pydiskcmd.pysata.sata_spec import SMART_KEY


class SmartReadData(PassThrough16):
    """
    A class to send smart command to a ATA device
    """
    # 386~510  用户定义
    _standard_bits = SMART_KEY

    def __init__(self,
                 opcode,
                 blocksize,
                 smart_key=None):
        PassThrough16.__init__(self,
                             opcode,
                             blocksize,
                             0xC24F << 8, # lba
                             0x4,         # protocal
                             2,           # t_length
                             1,           # t_dir
                             0xD0,        # features
                             0x1,         # sector_count
                             0xB0,        # command
                             ck_cond=1)
        if smart_key:
            Smart._standard_bits.update(smart_key)

    @classmethod
    def unmarshall_datain(cls, data):
        """
        Unmarshall the Identify datain buffer

        :param data: a byte array with inquiry data
        :return result: a dict
        """
        result = {}
        convert.decode_bits(data,
                            cls._standard_bits,
                            result)
        return result


class SmartReadThresh(PassThrough16):
    """
    A class to send smart command to a ATA device
    """
    def __init__(self,
                 opcode,
                 blocksize,):
        PassThrough16.__init__(self,
                             opcode,
                             blocksize,
                             0xC24F << 8, # lba
                             0x4,         # protocal
                             2,           # t_length
                             1,           # t_dir
                             0xD1,        # features
                             0x1,         # sector_count
                             0xB0,        # command
                             ck_cond=1)


class SmartExeOffLineImm(PassThrough16):
    """
    A class to send SMART EXECUTE OFF-LINE IMMEDIATE command to a ATA device
    """
    def __init__(self,
                 opcode,
                 blocksize,
                 subcommand):
        #             LL(8:15)     LL(0:7)       LM(8:15)       LM(0:7)        LH(8:15)       LH(0:7)
        lba_filed = subcommand + (0x4F << 8) + (0xC2 << 16) + (0x00 << 24) + (0x00 << 32) + (0x00 << 40)
        ##
        PassThrough16.__init__(self,
                             opcode,
                             blocksize,
                             lba_filed,   # lba
                             0x3,         # protocal
                             0,           # t_length
                             0,           # t_dir
                             0xD4,        # features
                             0,           # sector_count
                             0xB0,        # command
                             ck_cond=1)
    