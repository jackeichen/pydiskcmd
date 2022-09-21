#!/usr/bin/env python
# coding: utf-8
import sys,os
import optparse
from pydiskcmd.pynvme.nvme import NVMe
import pydiskcmd.utils

Version = '0.01'

def GetOptions():
    usage="usage: %prog <device> [OPTION args...]"
    parser = optparse.OptionParser(usage,version="%prog "+Version)
    parser.add_option("-n", "--namespace-id", type="int", dest="namespace_id", action="store",default=1,
        help="identifier of desired namespace. Default 1")
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
    device = pydiskcmd.utils.init_device(dev)
    with NVMe(device) as d:
        cmd = d.id_ns(options.namespace_id)
        print (cmd.data)

if __name__ == "__main__":
    main()
