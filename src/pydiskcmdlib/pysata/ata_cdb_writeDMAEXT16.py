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
from pydiskcmdlib.pysata.ata_command import ATACommand16


class WriteDMAEXT16(ATACommand16):
    """
    A class to send write dma command to a ATA device
    """
    def __init__(self,
                 lba,
                 count,
                 data,
                 blocksize):
        if count == 0:
            count = 65536
        ATACommand16.__init__(self,
                              0,         # fetures
                              count,     # count
                              lba,       # lba
                              0,         # device
                              0x35,      # command
                              0x06,      # protocal
                              2,         # t_length
                              0,         # t_dir
                              data=data,
                              t_type=1,
                              byte_block=1,
                              blocksize=blocksize) 
