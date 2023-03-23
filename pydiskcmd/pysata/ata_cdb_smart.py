# coding: utf-8

# Copyright (C) 2020 by Eric Gao<Eric-1128@outlook.com>
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
from pydiskcmd.pysata.ata_command import ATACommand12
from pydiskcmd.pysata.ata_command import ATACommand16
import pydiskcmd.utils.converter as convert
from pydiskcmd.pysata.sata_spec import SMART_KEY


class SmartReadData(ATACommand12):
    """
    A class to send smart command to a ATA device
    """
    # 386~510  用户定义
    _standard_bits = SMART_KEY

    def __init__(self,
                 smart_key=None):
        ##
        # count is not used by samrt read data in ATA command set,
        # so use it in ATAPassthrouh12, for setting transfer length
        ##
        ATACommand12.__init__(self,
                              0xD0,        # fetures
                              1,           # count
                              0xC24F << 8, # lba
                              0,           # device
                              0xB0,        # command
                              0x04,        # protocal
                              2,           # t_length
                              1)           # t_dir           

        if smart_key:
            SmartReadData._standard_bits.update(smart_key)

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


class SmartReadData16(ATACommand16):
    """
    A class to send smart command to a ATA device
    """
    # 386~510  用户定义
    _standard_bits = SMART_KEY

    def __init__(self,
                 smart_key=None):
        ##
        # count is not used by samrt read data in ATA command set,
        # so use it in ATAPassthrouh16, for setting transfer length
        ##
        ATACommand16.__init__(self,
                              0xD0,        # fetures
                              1,           # count
                              0xC24F << 8, # lba
                              0,           # device
                              0xB0,        # command
                              0x04,        # protocal
                              2,           # t_length
                              1)           # t_dir           

        if smart_key:
            SmartReadData._standard_bits.update(smart_key)

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


class SmartReadThresh(ATACommand12):
    """
    A class to send smart command to a ATA device
    """
    def __init__(self):
        ##
        # count is not used by samrt read thresh in ATA command set,
        # so use it in ATAPassthrouh12, for setting transfer length
        ##
        ATACommand12.__init__(self,
                              0xD1,        # fetures
                              1,           # count
                              0xC24F << 8, # lba
                              0,           # device
                              0xB0,        # command
                              0x04,        # protocal
                              2,           # t_length
                              1)           # t_dir


class SmartReadThresh16(ATACommand16):
    """
    A class to send smart command to a ATA device
    """
    def __init__(self):
        ##
        # count is not used by samrt read thresh in ATA command set,
        # so use it in ATAPassthrouh12, for setting transfer length
        ##
        ATACommand16.__init__(self,
                              0xD1,        # fetures
                              1,           # count
                              0xC24F << 8, # lba
                              0,           # device
                              0xB0,        # command
                              0x04,        # protocal
                              2,           # t_length
                              1)           # t_dir


class SmartExeOffLineImm(ATACommand12):
    """
    A class to send SMART EXECUTE OFF-LINE IMMEDIATE command to a ATA device
    """
    def __init__(self,
                 subcommand):
        #             LL(8:15)     LL(0:7)       LM(8:15)       LM(0:7)        LH(8:15)       LH(0:7)
        lba_filed = subcommand + (0x4F << 8) + (0xC2 << 16) + (0x00 << 24) + (0x00 << 32) + (0x00 << 40)
        ##
        ATACommand12.__init__(self,
                              0xD4,        # fetures
                              0,           # count
                              lba_filed,   # lba
                              0,           # device
                              0xB0,        # command
                              0x03,        # protocal
                              0,           # t_length
                              0,           # t_dir
                              )


class SmartExeOffLineImm16(ATACommand16):
    """
    A class to send SMART EXECUTE OFF-LINE IMMEDIATE command to a ATA device
    """
    def __init__(self,
                 subcommand):
        #             LL(8:15)     LL(0:7)       LM(8:15)       LM(0:7)        LH(8:15)       LH(0:7)
        lba_filed = subcommand + (0x4F << 8) + (0xC2 << 16) + (0x00 << 24) + (0x00 << 32) + (0x00 << 40)
        ##
        ATACommand16.__init__(self,
                              0xD4,        # fetures
                              0,           # count
                              lba_filed,   # lba
                              0,           # device
                              0xB0,        # command
                              0x03,        # protocal
                              0,           # t_length
                              0,           # t_dir
                              )


class SmartReadLog16(ATACommand16):
    """
    A class to send SMART EXECUTE OFF-LINE IMMEDIATE command to a ATA device
    """
    def __init__(self,
                 count,
                 log_address):
        #      
        lba_filed = log_address + (0xC24F << 8)
        ##
        ATACommand16.__init__(self,
                              0xD5,        # fetures
                              count,       # count
                              lba_filed,   # lba
                              0,           # device
                              0xB0,        # command
                              0x04,        # protocal
                              2,           # t_length
                              1,           # t_dir
                              )
