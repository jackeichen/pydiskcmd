# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later

from pydiskcmd.utils.converter import decode_bits,scsi_ba_to_int


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


SMART_ATTR = {1: "Raw_Read_Error_Rate ",
              2: "Throughput_Performance ",
              3: "Spin_Up_Time ",
              4: "Start_Stop_Count ",
              5: "Reallocated_Sector_Ct ",
              6: "Read_Channel_Margin ",
              7: "Seek_Error_Rate ",
              8: "Seek_Time_Performance ",
              9: "Power_On_Hours ",
              10: "Spin_Retry_Count ",
              11: "Calibration_Retry_Count ",
              12: "Power_Cycle_Count ",
              13: "Read_Soft_Error_Rate ",
              100:'Unknown_Attribute',                     # not
              101:'Unknown_Attribute',                     #
              170:'Unknown_Attribute',
              171:'Unknown_Attribute',
              172:'Unknown_Attribute',
              174:'Unknown_Attribute',
              175: "Program_Fail_Count_Chip ",
              176: "Erase_Fail_Count_Chip ",
              177: "Wear_Leveling_Count ",
              178: "Used_Rsvd_Blk_Cnt_Chip ",
              179: "Used_Rsvd_Blk_Cnt_Tot ",
              180: "Unused_Rsvd_Blk_Cnt_Tot ",
              181: "Program_Fail_Cnt_Total ",
              182: "Erase_Fail_Count_Total ",
              183: "Runtime_Bad_Block ",
              184: "End-to-End_Error ",
              187: "Reported_Uncorrect ",
              188: "Command_Timeout ",
              189: "High_Fly_Writes ",
              190: "Airflow_Temperature_Cel ",
              191: "G-Sense_Error_Rate ",
              192: "Power-Off_Retract_Count ",
              193: "Load_Cycle_Count ",
              194: "Temperature_Celsius ",
              195: "Hardware_ECC_Recovered ",
              196: "Reallocated_Event_Count ",
              197: "Current_Pending_Sector ",
              198: "Offline_Uncorrectable ",
              199: "UDMA_CRC_Error_Count ",
              200: "Multi_Zone_Error_Rate ",
              201: "Soft_Read_Error_Rate ",
              202: "Data_Address_Mark_Errs ",
              203: "Run_Out_Cancel ",
              204: "Soft_ECC_Correction ",
              205: "Thermal_Asperity_Rate ",
              206: "Flying_Height ",
              207: "Spin_High_Current ",
              208: "Spin_Buzz ",
              209: "Offline_Seek_Performnce ",
              220: "Disk_Shift ",
              221: "G-Sense_Error_Rate ",
              222: "Loaded_Hours ",
              223: "Load_Retry_Count ",
              224: "Load_Friction ",
              225: "Load_Cycle_Count ",
              226: "Load-in_Time ",
              227: "Torq-amp_Count ",
              228: "Power-off_Retract_Count ",
              230: "Head_Amplitude ",
              231: "Temperature_Celsius ",
              232: "Available_Reservd_Space ",
              233: "Media_Wearout_Indicator ",
              240: "Head_Flying_Hours ",
              241: "Total_LBAs_Written ",
              242: "Total_LBAs_Read ",
              250: "Read_Error_Retry_Rate ",
              254: "Free_Fall_Sensor "
             }


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

ReadLogLogDirectoryDescription = {0: "Log directory",
                                  1: "Summary SMART Error log",
                                  2: "Comprehensive SMART Error log",
                                  3: "Extended Comprehensive SMART Error log",
                                  4: "Device Statistics",
                                  5: "Reserved for CFA",
                                  6: "SMART Self-Test log",
                                  7: "Extended SMART Self-Test log",
                                  8: "Power Conditions",
                                  9: "Selective Self-Test log",
                                  10: "Device Statistics Notification",
                                  11: "Reserved for CFA",
                                  12: "Reserved",
                                  13: "LPS Mis-alignment log",
                                  range(14,16): "Reserved",
                                  0x10: "NCQ Command Error log",
                                  0x11: "SATA Phy Event Counters log",
                                  0x12: "SATA NCQ Queue Management log",
                                  0x13: "SATA NCQ Send and Receive log",
                                  range(14,18): "Reserved for Serial ATA",
                                  0x18: "Reserved",
                                  0x19: "LBA Status",
                                  range(0x1A,0x21): "Reserved",
                                  0x21: "Write Stream Error log",
                                  0x22: "Read Stream Error log",
                                  0x23: "Obsolete",
                                  0x24: "Current Device Internal Status Data log",
                                  0x25: "Saved Device Internal Status Data log",
                                  range(0x26,0x30): "Reserved",
                                  0x30: "IDENTIFY DEVICE data",
                                  range(0x31,0x80): "Reserved",
                                  range(0x80,0xA0): "Host Specific",
                                  range(0xA0,0xE0): "Device Vendor Specific",
                                  0xE0: "SCT Command/Status",
                                  0xE1: "SCT Data Transfer",
                                  range(0xE2,0x100): "Reserved",
                                 }


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

SmartExecuteOfflineImmediateSubcommandsDescription = {0: "off-line offline",
                                                      1: "Short offline",
                                                      2: "Extended offline",
                                                      3: "Conveyance offline",
                                                      4: "Selective offline",
                                                      0x7F: "Abort self-test",
                                                      0x81: "Short captive",
                                                      0x82: "Extended captive",
                                                      0x83: "Conveyance captive",
                                                      0x84: "Selective captive",
                                                      }
SelftestExecutionStatusDescription = {0: "Completed without error",
                                      1: "Aborted by host",
                                      2: "Interrupted by host",
                                      3: "Running unfinished",
                                      4: "Unkown failure",
                                      5: "Electrical failure",
                                      6: "Servo/Seek failure",
                                      7: "Read failure",
                                      8: "May handling damage",
                                      15: "In progress",
                                     }


class SmartAttr(object):
    def __init__(self, raw_data):
        self.id = raw_data[0]
        if self.id in SMART_ATTR:
            self.attr_name = SMART_ATTR[self.id]
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

    @property
    def flag_decode(self):
        return decode_smart_flag(self.flag)


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

def decode_read_log_log_directory(raw_data):
    result = {}
    decode_bits(raw_data, ReadLogLogDirectoryBitMap, result)
    for k in list(result.keys()):
        temp = result.pop(k)
        temp = temp[0]+(temp[1]<<8)
        if temp > 0:
            result[k] = temp
    return result

def decode_smart_read_log_log_directory(raw_data):
    result = {}
    decode_bits(raw_data, SmartReadLogLogDirectoryBitMap, result)
    rev = result.pop("LoggingVersion")
    rev = rev[0]+(rev[1]<<8)
    ##
    for k in list(result.keys()):
        temp = result.pop(k)
        temp = temp[0]
        if temp > 0:
            result[k] = temp
    ##
    result["LoggingVersion"] = rev
    return result

def decode_read_log_extend_selftest(raw_data):
    result = []
    if len(raw_data) % 512 == 0:
        offset = 0
        while (offset < len(raw_data)):
            temp = {}
            decode_bits(raw_data[offset:(offset+512)], ReadLogExtendedSelftestLogBitMap, temp)
            if not (temp["revision number"][0] & 0xFF): # not first log
                temp.pop("revision number")
                temp.pop("descriptor index")
                # 
            unused_type = b'\x00' * 26
            entry_raw_data = temp.pop("entry")
            temp["entry"] = []
            for i in range(19):
                raw_d = entry_raw_data[(i*26):(i*26+26)]
                if bytes(raw_d) != unused_type:
                    temp_result = {}
                    decode_bits(raw_d, ExtendedSelftestLogDsrEntryBitMap, temp_result)
                    temp["entry"].append(temp_result)
            ##
            result.append(temp)
            offset += 512
    return result


read_log_decode_set = {0: decode_read_log_log_directory, 7: decode_read_log_extend_selftest,}
smart_read_log_decode_set = {0: decode_smart_read_log_log_directory,}
