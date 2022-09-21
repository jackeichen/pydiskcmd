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


class CheckPowerMode(PassThrough16):
    """
    A class to send CheckPowerMode command to a ATA device
    """
    def __init__(self,
                 opcode,
                 blocksize):
        PassThrough16.__init__(self,
                             opcode,
                             blocksize,
                             0,  #lba
                             3,  #protocal
                             0,  #t_length 
                             1,  #t_dir
                             0,  #feature
                             0,  #sector_count
                             0xe5, # command
                             ck_cond=1,)