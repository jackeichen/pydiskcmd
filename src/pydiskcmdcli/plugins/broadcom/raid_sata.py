# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import sys
import optparse
import binascii
import re
#
from pydiskcmdlib.broadcom.linux_device import DcmdDevice
from pydiskcmdlib.broadcom.raid import get_raid_controllers,RaidController,SATADrive
from pydiskcmdcli import os_type
from pydiskcmdlib.utils.converter import scsi_ba_to_int
from pydiskcmdcli.utils.format_print import format_dump_bytes,human_read_capacity
from pydiskcmdcli.scripts import parser_update,script_check
from pydiskcmdcli.utils.string_utils import decode_bytes,string_strip
from pydiskcmdlib.utils.converter import bytearray2string,translocate_bytearray
from pydiskcmdcli.utils.ata_format_print import (
    _print_return_status,
    print_ata_cmd_status,
    read_log_format_print_set,
    smart_read_log_format_print_set,
    read_log_decode_set,
    format_print_identify,
    format_print_smart,
    format_print_set_feature_guide,
    )
##
CliVer = "0.1"

def _megaraid_print_help():
    if len(sys.argv) > 3 and sys.argv[3] in plugin_megaraid_commands_dict:
        func_name,sys.argv[3] = sys.argv[3],"--help"
        plugin_megaraid_commands_dict[func_name]()
    else:
        print ("usage: pysata megaraid <command> [<device>] [<args>]")
        print ("")
        print (r"The '<device>' is a string(ex: c0,d99) split by ',' that include")
        print (r"Controller ID(ex: c0) and Disk ID(ex: d99).")
        print ("")
        print ("Linux MegaRAID extensions")
        print ("")
        print ("The following are all implemented sub-commands:")
        print ("")
        print ("  list                          List all SATA devices attached to Broadcom RAID controllers")
        print ("  identify                      Get identify information")
        print ("  smart                         Get smart information")
        print ("  version                       Shows plugin version")
        print ("  help                          Display this help")
        print ("")
        print ("See 'pysata megaraid help <command>' for more information on a specific command")

def _megaraid_print_ver():
    print ("MegaRAID Plugin Version: %s" % CliVer)
    print ("")

def _megaraid_list():
    usage="usage: %prog megaraid list [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser_update(parser, add_output=["normal",])

    (options, args) = parser.parse_args()
    ##
    script_check(options, admin_check=True)
    ##
    print_format = "%-20s %-20s %-40s %-26s %-16s %-8s"
    print (print_format % ("Node", "SN", "Model", "Capacity", "Format(L/P)", "FW Rev"))
    print (print_format % ("-"*20, "-"*20, "-"*40, "-"*26, "-"*16, "-"*8))
    for ctrl in get_raid_controllers():
        for disk in ctrl.retrieve_pds():
            if disk.protocal == "SATA":
                id_info = disk.identify_raw
                node = "c%d,d%d" % (disk.bus_no, disk.device_id)
                # Get the information of device
                invalid_symbol = b'\x00'.decode()
                sn = bytearray2string(translocate_bytearray(id_info[20:40])).strip().strip(invalid_symbol)
                fw = bytearray2string(translocate_bytearray(id_info[46:54]))
                mn = bytearray2string(translocate_bytearray(id_info[54:94])).strip().strip(invalid_symbol)
                logical_sector_num = int(binascii.hexlify(translocate_bytearray(id_info[200:208], 2)),16)
                if id_info[213] & 0xC0 == 0x40: # word 106 valid
                    if id_info[213] & 0x10:
                        logical_sector_size = int(binascii.hexlify(translocate_bytearray(id_info[234:238], 2)),16) * 2
                    else:
                        logical_sector_size = 512
                    if id_info[213] & 0x20:
                        relationship = 2 ** (id_info[212] & 0x0F)
                    else:
                        relationship = 1
                    physical_sector_size = logical_sector_size * relationship
                    ##
                    disk_format = "%s / %s" % (logical_sector_size, physical_sector_size)
                    cap = human_read_capacity(logical_sector_num*logical_sector_size)
                else:
                    disk_format = "Unknown"
                    cap = "Unknown"
                #
                if options.output_format == "normal":
                    print (print_format % (node, sn, mn, cap, disk_format, fw))

def _megaraid_identify():
    usage="usage: %prog megaraid identify <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("", "--ignore_error", dest="ignore_error", action="store_true", default=False,
        help="Ignore error that was checked out and continue to show the result")
    parser_update(parser, add_output=["normal", "hex", "raw", "json"])

    if len(sys.argv) > 3:
        (options, args) = parser.parse_args(sys.argv[3:])
        ## check device
        dev = sys.argv[3]
        g = re.fullmatch(r"c(\d+),d(\d+)", dev)
        if g:
            bus_no = int(g.group(1))
            device_id = int(g.group(2))
        else:
            parser.error("Invalid device: %s" % dev)
        ##
        script_check(options, admin_check=True)
        ##
        device = SATADrive(bus_no, device_id)
        cmd = device.identify()
        cmd.check_return_status(raise_if_fail=not options.ignore_error)
        format_print_identify(cmd, print_type=options.output_format)
    else:
        parser.print_help()

def _megaraid_smart():
    usage="usage: %prog megaraid smart <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser_update(parser, add_output=["normal", "hex", "raw", "json"], add_debug=True)

    if len(sys.argv) > 3:
        (options, args) = parser.parse_args(sys.argv[3:])
        ## check device
        dev = sys.argv[3]
        g = re.fullmatch(r"c(\d+),d(\d+)", dev)
        if g:
            bus_no = int(g.group(1))
            device_id = int(g.group(2))
        else:
            parser.error("Invalid device: %s" % dev)
        ##
        script_check(options, admin_check=True)
        ##
        from pydiskcmdcli.sata_spec import SMART_KEY
        #
        device = SATADrive(bus_no, device_id)
        cmd_read_data = device.smart_read_data(smart_key=SMART_KEY)
        cmd_thread = device.smart_thread()
        ##
        format_print_smart(cmd_read_data, cmd_thread, print_type=options.output_format)
    else:
        parser.print_help()


plugin_megaraid_commands_dict = {"list": _megaraid_list,
                                 "identify": _megaraid_identify,
                                 "smart": _megaraid_smart,
                                 "version": _megaraid_print_ver,
                                 "help": _megaraid_print_help,}

def meraraid_sata():
    if os_type != 'Linux':
        raise NotImplementedError("Only Linux MegaRAID support")
    if len(sys.argv) > 2:
        plugin_command = sys.argv[2]
        if plugin_command in plugin_megaraid_commands_dict:
            plugin_megaraid_commands_dict[plugin_command]()
            return
    _megaraid_print_help()
