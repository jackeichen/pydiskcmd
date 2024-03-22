#!/usr/bin/env python
# coding: utf-8
import sys
from pydiskcmdlib.pysata.sata import SATA
from pydiskcmdlib.utils import init_device
import binascii
from pydiskcmdcli.sata_spec import decode_smart_info,decode_smart_thresh
from pydiskcmdlib.utils.converter import scsi_ba_to_int

def usage():
    print('Usage: smart.py <device>')
    print ('')

def bytearray2hex_l(data,start,offset):
    a = data[start:start+offset][::-1]
    t = binascii.hexlify(a)
    return int(t,16)

def main(device):
    with SATA(device, 512) as s:
        data = s.smart_read_data().result
        vs_smart = data.pop('smartInfo')
        general_smart = data
        ##
        cmd_thresh = s.smart_read_thresh()
        raw_data_thresh = cmd_thresh.datain
    ##
    smart_thresh = decode_smart_thresh(raw_data_thresh[2:362])
    ##
    print ('General SMART Values:')
    print ('=' * 100)
    for name,value in general_smart.items():
        dt = value[::-1]
        r = binascii.hexlify(dt)
        print ('%34s: %-10d [0x%s]' % (name,int(r,16),r.decode()))
    print ('')
    print ('Vendor Specific SMART Attributes with Thresholds:')
    print ('=' * 100)
    print_fomrat = '%3s %-25s %-6s %-6s %-6s %-10s %-10s'
    print (print_fomrat %
          ('ID#','ATTRIBUTE_NAME','FLAG','VALUE','WORST','THRESHOLD','RAW_VALUE'))
    print ('-'*100)
    print_fomrat = '%3s %-25s %#-6x %-6s %-6s %-10s %-10s'
    smart_dict = decode_smart_info(vs_smart)
    for _id,s in smart_dict.items():
        print (print_fomrat % (
               s.id,                                  # ID
               s.attr_name,                           # ATTRIBUTE_NAME
               scsi_ba_to_int(s.flag, 'little'),      # FLAG
               s.value,                               # VALUE
               s.worst,                               # WORST
               smart_thresh[s.id],                    # THRESHOLD
               scsi_ba_to_int(s.raw_value,'little'),) # RAW_VALUE
               #bytearray2hex_l(vs_smart, i+5, 2),    # RAW_VALUE
               )

if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(init_device(sys.argv[1]))
    else:
        usage()
