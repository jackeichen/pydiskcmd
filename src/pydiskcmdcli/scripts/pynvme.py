# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import sys,os
import optparse
from pydiskcmdlib.utils import init_device
from pydiskcmdlib.pynvme.nvme import NVMe
from pydiskcmdcli.plugins import ocp_plugin
from pydiskcmdcli.utils.format_print import format_dump_bytes,human_read_capacity
from pydiskcmdlib.utils.converter import scsi_ba_to_int
from pydiskcmdlib.pynvme.data_buffer import DataBuffer
from pydiskcmdcli.nvme_spec import (
    persistent_event_log_header_decode,
    persistent_event_log_events_decode,
)
## scan_nvme_ctrls
from pydiskcmdcli.utils import nvme_format_print
from pydiskcmdcli import os_type
from pydiskcmdcli import version as Version
from . import parser_update,script_check
from pydiskcmdcli.exceptions import (
    CommandSequenceError,
    CommandNotSupport,
    NonpydiskcmdError,
    UserDefinedError,
    FunctionNotImplementError,
)


def version():
    print ("pynvme version %s" % Version)

def print_help():
    if len(sys.argv) > 2 and sys.argv[2] in commands_dict:
        func_name,sys.argv[2] = sys.argv[2],"--help"
        commands_dict[func_name]()
    else:
        print ("pynvme-%s" % Version)
        print ("usage: pynvme <command> [<device>] [<args>]")
        print ("")
        print ("The '<device>' may be either an NVMe character device (ex: /dev/nvme0) or an")
        print ("nvme block device (ex: /dev/nvme0n1) in Linux, while PhysicalDrive<X> in Windows.")
        print ("")
        print ("The following are all implemented sub-commands:")
        print ("  list                  List all NVMe devices and namespaces on machine")
        print ("  list-subsys           List nvme subsystems")
        print ("  list-ns               Send NVMe Identify List, display structure")
        print ("  list-ctrl             Send NVMe Identify Controller List, display structure")
        print ("  id-ctrl               Send NVMe Identify Controller")
        print ("  id-ns                 Send NVMe Identify Namespace, display structure")
        print ("  id-uuid               Send NVMe Identify UUID List, display structure")
        print ("  create-ns             Creates a namespace with the provided parameters")
        print ("  delete-ns             Deletes a namespace from the controller")
        print ("  attach-ns             Attaches a namespace to requested controller(s)")
        print ("  detach-ns             Detaches a namespace from requested controller(s)")
        print ("  get-log               Generic NVMe get log, returns log in raw format")
        print ("  smart-log             Retrieve SMART Log, show it")
        print ("  error-log             Retrieve Error Log, show it")
        print ("  commands-se-log       Retrieve Commands Supported and Effects Log, and show it")
        print ("  fw-log                Retrieve FW Log, show it")
        print ("  sanitize-log          Retrieve Sanitize Log, show it")
        print ("  self-test-log         Retrieve the SELF-TEST Log, show it")
        print ("  telemetry-log         Retrieve the Telemetry Log, show it")
        print ("  persistent-event-log  Get persistent event log from device")
        print ("  reset                 Resets the controller")
        print ("  subsystem-reset       Resets the subsystem")
        print ("  fw-download           Download new firmware")
        print ("  fw-commit             Verify and commit firmware to a specific slot")
        print ("  get-feature           Get feature and show the resulting value")
        print ("  set-feature           Set a feature and show the resulting value")
        print ("  format                Format namespace with new block format")
        print ("  sanitize              Submit a sanitize command")
        print ("  device-self-test      Perform the necessary tests to observe the performance")
        print ("  pcie                  Get device PCIe status, show it")
        print ("  show-regs             Shows the controller registers or properties. Requires character device")
        print ("  flush                 Submit a flush command, return results")
        print ("  read                  Submit a read command, return results")
        print ("  verify                Submit a verify command, return results")
        print ("  write                 Submit a write command, return results")
        print ("  get-lba-status        Submit a Get LBA Status command, return results")
        print ("  version               Shows the program version")
        print ("  help                  Display this help")
        print ("")
        print ("See 'pynvme help <command>' or 'pynvme <command> --help' for more information on a sub-command")
        print ("")
        print ("The following are all installed plugin extensions:")
        print ("  ocp                   OCP cloud SSD extensions")
        print ("  vroc                  Windows NVMe VROC support") 
        print ("")
        print ("The following are pynvme cli management interface:")
        print ("  cli-info              Shows pynvme information")
        print ("  cli-autocmd           Enable or Update the command completion")
        print ("")
        print ("See 'pynvme <plugin> help' for more information on a plugin")

def _list():
    usage="usage: %prog list"
    parser = optparse.OptionParser(usage)
    parser_update(parser, add_output=["normal",])

    (options, args) = parser.parse_args()
    ##
    script_check(options, admin_check=True)
    ##
    print_format = "%-20s %-20s %-40s %-9s %-26s %-16s %-8s"
    print (print_format % ("Node", "SN", "Model", "Namespace", "Usage", "Format", "FW Rev"))
    print (print_format % ("-"*20, "-"*20, "-"*40, "-"*9, "-"*26, "-"*16, "-"*8))
    from pydiskcmdcli.system.lin_os_tool import scan_nvme_ctrls
    from pydiskcmdcli.utils.string_utils import decode_bytes,string_strip
    scsi_ba_to_int = nvme_format_print.scsi_ba_to_int
    if os_type == 'Linux':
        for ctrl_name,ctrl_info in scan_nvme_ctrls().items():
            with NVMe(init_device(ctrl_info.dev_path, open_t='nvme')) as d:
                cmd_id_ctrl = d.id_ctrl()
            result = nvme_format_print.nvme_id_ctrl_decode(cmd_id_ctrl.data)
            sn = string_strip(decode_bytes(result.get("SN")), b'\x00'.decode(), ' ')
            mn = string_strip(decode_bytes(result.get("MN")), b'\x00'.decode(), ' ')
            fw = string_strip(decode_bytes(result.get("FR")), b'\x00'.decode(), ' ')
            ##
            namespaces = ctrl_info.get_namespaces()
            for ns_name in sorted(namespaces.keys()):
                ns_info = namespaces[ns_name]
                node = ns_info.dev_path
                ns_id = ns_info.ns_id
                ## Get information now!
                ## send identify controller and identify namespace
                with NVMe(init_device(ctrl_info.dev_path, open_t='nvme')) as d:
                    cmd_id_ns = d.id_ns(ns_info.ns_id)
                ## para data
                result = nvme_format_print.nvme_id_ns_decode(cmd_id_ns.data)
                #
                lbaf = result.get("LBAF").get(scsi_ba_to_int(result.get("FLBAS"), 'little') & 0x0F)
                meta_size = scsi_ba_to_int(lbaf.get("MS"), 'little')
                lba_data_size = scsi_ba_to_int(lbaf.get("LBADS"), 'little')
                _format = "%-6sB + %-3sB" % (2 ** lba_data_size, meta_size)
                #
                NUSE_B = scsi_ba_to_int(result.get("NUSE"), 'little') * (2 ** lba_data_size)
                NCAP_B = scsi_ba_to_int(result.get("NCAP"), 'little') * (2 ** lba_data_size)
                usage = "%-6s / %-6s" % (human_read_capacity(NUSE_B), human_read_capacity(NCAP_B))
                if options.output_format == "normal":
                    print (print_format % (node, sn, mn, ns_id, usage, _format, fw))
    elif os_type == 'Windows':
        from  pydiskcmdcli.system.win_os_tool import scan_all_physical_drive
        for node in sorted([i for i in scan_all_physical_drive()]):
            ns_id = '-'  # windows should - , 
            ## Get information now!
            # send identify namespace, get the information
            # if physical drive cannot execute nvme identify namespace command,
            # then treat it as a non-nvme device.
            try:
                with NVMe(init_device(node, open_t='nvme')) as d:
                    cmd_id_ctrl = d.id_ctrl()
                    cmd_id_ns = d.id_ns()
            except:
                # may a non-nvme device, or an abnormal device,
                #
                continue
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
                print (print_format % (node, sn, mn, ns_id, usage, _format, fw))
    else:
        raise RuntimeError("OS %s Not support command list" % os_type)

def _list_subsys():
    usage="usage: %prog list-subsys"
    parser = optparse.OptionParser(usage)
    parser_update(parser, add_output=["normal",])
    (options, args) = parser.parse_args()
    ##
    script_check(options, admin_check=True)
    ##
    if os_type == 'Linux':
        from pydiskcmdcli.system.lin_os_tool import scan_nvme_subsystem
        subsystem = scan_nvme_subsystem()
        for name in sorted(subsystem):
            value = subsystem[name]
            print ("%s - NQN=%s" % (name, value.nqn))
            ctrls = value.get_ctrls()
            if ctrls:
                print ("\\")
                for i in sorted(ctrls):
                    ctrl = ctrls[i]
                    ## Get ctrl info
                    print (" +- %s %s %s %s - cntlid=%d" % (ctrl.ctrl_name, ctrl.transport, ctrl.address, ctrl.state, ctrl.cntlid))
                    nss = ctrl.get_namespaces()
                    if nss:
                        print (" \\")
                        for name in sorted(nss):
                            ns = nss[name]
                            print ("  +- %s - path=%s nsid=%d wwid=%s" % (name, ns.dev_path, ns.ns_id, ns.wwid))
    else:
        raise RuntimeError("OS %s Not support" % os_type)

def smart_log():
    usage="usage: %prog smart-log <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser_update(parser, add_output=["normal", "hex", "raw", "json"])

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, admin_check=True)
        with NVMe(init_device(dev, open_t='nvme')) as d:
            cmd = d.smart_log()
        cmd.check_return_status(raise_if_fail=True)
        ##
        nvme_format_print.format_print_smart_log(cmd.data, print_type=options.output_format)
    else:
        parser.print_help()

def id_ctrl():
    usage="usage: %prog id-ctrl <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-U", "--uuid-index", type="int", dest="uuid_index", action="store", default=0,
        help="UUID index")
    parser_update(parser, add_output=["normal", "hex", "raw", "json"])

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, admin_check=True)
        with NVMe(init_device(dev, open_t='nvme')) as d:
            cmd = d.id_ctrl(uuid=options.uuid_index)
        cmd.check_return_status(raise_if_fail=True)
        nvme_format_print.format_print_id_ctrl(cmd.data, print_type=options.output_format)
    else:
        parser.print_help()

def id_ns():
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
        dev = sys.argv[2]
        ## check namespace
        if not isinstance(options.namespace_id, int) or options.namespace_id < 1:
            parser.error("namespace id input error.")
        ##
        script_check(options, admin_check=True)
        with NVMe(init_device(dev, open_t='nvme')) as d:
            cmd = d.id_ns(options.namespace_id, uuid=options.uuid_index)
        cmd.check_return_status(raise_if_fail=True)
        ##
        nvme_format_print.format_print_id_ns(cmd.data, print_type=options.output_format)
    else:
        parser.print_help()

def id_uuid():
    usage="usage: %prog id-uuid <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser_update(parser, add_output=["normal", "hex", "raw", "json"])

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, admin_check=True)
        with NVMe(init_device(dev, open_t='nvme')) as d:
            cmd = d.uuid_list()
        SC,SCT = cmd.check_return_status(raise_if_fail=True)
        if SC == 0 and SCT == 0:
            nvme_format_print.format_print_id_uuid(cmd, print_type=options.output_format)
    else:
        parser.print_help()

def error_log():
    usage="usage: %prog error-log <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser_update(parser, add_output=["normal", "hex", "raw", "json"])

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, admin_check=True)
        with NVMe(init_device(dev, open_t='nvme')) as d:
            cmd = d.error_log_entry()
        cmd.check_return_status(raise_if_fail=True)
        ##
        nvme_format_print.format_print_error_log(cmd.data, dev=dev, print_type=options.output_format)
    else:
        parser.print_help()

def fw_log():
    usage="usage: %prog fw-log <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser_update(parser, add_output=["normal", "hex", "raw", "json"])

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, admin_check=True)
        with NVMe(init_device(dev, open_t='nvme')) as d:
            cmd = d.fw_slot_info()
        cmd.check_return_status(raise_if_fail=True)
        ##
        nvme_format_print.format_print_fw_log(cmd.data, dev=d.device.device_name, print_type=options.output_format)
    else:
        parser.print_help()

def sanitize_log():
    usage="usage: %prog sanitize-log <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser_update(parser, add_output=["normal", "hex", "raw", "json"])

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, admin_check=True)
        with NVMe(init_device(dev, open_t='nvme')) as d:
            cmd = d.sanitize_log(127, lpol=0)
        cmd.check_return_status(raise_if_fail=True)
        ##
        nvme_format_print.format_print_sanitize_log(cmd.data, dev=d.device.device_name, print_type=options.output_format)
    else:
        parser.print_help()

def telemetry_log():
    usage="usage: %prog telemetry-log <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-o", "--output-file", dest="output_file", action="store", default="",
        help="File name to save raw binary, includes header")
    parser.add_option("-g", "--host-generate", type="int", dest="host_generate", action="store", default=0,
        help="Have the host tell the controller to generate the report")
    parser.add_option("-c", "--controller-init", dest="controller_init", action="store_true", default=False,
        help="Gather report generated by the controller")
    parser.add_option("-d", "--data-area", type="int", dest="data_area", action="store", default=3,
        help="Pick which telemetry data area to report. Default is 3 to fetch areas 1-3. Valid options are 1, 2, 3, 4.")
    parser.add_option("-U", "--uuid-index", type="int", dest="uuid_index", action="store", default=0,
        help="UUID index")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        if not options.output_file:
            raise RuntimeError("Need an input file by -o/--output-file")
        ##
        script_check(options, admin_check=True)
        if options.controller_init: # Gather report generated by the controller
            with NVMe(init_device(dev, open_t='nvme')) as d:
                ## Get first 512 bytes log
                cmd = d.telemetry_ctrl_log(127)
                cmd.check_return_status(raise_if_fail=True)
                #
                if options.data_area == 1:
                    data_area_last = cmd.data[8] + (cmd.data[9] << 8)
                elif options.data_area == 2:
                    data_area_last = cmd.data[10] + (cmd.data[11] << 8)
                elif options.data_area == 3:
                    data_area_last = cmd.data[12] + (cmd.data[13] << 8)
                else:
                    data_area_last = 0
                with open(options.output_file, 'wb') as f:
                    ## 4k transfer
                    for i in range(data_area_last+1):
                        offset = int(i * 512)
                        lpol = offset & 0xFFFFFFFF
                        lpou = (offset >> 32) & 0xFFFFFFFF
                        cmd = d.telemetry_ctrl_log(127, lpol=lpol, lpou=lpou, uuid=options.uuid_index)
                        f.write(cmd.data)
        else: # Gather report generated by the host
            with NVMe(init_device(dev, open_t='nvme')) as d:
                ## Get first 512 bytes log
                cmd = d.telemetry_host_log(127)
                cmd.check_return_status(raise_if_fail=True)
                #
                data_area_last = 0
                if options.data_area == 1:
                    data_area_last = cmd.data[8] + (cmd.data[9] << 8)
                elif options.data_area == 2:
                    data_area_last = cmd.data[10] + (cmd.data[11] << 8)
                elif options.data_area == 3:
                    data_area_last = cmd.data[12] + (cmd.data[13] << 8)
                elif options.data_area == 4:
                    print ("Data area 4 Not support in pynvme!")
                with open(options.output_file, 'wb') as f:
                    for i in range(data_area_last+1):
                        offset = int(i * 512)
                        lpol = offset & 0xFFFFFFFF
                        lpou = (offset >> 32) & 0xFFFFFFFF
                        cmd = d.telemetry_host_log(127, lpol=lpol, lpou=lpou, uuid=options.uuid_index)
                        f.write(cmd.data)
    else:
        parser.print_help()

def fw_download():
    usage="usage: %prog fw-download <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-f", "--fw", type="str", dest="fw_path", action="store", default="",
        help="Firmware file path")
    parser.add_option("-x", "--xfer", type="int", dest="xfer", action="store", default=0,
        help="transfer chunksize in byte")
    parser.add_option("-o", "--offset", type="int", dest="offset", action="store", default=0,
        help="starting dword offset, default 0")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ## check namespace
        if not os.path.exists(options.fw_path):
            parser.error("No Firmware File provided")
        ##
        # if os_type == 'Windows':
        #     print ("Recommand a safety native methmod to download fimrware to device, with windows Power-Shell.")
        #     print ("")
        #     print ("1. First open Power-Shell with administrators;")
        #     print ("2. Get the UniqueId of PhysicalDriveX(X is the number):")
        #     print ("   > Get-Disk | Select Number, Uniqueid")
        #     print ("3. Download the firmware to target disk:")
        #     print ('   > Update-StorageFirmware -UniqueId "<UniqueId>" -ImagePath "<Firwmare_Ptah>" -SlotNumber <Slot_Number>')
        #     print ('')
        #     print ("Note: You may need to active the new firmware after download.")
        #     print ('')
        #     return 0
        script_check(options, admin_check=True)
        with NVMe(init_device(dev, open_t='nvme')) as d:
            ## Get FWUG, fwug is in dward
            fwug = d.ctrl_identify_info[319] & 0xFF
            # 0h indicates that no information on granularity is provided
            # FFh indicates there is no restriction
            # then default to 4KiB
            if fwug == 0 or fwug == 0xFF:
                fwug_b = 4096     # 0h indicates that no information on granularity is provided, but need alignment in dword 
            else:
                fwug_b = fwug * 4096  # fwug 
            # check numd, xfer is in bytes
            xfer = options.xfer
            if xfer == 0:
                xfer = fwug_b
            elif xfer and (xfer % fwug_b):
                xfer = fwug_b
            # check offset
            if options.offset % fwug_b != 0:
                print ("warning: offset is not matched with FWUG in Identify, it may failed with status of Invalid Field in Command.")
                print ("")
            with open(options.fw_path, 'rb') as f:
                offset = options.offset
                # seek the offset
                f.seek(offset*4)
                while True:
                    fw_data = f.read(xfer)
                    if fw_data:
                        cmd = d.nvme_fw_download(fw_data, offset)
                        SC,SCT = cmd.check_return_status(raise_if_fail=True)
                    else:
                        print ("Firmware Download Success")
                        break # download finished
                    offset += int(xfer/4)
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
        ##
        # if os_type == 'Windows':
        #     print ("Recommand a safety methmod to active fimrware in a device, with windows Power-Shell.")
        #     print ("")
        #     print ("1. First open Power-Shell with administrators;")
        #     print ("2. Get the UniqueId of PhysicalDriveX:")
        #     print ("   > Get-Disk | Select Number, Uniqueid")
        #     print ("3. Get firmware info on a disk:")
        #     print ('   > Get-StorageFirmwareInformation -Uniqueid "<UniqueId>"')
        #     print ("4. Active the firmware to target disk:")
        #     print ('   > Update-StorageFirmware -UniqueId "<UniqueId>" -SlotNumber <Slot_Number>')
        #     print ('')
        #     return 0
        ## native methmod to update firmware
        script_check(options, admin_check=True)
        smud = False
        with NVMe(init_device(dev, open_t='nvme')) as d:
            # get nvme ver
            smud = True if (d.ctrl_identify_info[260] & 0x20) else False
            #
            cmd = d.nvme_fw_commit(options.slot, options.action)
        cmd.check_return_status(True, False, raise_if_fail=True)
        ## nvme spec 2.0 
        if smud:
            # TODO
            if (cmd.cq_cmd_spec & 0x01):
                print ("Overlapping due to processing a command from an Admin Submission Queue.")
            if (cmd.cq_cmd_spec & 0x02):
                print ("Overlapping due to processing a command from a Management Endpoint.")
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
    parser.add_option("-p", "--pil", type="int", dest="pil", action="store", default=0,
        help="[0-1]: protection info location, last/first 8 bytes of metadata")
    parser.add_option("-m", "--ms", type="int", dest="ms", action="store", default=0,
        help="[0-1]: extended format off/on")
    parser_update(parser, add_force=True)

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        if options.lbaf < 0:
            parser.error("You need give the lbaf.")
        ##
        script_check(options, danger_check=True, delay_act=True, admin_check=True)
        with NVMe(init_device(dev, open_t='nvme')) as d:
            ### Check parameters
            if (d.ctrl_identify_info[524] & 0x01) and options.namespace_id != 0xFFFFFFFF:
                print ("All namespaces in an NVM subsystem shall be configured with the same attributes and a format (excluding secure erase) of any namespace results in a format of all namespaces in an NVM subsystem.")
            if (d.ctrl_identify_info[524] & 0x02) and options.ses and options.namespace_id != 0xFFFFFFFF:
                print ("Any secure erase performed as part of a format results in a secure erase of all the namespace specified")
            cmd = d.nvme_format(options.lbaf, nsid=options.namespace_id, mset=options.ms, pi=options.pi, pil=options.pil, ses=options.ses)
        cmd.check_return_status(True, raise_if_fail=True)
    else:
        parser.print_help()

def persistent_event_log():
    usage="usage: %prog persistent-event-log <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-a", "--action", type="int", dest="action", action="store", default=0,
        help="action of get persistent event log, 0: read log data, 1: establish context and read log data, 2: release context")
    parser.add_option("-l", "--numd", type="int", dest="numd", action="store", default=-1,
        help="the number of dwords to return.")
    parser.add_option("-s", "--lpo", type="int", dest="lpo", action="store", default=0,
        help="the location(aligned in byte) within a log page to start returning data from.")
    parser.add_option("-U", "--uuid-index", type="int", dest="uuid_index", action="store", default=0,
        help="UUID index")
    parser.add_option("-f", "--filter", type="str", dest="filter", action="store", default='',
        help="Show the event of the specified event type when --action=normal, split with comma(ex. 2,3)")
    parser_update(parser, add_output=["normal", "hex", "raw", "json"])

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, admin_check=True)
        #
        if options.action > 2:
            parser.error("action should be 0|1|2")
        # check options.filter
        _filter = []
        if options.filter:
            try:
                _filter = [int(i) for i in options.filter.split(',')]
            except ValueError:
                parser.error("int type is need with -f/--filter")
        with NVMe(init_device(dev, open_t='nvme')) as d:
            ## by nvme spec 1.4a
            if not (d.ctrl_identify_info[261] & 0x10):
                raise CommandNotSupport("Device Not support Persistent Event log.")
            extend_cap = (d.ctrl_identify_info[261] & 0x04)
            event_log_size_max = scsi_ba_to_int(d.ctrl_identify_info[352:356], 'little')  # 64Kib unit
            if options.action == 0:
                ## check the parameters
                lpo = options.lpo
                # TODO: Only lpo == 0 allowed for now, when utput=normal/json.
                if lpo > 0: 
                    if lpo > event_log_size_max * 65536:
                        parser.error("ERROR: lpo should less than the total number of page size %s KiB" % event_log_size_max)
                    if options.output_format in ("normal", "json"):
                        print ("NOTE: Only lpo = 0 allowed for now when output=normal/json, fix it to 0")
                        lpo = 0
                    if lpo % 4:
                        print ("WARNING: Log Page Offset shall be Dowrd aligned")
                ## step 1. Read Log Data, first 512 Bytes(Persistent Event Log Header) to be read here, 
                ##  to determine the "Total Log Length"(TLL)
                # build command
                # If extended data is not supported, then bits 27:16 of the Number of Dwords Lower field 
                # specify the Number of Dwords to transfer.
                # 0x0FFF is enough for 512 Bytes. We Do Not Need check the Log Page Attributes field
                cmd = d.get_persistent_event_log(0, 127, 0, uuid=options.uuid_index)
                # if command abort, then Context is already established
                SC,SCT = cmd.check_return_status(False, False)
                if (SCT == 0 and SC == 0):
                    # 
                    persistent_event_log_header = persistent_event_log_header_decode(cmd.data)
                    # total_number_of_events = scsi_ba_to_int(persistent_event_log_header.get("TNEV"), 'little')
                    total_log_length = scsi_ba_to_int(persistent_event_log_header.get("TLL"), 'little')
                    ## here to 512B aligned, althrough it should be dowrd aligned
                    if total_log_length % 512:
                        total_log_length = total_log_length + 512 - (total_log_length % 512)
                    # check Log Page Attributes field page of extend capacity
                    max_numd = (int(total_log_length / 4) - 1) if extend_cap else ((int(total_log_length / 4) - 1) & 0x0FFF)
                    lpo_dw = int(lpo / 4)

                    numd = options.numd
                    if numd < 0:
                        numd = max_numd
                    elif numd > (max_numd - lpo_dw):
                        print ("NOTE: numd is too big, fix it to a proper value")
                        numd = max_numd - lpo_dw
                    # Get raw data
                    ret_data = b''
                    chun_size= 128 * 1024  # 1MB every loop
                    actual_numd = int(chun_size/4-1)
                    remainder = numd % actual_numd
                    offset = lpo
                    for loop in range(int((numd - remainder)/actual_numd)):
                        cmd = d.get_persistent_event_log(0, actual_numd, offset, uuid=options.uuid_index)
                        cmd.check_return_status(True, True)
                        ret_data += cmd.data
                        offset += chun_size
                    if remainder:
                        cmd = d.get_persistent_event_log(0, remainder, offset, uuid=options.uuid_index)
                        cmd.check_return_status(True, True)
                        ret_data += cmd.data
                    cmd = None  # release the located memory
                    nvme_format_print.format_print_event_log(ret_data, dev=d.device.device_name, print_type=options.output_format, event_filter=_filter)
                elif SCT == 0 and SC == 0x0C: # if command abort, then Context is already established
                    raise CommandSequenceError("Command Sequence Error, may need establish the context")
                else:
                    cmd.check_return_status(True, True, raise_if_fail=True)
            elif options.action == 1:
                # Establish Context and Read Log Data: The controller shall:
                #   a) determine the length of the persistent event log page data;
                #   b) determine the set of events to report in the persistent event log 
                #      page data; and 
                #   c) establish a persistent event log reporting context to store 
                #      information describing the persistent event log data to be reported 
                #      and track persistent event log page data accesses.
                #
                # Establish Context and Read Log Data, first 512 Bytes(Persistent Event Log Header) to be read here, 
                #  to determine the "Total Log Length"(TLL)
                # try to Establish Context and Read Log Data
                # If extended data is not supported, then bits 27:16 of the Number of Dwords Lower field 
                # specify the Number of Dwords to transfer.
                # 0x0FFF is enough for 512 Bytes. we Do Not Need check the Log Page Attributes field
                cmd = d.get_persistent_event_log(1, 127, 0, uuid=options.uuid_index)
                SC,SCT = cmd.check_return_status(False, False)
                if SCT == 0 and SC == 0:
                    print ("Context is established.")
                    print ("")
                    nvme_format_print.format_print_event_log(cmd.data, dev=d.device.device_name, print_type=options.output_format)
                elif SCT == 0 and SC == 0x0C: # if command abort, then Context is already established
                    print ("Context is already established by others.")
                else:
                    cmd.check_return_status(False, True, raise_if_fail=True)
            elif options.action == 2:
                cmd = d.get_persistent_event_log(2, 0, 0, uuid=options.uuid_index)
                cmd.check_return_status(True, True, raise_if_fail=True)
    else:
        parser.print_help()

def device_self_test():
    usage="usage: %prog device-self-test <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-n", "--namespace-id", type="int", dest="namespace_id", action="store", default=0xFFFFFFFF,
        help="Indicate the namespace in which the device self-test has to be carried out")
    parser.add_option("-s", "--self-test-code", type="int", dest="test_code", action="store", default=0x01,
        help="This field specifies the action taken by the device \
self-test command:                                     \
0x1 Start a short device self-test operation           \
0x2 Start a extended device self-test operation        \
0xe Start a vendor specific device self-test operation \
0xf abort the device self-test")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        # 
        if options.test_code not in (1, 2, 0xe, 0xf):
            parser.error("-s/--self-test-code not match")
        ##
        script_check(options, admin_check=True)
        with NVMe(init_device(dev, open_t='nvme')) as d:
            cmd = d.self_test(options.test_code, ns_id=options.namespace_id)
        cmd.check_return_status(raise_if_fail=True)
        if cmd.cq_status == 0x1D:
            print ("The controller or NVM subsystem already has a device self-test operation in process.")
        else:
            print ("Command Specific Status ValuesL: %#x" % cmd.cq_status)
    else:
        parser.print_help()

def self_test_log():
    usage="usage: %prog self-test-log <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-U", "--uuid-index", type="int", dest="uuid_index", action="store", default=0,
        help="UUID index")
    parser_update(parser, add_output=["normal", "hex", "raw", "json"])

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, admin_check=True)
        with NVMe(init_device(dev, open_t='nvme')) as d:
            cmd = d.self_test_log(uuid=options.uuid_index)
        cmd.check_return_status(raise_if_fail=True)
        ##
        nvme_format_print.format_print_self_test_log(cmd.data, dev=d.device.device_name, print_type=options.output_format)
    else:
        parser.print_help()

def commands_supported_and_effects():
    usage="usage: %prog commands-se-log <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser_update(parser, add_output=["normal", "hex", "raw", "json"])

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, admin_check=True)
        with NVMe(init_device(dev, open_t='nvme')) as d:
            cmd = d.commands_supported_and_effects_log()
        ##
        nvme_format_print.format_print_supported_and_effects(cmd.data, dev=d.device.device_name, print_type=options.output_format)
    else:
        parser.print_help()

def _get_feature_power_management(device_context, options):
    cmd = device_context.get_feature(2, sel=options.sel)
    return cmd

def _get_feature_lba_range_type(device_context, options):
    options.data_len = 64
    cmd = device_context.get_feature(3, sel=options.sel, data_len=options.data_len)
    return cmd

def get_feature():
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
        dev = sys.argv[2]
        #
        if options.feature_id < 1:
            parser.error("You should give a valid feature id")
        ##
        script_check(options, admin_check=True)
        result = {}
        with NVMe(init_device(dev, open_t='nvme')) as d:
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
                                    data_len=options.data_len)
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

def set_feature():
    usage="usage: %prog set-feature <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-n", "--namespace-id", type="int", dest="namespace_id", action="store", default=0,
        help="identifier of desired namespace")
    parser.add_option("-f", "--feature-id", type="int", dest="feature_id", action="store", default=0,
        help="feature identifier (required)")
    parser.add_option("-v", "--value", type="int", dest="value", action="store", default=-1,
        help="new value of feature (required)")
    parser.add_option("-d", "--data", type="string", dest="file", action="store", default='',
        help="optional feature data file path")
    parser.add_option("-c", "--cdw12", type="int", dest="cdw12", action="store", default=0,
        help="feature cdw12, if used")
    parser.add_option("-s", "--save", dest="save", action="store_false", default=False,
        help="specifies that the controller shall save the attribute")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, admin_check=True)
        #
        if options.feature_id < 1:
            parser.error("You should give a valid feature id")
        if options.value < 0:
            parser.error("You should give a valid value")
        if options.save:
            options.save = 1
        else:
            options.save = 0
        raw_data = b''
        if options.file:
            if os.path.isfile(options.file):
                with open(options.file, 'rb') as f:
                    raw_data = f.read()
            else:
                parser.error("Data file not exists")
        ##
        with NVMe(init_device(dev, open_t='nvme')) as d:
            cmd = d.set_feature(options.feature_id,
                                nsid=options.namespace_id,
                                sv=options.save,
                                cdw11=options.value,
                                cdw12=options.cdw12,
                                data_out=raw_data)
        cmd.check_return_status(success_hint=True, fail_hint=True, raise_if_fail=True)
    else:
        parser.print_help()

def nvme_create_ns():
    usage="usage: %prog create-ns(alais nvme-create-ns) <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-s", "--nsze", type="int", dest="nsze", action="store", default=0,
        help="The namespace size.")
    parser.add_option("-c", "--ncap", type="int", dest="ncap", action="store", default=0,
        help="The namespace capacity.")
    parser.add_option("-f", "--flbas", type="int", dest="flbas", action="store", default=0,
        help="The namespace formatted logical block size setting.")
    parser.add_option("-d", "--dps", type="int", dest="dps", action="store", default=0,
        help="The data protection settings.")
    parser.add_option("-m", "--nmic", type="int", dest="nmic", action="store", default=0,
        help="Namespace multipath and sharing capabilities.")
    parser.add_option("-a", "--anagrp-id", type="int", dest="anagrpid", action="store", default=0,
        help="ANA Gorup Identifier. If this value is 0h specifies that the controller determines the value to use")
    parser.add_option("-i", "--nvmset-id", type="int", dest="nvmsetid", action="store", default=0,
        help="This field specifies the identifier of the NVM Set.")
    parser.add_option("-y", "--csi", type="int", dest="csi", action="store", default=0,
        help="command set identifier (CSI)")
    parser.add_option("", "--number", type="int", dest="number", action="store", default=1,
        help="Total number of namespaces to create, default 1")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, admin_check=True)
        #
        if options.nsze < 1:
            parser.error("namespace size should > 0")
        if options.ncap < 1:
            parser.error("namespace capacity should > 0")
        ##
        with NVMe(init_device(dev, open_t='nvme')) as d:
            for i in range(options.number):
                print ("Loop %d to create" % i)
                cmd = d.ns_create(options.nsze,
                                options.ncap,
                                options.flbas,
                                options.dps,
                                options.nmic,
                                options.anagrpid,
                                options.nvmsetid,
                                csi=options.csi,
                                )
                sc,sct = cmd.check_return_status(success_hint=True, fail_hint=True, raise_if_fail=True)
                if sc == 0 and sct == 0:
                    print ("Namespace Identifier is: %s" % cmd.cq_cmd_spec)
        ##
    else:
        parser.print_help()

def nvme_delete_ns():
    usage="usage: %prog delete-ns(alais nvme-delete-ns) <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-n", "--namespace-id", type="str", dest="namespace_id", action="store", default="1",
        help="The namespace identifier to delete.                      \
1           delete namespace id 1                      \
1,3,5       delete namepace id 1,3,5                   \
2:5         delete namepace id 2,3,4                   \
0xFFFFFFFF  delete all namepaces")
    parser_update(parser, add_force=True)

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, danger_check=True, admin_check=True)
        #
        namespace_id = []
        if options.namespace_id.isdigit():
            namespace_id.append(int(options.namespace_id))
        elif options.namespace_id == "0xFFFFFFFF":
            namespace_id.append(0xFFFFFFFF)
        elif ":" in options.namespace_id:
            symbol_location = options.namespace_id.find(":")
            start,stop = options.namespace_id[0:symbol_location],options.namespace_id[symbol_location+1:]
            if start.isdigit() and stop.isdigit():
                for i in range(int(start), int(stop)):
                    namespace_id.append(i)
        elif "," in options.namespace_id:
            for i in options.namespace_id.split(","):
                if i.isdigit():
                    namespace_id.append(int(i))
                else:
                    parser.error("Invalid namespace_id format")
        if not namespace_id:
            parser.error("Invalid namespace_id format")
        ##
        with NVMe(init_device(dev, open_t='nvme')) as d:
            for ns_id in namespace_id:
                print ("Deleting namespace id %d" % ns_id)
                cmd = d.ns_delete(ns_id)
                #
                cmd.check_return_status(success_hint=True, fail_hint=True, raise_if_fail=True)
    else:
        parser.print_help()

def nvme_attach_ns():
    usage="usage: %prog attach-ns(alais nvme-attach-ns) <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-n", "--namespace-id", type="str", dest="namespace_id", action="store", default='',
        help="The namespace identifier to attach.                     \
1           delete namespace id 1                      \
1,3,5       delete namepace id 1,3,5                   \
2:5         delete namepace id 2,3,4")

    parser.add_option("-c", "--controllers", dest="ctrl_list", action="store", default='',
        help="The comma separated list of controller identifiers to attach the namesapce to.")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, admin_check=True)
        #
        if options.ctrl_list:
            ctrl_list = options.ctrl_list.split(',')
            ctrl_list = [int(i.strip()) for i in ctrl_list]
        else:
            parser.error("give a ctrl_list")
        # 
        namespace_id = []
        if options.namespace_id.isdigit():
            namespace_id.append(int(options.namespace_id))
        elif ":" in options.namespace_id:
            symbol_location = options.namespace_id.find(":")
            start,stop = options.namespace_id[0:symbol_location],options.namespace_id[symbol_location+1:]
            if start.isdigit() and stop.isdigit():
                for i in range(int(start), int(stop)):
                    namespace_id.append(i)
        elif "," in options.namespace_id:
            for i in options.namespace_id.split(","):
                if i.isdigit():
                    namespace_id.append(int(i))
                else:
                    parser.error("Invalid namespace_id format")
        if not namespace_id:
            parser.error("Invalid namespace_id format")
        ##
        with NVMe(init_device(dev, open_t='nvme')) as d:
            for ns_id in namespace_id:
                print ("attaching namespace id %d" % ns_id)
                cmd = d.ns_attachment(ns_id, 0, ctrl_list)
                ##
                cmd.check_return_status(success_hint=True, fail_hint=True, raise_if_fail=True)
    else:
        parser.print_help()

def nvme_detach_ns():
    usage="usage: %prog detach-ns(alais nvme-detach-ns) <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-n", "--namespace-id", type="str", dest="namespace_id", action="store", default='',
        help="The namespace identifier to detach.                     \
1           delete namespace id 1                      \
1,3,5       delete namepace id 1,3,5                   \
2:5         delete namepace id 2,3,4")
    parser.add_option("-c", "--controllers", dest="ctrl_list", action="store", default='',
        help="The comma separated list of controller identifiers to detach the namesapce from.")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, admin_check=True)
        #
        ctrl_list = []
        if options.ctrl_list:
            ctrl_list = options.ctrl_list.split(',')
            ctrl_list = [int(i.strip()) for i in ctrl_list]
        else:
            parser.error("give a ctrl_list")
        # 
        namespace_id = []
        if options.namespace_id.isdigit():
            namespace_id.append(int(options.namespace_id))
        elif ":" in options.namespace_id:
            symbol_location = options.namespace_id.find(":")
            start,stop = options.namespace_id[0:symbol_location],options.namespace_id[symbol_location+1:]
            if start.isdigit() and stop.isdigit():
                for i in range(int(start), int(stop)):
                    namespace_id.append(i)
        elif "," in options.namespace_id:
            for i in options.namespace_id.split(","):
                if i.isdigit():
                    namespace_id.append(int(i))
                else:
                    parser.error("Invalid namespace_id format")
        if not namespace_id:
            parser.error("Invalid namespace_id format")
        ##
        with NVMe(init_device(dev, open_t='nvme')) as d:
            for ns_id in namespace_id:
                print ("detaching namespace id %d" % ns_id)
                cmd = d.ns_attachment(ns_id, 1, ctrl_list)
                ##
                cmd.check_return_status(success_hint=True, fail_hint=True, raise_if_fail=True)
    else:
        parser.print_help()

def list_ns():
    usage="usage: %prog list-ns <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-n", "--namespace-id", type="int", dest="namespace_id", action="store", default=0,
        help="first nsid returned list should start from(0 based value)")
    parser.add_option("-a", "--all", dest="all", action="store_true", default=False,
        help="show all namespaces in the subsystem, whether attached or inactive")
    parser_update(parser, add_output=["normal", "hex", "raw", "json"])

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, admin_check=True)
        #
        if options.all:
            with NVMe(init_device(dev, open_t='nvme')) as d:
                cmd = d.allocated_ns_ids(options.namespace_id)
        ##
        else:
            with NVMe(init_device(dev, open_t='nvme')) as d:
                cmd = d.active_ns_ids(options.namespace_id)
        cmd.check_return_status(success_hint=False, fail_hint=True, raise_if_fail=True)
        ##
        nvme_format_print.format_print_list_ns(cmd.data, dev=d.device.device_name, print_type=options.output_format)
        ##
    else:
        parser.print_help()

def list_ctrl():
    usage="usage: %prog list-ctrl <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-c", "--cntid", type="int", dest="cntid", action="store", default=0,
        help="controller to display(0 means all)")
    parser.add_option("-n", "--namespace-id", type="int", dest="namespace_id", action="store", default=None,
        help="optional namespace attached to controller")
    parser_update(parser, add_output=["normal", "hex", "raw", "json"])

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, admin_check=True)
        #
        if (options.namespace_id is not None) and (options.namespace_id < 1):
            parser.error("namespace-id should > 0")
        ##
        if options.namespace_id is None:
            with NVMe(init_device(dev, open_t='nvme')) as d:
                cmd = d.cnt_ids(options.cntid)
        ##
        else:
            with NVMe(init_device(dev, open_t='nvme')) as d:
                cmd = d.ns_attached_cnt_ids(options.namespace_id, options.cntid)
        cmd.check_return_status(success_hint=False, fail_hint=True, raise_if_fail=True)
        ##
        nvme_format_print.format_print_list_ctrl(cmd.data, dev=d.device.device_name, print_type=options.output_format)
        ##
    else:
        parser.print_help()

def sanitize():
    usage="usage: %prog sanitize <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-d", "--no-dealloc", dest="no_dealloc", action="store_false", default=True,
        help="No deallocate after sanitize.")
    parser.add_option("-i", "--oipbp", type="int", dest="oipbp", action="store", default=0,
        help="Overwrite invert pattern between passes.")
    parser.add_option("-n", "--owpass", type="int", dest="owpass", action="store", default=1,
        help="Overwrite pass count.")
    parser.add_option("-u", "--ause", type="int", dest="ause", action="store", default=0,
        help="Allow unrestricted sanitize exit.")
    parser.add_option("-a", "--sanact", type="int", dest="sanact", action="store", default=0,
        help="Sanitize action.")
    parser.add_option("-p", "--ovrpat", type="int", dest="ovrpat", action="store", default=0,
        help="Overwrite pattern.")
    parser_update(parser, add_force=True)

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, danger_check=True, admin_check=True)
        #
        if options.no_dealloc:
            no_dealloc = 0
        else:
            no_dealloc = 1
        if options.oipbp:
            oipbp = 1
        else:
            oipbp = 0
        if 0 <= options.owpass <= 15:
            owpass = options.owpass
        else:
            parser.error("owpass should be 0-15")
        if options.ause:
            ause = 1
        else:
            ause = 0
        if 0 <= options.sanact <= 7:
            sanact = options.sanact
        else:
            parser.error("sanact should be 0-7")
        ##
        with NVMe(init_device(dev, open_t='nvme')) as d:
            cmd = d.sanitize(sanact, ause, owpass, oipbp, no_dealloc, ovrpat=options.ovrpat)
        cmd.check_return_status(success_hint=True, fail_hint=True, raise_if_fail=True)
    else:
        parser.print_help()

def read():
    usage="usage: %prog read <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-n", "--namespace-id", type="int", dest="namespace_id", action="store", default=1,
        help="namespace to read(default 1)")
    parser.add_option("-s", "--start-block", type="int", dest="start_block", action="store", default=0,
        help="64-bit addr of first block to access")
    parser.add_option("-c", "--block-count", type="int", dest="block_count", action="store", default=0,
        help="number of blocks (zeroes based) on device to access")
    parser_update(parser, add_output=["raw", "hex"])

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, admin_check=True)
        ##
        with NVMe(init_device(dev, open_t='nvme')) as d:
            cmd = d.read(options.namespace_id, options.start_block, options.block_count)
        cmd.check_return_status(success_hint=False, fail_hint=True, raise_if_fail=True)
        ##
        nvme_format_print.format_print_read_data(cmd.metadata, cmd.data, dev=d.device.device_name, print_type=options.output_format)
        ##
    else:
        parser.print_help()

def verify():
    usage="usage: %prog verify <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-n", "--namespace-id", type="int", dest="namespace_id", action="store", default=1,
        help="namespace to read(default 1)")
    parser.add_option("-s", "--start-block", type="int", dest="start_block", action="store", default=0,
        help="64-bit addr of first block to access")
    parser.add_option("-c", "--block-count", type="int", dest="block_count", action="store", default=0,
        help="number of blocks (zeroes based) on device to access")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, admin_check=True)
        ##
        with NVMe(init_device(dev, open_t='nvme')) as d:
            cmd = d.verify(options.namespace_id, options.start_block, options.block_count)
        cmd.check_return_status(success_hint=True, fail_hint=True, raise_if_fail=True)
    else:
        parser.print_help()

def write():
    usage="usage: %prog write <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-n", "--namespace-id", type="int", dest="namespace_id", action="store", default=1,
        help="namespace to read(default 1)")
    parser.add_option("-s", "--start-block", type="int", dest="start_block", action="store", default=0,
        help="64-bit addr of first block to access")
    parser.add_option("-c", "--block-count", type="int", dest="block_count", action="store", default=0,
        help="number of blocks (zeroes based) on device to access")
    parser.add_option("-d", "--data", type="str", dest="data", action="store", default='',
        help="String containing the data to write")
    parser.add_option("-f", "--data-file", type="str", dest="dfile", action="store", default='',
        help="File(Read first) containing the data to write")
    parser_update(parser, add_force=True)

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, danger_check=True, admin_check=True)
        ## check data
        temp_data = b''
        if options.data:
            temp_data = bytes(options.data, 'utf-8')
        elif options.dfile:
            if os.path.isfile(options.dfile):
                with open(options.dfile, 'rb') as f:
                    temp_data = f.read()
        if not temp_data:
            parser.error("Lack of input data")
        ##
        with NVMe(init_device(dev, open_t='nvme')) as d:
            cmd = d.id_ns(options.namespace_id)
            result = nvme_format_print.nvme_id_ns_decode(cmd.data)
            lbaf = result.get("LBAF").get(scsi_ba_to_int(result.get("FLBAS"), 'little') & 0x0F)
            lba_data_size = scsi_ba_to_int(lbaf.get("LBADS"), 'little')
            lba_size = 2 ** lba_data_size
            ##
            data_l = len(temp_data)
            remainder = data_l % lba_size
            if remainder:
                data_l += (lba_size-remainder) 
            temp_data.ljust(data_l, b'\x00')
            ##
            print ('issuing write command')
            print ("%s:" % d.device._file_name)
            print ('')
            cmd = d.write(options.namespace_id, options.start_block, options.block_count, temp_data, b'')
        cmd.check_return_status(True, raise_if_fail=True)
    else:
        parser.print_help()

def flush():
    usage="usage: %prog flush <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-n", "--namespace-id", type="int", dest="namespace_id", action="store", default=0xFFFFFFFF,
        help="Indicate the namespace in which the device flush has to be carried out")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, admin_check=True)
        ##
        with NVMe(init_device(dev, open_t='nvme')) as d:
            cmd = d.flush(options.namespace_id)
        cmd.check_return_status(True, raise_if_fail=True)
    else:
        parser.print_help()

def get_lba_status():
    usage="usage: %prog get-lba-status <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-n", "--namespace-id", type="int", dest="namespace_id", action="store", default=0xFFFFFFFF,
        help="Indicate the namespace in which the device flush has to be carried out")
    parser.add_option("-s", "--start-block", type="int", dest="start_block", action="store", default=0,
        help="64-bit address of the first logical block addressed by this command")
    parser.add_option("-c", "--block-count", type="int", dest="block_count", action="store", default=1,
        help="the length(zeroes based) of the range of contiguous LBAs, default 1.")
    parser.add_option("-e", "--entry-count", type="int", dest="entry_count", action="store", default=0,
        help="the maximum number of dwords to return")
    parser.add_option("-a", "--action-type", type="int", dest="action_type", action="store", default=16,
        help="the mechanism the controller uses in determining the LBA Status Descriptors to return. 0x10 Untracked LBAs, 0x11 Tracked LBAs.")
    parser.add_option("-t", "--timeout", type="int", dest="timeout", action="store", default=60000,
        help="timeout value, in milliseconds")
    parser_update(parser, add_output=["normal", "hex", "raw", "json"])

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        mndw = 2 + 4*options.entry_count - 1 # zero based
        ##
        script_check(options, admin_check=True)
        ##
        with NVMe(init_device(dev, open_t='nvme')) as d:
            cmd = d.get_lba_status(options.namespace_id, # ns_id
                                   options.start_block,  # slba
                                   mndw,                 # mndw
                                   options.action_type,  # atype
                                   options.block_count,  # Range Length
                                   timeout=options.timeout, # timeout
                                   )
        SC,SCT = cmd.check_return_status(False, raise_if_fail=True)
        ##
        if SC == 0 and SCT == 0:
            nvme_format_print.format_print_LBA_Status_Descriptor(cmd.data, print_type=options.output_format)
    else:
        parser.print_help()

def get_log():
    usage="usage: %prog get-lba-status <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-n", "--namespace-id", type="int", dest="namespace_id", action="store", default=0,
        help="desired namespace")
    parser.add_option("-i", "--log-id", type="int", dest="log_id", action="store", default=-1,
        help="identifier of log to retrieve")
    parser.add_option("-l", "--log-len", type="int", dest="log_len", action="store", default=4096,
        help="how many bytes to retrieve,default 4096")
    parser.add_option("-o", "--lpo", type="int", dest="lpo", action="store", default=0,
        help="log page offset specifies the location within a log page from where to start returning data")
    parser.add_option("-s", "--lsp", type="int", dest="lsp", action="store", default=0,
        help="log specific field")
    parser.add_option("-S", "--lsi", type="int", dest="lsi", action="store", default=0,
        help="log specific identifier specifies an identifier that is required for a particular log page")
    parser.add_option("-r", "--rae", type="int", dest="rae", action="store", default=0,
        help="retain an asynchronous event")
    parser.add_option("-U", "--uuid-index", type="int", dest="uuid_index", action="store", default=0,
        help="UUID index")
    parser.add_option("-y", "--csi", type="int", dest="csi", action="store", default=0,
        help="command set identifier")
    parser.add_option("-O", "--ot", type="int", dest="ot", action="store", default=0,
        help="command set identifier")
    parser.add_option("", "--output-format", type="choice", dest="output_format", action="store", choices=["hex", "raw"],default="hex",
        help="Output format: hex|raw, default normal")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, admin_check=True)
        #
        if options.log_id < 0:
            parser.error("You need a log id")
        log_dw = int(options.log_len / 4) - 1
        numdl = log_dw & 0xFFFF
        numdu = (log_dw >> 16) & 0xFFFF
        log_dw = int(options.lpo)
        lpol = log_dw & 0xFFFFFFFF
        lpou = (log_dw >> 32) & 0xFFFFFFFF
        ##
        with NVMe(init_device(dev, open_t='nvme')) as d:
            cmd = d.get_log_page(options.namespace_id, # ns_id
                                 options.log_id,       # log id
                                 options.lsp,          # lsp
                                 options.rae,
                                 numdl,
                                 numdu,
                                 options.lsi,
                                 lpol,
                                 lpou,
                                 options.uuid_index,
                                 options.ot,
                                 options.csi,
                                 )
            
        if options.output_format == "hex":
            format_dump_bytes(cmd.data)
        else:
            print(bytes(cmd.data))
    else:
        parser.print_help()


def pcie():
    usage="usage: %prog pcie <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-p", "--power", type="str", dest="power", action="store",default="",
        help="Check or set Pcie power(status|on|off), combine with --slot_num if set power on.")
    parser.add_option("", "--slot_num", type="int", dest="slot_num", action="store", default=-1,
        help="combine with -p on|status")
    parser.add_option("-d", "--detail", dest="detail_info", action="store_true", default=False,
        help="Get the detail information.")
    parser.add_option("", "--update_pci_ids", dest="update_pci_ids", action="store_true", default=False,
        help="Update the pci.ids online")
    parser_update(parser, add_output=["normal", "hex", "raw"])

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        if options.update_pci_ids:
            from pydiskcmdcli.utils.update_pci_ids import update_pci_ids_online
            return update_pci_ids_online(print_detail=True)
        ##
        PCIePowerPath = "/sys/bus/pci/slots/%s/power"
        ##
        if options.power and options.power not in ("status", "on", "off"):
            parser.error("Check or set Pcie power should be in (status|on|off)")
        ##
        script_check(options)
        ## check device
        from pydiskcmdcli.system.os_tool import check_device_exist
        dev = sys.argv[2] 
        if not check_device_exist(dev):
            if options.power == "on":
                if options.slot_num >= 0:
                    print ("Device is offline, and you set the device slot number is %s." % options.slot_num)
                    print ("")
                    power_file = PCIePowerPath % options.slot_num
                    if os.path.isfile(power_file):
                        print ("Powering on device")
                        with open(power_file, 'w') as f:
                            f.write("1")
                    else:
                        parser.error("Cannot find power file in %s" % power_file)
                else:
                    parser.error("You may need combine with --slot_num")
            elif options.power == "status":
                print ("Device is offline")
                print ("")
            else:
                print ("Device is offline")
                print ("")
            return
        ##
        from pydiskcmdlib.pynvme.nvme_pcie_lib import NVMePCIe
        ##
        try:
            pcie_dev = NVMePCIe(dev)
        except FileNotFoundError as e:
            parser.error("Cannot init pcie context, device %s, %s \nYou may need a device controller path, like /dev/nvme1, but not /dev/nvme1n1" % (dev, str(e)))
        except Exception as e:
            print (str(e))
        else:
            bus_address = pcie_dev.address
            print ("Device %s mapped to pcie address %s" % (dev, bus_address))
            print ('')
            ##
            if options.power:
                pcie_parent = pcie_dev.get_parent()
                if pcie_parent and pcie_parent.pcie_cap:
                    slot = pcie_parent.pcie_cap.slot_cap.decode_data["PhysicalSlotNumber"]
                    print ("Device Slot number is %d" % slot)
                    power_file = PCIePowerPath % slot
                    if os.path.isfile(power_file):
                        if options.power == "status":
                            with open(power_file, 'r') as f:
                                status = f.read().strip()
                            print ("Current PCIe power status: %s" % ("on" if status == '1' else "off"))
                        elif options.power == "off":
                            print ("Powering off device")
                            with open(power_file, 'w') as f:
                                f.write("0")
                        else:
                            print ("No need power on, device is online")
                    else:
                        parser.error("Cannot find power file, device %s: %s" % (dev, bus_address))
                else:
                    print ("Cannot find upstream device slot information.")
            elif options.detail_info:
                if options.output_format == 'normal':
                    pcie_dev.simple_info_print()
                elif options.output_format == 'hex':
                    nvme_format_print.format_dump_bytes(pcie_dev.raw_data, byteorder='obverse')
                else:
                    print (bytes(pcie_dev.raw_data))
            else:
                pass
    else:
        parser.print_help()

def reset():
    usage="usage: %prog reset <device>"
    parser = optparse.OptionParser(usage)

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, admin_check=True)
        ##
        with NVMe(init_device(dev, open_t='nvme')) as d:
            cmd = d.reset_ctrl()
    else:
        parser.print_help()

def subsystem_reset():
    usage="usage: %prog subsystem-reset <device>"
    parser = optparse.OptionParser(usage)

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, admin_check=True)
        ##
        with NVMe(init_device(dev, open_t='nvme')) as d:
            cmd = d.subsystem_reset()
    else:
        parser.print_help()

def show_regs():
    usage="usage: %prog show-regs <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser_update(parser, add_output=["normal", "hex", "raw", "json"])

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, admin_check=True)
        ##
        from pydiskcmdlib.pynvme.nvme_ctrl_register import PCIeNVMeBar
        bar = PCIeNVMeBar(dev)
        raw = bar.read(0, 3612)
        nvme_format_print.format_print_ctrl_register(raw, print_type=options.output_format)
    else:
        parser.print_help()

#################################################
# Bellow is plugin extensions
#   - OCP NVMe SSD SPEC Command, Spec can be download in https://www.opencompute.org/
#################################################
def _ocp_print_help():
    if len(sys.argv) > 3 and sys.argv[3] in plugin_ocp_commands_dict:
        func_name,sys.argv[3] = sys.argv[3],"--help"
        plugin_ocp_commands_dict[func_name]()
    else:
        print ("pynvme-%s" % Version)
        print ("usage: pynvme ocp <command> [<device>] [<args>]")
        print ("")
        print ("The '<device>' may be either an NVMe character device (ex: /dev/nvme0) or an")
        print ("nvme block device (ex: /dev/nvme0n1) in Linux, while PhysicalDrive<X> in Windows.")
        print ("")
        print ("OCP cloud SSD extensions")
        print ("")
        print ("The following are all implemented sub-commands:")
        print ("")
        print ("  ocp-check                     OCP support and version check")
        print ("  smart-add-log                 Retrieve extended SMART Information")
        print ("  error-recovery-log            Retrieve error recovery Information")
        print ("  cloud-SSD-plugin-version      Shows cloud SSD plugin version")
        print ("  Help                          Display this help")
        print ("")
        print ("See 'pynvme ocp help <command>' for more information on a specific command")

def _ocp_print_ver():
    print ("Cloud SSD Plugin Version: %s" % "1.0")
    print ("")

def _ocp_info_check():
    usage="usage: %prog ocp ocp-check <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser_update(parser, add_output=["normal", "json"])

    if len(sys.argv) > 3:
        (options, args) = parser.parse_args(sys.argv[3:])
        ## check device
        dev = sys.argv[3]
        ##
        ##
        script_check(options, admin_check=True)
        ##
        with NVMe(init_device(dev, open_t='nvme')) as d:
            decode_data = {"device": {"dev_path": d.device._file_name},
                           "ocp_info": {"support": d.ocp_support, "version": d.ocp_ver}
                           }
        ##
        nvme_format_print.format_print_ocp_info_check(decode_data, options.output_format)
    else:
        parser.print_help()

def _ocp_smart_extended_log():
    usage="usage: %prog ocp smart-extended-log <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser_update(parser, add_output=["normal", "hex", "raw", "json"])

    if len(sys.argv) > 3:
        (options, args) = parser.parse_args(sys.argv[3:])
        ## check device
        dev = sys.argv[3]
        ##
        script_check(options, admin_check=True)
        ##
        with NVMe(init_device(dev, open_t='nvme')) as d:
            cmd = ocp_plugin["SmartExtendedLog"]()
            d.execute(cmd)
        ##
        nvme_format_print.format_print_ocp_smart_extended_log(cmd, options.output_format)
    else:
        parser.print_help()

def _ocp_error_recovery_log():
    usage="usage: %prog ocp error-recovery-log <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser_update(parser, add_output=["normal", "hex", "raw", "json"])

    if len(sys.argv) > 3:
        (options, args) = parser.parse_args(sys.argv[3:])
        ## check device
        dev = sys.argv[3]
        ##
        script_check(options, admin_check=True)
        ##
        with NVMe(init_device(dev, open_t='nvme')) as d:
            cmd = ocp_plugin["ErrorRecoveryLog"]()
            d.execute(cmd)
        ##
        nvme_format_print.format_print_ocp_error_recovery_log(cmd, options.output_format)
    else:
        parser.print_help()

plugin_ocp_commands_dict = {"ocp-check": _ocp_info_check,
                            "smart-add-log": _ocp_smart_extended_log,
                            "error-recovery-log": _ocp_error_recovery_log,
                            "cloud-SSD-plugin-version": _ocp_print_ver,
                            "Help": _ocp_print_help,}

def ocp():
    if len(sys.argv) > 2:
        plugin_command = sys.argv[2]
        if plugin_command in plugin_ocp_commands_dict:
            plugin_ocp_commands_dict[plugin_command]()
            return
    _ocp_print_help()

#################################################
# Bellow is plugin extensions
#   - Windows NVMe VROC Support
#################################################
from pydiskcmdcli.plugins import vroc_plugin,VROC_ENABLE
from pydiskcmdcli.utils.string_utils import decode_bytes,string_strip
if VROC_ENABLE:
    from pydiskcmdlib.vroc.nvme_raid import NVMeDisk  # noqa

def _win_nvme_vroc_print_help():
    if len(sys.argv) > 3 and sys.argv[3] in plugin_ocp_commands_dict:
        func_name,sys.argv[3] = sys.argv[3],"--help"
        plugin_win_nvme_vroc_commands_dict[func_name]()
    else:
        print ("pynvme-%s" % Version)
        print ("usage: pynvme vroc <command> [<device>] [<args>]")
        print ("")
        print ("The '<device>' is a string(ex: \\.\Scsi0:/390) split by '/' that include")
        print ("VROC Controller(ex: \\.\Scsi0:) and VROC Disk ID.")
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

#################################################
# Bellow is cli management interface 
#################################################
def cli_info():
    from pydiskcmdlib import version as lib_version
    from pydiskcmdlib.pynvme import version as nvme_version
    version()
    print ('')
    print ('pydiskcmdlib version : %s' % lib_version)
    print ('  - nvme code version: %s' % nvme_version)

def cli_autocmd():
    from pydiskcmdcli.system.bash_completion import enable_cmd_completion
    enable_cmd_completion()

###########################
###########################
commands_dict = {"list": _list,
                 "list-subsys": _list_subsys,
                 "list-ctrl": list_ctrl,
                 "list-ns": list_ns,
                 "smart-log": smart_log,
                 "id-ctrl": id_ctrl,
                 "id-ns": id_ns,
                 "id-uuid": id_uuid,
                 "get-log": get_log,
                 "error-log": error_log,
                 "fw-log": fw_log,
                 "telemetry-log": telemetry_log,
                 "sanitize-log": sanitize_log,
                 "reset": reset,
                 "subsystem-reset": subsystem_reset,
                 "fw-download": fw_download, 
                 "fw-commit": fw_commit, 
                 "nvme-create-ns": nvme_create_ns,
                 "create-ns": nvme_create_ns,
                 "nvme-delete-ns": nvme_delete_ns,
                 "delete-ns": nvme_delete_ns,
                 "nvme-attach-ns": nvme_attach_ns,
                 "attach-ns": nvme_attach_ns,
                 "nvme-detach-ns": nvme_detach_ns,
                 "detach-ns": nvme_detach_ns,
                 "get-feature": get_feature,
                 "set-feature": set_feature,
                 "format": nvme_format,
                 "sanitize": sanitize,
                 "persistent-event-log": persistent_event_log,
                 "device-self-test": device_self_test,
                 "self-test-log": self_test_log,
                 "commands-se-log": commands_supported_and_effects,
                 "pcie": pcie,
                 "show-regs": show_regs,
                 "flush": flush,
                 "read": read,
                 "verify": verify,
                 "write": write,
                 "get-lba-status":get_lba_status,
                 "version": version,
                 "help": print_help,
                 "ocp": ocp,
                 "vroc": win_nvme_vroc,
                 "cli-info": cli_info,
                 "cli-autocmd": cli_autocmd,
                 }

def pynvme():
    '''
    Execute command cli inetrface.

    :return: None
    :exit: exit code of command
      code: bit 0-3
        0: command success
        1: non pydiskcmd error
        2: command parameters error
        3: device operation error
          subcode: bit 4-7
            0: ...  # TODO
        4: command build error
          subcode: bit 4-7
            0: ...  # TODO
        5: command execute error
          subcode: bit 4-7
            0: ...  # TODO
        6: check command return status error
          subcode: bit 4-7
            0: ...  # TODO
        7: check command return data error
          subcode: bit 4-7
            0: ...  # TODO
        ...
        13: function error
          subcode: bit 4-7
            0: ...  # TODO
        14: user defined error
          subcode: bit 4-7
            0: ...  # TODO
        15: reservd
    '''
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command in commands_dict:
            try:
                ret = commands_dict[command]()
            except Exception as e:
                e = NonpydiskcmdError(str(e))
                print (str(e))
                # import traceback
                # traceback.print_exc()
                sys.exit(e.exit_code)
            else:
                if (ret is not None) and ret > 0:
                    # function return a number, and is not None and > 0
                    e = UserDefinedError("pynvme command of <%s> error" % command, ret)
                    print (str(e))
                    sys.exit(e.exit_code)
        else:
            print_help()
            e = FunctionNotImplementError("pynvme command of <%s> Not Implement error" % command)
            print ('')
            print (str(e))
            sys.exit(e.exit_code)
    else:
        print_help()
    sys.exit(0)
