# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import sys
import binascii
import optparse

from pydiskcmdcli import os_type
from pydiskcmdlib.utils import init_device
from pydiskcmdlib.utils.converter import scsi_ba_to_int
from pydiskcmdcli.utils.format_print import format_dump_bytes,human_read_capacity
from pydiskcmdcli.scripts import parser_update,script_check
from pydiskcmdcli.utils.string_utils import decode_bytes,string_strip
from pydiskcmdcli.system.win_os_tool import scan_all_physical_drive
from pydiskcmdlib.rst.rst_controller import RSTController
from pydiskcmdlib.utils.converter import bytearray2string,translocate_bytearray

def scan_rst_controller():
    for device in scan_all_physical_drive(device_type='Scsi'):
        try:
            device = init_device(device, open_t='csmi')
            raid_controller = RSTController(device)
            yield raid_controller
        except Exception as e:
            # import traceback
            # traceback.print_exc()
            # print ("Device %s occur error: %s" % (device, str(e)))
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
        print ("  version                       Shows Windows NVMe VROC plugin version")
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
        for disk in ctrl.get_sata_disks():
            node = "\\\\.\\%s/%s" % (disk.device.device_name, disk.dev_node)
            cmd = disk.identify()
            cmd.check_return_status(raise_if_fail=True)
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


plugin_win_sata_rst_commands_dict = {"list": _win_sata_rst_list,
                                     "version": _win_sata_rst_print_ver,
                                     "help": _win_sata_rst_print_help,}

def win_sata_rst():
    if os_type != 'Windows':
        raise NotImplementedError("Only Windows NVMe VROC support")
    if len(sys.argv) > 2:
        plugin_command = sys.argv[2]
        if plugin_command in plugin_win_sata_rst_commands_dict:
            plugin_win_sata_rst_commands_dict[plugin_command]()
            return
    _win_sata_rst_print_help()
