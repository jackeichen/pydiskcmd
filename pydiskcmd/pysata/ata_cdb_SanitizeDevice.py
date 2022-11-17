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
from pydiskcmd.pysata.ata_command import ATACommand16
from pydiskcmd.utils.converter import scsi_ba_to_int


class SanitizeDevice(ATACommand16):
    """
    A class to send Sanitize Device command to a ATA device
    """
    _cmd_error_descriptor = {0: "success", 1:"sense not available", 2:"command abort", 3: "Other errors"}
    def __init__(self,
                 feature,
                 count,
                 over_write_pattern=b''):
        if feature == 0x0012:
            lba = 0x4572 + (0x426B << 16)
        elif feature == 0x0011:
            lba = 0x7970 + (0x4372 << 16)
        elif feature == 0x0014 and over_write_pattern:
            lba = scsi_ba_to_int(over_write_pattern, 'little') + (0x4F57 << 32)
        elif feature == 0x0040:
            lba = 0x7469 + (0x416E << 16)
            count = 0
        elif feature == 0x0020:
            lba = 0x4C6B + (0x4672 << 16)
            count = 0
        elif feature == 0:
            lba = 0
        else:
            raise RuntimeError("feature(%s) invalid" % feature)
        
        ATACommand16.__init__(self,
                              feature,   # fetures
                              count,     # count
                              lba,       # lba
                              0,         # device
                              0xB4,      # command
                              0x03,      # protocal
                              0,         # t_length
                              0)         # t_dir
