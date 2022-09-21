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
from pydiskcmd.pyscsi.scsi_cdb_passthrough12 import PassThrough12
import pydiskcmd.utils.converter as convert


class Smart(PassThrough16):
    """
    A class to send smart command to a ATA device
    """
    # 386~510  用户定义
    _standard_bits =                     {'smartRevision': ['b', 0, 2],
                                          'smartInfo': ['b', 2, 360],
                                          'offlineStatus': ['b', 362, 1],
                                          'selfTestStatus': ['b', 363, 1],
                                          'offlineDataCollectionTimeInSec': ['b', 364, 2],
                                          'smartFlags':['b', 366, 1],
                                          'offlineDataCollectionCapabilities':['b', 367, 1],
                                          'smart capability':['b', 368, 2],
                                          'Error logging capability':['b', 370, 1],
                                          'VendorSpecific1':['b', 371, 1],
                                          'ShortSelftestPollingTimeInMin':['b', 372, 1],
                                          'longSelftestPollingTimeInMin':['b', 373, 1], #如果是0xFF，用375~376() minutes.
                                          'convSelftestPollingtimeInMin':['b', 374, 1], #() minutes.
                                          'extSelftestPollingTimeInMin':['b', 375, 2],
                                          'reserved[9]':['b', 377, 9],
                                          'normalizedEraseCount': ['b',386,1],
                                          'worstValueForRawRdErrorRate': ['b',387,1],
                                          'BadBlocksBufferUpdated': ['b',388,1],
                                          'nandChanBistTestResult': ['b',389,1],
                                          'selfTestBB': ['b',390,2],
                                          'factoryTestBB': ['b',392,2],
                                          'reserved1': ['b',394,2],
                                          'factoryBadBlocks': ['b',396,4],
                                          'grownBadBlocks': ['b',400,4],
                                          'pendingBadBlocks': ['b',404,4],
                                          'totalHardwareResets': ['b',408,4],
                                          'eccOverLimitCount': ['b',416,8],
                                          'nvWrAuCount': ['b',424,8],
                                          'programFailureCount': ['b',432,4],
                                          'eraseFailureCount': ['b',436,4],
                                          'hostReadSectorCount': ['b',440,8],
                                          'nvRdCountSave': ['b',448,8],
                                          'numSpareBlocks': ['b',456,4],
                                          'sparePercent': ['b',460,4],
                                          'writeAmp': ['b',464,4],
                                          'reserved468': ['b',468,4],
                                          'autoSaveTimerID': ['b',472,4],
                                          'pOfflineQ': ['b',476,4],
                                          'erase2WrRatio': ['b',480,4],
                                          'reserved484': ['b',484,4],
                                          'hostUEccCount': ['b',488,8],
                                          'lastUncorrectablePaa': ['b',496,4],
                                          'lastUncorrectablePOS': ['b',500,4],
                                          'auPerPage': ['b',504,1],
                                          'numOfDie': ['b',505,1],
                                          'vendorSpecific4[5]': ['b',506,5],
                                          'checkSum':['b', 511, 1],}
    
    def __init__(self,
                 opcode,
                 blocksize,
                 smart_key=None):
        PassThrough16.__init__(self,
                             opcode,
                             blocksize,
                             0xC24F << 8, # lba
                             0x4,         # protocal
                             2,           # t_length
                             1,           # t_dir
                             0xD0,        # features
                             0x1,         # sector_count
                             0xB0,        # command
                             ck_cond=1)
        if smart_key:
            self._standard_bits = self._standard_bits.update(smart_key)
    
    @classmethod
    def unmarshall_datain(cls, data):
        """
        Unmarshall the Identify datain buffer

        :param data: a byte array with inquiry data
        :return result: a dict
        """
        result = {}
        convert.decode_bits(data,
                            cls._standard_bits,
                            result)
        return result


class SmartExeOffLineImm(PassThrough16):
    """
    A class to send SMART EXECUTE OFF-LINE IMMEDIATE command to a ATA device
    """
    def __init__(self,
                 opcode,
                 blocksize,
                 subcommand):
        #             LL(8:15)     LL(0:7)       LM(8:15)       LM(0:7)        LH(8:15)       LH(0:7)
        lba_filed = subcommand + (0x4F << 8) + (0xC2 << 16) + (0x00 << 24) + (0x00 << 32) + (0x00 << 40)
        ##
        PassThrough16.__init__(self,
                             opcode,
                             blocksize,
                             lba_filed,   # lba
                             0x3,         # protocal
                             0,           # t_length
                             0,           # t_dir
                             0xD4,        # features
                             0,           # sector_count
                             0xB0,        # command
                             ck_cond=1)
    