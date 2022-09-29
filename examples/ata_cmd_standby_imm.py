#!/usr/bin/env python
# coding: utf-8
import sys
import pydiskcmd.pysata.sata
import pydiskcmd.utils


def usage():
    print('Usage: standby.py <device>')
    print ('')

def main(device):
    with pydiskcmd.pysata.sata.SATA(device,512) as s:
        print ('issuing standby command')
        print ("%s:" % device._file_name)
        cmd = s.standby_imm()
        return_descriptor = cmd.ata_status_return_descriptor
        print ('')
        print ('status err_bit:', return_descriptor.get("status") & 0x01)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(pydiskcmd.utils.init_device(sys.argv[1]))
    else:
        usage()
