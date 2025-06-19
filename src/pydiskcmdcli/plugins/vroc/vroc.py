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
        print ("  id-ctrl                       Send NVMe Identify Controller")
        print ("  id-ns                         Send NVMe Identify Namespace, display structure")
        print ("  smart-log                     Retrieve SMART Log, show it")
        print ("  error-log                     Retrieve Error Log, show it")
        print ("  get-feature                   Get feature and show the resulting value")
        print ("  version                       Shows Windows NVMe VROC plugin version")
        print ("  help                          Display this help")
        print ("")
        print ("See 'pynvme vroc help <command>' for more information on a specific command")

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

def _id_ctrl():
    usage="usage: %prog id-ctrl <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-U", "--uuid-index", type="int", dest="uuid_index", action="store", default=0,
        help="UUID index")
    parser_update(parser, add_output=["normal", "hex", "raw", "json"])

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[3].strip().split('/')
        ctrl_path,vrocDiskID = dev
        vrocDiskID = int(vrocDiskID, 16)
        ##
        script_check(options, admin_check=True)
        with NVMeDisk(init_device(ctrl_path, open_t='vroc'), vrocDiskID) as d:
            cmd = d.id_ctrl(uuid=options.uuid_index)
        cmd.check_return_status(raise_if_fail=True)
        nvme_format_print.format_print_id_ctrl(cmd.data, print_type=options.output_format)
    else:
        parser.print_help()

def _id_ns():
    usage="usage: %prog id-ns <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-n", "--namespace-id", type="int", dest="namespace_id", action="store",default=1,
        help="identifier of desired namespace. Default 1")
    parser.add_option("-U", "--uuid-index", type="int", dest="uuid_index", action="store", default=0,
        help="UUID index")
    parser_update(parser, add_output=["normal", "hex", "raw", "json"])

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[3].strip().split('/')
        ctrl_path,vrocDiskID = dev
        vrocDiskID = int(vrocDiskID, 16)
        ## check namespace
        if not isinstance(options.namespace_id, int) or options.namespace_id < 1:
            parser.error("namespace id input error.")
        ##
        script_check(options, admin_check=True)
        with NVMeDisk(init_device(ctrl_path, open_t='vroc'), vrocDiskID) as d:
            cmd = d.id_ns(options.namespace_id, uuid=options.uuid_index)
        cmd.check_return_status(raise_if_fail=True)
        ##
        nvme_format_print.format_print_id_ns(cmd.data, print_type=options.output_format)
    else:
        parser.print_help()

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

def _error_log():
    usage="usage: %prog vroc error-log <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser_update(parser, add_output=["normal", "hex", "raw", "json"])

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[3].strip().split('/')
        ctrl_path,vrocDiskID = dev
        vrocDiskID = int(vrocDiskID, 16)
        ##
        script_check(options, admin_check=True)
        with NVMeDisk(init_device(ctrl_path, open_t='vroc'), vrocDiskID) as d:
            cmd = d.error_log_entry()
        cmd.check_return_status(raise_if_fail=True)
        ##
        nvme_format_print.format_print_error_log(cmd.data, dev=dev, print_type=options.output_format)
    else:
        parser.print_help()

def _get_feature_power_management(device_context, options):
    cmd = device_context.get_feature(2, sel=options.sel)
    return cmd

def _get_feature_lba_range_type(device_context, options):
    options.data_len = 64
    cmd = device_context.get_feature(3, sel=options.sel, data_length=options.data_len)
    return cmd

def _get_feature():
    usage="usage: %prog get-feature <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-n", "--namespace-id", type="int", dest="namespace_id", action="store", default=0,
        help="identifier of desired namespace")
    parser.add_option("-f", "--feature-id", type="int", dest="feature_id", action="store", default=0,
        help="feature identifier")
    parser.add_option("-s", "--sel", type="int", dest="sel", action="store", default=0,
        help="[0-3]: current/default/saved/supported")
    parser.add_option("-l", "--data-len", type="int", dest="data_len", action="store", default=0,
        help="buffer len if data is returned through host memory buffer")
    parser.add_option("-c", "--cdw11", type="int", dest="cdw11", action="store", default=0,
        help="dword 11 for interrupt vector config")
    parser_update(parser, add_output=["normal", "hex", "raw"])

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[3].strip().split('/')
        ctrl_path,vrocDiskID = dev
        vrocDiskID = int(vrocDiskID, 16)
        #
        if options.feature_id < 1:
            parser.error("You should give a valid feature id")
        ##
        script_check(options, admin_check=True)
        result = {}
        with NVMeDisk(init_device(ctrl_path, open_t='vroc'), vrocDiskID) as d:
            if options.feature_id == 2:
                cmd = _get_feature_power_management(d, options)
                result = nvme_format_print.nvme_power_management_cq_decode(cmd.cq_cmd_spec)
            elif options.feature_id == 3:
                cmd = _get_feature_lba_range_type(d, options)
            else:
                cmd = d.get_feature(options.feature_id,
                                    nsid=options.namespace_id,
                                    sel=options.sel,
                                    cdw11=options.cdw11,
                                    data_length=options.data_len)
        cmd.check_return_status(raise_if_fail=True)
        ##
        if options.output_format == "hex":
            print ("cmd spec data: %#x" % cmd.cq_cmd_spec)
            print ('')
            if options.data_len > 0:
                print ('')
                print ("cmd data:")
                format_dump_bytes(cmd.data)
        elif options.output_format == "normal":
            if result:
                for k,v in result.items():
                    print ("%-5s: %s" % (k,v))
            else:
                print ("cmd spec data: %#x" % cmd.cq_cmd_spec)
                print ('')
                if options.data_len > 0:
                    print ('')
                    print ("cmd data:")
                    format_dump_bytes(cmd.data)
        else:
            print ("cmd spec data: %#x" % cmd.cq_cmd_spec)
            print ('')
            if options.data_len > 0:
                print ('')
                print ("cmd data:")
                print (cmd.data)
    else:
        parser.print_help()

plugin_win_nvme_vroc_commands_dict = {"list": _win_nvme_vroc_list,
                                      "id-ctrl": _id_ctrl,
                                      "id-ns": _id_ns,
                                      "smart-log": _win_nvme_vroc_smart_log,
                                      "error-log": _error_log,
                                      "get-feature": _get_feature,
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
