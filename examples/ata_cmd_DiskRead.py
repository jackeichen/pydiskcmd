#!/usr/bin/env python
# coding: utf-8
import sys,os
import optparse
from pydiskcmdlib.pysata.sata import SATA
from pydiskcmdlib.utils import init_device
Version = '0.0.1'
options = args = dev = None

def GetOptions():
    usage="usage: %prog <device> [OPTION args...]"
    parser = optparse.OptionParser(usage,version="%prog "+Version)
    parser.add_option("-s", "--start-block", type="int", dest="slba", action="store", default=0,
        help="Logical Block Address to write to. Default 0")
    parser.add_option("-c", "--block-count", type="int", dest="nlb", action="store", default=1,
        help="Transfer Length in blocks. Default 1")
    parser.add_option("-b", "--block-size", type="int", dest="bs", action="store", default=512,
        help="To fix the block size of the device. Default 512")
    
    global options,args,dev
    (options, args) = parser.parse_args()
    ## check options
    dev = sys.argv[1]
    if not os.path.exists(dev):
        raise RuntimeError("Device not support!")

def main():
    GetOptions()
    device = init_device(dev)
    with SATA(device,options.bs) as s:
        print ('issuing read command')
        print ("%s:" % device._file_name)
        cmd = s.read_DMAEXT16(options.slba, options.nlb)
        return_descriptor = cmd.ata_status_return_descriptor
        print ('')
        print ('ata_return_descriptor: ', return_descriptor)
        print ('status error bit: ', return_descriptor.get("status") & 0x01)
        print ('')
        print ('Data Out:')
        print ('len: %d' % (len(cmd.datain)))
        print (cmd.datain)

if __name__ == "__main__":
    main()
