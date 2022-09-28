#!/usr/bin/env python
# coding: utf-8
import sys,os
import optparse
from pydiskcmd.pynvme.nvme import NVMe
import pydiskcmd.utils
from pydiskcmd.utils.format_print import format_dump_bytes,nvme_id_ctrl_decode
from pydiskcmd.utils.converter import scsi_ba_to_int,ba_to_ascii_string


Version = '0.01'

def GetOptions():
    usage="usage: %prog <device> [OPTION args...]"
    parser = optparse.OptionParser(usage,version="%prog "+Version)
    parser.add_option("-o", "--output-format", type="choice", dest="output_format", action="store", choices=["normal", "binary", "raw"],default="normal",
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
    device = pydiskcmd.utils.init_device(dev)
    with NVMe(device) as d:
        cmd = d.id_ctrl()
    if options.output_format == "binary":
        format_dump_bytes(cmd.data)
    elif options.output_format == "normal":
        result = nvme_id_ctrl_decode(cmd.data)
        for k,v in result.items():
            if k in ("VID", "SSVID", "VER", "RTD3R", "RTD3E", "OAES", "OACS", "FRMW", "LPA", "SANICAP", "SQES", "CQES", "FNA", "SGLS"):
                print ("%-10s: %#x" % (k,scsi_ba_to_int(v, 'little')))
            elif k in ("SN", "MN", "FR", "SUBNQN"):
                print ("%-10s: %s" % (k,ba_to_ascii_string(v, "")))
            elif k in ("IEEE",):
                print ("%-10s: %x" % (k,scsi_ba_to_int(v, 'little')))
            elif k.startswith("PSD"):
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
