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


class WriteLogExt(ATACommand16):
    """
    A class to send WriteLogExt command to a ATA device

    This command writes a specified number of 512 byte data logical sectors to the specified log.
    """
    def __init__(self,
                 count,         # Sector Count - Specifies the number of log pages that shall be written to the specified log
                 log_address,   # Log Address - Specifies the log to be written as described in Table 29. A device may support a subset of the available logs
                 page_number, # Sector Offset - Specifies the first logical sector of the log to be written.
                 data=None,
                 ):
        lba = log_address + ((page_number & 0xFF) << 8) + (((page_number >> 8) & 0xFF) << 32)
        ATACommand16.__init__(self,
                              0,         # fetures
                              count,     # count, log page address
                              lba,       # lba
                              0,         # device
                              0x3F,      # command
                              ProtocalMap.PIODataOut.value,      # protocal
                              1,         # t_length
                              TransferDirection.Host2Device.value, # t_dir 
                              byte_block=1,
                              t_type=0,
                              data=data,)


class WriteLogDMAExt(ATACommand16):
    """
    A class to send WriteLogExt command to a ATA device

    This command writes a specified number of 512 byte data logical sectors to the specified log.
    """
    def __init__(self,
                 count,         # Sector Count - Specifies the number of log pages that shall be written to the specified log
                 log_address,   # Log Address - Specifies the log to be written as described in Table 29. A device may support a subset of the available logs
                 page_number, # Sector Offset - Specifies the first logical sector of the log to be written.
                 data=None,
                 ):
        lba = log_address + ((page_number & 0xFF) << 8) + (((page_number >> 8) & 0xFF) << 32)
        ATACommand16.__init__(self,
                              0,         # fetures
                              count,     # count, log page address
                              lba,       # lba
                              0,         # device
                              0x57,      # command
                              ProtocalMap.DMA.value,      # protocal
                              1,         # t_length
                              TransferDirection.Host2Device.value, # t_dir 
                              byte_block=1,
                              t_type=0,
                              data=data,)
