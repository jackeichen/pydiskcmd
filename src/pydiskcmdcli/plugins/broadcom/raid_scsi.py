# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import sys
import optparse
import re
#
from pydiskcmdcli import os_type
from pydiskcmdlib.utils.converter import scsi_ba_to_int
from pydiskcmdcli.utils.format_print import format_dump_bytes,human_read_capacity
from pydiskcmdcli.scripts import parser_update,script_check
from pydiskcmdcli.utils.string_utils import decode_bytes,string_strip
from pydiskcmdlib.broadcom.raid import get_raid_controllers,RaidController,SASDrive
from pyscsi.pyscsi import scsi_enum_inquiry as INQUIRY
from pydiskcmdcli.scripts._scsi_common import (
    _inquiry_standard,
    _inquiry_supported_vpd_pages,
    _inquiry_block_limits,
    _inquiry_block_dev_char,
    _inquiry_logical_block_prov,
    _inquiry_unit_serial_number,
    _inquiry_device_identification,
    _inquiry_ata_information,
    _no_match_inq,
)
##
CliVer = "0.1"

def _megaraid_print_help():
    if len(sys.argv) > 3 and sys.argv[3] in plugin_megaraid_commands_dict:
        func_name,sys.argv[3] = sys.argv[3],"--help"
        plugin_megaraid_commands_dict[func_name]()
    else:
        print ("usage: pyscsi megaraid <command> [<device>] [<args>]")
        print ("")
        print (r"The '<device>' is a string(ex: c0,d99) split by ',' that include")
        print (r"Controller ID(ex: c0) and Disk ID(ex: d99).")
        print ("")
        print ("Linux MegaRAID extensions")
        print ("")
        print ("The following are all implemented sub-commands:")
        print ("")
        print ("  list                          List all SAS devices attached to Broadcom RAID controllers")
        print ("  inq                           Send scsi inquiry command")
        print ("  readcap                       Read capacity from target SCSI device")
        print ("  version                       Shows plugin version")
        print ("  help                          Display this help")
        print ("")
        print ("See 'pyscsi megaraid help <command>' for more information on a specific command")

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
    print_format = "%-20s %-10s %-30s %-40s %-26s %-16s %-8s"
    print (print_format % ("Node", "Protocal", "SN", "Model", "Capacity", "Format(L/P)", "FW Rev"))
    print (print_format % ("-"*20, "-"*10, "-"*30, "-"*40, "-"*26, "-"*16, "-"*8))
    ##
    for ctrl in get_raid_controllers():
        for disk in ctrl.retrieve_pds():
            if disk.protocal == "SAS":
                device_type = 'scsi'
            elif disk.protocal == "SATA":
                device_type = 'ata'
                # force to SAS device
                disk = SASDrive(disk.bus_no, disk.device_id)
            else:
                continue
            #
            dev_path = "c%s,d%s" % (disk.bus_no, disk.device_id)
            serial_info = disk.inquiry(evpd=1, page_code=INQUIRY.VPD.UNIT_SERIAL_NUMBER).result
            inq_info = disk.inquiry().result
            cap = disk.readcapacity16().result
            # Get the information of device
            serial = 'Unknown'
            model = 'Unknown'

            serial = string_strip(decode_bytes(serial_info.get('unit_serial_number')), b'\x00'.decode(), ' ')
            serial = serial if serial else 'Unknown'
            model = string_strip(decode_bytes(inq_info.get('product_identification')), b'\x00'.decode(), ' ')
            model = model if model else 'Unknown'
            fw = decode_bytes(inq_info.get('product_revision_level'))
            logical_sector_num = cap["returned_lba"]
            logical_sector_size = cap["block_length"]
            physical_sector_size = (2 ** cap["lbppbe"]) * logical_sector_size
            disk_format = "%s / %s" % (logical_sector_size, physical_sector_size)
            disk_cap = human_read_capacity(logical_sector_size * logical_sector_num)
            if options.output_format == "normal":
                print (print_format % (dev_path, device_type, serial, model, disk_cap, disk_format, fw))

def _megaraid_inq():
    usage="usage: %prog megaraid inq <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-p", "--page", type="int", dest="page_code", action="store", default=-1,
        help="Vital Product Data (VPD) page number or abbreviation")
    parser.add_option("-l", "--alloclen", type="int", dest="alloclen", action="store", default=96,
        help="Transfer data length, default 96")
    parser_update(parser, add_output=["normal", "hex", "raw"], add_debug=True)

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
        #
        evpd = 0
        if options.page_code >= 0:
            evpd = 1
        ##
        d = SASDrive(bus_no, device_id)
        if not evpd:
            _inquiry_standard(d, options)
            return

        if options.page_code == INQUIRY.VPD.SUPPORTED_VPD_PAGES:
            _inquiry_supported_vpd_pages(d, options)
            return

        if options.page_code == INQUIRY.VPD.BLOCK_LIMITS:
            _inquiry_block_limits(d, options)
            return

        if options.page_code == INQUIRY.VPD.BLOCK_DEVICE_CHARACTERISTICS:
            _inquiry_block_dev_char(d, options)
            return

        if options.page_code == INQUIRY.VPD.LOGICAL_BLOCK_PROVISIONING:
            _inquiry_logical_block_prov(d, options)
            return

        if options.page_code == INQUIRY.VPD.UNIT_SERIAL_NUMBER:
            _inquiry_unit_serial_number(d, options)
            return

        if options.page_code == INQUIRY.VPD.DEVICE_IDENTIFICATION:
            _inquiry_device_identification(d, options)
            return

        if options.page_code == INQUIRY.VPD.ATA_INFORMATION:
            _inquiry_ata_information(d, options)
            return

        _no_match_inq(d, options)
    else:
        parser.print_help()

def _megaraid_readcap():
    usage="usage: %prog megaraid readcap <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser_update(parser, add_output=["normal", "hex", "raw"])

    if len(sys.argv) > 2:
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
        d = SASDrive(bus_no, device_id)
        ##
        cmd = d.readcapacity16()
        r = cmd.result
        if not r['lbpme']:
            print('LUN is fully provisioned.')
            print ("")
        ##
        if options.output_format == "normal":
            print ("Read Capacity results:")
            print ("  Last LBA=%d (%#x), Number of logical blocks=%d" % (r["returned_lba"], r["returned_lba"], r["returned_lba"]+1))
            print ("  Logical block length=%d bytes" % r["block_length"])
            if r["lbppbe"] == 0:
                print ("  Physical block length is One or more physical blocks per logical block")
            else:
                print ("  Physical block length=%d bytes" % (2 ** r["lbppbe"] * r["block_length"]))
        elif options.output_format == "hex":
            format_dump_bytes(cmd.datain)
        else:
            print (bytes(cmd.datain))
    else:
        parser.print_help()

plugin_megaraid_commands_dict = {"list": _megaraid_list,
                                 "inq": _megaraid_inq,
                                 "readcap": _megaraid_readcap,
                                 "version": _megaraid_print_ver,
                                 "help": _megaraid_print_help,}

def meraraid_scsi():
    if os_type != 'Linux':
        raise NotImplementedError("Only Linux MegaRAID support")
    if len(sys.argv) > 2:
        plugin_command = sys.argv[2]
        if plugin_command in plugin_megaraid_commands_dict:
            plugin_megaraid_commands_dict[plugin_command]()
            return
    _megaraid_print_help()
