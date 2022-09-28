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
    parser.add_option("-f", "--fw", type="str", dest="fw_path", action="store", default="",
        help="Firmware file path")
    parser.add_option("-x", "--xfer", type="int", dest="xfer", action="store", default=0,
        help="transfer chunksize limit")
    parser.add_option("-o", "--offset", type="int", dest="offset", action="store", default=0,
        help="starting dword offset, default 0")

    (options, args) = parser.parse_args()
    ## check options
    dev = sys.argv[1]
    if not os.path.exists(dev):
        raise RuntimeError("Device not support!")
    ##
    if (not options.fw_path) or (not os.path.exists(options.fw_path)):
        raise RuntimeError("Firmware File Not exist!")
    ##
    return dev,options


def main():
    '''
    Now trim is must 4k aligned.
    '''
    dev,options = GetOptions()
    device = pydiskcmd.utils.init_device(dev)
    with NVMe(device) as d:
        cmd = d.nvme_fw_download(options.fw_path, xfer=options.xfer, offset=options.offset)
    

if __name__ == "__main__":
    main()
