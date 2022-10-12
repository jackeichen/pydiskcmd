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


class ReadDMAEXT16(PassThrough16):
    """
    A class to send read dma command to a ATA device.
    """
    def __init__(self,
                 opcode,
                 blocksize,
                 lba,
                 tl,):
        PassThrough16.__init__(self,
                             opcode,
                             blocksize,
                             lba,
                             0x6,
                             2,
                             1,
                             0,
                             tl,
                             0x25,
                             ck_cond=1)
        