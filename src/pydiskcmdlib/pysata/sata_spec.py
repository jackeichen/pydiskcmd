# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later

from pydiskcmdlib.utils.converter import decode_bits,scsi_ba_to_int


SMART_KEY = {'smartRevision': ['b', 0, 2],
             'smartInfo': ['b', 2, 360],    # vendor_spec smart
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
             'checkSum':['b', 511, 1], }

Identify_Info = {'GeneralConfiguration': ['b',0,2],
                 'SerialNumber': ['b',20,20],
                 'FirmwareRevision': ['b',46,8],
                 'ModelNumber': ['b',54,40],
                 'DRQLBAMax': ['b',94,2],
                 'TrustedComputingSet': ['b',96,2],
                 'Capabilities': ['b',98,2],
                 'UltraDMAModes': ['b',176,2],
                 'NormalEraseTime': ['b',178,2],
                 'EnhancedEraseTime': ['b',180,2],
                 'CurrentAPMLevel': ['b',182,2],
                 'MasterPasswordIdentifier': ['b',184,2],
                 'HardwareResetResult': ['b',186,2],
                 'TotalUserLBA': ['b', 200, 8],
                 'WorldWideName': ['b',216,8],
                 'IntegrityWord': ['b',510,2],
                }

VSSmartPerAttrBitMap = {"ID": ['b', 0, 1],
                        "flag": ['b', 1, 2],
                        "value": ['b', 3, 1],
                        "worst": ['b', 4, 1],
                        "raw_value": ['b', 5, 6],
                         "reserved": ['b', 11, 1],
                        }

SmartFlagBitMap = {"Pre-fail": [0x01, 0],
                   "OnlineBit": [0x02, 0],
                   "PerformanceType": [0x04, 0],
                   "ErrorRate": [0x08, 0],
                   "Eventcount": [0x10, 0],
                   "Selfpereserving": [0x20, 0],
                  }


ReadLogLogDirectoryBitMap = {i: ['b', i*2, 2] for i in range(1, 256)}
ReadLogLogDirectoryBitMap["LoggingVersion"] = ['b', 0, 2]
SmartReadLogLogDirectoryBitMap = {i: ['b', i*2, 1] for i in range(1, 256)}
SmartReadLogLogDirectoryBitMap["LoggingVersion"] = ['b', 0, 2]


ReadLogExtendedSelftestLogBitMap = {"revision number": ['b', 0, 1],
                                    "descriptor index": ['b', 2, 2],
                                    "entry": ['b', 4, 494],
                                    "checksum": ['b', 511, 1],
                                    }

ExtendedSelftestLogDsrEntryBitMap = {"subcommand_lba": ['b', 0, 1],
                                     "status": ['b', 1, 1],
                                     "life_timestamp": ['b', 2, 2],
                                     "failure_checkpoint": ['b', 4, 1],
                                     "failing_lba": ['b', 5, 6],
                                     "vendor_spec": ['b', 11, 15],
                                     }
