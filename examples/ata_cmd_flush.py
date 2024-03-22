#!/usr/bin/env python
# coding: utf-8
import sys
from pydiskcmdlib.pysata.sata import SATA
from pydiskcmdlib.utils import init_device


def usage():
    print('Usage: flush.py <device>')
    print ('')

def main(device):
    with SATA(device,512) as s:
        print ('issuing flush command')
        print ("%s:" % device._file_name)
        cmd = s.flush()
        return_descriptor = cmd.ata_status_return_descriptor
        print ('')
        print ('status err_bit:', return_descriptor.get("status") & 0x01)

if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(init_device(sys.argv[1]))
    else:
        usage()
