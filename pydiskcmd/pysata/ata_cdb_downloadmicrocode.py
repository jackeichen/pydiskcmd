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
from pydiskcmd.pyscsi.scsi_cdb_passthrough16 import PassThrough16


class DownloadMicrocode(PassThrough16):
    """
    A class to send download microcode command to a ATA device
    """
    def __init__(self,
                 opcode,
                 blocksize,
                 lba,
                 tl,
                 data,
                 feature=0x03):
        count_l = (tl & 0xff)
        count_h = (tl >> 8)
        lba_pass = (lba << 8) + count_h
        PassThrough16.__init__(self,
                             opcode,
                             blocksize,
                             lba_pass, # lba
                             0x5,      # protocal, 0x5: PIO Data-Out
                             2,        # t_length 
                             0,        # t_dir
                             feature,  # feature
                             count_l,  # sector_count
                             0x92,     # command
                             dataout=data,
                             ck_cond=1)


class ActivateMicrocode(PassThrough16):
    """
    A class to send activate download microcode command to a ATA device
    """
    def __init__(self,
                 opcode,
                 blocksize):
        PassThrough16.__init__(self,
                             opcode,
                             blocksize,
                             0,        # lba
                             0x3,      # protocal, 0x3: Non-data
                             0,        # t_length, 00h: No data is transferred
                             0,        # t_dir, this field shall be ignored when T_Length=0
                             0x0F,     # feature
                             0,        # sector_count
                             0x92,     # command
                             ck_cond=1)

        