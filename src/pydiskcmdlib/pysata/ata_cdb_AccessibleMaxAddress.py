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
from pydiskcmdlib.pysata.ata_command import ATACommand16


class AccessibleMaxAddressCfg(ATACommand16):
    """
    A class to send GetAccessibleMaxAddress command to a ATA device

    AccessibleMaxAddressCfg is 48 bit command
    """
    #_cmd_error_descriptor = {0: "success", 1:"sense not available", 2:"command abort", 3: "Other errors"}
    def __init__(self,
                 feature):
        if feature not in (0,1,2):
            raise RuntimeError("feature should be 0/1/2")
        ATACommand16.__init__(self,
                              feature,   # fetures
                              0,         # count
                              0,         # lba
                              0,         # device
                              0x78,      # command
                              0x03,      # protocal
                              0,         # t_length
                              0)         # t_dir

