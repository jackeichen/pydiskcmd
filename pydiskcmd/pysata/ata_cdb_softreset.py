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


class SoftReset(PassThrough16):
    """
    A class to send soft reset command to a ATA device
    
    If the PROTOCOL field is set to a value of 1 the SATL shall issue a soft reset to the attached ATA 
    device (see ATA/ATAPI-7). When this protocol is selected, only the PROTOCOL and OFF_LINE
    fields are valid. The SATL shall ignore all other fields in the CDB.
    """
    
    def __init__(self,
                 opcode,
                 blocksize):
        PassThrough16.__init__(self,
                             opcode,
                             blocksize,
                             0,  #lba
                             1,  #protocal
                             0,  #t_length 
                             0,  #t_dir
                             0,  #feature
                             0,  #sector_count
                             0,  # command
                             ck_cond=1,
                             off_line=3)

        