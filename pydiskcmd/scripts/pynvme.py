# SPDX-FileCopyrightText: 2014 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import sys,os
import optparse
from pydiskcmd.utils import init_device
from pydiskcmd.pynvme.nvme import NVMe
from pydiskcmd.utils.format_print import format_dump_bytes
from pydiskcmd.utils.converter import scsi_ba_to_int,ba_to_ascii_string
##
from pydiskcmd.pynvme.nvme_spec import *

Version = '0.0.1'

def version():
    print ("pynvme version %s" % Version)
    return 0

def print_help():
    print ("pynvme-%s" % Version)
    print ("usage: pynvme <command> [<device>] [<args>]")
    print ("")
    print ("The '<device>' may be either an NVMe character device (ex: /dev/nvme0) or an")
    print ("nvme block device (ex: /dev/nvme0n1).")
    print ("")
    print ("The following are all implemented sub-commands:")
    print ("  smart-log             Retrieve SMART Log, show it")
    print ("  id-ctrl               Send NVMe Identify Controller")
    print ("  id-ns                 Send NVMe Identify Namespace, display structure")
    print ("  error-log             Retrieve Error Log, show it")
    print ("  fw-log                Retrieve FW Log, show it")
    print ("  fw-download           Download new firmware")
    print ("  fw-commit             Verify and commit firmware to a specific slot")
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
            format_dump_bytes(cmd.data, byteorder='big')
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

def id_ns():
    usage="usage: %prog id-ns <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-n", "--namespace-id", type="int", dest="namespace_id", action="store",default=1,
        help="identifier of desired namespace. Default 1")
    parser.add_option("-o", "--output-format", type="choice", dest="output_format", action="store", choices=["normal", "binary", "raw"],default="normal",
        help="Output format: normal|binary|raw, default normal")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        if not os.path.exists(dev):
            raise RuntimeError("Device not support!")
        ## check namespace
        if not isinstance(options.namespace_id, int) or options.namespace_id < 1:
            parser.error("namespace id input error.")
            return
        ##
        with NVMe(init_device(dev)) as d:
            cmd = d.id_ns(options.namespace_id)
        ##
        if options.output_format == "binary":
            format_dump_bytes(cmd.data)
        elif options.output_format == "normal":
            result = nvme_id_ns_decode(cmd.data)
            for k,v in result.items():
                if k in ("NSZE", "NCAP", "NUSE", "MC", "DPC"):
                    print ("%-10s: %#x" % (k,scsi_ba_to_int(v, 'little')))
                elif k in ("NGUID", "EUI64"):
                    print ("%-10s: %x" % (k,scsi_ba_to_int(v, 'big')))
                elif k.startswith("LBAF"):
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

def error_log():
    usage="usage: %prog error-log <device> [OPTIONS]"
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
            cmd = d.error_log_entry()
        ##
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
    else:
        parser.print_help()

def fw_log():
    usage="usage: %prog fw-log <device> [OPTIONS]"
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
            cmd = d.fw_slot_info()
        ##
        if options.output_format == "binary":
            format_dump_bytes(cmd.data, end=511)
        elif options.output_format == "normal":
            result = nvme_fw_slot_info_decode(cmd.data)
            for k,v in result.items():
                if "FRS" in k:
                    print ("%-5s: %s" % (k,ba_to_ascii_string(v, "")))
                else:
                    print ("%-5s: %#x" % (k,scsi_ba_to_int(v, 'little')))
        else:
            print (cmd.data)
    else:
        parser.print_help()

def fw_download():
    usage="usage: %prog fw-download <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-f", "--fw", type="str", dest="fw_path", action="store", default="",
        help="Firmware file path")
    parser.add_option("-x", "--xfer", type="int", dest="xfer", action="store", default=0,
        help="transfer chunksize limit")
    parser.add_option("-o", "--offset", type="int", dest="offset", action="store", default=0,
        help="starting dword offset, default 0")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        if not os.path.exists(dev):
            raise RuntimeError("Device not support!")
        ## check namespace
        if not os.path.exists(options.fw_path):
            parser.error("No Firmware File provided")
            return
        ##
        with NVMe(init_device(dev)) as d:
            rc = d.nvme_fw_download(options.fw_path, xfer=options.xfer, offset=options.offset)
    else:
        parser.print_help()

def fw_commit():
    usage="usage: %prog fw-commit <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-s", "--slot", type="int", dest="slot", action="store", default=0,
        help="firmware slot to sctive")
    parser.add_option("-a", "--action", type="int", dest="action", action="store", default=0,
        help="active action")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        if not os.path.exists(dev):
            raise RuntimeError("Device not support!")
        ##
        with NVMe(init_device(dev)) as d:
            cmd = d.nvme_fw_commit(options.slot, options.action)
    else:
        parser.print_help()


commands_dict = {"smart-log": smart_log,
                 "id-ctrl": id_ctrl,
                 "id-ns": id_ns,
                 "error-log": error_log,
                 "fw-log": fw_log,
                 "fw-download": fw_download, 
                 "fw-commit": fw_commit, 
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
