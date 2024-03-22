#!/usr/bin/env python
# coding: utf-8
import sys
from pydiskcmdlib.pysata.sata import SATA
from pydiskcmdlib.utils import init_device

Version = '0.01'
def usage():
    print('Usage: flush.py <device> <startLBA:LBAlength,startLBA:LBAlength,...>')
    print ('')

def handle_para():
    if "-h" in sys.argv or "--help" in sys.argv:
        usage()
        sys.exit()
    if "-V" in sys.argv or '--version' in sys.argv:
        print ("%s %s" % (sys.argv[0], Version))
        print ('')
        sys.exit()
    if len(sys.argv) == 3:
        dev = sys.argv[1]
        if "/dev/" in dev:
            device = init_device(dev)
        else:
            raise RuntimeError("device Format Error!")
        LBAs = sys.argv[2]
        LBA_list = LBAs.split(',')
        if 0 < len(LBA_list) < 65:
            lba_description = []
            for lba_des in LBA_list:
                lba_des_list = lba_des.split(':')
                if len(lba_des_list) != 2:
                    raise RuntimeError("lba description Format Error!")
                lba_des_tuple = (int(lba_des_list[0]), int(lba_des_list[1]))
                lba_description.append(lba_des_tuple)
        else:
            raise RuntimeError("lba description Format Error!")
    else:
        usage()
        sys.exit()
    ParaDict = {"device": device, "lba_description": lba_description}
    return ParaDict


def main():
    '''
    Now trim is must 4k aligned.
    '''
    ParaDict = handle_para()
    device = ParaDict["device"]
    lba_description = ParaDict["lba_description"]
    with SATA(device,512) as s:
        print ("Note: If you want trim command works, lba_description need 4k aligned!")
        print ('')
        print ('issuing trim command')
        print ("%s:" % device._file_name)
        cmd = s.trim(lba_description)
        return_descriptor = cmd.ata_status_return_descriptor
        print ('')
        print ('status err_bit:', return_descriptor.get("status") & 0x01)
        print ('')

if __name__ == "__main__":
    main()
