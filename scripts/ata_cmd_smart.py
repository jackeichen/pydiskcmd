#!/usr/bin/env python
# coding: utf-8
import sys
import pydiskcmd.pysata.sata
import pydiskcmd.utils
import binascii
#from pyscsi.utils.bytearray_converter import prtsmartinfo

SMART_KEY = {'normalizedEraseCount': ['b',386,1],
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
             'vendorSpecific4[5]': ['b',506,5]}

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


def usage():
    print('Usage: smart.py <device>')
    print ('')

def bytearray2hex_l(data,start,offset):
    a = data[start:start+offset][::-1]
    t = binascii.hexlify(a)
    return int(t,16)

def main(device):
    with pydiskcmd.pysata.sata.SATA(device, 512) as s:
        data = s.smart(SMART_KEY).result
        vs_smart = data.pop('smartInfo')
        general_smart = data

    print ('General SMART Values:')
    print ('=' * 100)
    for name,value in general_smart.items():
        dt = value[::-1]
        r = binascii.hexlify(dt)
        print ('%34s: %-10d [0x%s]' % (name,int(r,16),r.decode()))
    print ('')
    print ('Vendor Specific SMART Attributes with Thresholds:')
    print ('=' * 100)
    print_fomrat = '%3s %-25s %-6s %-6s %-6s %-10s %-10s %-10s %-10s'
    print (print_fomrat %
          ('ID#','ATTRIBUTE_NAME','FLAG','VALUE','WORST','RAW_VALUE0','RAW_V_MIN','RAW_V_MAX','THRESHOLD'))
    print ('-'*100)
    for i in range(0, 359, 12):
        ID = str(vs_smart[i])
        if ID not in SMART_ATTR:
            continue
        print (print_fomrat %
              (ID,                                      # ID
               SMART_ATTR[ID],                          # ATTRIBUTE_NAME
               vs_smart[i+1],                           # FLAG
               vs_smart[i+3],                           # VALUE
               vs_smart[i+4],                           # WORST
               bytearray2hex_l(vs_smart, i+5, 2),       # RAW_VALUE0
               bytearray2hex_l(vs_smart, i+7, 2),       # RAW_V_MIN
               bytearray2hex_l(vs_smart, i+9, 2),       # RAW_V_MAX
               vs_smart[i+11])                          # THRESHOLD
               )

if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(pydiskcmd.utils.init_device(sys.argv[1]))
    else:
        usage()
