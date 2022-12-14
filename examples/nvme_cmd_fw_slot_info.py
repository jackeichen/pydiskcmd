#!/usr/bin/env python
# coding: utf-8
import sys,os
import optparse
from pydiskcmd.pynvme.nvme import NVMe
from pydiskcmd.pynvme.nvme_spec import nvme_fw_slot_info_decode
from pydiskcmd.utils import init_device
from pydiskcmd.utils.format_print import format_dump_bytes
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
    device = init_device(dev)
    with NVMe(device) as d:
        cmd = d.fw_slot_info()
    if options.output_format == "binary":
        format_dump_bytes(cmd.data)
    elif options.output_format == "normal":
        result = nvme_fw_slot_info_decode(cmd.data)
        for k,v in result.items():
            if "FRS" in k:
                print ("%-5s: %s" % (k,ba_to_ascii_string(v, "")))
            else:
                print ("%-5s: %#x" % (k,scsi_ba_to_int(v, 'little')))
    else:
        print (cmd.data)

if __name__ == "__main__":
    main()
