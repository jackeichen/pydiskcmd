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


class CheckPowerMode16(RSTATAPass16):
    """
    A class to send CheckPowerMode command to a ATA device
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
                              0xe5,      # command
                              0,         # fetures
                              0,         # lba
                              0,         # device
                              0,         # count
                              ATA_DATA_TRANSFER_DIRECTION.NO_DATA.value, # 0 for NO_DATA, 1 for DATA_IN, 2 for DATA_OUT
                              data_len=0, # data_len
                              )
