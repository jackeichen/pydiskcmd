#!/usr/bin/env python
# coding: utf-8
# DiskWrite.py
#  Write LBA to scsi device
#
import os
import sys
import optparse
import pydiskcmd.pysata.sata
import pydiskcmd.utils
Version = '0.0.1'
options = args = dev = None

def GetOptions():
    usage="usage: %prog <device> [OPTION args...]"
    parser = optparse.OptionParser(usage,version="%prog "+Version)
    parser.add_option("-s", "--start-block", type="int", dest="slba", action="store", default=0,
        help="Logical Block Address to write to. Default 0")
    parser.add_option("-c", "--block-count", type="int", dest="nlb", action="store", default=1,
        help="Transfer Length in blocks. Default 1")
    parser.add_option("-d", "--data", type="str", dest="data", action="store", default='',
        help="String containing the block to write")
    parser.add_option("-f", "--data-file", type="str", dest="dfile", action="store", default='',
        help="File(Read first) containing the block to write")
    parser.add_option("-b", "--block-size", type="int", dest="bs", action="store", default=512,
        help="To fix the block size of the device. Default 512")
    
    global options,args,dev
    (options, args) = parser.parse_args()
    ## check options
    dev = sys.argv[1]
    if not os.path.exists(dev):
        raise RuntimeError("Device not support!")
    #
    if options.data:
        options.data = bytearray(options.data, 'utf-8')
    elif options.dfile:
        if os.path.isfile(options.dfile):
            with open(options.dfile, 'rb') as f:
                data = f.read()
            options.data = bytearray(data)
    if options.data:
        data_l = len(options.data)
        data_size = options.nlb * options.bs
        if data_size < data_l:
            options.data = options.data[0:data_size]
        elif data_size > data_l:
            options.data = options.data + bytearray(data_size-data_l)
        else:
            pass
    else:
        raise RuntimeError("You need some data to write in.")
    
def main():
    GetOptions()
    device = pydiskcmd.utils.init_device(dev)
    with pydiskcmd.pysata.sata.SATA(device,options.bs) as s:
        print ('issuing write command')
        print ("%s:" % device._file_name)
        print ('')
        cmd = s.write_DMAEXT16(options.slba, options.nlb, options.data)
        return_descriptor = cmd.ata_status_return_descriptor
        print ('ata_return_descriptor: ', return_descriptor)
        print ('status error bit: ', return_descriptor.get("status") & 0x01)
        print ('')

if __name__ == "__main__":
    main()
