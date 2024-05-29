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
from pydiskcmdlib.pysata.ata_command import ATACommand16,ProtocalMap,TransferDirection


class ReadVerifySectorEXT(ATACommand16):
    """
    A class to send ReadVerifySectorEXT command to a ATA device.
    """
    def __init__(self,
                 lba,
                 tl,):
        ATACommand16.__init__(self,
                              0,         # fetures
                              tl,        # count
                              lba,       # lba
                              0,         # device
                              0x42,      # command
                              ProtocalMap.NonData.value,      # protocal
                              0,         # t_length
                              TransferDirection.NonData.value)         # t_dir


class ReadVerifySector(ATACommand16):
    """
    A class to send ReadVerifySector command to a ATA device.
    """
    def __init__(self,
                 lba,
                 tl,):
        ATACommand16.__init__(self,
                              0,         # fetures
                              tl,        # count
                              lba,       # lba
                              0,         # device
                              0x42,      # command
                              ProtocalMap.NonData.value,      # protocal
                              0,         # t_length
                              TransferDirection.NonData.value)         # t_dir
