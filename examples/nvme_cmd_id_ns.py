#!/usr/bin/env python
# coding: utf-8
import sys,os
import optparse
from pydiskcmd.pynvme.nvme import NVMe
from pydiskcmd.pynvme.nvme_spec import nvme_id_ns_decode
from pydiskcmd.utils import init_device
from pydiskcmd.utils.format_print import format_dump_bytes
from pydiskcmd.utils.converter import scsi_ba_to_int,ba_to_ascii_string

Version = '0.01'

def GetOptions():
    usage="usage: %prog <device> [OPTION args...]"
    parser = optparse.OptionParser(usage,version="%prog "+Version)
    parser.add_option("-n", "--namespace-id", type="int", dest="namespace_id", action="store",default=1,
        help="identifier of desired namespace. Default 1")
    parser.add_option("-o", "--output-format", type="choice", dest="output_format", action="store", choices=["normal", "binary"],default="normal",
        help="Output format: normal|binary")

    (options, args) = parser.parse_args()
    ## check options
    dev = sys.argv[1]
    if not os.path.exists(dev):
        raise RuntimeError("Device not support!")
    return dev,options


def main():
    '''
    Now trim is must 4k aligned.
    '''
    dev,options = GetOptions()
    device = init_device(dev)
    with NVMe(device) as d:
        cmd = d.id_ns(options.namespace_id)
    if options.output_format == "binary":
        format_dump_bytes(cmd.data)
    elif options.output_format == "normal":
        result = nvme_id_ns_decode(cmd.data)
        for k,v in result.items():
            if k in ("NSZE", "NCAP", "NUSE", "MC", "DPC"):
                print ("%-10s: %#x" % (k,scsi_ba_to_int(v, 'little')))
            elif k in ("NGUID", "EUI64"):
                print ("%-10s: %x" % (k,scsi_ba_to_int(v, 'big')))
            elif k.startswith("LBAF"):
                print ("%-10s:" % k)
                for m,n in result[k].items():
                    if isinstance(n, bytes):
                        print ("     %-5s:%s" % (m,scsi_ba_to_int(n, 'little')))
                    else:
                        print ("     %-5s:%s" % (m,n))
            else:
                print ("%-10s: %s" % (k,scsi_ba_to_int(v, 'little')))
    else:
        print (cmd.data)


if __name__ == "__main__":
    main()
