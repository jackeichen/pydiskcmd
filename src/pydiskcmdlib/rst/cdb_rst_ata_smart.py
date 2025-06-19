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
from .cdb_rst_ata_passthr import RSTATAPass12, RSTATAPass16, ATA_DATA_TRANSFER_DIRECTION
import pydiskcmdlib.utils.converter as convert
from pydiskcmdlib.pysata.sata_spec import SMART_KEY


class SmartReadData(RSTATAPass12):
    """
    A class to send smart command to a ATA device
    """
    # 386~510  vendor spec
    _standard_bits = SMART_KEY

    def __init__(self,
                 phy_id,
                 port_id,
                 sas_addr,
                 smart_key=None):
        RSTATAPass12.__init__(self,
                              phy_id,
                              port_id,
                              sas_addr,
                              0xB0,        # command
                              0xD0,        # fetures
                              0xC24F << 8, # lba
                              0,           # device
                              0,           # count
                              ATA_DATA_TRANSFER_DIRECTION.DATA_IN.value, # 0 for NO_DATA, 1 for DATA_IN, 2 for DATA_OUT
                              data_len=512, # data_len
                              )

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


class SmartReadData16(RSTATAPass16):
    """
    A class to send smart command to a ATA device
    """
    # 386~510  vendor spec
    _standard_bits = SMART_KEY

    def __init__(self,
                 phy_id,
                 port_id,
                 sas_addr,
                 smart_key=None):
        RSTATAPass16.__init__(self,
                              phy_id,
                              port_id,
                              sas_addr,
                              0xB0,        # command
                              0xD0,        # fetures
                              0xC24F << 8, # lba
                              0,           # device
                              0,           # count
                              ATA_DATA_TRANSFER_DIRECTION.DATA_IN.value, # 0 for NO_DATA, 1 for DATA_IN, 2 for DATA_OUT
                              data_len=512, # data_len
                              )                

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


class SmartReadThresh(RSTATAPass12):
    """
    A class to send smart command to a ATA device
    """
    def __init__(self,
                 phy_id,
                 port_id,
                 sas_addr,):
        RSTATAPass12.__init__(self,
                              phy_id,
                              port_id,
                              sas_addr,
                              0xB0,        # command
                              0xD1,        # fetures
                              0xC24F << 8, # lba
                              0,           # device
                              0,           # count
                              ATA_DATA_TRANSFER_DIRECTION.DATA_IN.value, # 0 for NO_DATA, 1 for DATA_IN, 2 for DATA_OUT
                              data_len=512, # data_len
                              )


class SmartReadThresh16(RSTATAPass16):
    """
    A class to send smart command to a ATA device
    """
    def __init__(self,
                 phy_id,
                 port_id,
                 sas_addr,
                 ):
        RSTATAPass16.__init__(self,
                              phy_id,
                              port_id,
                              sas_addr,
                              0xB0,        # command
                              0xD1,        # fetures
                              0xC24F << 8, # lba
                              0,           # device
                              0,           # count
                              ATA_DATA_TRANSFER_DIRECTION.DATA_IN.value, # 0 for NO_DATA, 1 for DATA_IN, 2 for DATA_OUT
                              data_len=512, # data_len
                              )
