#!/usr/bin/env python
# coding: utf-8
import sys
import pydiskcmd.pysata.sata
import pydiskcmd.utils

def usage():
    print('Usage: execute_device_diagnostic.py <device>')
    print ('')

def main(device):
    with pydiskcmd.pysata.sata.SATA(device,512) as s:
        print ('issuing execute device diagnostic command')
        print ("%s:" % device._file_name)
        cmd = s.execute_device_diagnostic()
        return_descriptor = cmd.ata_status_return_descriptor
        print ('')
        ####
        print ("diagnostic result: ")
        if return_descriptor.get("error") == 0x01:
            print ('Device 0 passed, Device 1 passed or not present')
        elif sreturn_descriptor.get("error") < 0x81:
            print ('Device 0 failed, Device 1 passed or not present')
        elif return_descriptor.get("error") == 0x81:
            print ('Device 0 passed, Device 1 failed')
        else:
            print ('Device 0 failed, Device 1 failed')
        if return_descriptor.get("extend") == 0:
            print ("something wrong with this command, need Extend=1")
        else:
            print ("Device type in command: ")
            if return_descriptor.get("sector_count") == 0x01:
                if return_descriptor.get("lba_low") == 0x01:
                    if return_descriptor.get("lba_low_rsvd") == 0x00 and return_descriptor.get("lba_mid_rsvd") == 0x00:
                        print ("ATA device")
                    elif return_descriptor.get("lba_low_rsvd") == 0x14 and return_descriptor.get("lba_mid_rsvd") == 0xEB:
                        print ("ATAPI device")
                    elif return_descriptor.get("lba_low_rsvd") == 0x3c and return_descriptor.get("lba_mid_rsvd") == 0xc3:
                        print ("Reserved for SATA device")
                    elif return_descriptor.get("lba_low_rsvd") == 0x69 and return_descriptor.get("lba_mid_rsvd") == 0x96:
                        print ("Reserved for SATA device")
                    else:
                        print ("something wrong with this command in LBA filed(15:8)/LBA filed(23:16) check.")
                else:
                    print ("something wrong with this command in LBA filed(7:0) check")
            else:
                if return_descriptor.get("lba_low_rsvd") == 0xce and return_descriptor.get("lba_mid_rsvd") == 0xaa:
                    print ("Obsolete by Count field")
                else:
                    print ("something wrong with this command in Count&LBA check.")
        ####
        print ('')

if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(pydiskcmd.utils.init_device(sys.argv[1]))
    else:
        usage()
