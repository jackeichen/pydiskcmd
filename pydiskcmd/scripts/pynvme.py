# SPDX-FileCopyrightText: 2014 The python-scsi Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import sys,os
import optparse
from pydiskcmd.utils import init_device
from pydiskcmd.pynvme.nvme import NVMe
from pydiskcmd.utils.format_print import format_dump_bytes
from pydiskcmd.utils.converter import scsi_ba_to_int,ba_to_ascii_string
##
from pydiskcmd.pynvme.nvme_spec import nvme_smart_decode
from pydiskcmd.pynvme.nvme_spec import nvme_id_ctrl_decode

Version = '0.0.1'

def version():
    print ("pynvme version %s" % Version)
    return 0

def print_help():
    print ("pynvme-%s" % Version)
    print ("sage: nvme <command> [<device>] [<args>]")
    print ("")
    print ("The '<device>' may be either an NVMe character device (ex: /dev/nvme0) or an")
    print ("nvme block device (ex: /dev/nvme0n1).")
    print ("")
    print ("The following are all implemented sub-commands:")
    print ("  smart-log             Retrieve SMART Log, show it")
    print ("  id-ctrl               Send NVMe Identify Controller")
    print ("  version               Shows the program version")
    print ("  help                  Shows the program version")
    print ("")
    print ("See 'nvme <plugin> --help' for more information on a plugin")
    return 0

def smart_log():
    usage="usage: %prog smart-log <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-o", "--output-format", type="choice", dest="output_format", action="store", choices=["normal", "binary", "raw"],default="normal",
        help="Output format: normal|binary|raw, default normal")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        if not os.path.exists(dev):
            raise RuntimeError("Device not support!")
        ##
        with NVMe(init_device(dev)) as d:
            cmd = d.smart_log()
        ##
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
        else:
            print (cmd.data)
    else:
        parser.print_help()

def id_ctrl():
    usage="usage: %prog id-ctrl <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-o", "--output-format", type="choice", dest="output_format", action="store", choices=["normal", "binary", "raw"],default="normal",
        help="Output format: normal|binary|raw")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        if not os.path.exists(dev):
            raise RuntimeError("Device not support!")
        ##
        with NVMe(init_device(dev)) as d:
            cmd = d.id_ctrl()
        if options.output_format == "binary":
            format_dump_bytes(cmd.data)
        elif options.output_format == "normal":
            result = nvme_id_ctrl_decode(cmd.data)
            for k,v in result.items():
                if k in ("VID", "SSVID", "VER", "RTD3R", "RTD3E", "OAES", "OACS", "FRMW", "LPA", "SANICAP", "SQES", "CQES", "FNA", "SGLS"):
                    print ("%-10s: %#x" % (k,scsi_ba_to_int(v, 'little')))
                elif k in ("SN", "MN", "FR", "SUBNQN"):
                    print ("%-10s: %s" % (k,ba_to_ascii_string(v, "")))
                elif k in ("IEEE",):
                    print ("%-10s: %x" % (k,scsi_ba_to_int(v, 'little')))
                elif k.startswith("PSD"):
                    print ("%-10s:" % k)
                    for m,n in result[k].items():
                        if isinstance(n, bytes):
                            print ("     %-5s:%s" % (m,scsi_ba_to_int(n, 'little')))
                        else:
                            print ("     %-5s:%s" % (m,n))
                else:
                    print ("%-10s: %s" % (k,scsi_ba_to_int(v, 'little')))
        else:
            print (cmd.data)
    else:
        parser.print_help()


commands_dict = {"smart-log": smart_log,
                 "id-ctrl": id_ctrl,
                 "version": version,
                 "help": print_help}

def pynvme():
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command in commands_dict:
            commands_dict[command]()
        else:
            print_help()
    else:
        print_help()

