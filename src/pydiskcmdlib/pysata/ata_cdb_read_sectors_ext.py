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
from pydiskcmdlib.pysata.ata_command import ATACommand16,ProtocalMap


class ReadSectorsEXT16(ATACommand16):
    """
    A class to send read sector(s) EXT command to a ATA device.
    """
    def __init__(self,
                 lba,
                 tl,
                 blocksize):
        ATACommand16.__init__(self,
                              0,         # fetures
                              tl,        # count
                              lba,       # lba
                              0,         # device
                              0x24,      # command
                              ProtocalMap.PIODataIn.value,      # protocal
                              2,         # t_length
                              1,         # t_dir
                              t_type=1,
                              byte_block=1,
                              blocksize=blocksize) 
