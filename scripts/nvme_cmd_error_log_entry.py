#!/usr/bin/env python
# coding: utf-8
import sys,os
import optparse
from pydiskcmd.pynvme.nvme import NVMe
import pydiskcmd.utils

Version = '0.01'

class ErrorInfomationLogEntryUnit(object):
    def __init__(self, data):
        self.error_count = int.from_bytes(data[0:8], byteorder='little', signed=False)
        self.sqid = int.from_bytes(data[8:10], byteorder='little', signed=False)
        self.cid = int.from_bytes(data[10:12], byteorder='little', signed=False)
        self.phase_tag = data[12] & 0x01
        self.status_field = ((data[12] >> 1) & 0x7F) + (data[13] << 15)
        self.para_error_location = int.from_bytes(data[14:16], byteorder='little', signed=False)
        self.lba = int.from_bytes(data[16:24], byteorder='little', signed=False)
        self.ns = int.from_bytes(data[24:28], byteorder='little', signed=False)
        self.vendor_spec_info_ava = data[28]
        self.transport_type = data[29]
        self.command_spec_info = data[32:40]
        self.transport_type_spec_info = data[40:42]


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
    device = pydiskcmd.utils.init_device(dev)
    with NVMe(device) as d:
        cmd = d.error_log_entry()
        ## para return data
        error_log_entry_list = []
        offset = 0
        while True:
            if offset >= len(cmd.data):
                break
            error_log_entry_list.insert(0, ErrorInfomationLogEntryUnit(cmd.data[offset:(offset+64)]))
            offset += 64
        if error_log_entry_list:
            print ('Error Log Entries for device:%s entries:%s' % (dev, len(error_log_entry_list)))
            print ('.................')
        for index,unit in enumerate(error_log_entry_list):
            print ('Entry[%s]' % index)
            print ('.................')
            print ('error_count     : %s' % unit.error_count)
            print ('sqid            : %s' % unit.sqid)
            print ('cmdid           : %s' % unit.cid)
            print ('status_field    : %s' % unit.status_field)
            print ('parm_err_loc    : %s' % unit.para_error_location)
            print ('lba             : %s' % unit.lba)
            print ('nsid            : %s' % unit.ns)
            print ('vs              : %s' % unit.vendor_spec_info_ava)
            print ('trtype          : %s' % unit.transport_type)
            print ('cs              : %s' % unit.command_spec_info)
            print ('trtype_spec_info: %s' % unit.transport_type_spec_info)
            print ('.................')


if __name__ == "__main__":
    main()
