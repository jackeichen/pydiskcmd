# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import sys
import binascii
import optparse
import traceback

from pydiskcmdcli import os_type,log
from pydiskcmdlib.utils import init_device
from pydiskcmdlib.utils.converter import scsi_ba_to_int
from pydiskcmdcli.utils.format_print import format_dump_bytes,human_read_capacity
from pydiskcmdcli.scripts import parser_update,script_check
from pydiskcmdcli.utils.string_utils import decode_bytes,string_strip
from pydiskcmdcli.system.win_os_tool import scan_all_physical_drive
from pydiskcmdlib.rst.rst_controller import RSTController
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
from pydiskcmdcli import log

def scan_rst_controller():
    for device_path in scan_all_physical_drive(device_type='Scsi'):
        try:
            log.debug("Find Device Node %s" % device_path)
            device = init_device(device_path, open_t='rst')
            raid_controller = RSTController(device)
            log.debug("Find RST Controller %s" % device)
            yield raid_controller
        except Exception as e:
            # import traceback
            # traceback.print_exc()
            # print ("Device %s occur error: %s" % (device, str(e)))
            log.debug("May Not a RST Controller, close Device Node %s" % device_path)
            device.close()
    return

def _win_sata_rst_print_help():
    if len(sys.argv) > 3 and sys.argv[3] in plugin_win_sata_rst_commands_dict:
        func_name,sys.argv[3] = sys.argv[3],"--help"
        plugin_win_sata_rst_commands_dict[func_name]()
    else:
        print ("usage: pysata rst <command> [<device>] [<args>]")
        print ("")
        print (r"The '<device>' is a string(ex: \\.\Scsi0:/0) split by '/' that include")
        print (r"RST Controller(ex: \\.\Scsi0:) and RST Disk PHY ID.")
        print ("")
        print ("Windows SATA RST extensions")
        print ("")
        print ("The following are all implemented sub-commands:")
        print ("")
        print ("  list                          List All SATA RST disks")
        print ("  identify                      Send Identify command to SATA Disk under RST controller")
        print ("  smart                         Send SMART command to SATA Disk under RST controller")
        print ("  smart-return-status           Get SMART Return Status")
        print ("  smart-read-log                Get SMART Log Data")
        print ("  read-log                      Get Log Data")
        print ("  get-fw-info                   Get SATA RST disk firmware info")
        print ("  version                       Shows Windows SATA RST plugin version")
        print ("  help                          Display this help")
        print ("")
        print ("See 'pysata rst help <command>' for more information on a specific command")

def _win_sata_rst_print_ver():
    print ("Windows SATA RST Plugin Version: %s" % "1.0")
    print ("")

def _win_sata_rst_list():
    usage="usage: %prog rst list"
    parser = optparse.OptionParser(usage)
    parser_update(parser, add_output=["normal", "json"])

    (options, args) = parser.parse_args()
    ##
    script_check(options, admin_check=True)
    ##
    print_format = "%-20s %-20s %-40s %-26s %-16s %-8s"
    print (print_format % ("Node", "SN", "Model", "Capacity", "Format(L/P)", "FW Rev"))
    print (print_format % ("-"*12, "-"*20, "-"*40, "-"*26, "-"*16, "-"*8))
    ##
    for ctrl in scan_rst_controller():
        log.debug("Scan disks ...")
        for disk in ctrl.get_sata_disks():
            node = "Unknown"
            try:
                node = "\\\\.\\%s/%s" % (disk.device.device_name, disk.dev_node)
                log.debug("disks %s init information" % node)
                cmd = disk.identify()
                log.debug("disks %s init information done!" % node)
                cmd.check_return_status(fail_hint=False, raise_if_fail=True)
                id_info = bytes(cmd.cdb.bDataBuffer)
                invalid_symbol = b'\x00'.decode()
                sn = bytearray2string(translocate_bytearray(bytearray(id_info[20:40]))).strip().strip(invalid_symbol)
                fw = bytearray2string(translocate_bytearray(bytearray(id_info[46:54])))
                mn = bytearray2string(translocate_bytearray(bytearray(id_info[54:94]))).strip().strip(invalid_symbol)
                logical_sector_num = int(binascii.hexlify(translocate_bytearray(bytearray(id_info[200:208]), 2)),16)
                if id_info[213] & 0xC0 == 0x40: # word 106 valid
                    if id_info[213] & 0x10:
                        logical_sector_size = int(binascii.hexlify(translocate_bytearray(bytearray(id_info[234:238]), 2)),16) * 2
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
                    if options.output_format == "normal":
                        print (print_format % (node, sn, mn, cap, disk_format, fw))
            except:
                log.debug("Skip Device[%s]: %s" % (node, traceback.format_exc()))

def _win_sata_rst_identify():
    usage="usage: %prog rst identify <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser_update(parser, add_output=["normal", "hex", "raw", "json"], add_debug=True)

    (options, args) = parser.parse_args()
    if len(sys.argv) > 3:
        script_check(options, admin_check=True)
        ## device path
        dev = sys.argv[3].strip().split('/')
        ctrl_path,phy_id = dev
        phy_id = int(phy_id)
        # print (dev, ctrl_path,phy_id)
        ## check out the target disk
        with RSTController(init_device(ctrl_path, open_t='rst')) as ctrl:
            for disk in ctrl.get_sata_disks():
                if disk._phy_id == phy_id:
                    break
            else:
                print ("Disk %s not found" % sys.argv[3])
                return 1
            ##
            cmd = disk.identify()
        cmd.unmarshall_datain()
        format_print_identify(cmd, print_type=options.output_format)
    else:
        parser.print_help()

def _win_sata_rst_smart():
    usage="usage: %prog rst smart <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser_update(parser, add_output=["normal", "hex", "raw", "json"], add_debug=True)

    (options, args) = parser.parse_args()
    if len(sys.argv) > 3:
        script_check(options, admin_check=True)
        ## device path
        dev = sys.argv[3].strip().split('/')
        ctrl_path,phy_id = dev
        phy_id = int(phy_id)
        # print (dev, ctrl_path,phy_id)
        ## check out the target disk
        with RSTController(init_device(ctrl_path, open_t='rst')) as ctrl:
            for disk in ctrl.get_sata_disks():
                if disk._phy_id == phy_id:
                    break
            else:
                print ("Disk %s not found" % sys.argv[3])
                return 1
            ##
            from pydiskcmdcli.sata_spec import SMART_KEY
            cmd_read_data = disk.smart_read_data(SMART_KEY)
            cmd_read_data.check_return_status()
            #
            cmd_thread = disk.smart_read_thresh()
            cmd_thread.check_return_status()
        cmd_read_data.unmarshall_datain()
        format_print_smart(cmd_read_data, cmd_thread, print_type=options.output_format)
    else:
        parser.print_help()


def _win_sata_rst_smart_return_status():
    usage="usage: %prog rst smart-return-status <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser_update(parser, add_debug=True)

    (options, args) = parser.parse_args()
    if len(sys.argv) > 3:
        script_check(options, admin_check=True)
        ## device path
        dev = sys.argv[3].strip().split('/')
        ctrl_path,phy_id = dev
        phy_id = int(phy_id)
        # print (dev, ctrl_path,phy_id)
        ## check out the target disk
        with RSTController(init_device(ctrl_path, open_t='rst')) as ctrl:
            for disk in ctrl.get_sata_disks():
                if disk._phy_id == phy_id:
                    break
            else:
                print ("Disk %s not found" % sys.argv[3])
                return 1
            ##
            cmd = disk.smart_return_status()
        cmd.check_return_status()
        status_code = cmd.ata_status_return_descriptor['LBA'] >> 8
        if status_code == 0xC24F:
            print ("The subcommand specified a captive self-test that has completed without error")
        elif status_code == 0x2CF4:
            print ("The device has detected a threshold exceeded condition")
        else:
            print ("Got Undefined Values %#X" % status_code)
    else:
        parser.print_help()

def _win_sata_rst_smart_read_log():
    usage="usage: %prog rst smart-read-log <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-l", "--log-address", type="int", dest="log_address", action="store", default=0,
        help="Log address to read")
    parser.add_option("-c", "--count", type="int", dest="count", action="store", default=1,
        help="Read log data transfer length, 512 Bytes per count")
    parser_update(parser, add_output=["normal", "hex", "raw"])

    (options, args) = parser.parse_args()
    if len(sys.argv) > 3:
        script_check(options, admin_check=True)
        ## device path
        dev = sys.argv[3].strip().split('/')
        ctrl_path,phy_id = dev
        phy_id = int(phy_id)
        # print (dev, ctrl_path,phy_id)
        ## check out the target disk
        with RSTController(init_device(ctrl_path, open_t='rst')) as ctrl:
            for disk in ctrl.get_sata_disks():
                if disk._phy_id == phy_id:
                    break
            else:
                print ("Disk %s not found" % sys.argv[3])
                return 1
            ##
            cmd = disk.smart_read_log(options.log_address, options.count)
        cmd.check_return_status()
        if cmd.datain:
            if options.output_format == "normal":
                func = smart_read_log_format_print_set.get(options.log_address)
                if func:
                    func(cmd.datain)
                else:
                    format_dump_bytes(cmd.datain) 
            elif options.output_format == "raw":
                print (cmd.datain)
            else:
                format_dump_bytes(cmd.datain) 
        else:
            print ("Something wrong while read log, no data read from log page.")
    else:
        parser.print_help()

def _win_sata_rst_read_log():
    usage="usage: %prog rst read-log <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-l", "--log-address", type="int", dest="log_address", action="store", default=0,
        help="Log address to read")
    parser.add_option("-p", "--page-number", type="int", dest="page_number", action="store", default=0,
        help="Page number offset in this log address")
    parser.add_option("-c", "--count", type="int", dest="count", action="store", default=1,
        help="Read log data transfer length, 512 Bytes per count")
    parser.add_option("-f", "--feature", type="int", dest="feature", action="store", default=0,
        help="Specify a feature in read log")
    parser_update(parser, add_output=["normal", "hex", "raw"])

    (options, args) = parser.parse_args()
    if len(sys.argv) > 3:
        script_check(options, admin_check=True)
        ## device path
        dev = sys.argv[3].strip().split('/')
        ctrl_path,phy_id = dev
        phy_id = int(phy_id)
        # print (dev, ctrl_path,phy_id)
        ## check out the target disk
        with RSTController(init_device(ctrl_path, open_t='rst')) as ctrl:
            for disk in ctrl.get_sata_disks():
                if disk._phy_id == phy_id:
                    break
            else:
                print ("Disk %s not found" % sys.argv[3])
                return 1
            ##
            cmd = disk.read_log(options.log_address, options.count, page_number=options.page_number, feature=options.feature)
        cmd.check_return_status()
        if cmd.datain:
            if options.output_format == "normal":
                func = read_log_format_print_set.get(options.log_address)
                if func:
                    if options.log_address == 0x07:
                        func(cmd.datain, options.page_number)
                    else:
                        func(cmd.datain)
                else:
                    format_dump_bytes(cmd.datain) 
            elif options.output_format == "raw":
                print (cmd.datain)
            else:
                format_dump_bytes(cmd.datain) 
        else:
            print ("Something wrong while read log, no data read from log page.")
    else:
        parser.print_help()

def _win_sata_rst_get_fw_info():
    usage="usage: %prog rst get-fw-info"
    parser = optparse.OptionParser(usage)
    parser_update(parser, add_output=["normal", "json"])

    (options, args) = parser.parse_args()
    ##
    script_check(options, admin_check=True)
    ##
    if len(sys.argv) > 3:
        ## device path
        dev = sys.argv[3].strip().split('/')
        ctrl_path,phy_id = dev
        phy_id = int(phy_id)
        # print (dev, ctrl_path,phy_id)
        ##
        with RSTController(init_device(ctrl_path, open_t='csmi')) as ctrl:
            for disk in ctrl.get_sata_disks():
                if disk._phy_id == phy_id:
                    break
            else:
                print ("Disk %s not found" % sys.argv[3])
                return 1
            ##
            cmd = disk.get_firmware_info()
        cmd.check_return_status(raise_if_fail=True)
        print (cmd.unmarshall_cdb())
    else:
        parser.print_help()


plugin_win_sata_rst_commands_dict = {"list": _win_sata_rst_list,
                                     "identify": _win_sata_rst_identify,
                                     "smart": _win_sata_rst_smart,
                                     "smart-return-status": _win_sata_rst_smart_return_status,
                                     "smart-read-log": _win_sata_rst_smart_read_log,
                                     "read-log": _win_sata_rst_read_log,
                                     "get-fw-info": _win_sata_rst_get_fw_info,
                                     "version": _win_sata_rst_print_ver,
                                     "help": _win_sata_rst_print_help,}

def win_sata_rst():
    if os_type != 'Windows':
        raise NotImplementedError("Only Windows NVMe VROC support")
    if len(sys.argv) > 2:
        plugin_command = sys.argv[2]
        if plugin_command in plugin_win_sata_rst_commands_dict:
            return plugin_win_sata_rst_commands_dict[plugin_command]()
    _win_sata_rst_print_help()
