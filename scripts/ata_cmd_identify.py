#!/usr/bin/env python
# coding: utf-8
import sys
import binascii
#from pyscsi.utils.converter import translocate_bytearray,bytearray2string,bytearray2int
import pydiskcmd.pysata.sata
import pydiskcmd.utils

Identify_Element_Type = {"FW": 'string',
                         "SerialNo": 'string',
                         "Capacity": 'int',
                         "Model": 'string'}

def usage():
    print('Usage: identify.py <device>')
    print ('')


def main(device):
    with pydiskcmd.pysata.sata.SATA(device, 512) as s:
        print ('issuing identify command')
        print ("%s:" % device._file_name)
        print ('==========================================\n')
        cmd = s.identify()
        data = cmd.result
        for k,v in data.items():
            type = Identify_Element_Type.get(k)
            if type == 'string':
                value = pydiskcmd.utils.converter.bytearray2string(pydiskcmd.utils.converter.translocate_bytearray(v))
            elif type == 'int':
                value = int(binascii.hexlify(pydiskcmd.utils.converter.translocate_bytearray(v, 2)),16)
                value = value *512/1024/1024/1024  # byte --> GB
                value = "%.2f GB" % value
            elif type:
                value = pydiskcmd.utils.converter.bytearray2string(pydiskcmd.utils.converter.translocate_bytearray(v))
            else:
                continue
            print ("%s: %s" % (k, value))

if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(pydiskcmd.utils.init_device(sys.argv[1]))
    else:
        usage()

