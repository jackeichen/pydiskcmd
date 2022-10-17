# SPDX-FileCopyrightText: 2014 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import sys,os
import re
import optparse
from pydiskcmd.utils import init_device
from pydiskcmd.pynvme.nvme import NVMe
from pydiskcmd.utils.format_print import format_dump_bytes,human_read_capacity
from pydiskcmd.utils.converter import scsi_ba_to_int,ba_to_ascii_string
##
from pydiskcmd.pynvme.nvme_spec import *

Version = '0.1.0'

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
    print ("  list                  List all NVMe devices and namespaces on machine")
    print ("  smart-log             Retrieve SMART Log, show it")
    print ("  id-ctrl               Send NVMe Identify Controller")
    print ("  id-ns                 Send NVMe Identify Namespace, display structure")
    print ("  error-log             Retrieve Error Log, show it")
    print ("  fw-log                Retrieve FW Log, show it")
    print ("  fw-download           Download new firmware")
    print ("  fw-commit             Verify and commit firmware to a specific slot")
    print ("  format                Format namespace with new block format")
    print ("  version               Shows the program version")
    print ("  help                  Shows the program version")
    print ("")
    print ("See 'pynvme <plugin> --help' for more information on a plugin")
    return 0

def _list():
    usage="usage: %prog smart-log <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-o", "--output-format", type="choice", dest="output_format", action="store", choices=["normal",],default="normal",
        help="Output format: normal, default normal")
    
    (options, args) = parser.parse_args()
    ##
    print_format = "%-16s %-20s %-40s %-9s %-26s %-16s %-8s"
    print (print_format % ("Node", "SN", "Model", "Namespace", "Usage", "Format", "FW Rev"))
    print (print_format % ("-"*16, "-"*20, "-"*40, "-"*9, "-"*26, "-"*16, "-"*8))
    from pydiskcmd.system.os_tool import get_block_devs
    blk_dev = get_block_devs(print_detail=False)
    included_block_devices = ("nvme",)
    for dev in blk_dev:
        if dev.startswith(included_block_devices):
            g = re.match(r"nvme([0-9]+)n([0-9]+)", dev)
            ctrl_id = int(g[1])
            ns_id = int(g[2])
            #
            nvme_ctrl_dev = "/dev/nvme%s" % ctrl_id
            nvme_block_dev = "/dev/%s" % dev
            ## send identify controller and identify namespace
            with NVMe(init_device(nvme_ctrl_dev)) as d:
                cmd_id_ctrl = d.id_ctrl()
                cmd_id_ns = d.id_ns(ns_id)
            ## para data
            result = nvme_id_ctrl_decode(cmd_id_ctrl.data)
            sn = ba_to_ascii_string(result.get("SN"), "")
            mn = ba_to_ascii_string(result.get("MN"), "")
            fw = ba_to_ascii_string(result.get("FR"), "")
            ##
            result = nvme_id_ns_decode(cmd_id_ns.data)
            #
            lbaf = result.get("LBAF%s" % scsi_ba_to_int(result.get("FLBAS"), 'little'))
            meta_size = scsi_ba_to_int(lbaf.get("MS"), 'little')
            lba_data_size = scsi_ba_to_int(lbaf.get("LBADS"), 'little')
            _format = "%-6sB + %-3sB" % (2 ** lba_data_size, meta_size)
            #
            NUSE_B = scsi_ba_to_int(result.get("NUSE"), 'little') * (2 ** lba_data_size)
            NCAP_B = scsi_ba_to_int(result.get("NCAP"), 'little') * (2 ** lba_data_size)
            usage = "%-6s / %-6s" % (human_read_capacity(NUSE_B), human_read_capacity(NCAP_B))
            if options.output_format == "normal":
                print (print_format % (nvme_block_dev, sn, mn, ns_id, usage, _format, fw))

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

def nvme_format():
    usage="usage: %prog format <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-n", "--namespace-id", type="int", dest="namespace_id", action="store", default=0xFFFFFFFF,
        help="identifier of desired namespace. Default 0xFFFFFFFF")
    parser.add_option("-l", "--lbaf", type="int", dest="lbaf", action="store", default=-1,
        help="LBA format to apply (required)")
    parser.add_option("-s", "--ses", type="int", dest="ses", action="store", default=0,
        help="[0-2]: secure erase")
    parser.add_option("-i", "--pi", type="int", dest="pi", action="store", default=0,
        help="[0-3]: protection info off/Type, 1/Type 2/Type 3")
    parser.add_option("-p", "--pil", type="int", dest="pil", action="store", default=1,
        help="[0-1]: protection info location, last/first 8 bytes of metadata")
    parser.add_option("-m", "--ms", type="int", dest="ms", action="store", default=0,
        help="[0-1]: extended format off/on")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        if not os.path.exists(dev):
            raise RuntimeError("Device not support!")
        if options.lbaf < 0:
            parser.error("You need give the lbaf.")
        ##
        with NVMe(init_device(dev)) as d:
            cmd = d.nvme_format(options.lbaf, nsid=options.namespace_id, mset=options.ms, pi=options.pi, pil=options.pil, ses=options.ses)
    else:
        parser.print_help()

def persistent_event_log():
    usage="usage: %prog fw-commit <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-a", "--action", type="int", dest="action", action="store", default=3,
        help="action of get persistent event log, 0: open, 1: read, 2: close, 3: check status")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        if not os.path.exists(dev):
            raise RuntimeError("Device not support!")
        ##
        with NVMe(init_device(dev)) as d:
            ret = d.get_persistent_event_log(options.action)
            if options.action == 3:
                if ret == 0:
                    print ("Context Not Established!")
                elif ret == 1:
                    print ("Context Established!")
                else:
                    print ("Command failed.")
            elif isinstance(ret, int):
                if ret == 0:
                    print ("Command success.")
                else:
                    print ("Command failed.")
            elif options.action == 1:
                event_log_header = persistent_event_log_header_decode(ret[0:512])
                event_log_events = persistent_event_log_events_decode(ret[512:], scsi_ba_to_int(event_log_header.get("TNEV"), 'little'))
                ## format print
                print ("Persistent Event Log Header: ")
                for k,v in event_log_header.items():
                    if k in ("LogID", "VID", "SSVID"):
                        print ("%-10s: %#x" % (k,scsi_ba_to_int(v, 'little')))
                    elif k in ("SN", "MN", "SUBNQN"):
                        print ("%-10s: %s" % (k,ba_to_ascii_string(v, "")))
                    elif k == "SEB":
                        print ("Supported Events Bitmap: ")
                        for m,n in v.items():
                            print ("     %-20s:%s" % (m,n))
                    else:
                        print ("%-10s: %s" % (k,scsi_ba_to_int(v, 'little')))
                ##
                print ("="*60)
                if event_log_events:
                    print ("Persistent Event Log Events: ")
                    print ('......................')
                for k,v in event_log_events.items():
                    print ('Entry[%s]' % k)
                    print ('......................')
                    for m,n in v.items():
                        if m == 'event_log_event_header' and n:
                            for p,q in n.items():
                                print ('%-20s : %s' % (p,scsi_ba_to_int(q, 'little')))
                        elif m in ("vendor_spec_info", "event_log_event_data"):
                            print ('%-20s : %s' % (m,n))
                        else:
                            print ('%-20s : %s' % (m,scsi_ba_to_int(n, 'little')))
                    print ('......................')
    else:
        parser.print_help()
    

commands_dict = {"list": _list,
                 "smart-log": smart_log,
                 "id-ctrl": id_ctrl,
                 "id-ns": id_ns,
                 "error-log": error_log,
                 "fw-log": fw_log,
                 "fw-download": fw_download, 
                 "fw-commit": fw_commit, 
                 "format": nvme_format,
                 "persistent_event_log": persistent_event_log,
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
