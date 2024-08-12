# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import sys
import optparse

from pydiskcmdcli import os_type
from pydiskcmdlib.utils import init_device
from pydiskcmdcli.utils import nvme_format_print
from pydiskcmdlib.utils.converter import scsi_ba_to_int
from pydiskcmdcli.utils.format_print import format_dump_bytes,human_read_capacity
from pydiskcmdcli.scripts import parser_update,script_check
from pydiskcmdcli.utils.string_utils import decode_bytes,string_strip
from .scan_nvme_raid_controller import (
    VROC_ENABLE,
    scan_nvme_raid_controller,
)

vroc_plugin = {"scan_nvme_raid_controller": scan_nvme_raid_controller,
               }

if VROC_ENABLE:
    from pydiskcmdlib.vroc.nvme_raid import NVMeDisk  # noqa

def _win_nvme_vroc_print_help():
    if len(sys.argv) > 3 and sys.argv[3] in plugin_win_nvme_vroc_commands_dict:
        func_name,sys.argv[3] = sys.argv[3],"--help"
        plugin_win_nvme_vroc_commands_dict[func_name]()
    else:
        print ("usage: pynvme vroc <command> [<device>] [<args>]")
        print ("")
        print (r"The '<device>' is a string(ex: \\.\Scsi0:/390) split by '/' that include")
        print (r"VROC Controller(ex: \\.\Scsi0:) and VROC Disk ID.")
        print ("")
        print ("Windows NVMe VROC extensions")
        print ("")
        print ("The following are all implemented sub-commands:")
        print ("")
        print ("  list                          List All NVME VROC disks")
        print ("  smart-log                     Retrieve SMART Log, show it")
        print ("  version                       Shows Windows NVMe VROC plugin version")
        print ("  help                          Display this help")
        print ("")
        print ("See 'pynvme ocp help <command>' for more information on a specific command")

def _win_nvme_vroc_print_ver():
    print ("Windows NVMe VROC Plugin Version: %s" % "1.0")
    print ("")

def _win_nvme_vroc_list():
    usage="usage: %prog vroc list"
    parser = optparse.OptionParser(usage)
    parser_update(parser, add_output=["normal", "json"])

    (options, args) = parser.parse_args()
    ##
    script_check(options, admin_check=True)
    ##
    print_format = "%-20s %-11s %-20s %-40s %-9s %-26s %-16s %-8s"
    print (print_format % ("Node", "Raid Type", "SN", "Model", "Namespace", "Usage", "Format", "FW Rev"))
    print (print_format % ("-"*20, "-"*11, "-"*20, "-"*40, "-"*9, "-"*26, "-"*16, "-"*8))
    ##
    def list_disk(ctrl_path, raid_type, disk):
        node = "%s/%#x" % (ctrl_path, disk._vrocDiskID)
        ns_id = '-'  # windows should - , 
        try:
            cmd_id_ctrl = disk.id_ctrl()
            cmd_id_ns = disk.id_ns()
        except OSError:
            return 1
        # para data
        result = nvme_format_print.nvme_id_ctrl_decode(cmd_id_ctrl.data)
        sn = string_strip(decode_bytes(result.get("SN")), b'\x00'.decode(), ' ')
        mn = string_strip(decode_bytes(result.get("MN")), b'\x00'.decode(), ' ')
        fw = string_strip(decode_bytes(result.get("FR")), b'\x00'.decode(), ' ')
        #
        result = nvme_format_print.nvme_id_ns_decode(cmd_id_ns.data)
        lbaf = result.get("LBAF").get(scsi_ba_to_int(result.get("FLBAS"), 'little') & 0x0F)
        meta_size = scsi_ba_to_int(lbaf.get("MS"), 'little')
        lba_data_size = scsi_ba_to_int(lbaf.get("LBADS"), 'little')
        _format = "%-6sB + %-3sB" % (2 ** lba_data_size, meta_size)
        #
        NUSE_B = scsi_ba_to_int(result.get("NUSE"), 'little') * (2 ** lba_data_size)
        NCAP_B = scsi_ba_to_int(result.get("NCAP"), 'little') * (2 ** lba_data_size)
        usage = "%-6s / %-6s" % (human_read_capacity(NUSE_B), human_read_capacity(NCAP_B))
        if options.output_format == "normal":
            print (print_format % (node, raid_type, sn, mn, ns_id, usage, _format, fw))
    ##
    for vroc_ctrl in vroc_plugin['scan_nvme_raid_controller']():
        ## First check disks in raid volume
        ctrl_path = vroc_ctrl.device._file_name
        for raid in vroc_ctrl.get_raid_volumes():
            cmd = raid.raid_information()
            raid_type = bytes(cmd.cdb.raidType).strip(b'\x00').decode()
            for disk in raid.get_disk():
                list_disk(ctrl_path, raid_type, disk)
        ## then check passthrough disks
        raid_type = 'PASSTHROUGH'          
        for disk in vroc_ctrl.get_passthrough_disks():
            list_disk(ctrl_path, raid_type, disk)
        ## 
        raid_type = 'SPARE'          
        for disk in vroc_ctrl.get_spare_disks():
            list_disk(ctrl_path, raid_type, disk)
        ##
        raid_type = 'JOURNALING'          
        for disk in vroc_ctrl.get_journaling_disks():
            list_disk(ctrl_path, raid_type, disk)

def _win_nvme_vroc_smart_log():
    usage="usage: %prog vroc smart-log <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser_update(parser, add_output=["normal", "hex", "raw", "json"])

    if len(sys.argv) > 3:
        (options, args) = parser.parse_args(sys.argv[3:])
        ##
        script_check(options, admin_check=True)
        ## check device
        dev = sys.argv[3].strip().split('/')
        ctrl_path,vrocDiskID = dev
        vrocDiskID = int(vrocDiskID, 16)
        ##
        with NVMeDisk(init_device(ctrl_path, open_t='vroc'), vrocDiskID) as d:
            cmd = d.smart_log()
        cmd.check_return_status()
        ##
        nvme_format_print.format_print_smart_log(cmd.data, print_type=options.output_format)
    else:
        parser.print_help()


plugin_win_nvme_vroc_commands_dict = {"list": _win_nvme_vroc_list,
                                      "smart-log": _win_nvme_vroc_smart_log,
                                      "version": _win_nvme_vroc_print_ver,
                                      "help": _win_nvme_vroc_print_help,}

def win_nvme_vroc():
    if not VROC_ENABLE:
        raise NotImplementedError(" NVMe VROC does not support due to Not Enable")
    if os_type != 'Windows':
        raise NotImplementedError("Only Windows NVMe VROC support")
    if len(sys.argv) > 2:
        plugin_command = sys.argv[2]
        if plugin_command in plugin_win_nvme_vroc_commands_dict:
            plugin_win_nvme_vroc_commands_dict[plugin_command]()
            return
    _win_nvme_vroc_print_help()
