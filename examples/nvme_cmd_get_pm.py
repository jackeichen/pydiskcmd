#!/usr/bin/env python
# coding: utf-8
import sys,os
import optparse
from pydiskcmdlib.pynvme.nvme import NVMe
from pydiskcmdcli.nvme_spec import nvme_power_management_cq_decode
from pydiskcmdlib.utils import init_device

Version = '0.01'

def GetOptions():
    usage="usage: %prog <device> [OPTION args...]"
    parser = optparse.OptionParser(usage,version="%prog "+Version)
    parser.add_option("-o", "--output-format", type="choice", dest="output_format", action="store", choices=["normal", "binary"],default="binary",
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
        cmd = d.get_feature(2, sel=0)
    if options.output_format == "binary":
        print (cmd.cq_cmd_spec)
    elif options.output_format == "normal":
        result = nvme_power_management_cq_decode(cmd.cq_cmd_spec)
        for k,v in result.items():
            print ("%-5s: %s" % (k,v))

if __name__ == "__main__":
    main()
