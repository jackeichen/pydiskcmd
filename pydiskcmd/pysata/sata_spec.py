# SPDX-FileCopyrightText: 2014 The python-scsi Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmd.utils.converter import decode_bits,scsi_ba_to_int


SMART_KEY = {'smartRevision': ['b', 0, 2],
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
             'checkSum':['b', 511, 1], }


SMART_ATTR = {'1':'Raw_Read_Error_Rate',                     # Not
              '5':'Reallocated_Sector_Ct',
              '9':'Power_On_Hours',
              '12':'Power_Cycle_Count',
              '100':'Unknown_Attribute',                     # not
              '101':'Unknown_Attribute',                     #
              '170':'Unknown_Attribute',
              '171':'Unknown_Attribute',
              '172':'Unknown_Attribute',
              '174':'Unknown_Attribute',
              '175':'Program_Fail_Count_Chip',
              '176':'Erase_Fail_Count_Chip',
              '177':'Wear_Leveling_Count',
              '178':'Used_Rsvd_Blk_Cnt_Chip',
              '180':'Unused_Rsvd_Blk_Cnt_Tot',
              '183':'Runtime_Bad_Block',
              '187':'Reported_Uncorrect',
              '194':'Temperature_Celsius',
              '195':'Hardware_ECC_Recovered',
              '196':'Reallocated_Event_Count',
              '197':'Current_Pending_Sector',
              '199':'UDMA_CRC_Error_Count',
              '201':'Unknown_SSD_Attribute',
              '204':'Soft_ECC_Correction',
              '231':'Temperature_Celsius',
              '233':'Media_Wearout_Indicator',
              '234':'Unknown_Attribute',
              '241':'Total_LBAs_Written',
              '242':'Total_LBAs_Read',
              '250':'Read_Error_Retry_Rate', }

Identify_Info = {'GeneralConfiguration': ['b',0,2],
                 'SerialNumber': ['b',20,20],
                 'FirmwareRevision': ['b',46,8],
                 'ModelNumber': ['b',54,40],
                 'Capabilities': ['b',98,4],
                 'UltraDMAModes': ['b',176,2],
                 'NormalEraseTime': ['b',178,2],
                 'EnhancedEraseTime': ['b',180,2],
                 'CurrentAPMLevel': ['b',182,2],
                 'MasterPasswordIdentifier': ['b',184,2],
                 'HardwareResetResult': ['b',186,2],
                 'Capacity': ['b', 200, 4],
                 'WorldWideName': ['b',216,8],
                 'IntegrityWord': ['w',510,2],
                }

Identify_Element_Type = {"FirmwareRevision": 'string',
                         "SerialNumber": 'string',
                         "Capacity": 'int',
                         "ModelNumber": 'string'}

SmartFlagBitMap = {"Pre-fail": [0x01, 0],
                   "OnlineBit": [0x02, 0],
                   "PerformanceType": [0x04, 0],
                   "ErrorRate": [0x08, 0],
                   "Eventcount": [0x10, 0],
                   "Selfpereserving": [0x20, 0],
                  }


class SmartAttr(object):
    def __init__(self, raw_data):
        self.id = raw_data[0]
        if str(self.id) in SMART_ATTR:
            self.attr_name = SMART_ATTR[str(self.id)]
        else:
            self.attr_name = 'Unknown_Attribute'
        self.flag = bytes(raw_data[1:3])
        self.value = raw_data[3]
        self.worst = raw_data[4]
        self.raw_value = bytes(raw_data[5:11])

    @property
    def raw_value_int(self):
        return scsi_ba_to_int(self.raw_value,'little')

    @property
    def flag_int(self):
        return scsi_ba_to_int(self.flag,'little')


class SmartThresh(object):
    def __init__(self, raw_data):
        self.id = raw_data[0]
        self.thresh = raw_data[1]


def decode_smart_info(smart_info_raw):
    smart = {}
    ##
    for i in range(0, 359, 12):
        smart_attr = SmartAttr(smart_info_raw[i:(i+12)])
        if smart_attr.id != 0:
            smart[smart_attr.id] = smart_attr
    return smart

def decode_smart_thresh(smart_info_raw):
    smart_thresh_map = {}
    ##
    for i in range(0, 359, 12):
        smart_thresh = SmartThresh(smart_info_raw[i:(i+12)])
        if smart_thresh.id != 0:
            smart_thresh_map[smart_thresh.id] = smart_thresh.thresh
    return smart_thresh_map 

def decode_smart_flag(raw_data):
    result = {}
    decode_bits(raw_data, SmartFlagBitMap, result)
    return result
