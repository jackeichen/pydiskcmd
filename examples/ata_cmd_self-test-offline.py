#!/usr/bin/env python
# coding: utf-8
import sys,os
import pydiskcmdlib

max_short_polling_t = 10 # minutes
##
# OP    Action
# 0     start short-selfTest
# 1     start Extend SlefTest
# 2     NA
# 3     NA

def usage():
    print('Usage: self-test-offline.py <device> <Operation>')
    print ('')
    print ('device:    Device that you need open')
    print ('Operation: 1 ->start short-selfTest, 2->start Extend SlefTest')
    print ('')

def get_para():
    if len(sys.argv) == 3:
        dev = sys.argv[1]
        if not os.path.exists(dev):
            raise RuntimeError("Device not found")
        OP = int(sys.argv[2])
        if OP not in (1,2):
            raise RuntimeError("Operation should be 1|2.")
        return dev,OP
    else:
        usage()
        sys.exit(0)


def main(device, op):
    with pydiskcmdlib.pysata.sata.SATA(device,512) as s:
        print ('issuing self-test command')
        print ("%s:" % device._file_name)
        print ('')
        if op == 1:
            cmd = s.smart()
            data = cmd.result
            #print ('selfTestStatus: ', data['selfTestStatus'])
            print ('ShortSelftestPollingTimeInMin: %s min' % data['ShortSelftestPollingTimeInMin'][0])
            print ('longSelftestPollingTimeInMin: %s min' % data['longSelftestPollingTimeInMin'][0])
            print ('')
            cmd2 = s.smart_exe_offline_imm(0x01)
            return_descriptor = cmd2.ata_status_return_descriptor
            print ('status error bit:', return_descriptor.get("status") & 0x01)
            print ('')
        elif op == 2:
            cmd = s.smart()
            data = cmd.result
            #print ('selfTestStatus: ', data['selfTestStatus'])
            print ('ShortSelftestPollingTimeInMin: %s min' % data['ShortSelftestPollingTimeInMin'][0])
            print ('longSelftestPollingTimeInMin: %s min' % data['longSelftestPollingTimeInMin'][0])
            print ('')
            cmd2 = s.smart_exe_offline_imm(0x02)
            return_descriptor = cmd2.ata_status_return_descriptor
            print ('status error bit:', return_descriptor.get("status") & 0x01)
            print ('')

if __name__ == "__main__":
    dev,OP = get_para()
    main(pydiskcmdlib.utils.init_device(dev), OP)

