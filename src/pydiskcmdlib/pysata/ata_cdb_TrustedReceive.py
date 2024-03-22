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
from enum import Enum
from pydiskcmdlib.pysata.ata_command import ATACommand16


class SecurityProtocol(Enum):
    TCG_SECURITY_PROTOCOL_INFO      = 0x00
    TCG_OPAL_SECURITY_PROTOCOL_1    = 0x01
    TCG_OPAL_SECURITY_PROTOCOL_2    = 0x02
    TCG_SECURITY_PROTOCOL_TCG3      = 0x03
    TCG_SECURITY_PROTOCOL_TCG4      = 0x04


class TrustedReceiveDMA(ATACommand16):
    """
    A class to send TrustedReceive DMA command to a ATA device
    
    This will be a limitted function, for only 255 blocks can be transferred,
    while blocks will be 1 byte or 512 bytes
    """
    def __init__(self,
                 security_protocol,
                 transfer_length,
                 SP,
                 INC_512=1,
                 ):
        ##
        lba = SP << 8
        if INC_512 == 1:
            byte_block = 1
            t_type = 0
        elif INC_512 == 0:
            byte_block = 0
        else:
            raise RuntimeError("TrustedReceiveDMA by ATA passthrough only support INC_512 0|1")
        ATACommand16.__init__(self,
                              security_protocol,        # fetures
                              transfer_length,          # count
                              lba,                      # lba
                              0,                        # device
                              0x5D,                     # command
                              0x06,                     # protocal
                              2,                        # t_length
                              1,                        # t_dir
                              byte_block=byte_block,    # byte_block
                              t_type=t_type,            # t_type
                              extend=0,                 # 28 bit command
                              )
