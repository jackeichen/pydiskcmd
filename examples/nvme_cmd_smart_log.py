#!/usr/bin/env python
# coding: utf-8
import sys,os
import optparse
from pydiskcmdlib.pynvme.nvme import NVMe
from pydiskcmdcli.nvme_spec import nvme_smart_decode
from pydiskcmdlib.utils import init_device
from pydiskcmdcli.utils.format_print import format_dump_bytes
from pydiskcmdlib.utils.converter import scsi_ba_to_int

Version = '0.01'


def GetOptions():
    usage="usage: %prog <device> [OPTION args...]"
    parser = optparse.OptionParser(usage,version="%prog "+Version)
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
        cmd = d.smart_log()
        ## para return data
        #print (cmd.data)
    if options.output_format == "binary":
        format_dump_bytes(cmd.data, end=511)
    elif options.output_format == "normal":
        result = nvme_smart_decode(cmd.data)
        for k,v in result.items():
            if k == "Composite Temperature":
                print ("%-40s: %.2f" % ("%s(C)" % k,scsi_ba_to_int(v, 'little')-273.15))
            elif k in ("Critical Warning",):
                print ("%-40s: %#x" % (k,scsi_ba_to_int(v, 'little')))
            else:
                print ("%-40s: %s" % (k,scsi_ba_to_int(v, 'little')))

if __name__ == "__main__":
    main()
