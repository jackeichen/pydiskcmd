#!/usr/bin/env python
# coding: utf-8
import sys
import pydiskcmd.pysata.sata
import pydiskcmd.utils


def usage():
    print('Usage: get_accessible_max_address.py <device>')
    print ('')

def main(device):
    LBA_max = None
    with pydiskcmd.pysata.sata.SATA(device,512) as s:
        print ('issuing get accessible max address')
        print ("%s:" % device._file_name)
        cmd = s.getAccessibleMaxAddress()
        return_descriptor = cmd.ata_status_return_descriptor
        ##
        LBA_ordinal = bytearray(6)
        #
        LBA_ordinal[0] = return_descriptor.get("lba_low")
        LBA_ordinal[1] = return_descriptor.get("lba_mid")
        LBA_ordinal[2] = return_descriptor.get("lba_high")
        if return_descriptor.get("extend"):
            LBA_ordinal[3] = return_descriptor.get("lba_low_rsvd")  
            LBA_ordinal[4] = return_descriptor.get("lba_mid_rsvd")   
            LBA_ordinal[5] = return_descriptor.get("lba_high_rsvd")
        ##
        LBA_max = int.from_bytes(LBA_ordinal, byteorder='little', signed=False)
        print ("Max LBA address: %s" % LBA_max)
        print ("That will present total LBAs: %s" % (LBA_max+1))
    print ('')
    return LBA_max

if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(pydiskcmd.utils.init_device(sys.argv[1]))
    else:
        usage()
