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
    parser.add_option("-s", "--slot", type="int", dest="slot", action="store", default=0,
        help="firmware slot to sctive")
    parser.add_option("-a", "--action", type="int", dest="action", action="store", default=0,
        help="active action")
    parser.add_option("-b", "--behavior", type="int", dest="behavior", action="store", default=3,
        help="firmware update behavior(default 3): 1-only fw download, 2-only active, 3-download&active")

    (options, args) = parser.parse_args()
    ## check options
    dev = sys.argv[1]
    if not os.path.exists(dev):
        raise RuntimeError("Device not support!")
    ##
    if options.behavior & 0x01:
        if (not options.fw_path) or (not os.path.exists(options.fw_path)):
            raise RuntimeError("Firmware File Not exist!")
    ##
    if options.behavior & 0x02:
        pass
    return dev,options


def main():
    '''
    Now trim is must 4k aligned.
    '''
    dev,options = GetOptions()
    device = pydiskcmd.utils.init_device(dev)
    with NVMe(device) as d:
        if options.behavior & 0x01:
            rc = d.nvme_fw_download(options.fw_path, xfer=options.xfer, offset=options.offset)
            if rc:
                return rc
        if options.behavior & 0x02:
            print ("Firmware Commit Now")
            cmd = d.nvme_fw_commit(options.slot, options.action)

if __name__ == "__main__":
    main()
