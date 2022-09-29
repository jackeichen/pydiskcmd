#!/usr/bin/env python
# coding: utf-8
import sys
import time
import pydiskcmd.pyscsi.scsi
import pydiskcmd.pysata.sata
import pydiskcmd.utils

Version = '0.01'

def usage():
    print('Usage: trimall.py <device>')
    print ('')

def handle_para():
    if "-h" in sys.argv or "--help" in sys.argv:
        usage()
        sys.exit()
    if "-V" in sys.argv or '--version' in sys.argv:
        print ("%s %s" % (sys.argv[0], Version))
        print ('')
        sys.exit()
    if len(sys.argv) == 2:
        dev = sys.argv[1]
        if "/dev/" in dev:
            device = pydiskcmd.utils.init_device(dev)
        else:
            raise RuntimeError("device Format Error!")
    else:
        usage()
        sys.exit()
    ParaDict = {"device": device}
    return ParaDict


def main():
    '''
    Now trim is must 4k aligned.
    '''
    ParaDict = handle_para()
    device = ParaDict["device"]
    with pydiskcmd.pyscsi.scsi.SCSI(device,512) as s:
        capacity = s.readcapacity10().result
        LBAs = int(capacity['returned_lba'])+1
        print ("Trim total LBA: %s" % LBAs)
    ## trim all
    with pydiskcmd.pysata.sata.SATA(device,512) as s:
        while 1:
            ret = input ("WARNING: Dangerous operation, will destroy all data in the disk, continue (y/n)? ")
            if ret.lower() == 'y': 
                print ('')
                print ('issuing trim command for the whole disk')
                print ("%s:" % device._file_name)
                start_t = time.time()
                r = s.trimall(LBAs)
                print ("Trim done, total used: %ss" % (time.time()-start_t))
                print ('')
            elif ret.lower() == 'n': 
                print ("Exit...")
            else:
                print ("Wrong input!")
                continue
            break

if __name__ == "__main__":
    main()
