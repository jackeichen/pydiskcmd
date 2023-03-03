# coding: utf-8

# Copyright (C) 2022 by Ronnie Sahlberg<ronniesahlberg@gmail.com>
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
from pydiskcmd.pysata.sata_spec import Identify_Info
import pydiskcmd.utils.converter as convert


class Identify(ATACommand12):
    """
    A class to send identify command to a ATA device
    """
    _standard_bits =  Identify_Info

    def __init__(self):
        ##
        # count is not used by identify in ATA command set,
        # so use it in ATAPassthrouh12, for setting transfer length
        ##
        ATACommand12.__init__(self,
                              0,         # fetures
                              1,         # count
                              0,         # lba
                              0,         # device
                              0xec,      # command
                              0x04,      # protocal
                              2,         # t_length
                              1)         # t_dir

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


class Identify16(ATACommand16):
    """
    A class to send identify command to a ATA device
    """
    _standard_bits =  Identify_Info

    def __init__(self):
        ##
        # count is not used by identify in ATA command set,
        # so use it in ATAPassthrouh16, for setting transfer length
        ##
        ATACommand16.__init__(self,
                              0,         # fetures
                              1,         # count
                              0,         # lba
                              0,         # device
                              0xec,      # command
                              0x04,      # protocal
                              2,         # t_length
                              1)         # t_dir 

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
