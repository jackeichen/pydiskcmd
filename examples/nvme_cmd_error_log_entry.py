#!/usr/bin/env python
# coding: utf-8
import sys,os
import optparse
from pydiskcmd.pynvme.nvme import NVMe
from pydiskcmd.pynvme.nvme_spec import nvme_error_log_decode
from pydiskcmd.utils import init_device
from pydiskcmd.utils.format_print import format_dump_bytes

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
        cmd = d.error_log_entry()
        ## para return data
    if options.output_format == "binary":
        format_dump_bytes(cmd.data)
    elif options.output_format == "normal":
        error_log_entry_list = nvme_error_log_decode(cmd.data)
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
    else:
        print (cmd.data)

if __name__ == "__main__":
    main()
