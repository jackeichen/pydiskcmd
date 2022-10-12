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


class SanitizeDevice(PassThrough16):
    """
    A class to send Sanitize Device command to a ATA device
    """
    _cmd_error_descriptor = {0: "success", 1:"sense not available", 2:"command abort", 3: "Other errors"}
    def __init__(self,
                 opcode,
                 blocksize,
                 feature):
        values = (0x0000,0x0011,0x0012,0x0013,0x0014,0x0020,0x0040)
        if feature not in values:
            raise RuntimeError("feature should be value in %s" % str(values))
        PassThrough16.__init__(self,
                             opcode,
                             blocksize,
                             0,  #lba
                             3,  #protocal
                             0,  #t_length 
                             1,  #t_dir
                             feature,  #feature
                             0,  #sector_count
                             0xB4, # command
                             ck_cond=1)

