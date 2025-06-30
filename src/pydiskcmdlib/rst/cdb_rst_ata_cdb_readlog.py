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
from .cdb_rst_ata_passthr import RSTATAPass16, ATA_DATA_TRANSFER_DIRECTION


class ReadLogExt(RSTATAPass16):
    """
    A class to send smart command to a ATA device
    """
    def __init__(self,
                 phy_id,
                 port_id,
                 sas_addr,
                 count,
                 log_address,
                 page_number,
                 feature=0,
                 ):
        lba = log_address + ((page_number & 0xFF) << 8) + (((page_number >> 8) & 0xFF) << 32)
        RSTATAPass16.__init__(self,
                              phy_id,
                              port_id,
                              sas_addr,
                              0x2F,        # command
                              feature,     # fetures
                              lba,         # lba
                              0,           # device
                              count,       # count
                              ATA_DATA_TRANSFER_DIRECTION.DATA_IN.value, # 0 for NO_DATA, 1 for DATA_IN, 2 for DATA_OUT
                              data_len=512*count, # data_len
                              )
