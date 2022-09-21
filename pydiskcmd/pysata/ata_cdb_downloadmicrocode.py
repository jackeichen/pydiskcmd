# coding: utf-8

# Copyright (C) 2014 by Ronnie Sahlberg<ronniesahlberg@gmail.com>
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


class DownloadMicrocodeDMA(PassThrough16):
    """
    A class to send download microcode command to a ATA device
    """
    def __init__(self,
                 opcode,
                 blocksize,
                 lba,
                 tl,
                 data):
        count_h = (tl >> 8)
        lba_pass = (lba << 8) + count_h
        count_l = (tl & 0xff)
        PassThrough16.__init__(self,
                             opcode,
                             blocksize,
                             lba_pass, # lba
                             0x6,      # protocal
                             2,        # t_length 
                             0,        # t_dir
                             3,        # feature
                             count_l,  # sector_count
                             0x93,     # command
                             dataout=data,
                             ck_cond=1)
        