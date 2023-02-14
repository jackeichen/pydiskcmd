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


class DownloadMicrocode(ATACommand12):
    """
    A class to send download microcode command to a ATA device
    """
    def __init__(self,
                 lba,
                 count,
                 data,
                 feature=0x03):
        ATACommand12.__init__(self,
                              feature,   # fetures
                              count,     # count
                              lba,       # lba
                              0,         # device
                              0x92,      # command
                              0x05,      # protocal
                              2,         # t_length
                              0,         # t_dir
                              data=data)


class DownloadMicrocode16(ATACommand16):
    """
    A class to send download microcode command to a ATA device
    """
    def __init__(self,
                 lba,
                 count,
                 data,
                 feature=0x03):
        ATACommand16.__init__(self,
                              feature,   # fetures
                              count,     # count
                              lba,       # lba
                              0,         # device
                              0x92,      # command
                              0x05,      # protocal
                              2,         # t_length
                              0,         # t_dir
                              data=data)


class ActivateMicrocode(ATACommand12):
    """
    A class to send activate download microcode command to a ATA device
    """
    def __init__(self):
        ATACommand12.__init__(self,
                              0x0F,      # fetures
                              0,         # count
                              0,         # lba
                              0,         # device
                              0x92,      # command
                              0x03,      # protocal
                              0,         # t_length
                              0)         # t_dir


class ActivateMicrocode16(ATACommand16):
    """
    A class to send activate download microcode command to a ATA device
    """
    def __init__(self):
        ATACommand16.__init__(self,
                              0x0F,      # fetures
                              0,         # count
                              0,         # lba
                              0,         # device
                              0x92,      # command
                              0x03,      # protocal
                              0,         # t_length
                              0)  
