# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import sys,os
import optparse
from pydiskcmd.utils import init_device
from pydiskcmd.pynvme.nvme import NVMe
from pydiskcmd.utils.format_print import format_dump_bytes,human_read_capacity
from pydiskcmd.pynvme.nvme_command import DataBuffer
##
from pydiskcmd.utils import nvme_format_print
from pydiskcmd.system.env_var import os_type
from pydiskcmd.system.os_tool import check_device_exist

Version = '0.1.0'

def version():
    print ("pynvme version %s" % Version)
    return 0

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
        print ("  list-ns               Send NVMe Identify List, display structure")
        print ("  list-ctrl             Send NVMe Identify Controller List, display structure")
        print ("  id-ctrl               Send NVMe Identify Controller")
        print ("  id-ns                 Send NVMe Identify Namespace, display structure")
        print ("  nvme-create-ns        Creates a namespace with the provided parameters")
        print ("  nvme-delete-ns        Deletes a namespace from the controller")
        print ("  nvme-attach-ns        Attaches a namespace to requested controller(s)")
        print ("  nvme-detach-ns        Detaches a namespace from requested controller(s)")
        print ("  get-log               Generic NVMe get log, returns log in raw format")
        print ("  smart-log             Retrieve SMART Log, show it")
        print ("  error-log             Retrieve Error Log, show it")
        print ("  commands-se-log       Retrieve Commands Supported and Effects Log, and show it")
        print ("  fw-log                Retrieve FW Log, show it")
        print ("  sanitize-log          Retrieve Sanitize Log, show it")
        print ("  self-test-log         Retrieve the SELF-TEST Log, show it")
        print ("  telemetry-log         Retrieve the Telemetry Log, show it")
        print ("  persistent_event_log  Get persistent event log from device")
        print ("  fw-download           Download new firmware")
        print ("  fw-commit             Verify and commit firmware to a specific slot")
        print ("  get-feature           Get feature and show the resulting value")
        print ("  set-feature           Set a feature and show the resulting value")
        print ("  format                Format namespace with new block format")
        print ("  sanitize              Submit a sanitize command")
        print ("  device-self-test      Perform the necessary tests to observe the performance")
        print ("  pcie                  Get device PCIe status, show it")
        print ("  flush                 Submit a flush command, return results")
        print ("  read                  Submit a read command, return results")
        print ("  verify                Submit a verify command, return results")
        print ("  write                 Submit a write command, return results")
        print ("  get-lba-status        Submit a Get LBA Status command, return results")
        print ("  version               Shows the program version")
        print ("  help                  Display this help")
        print ("")
        print ("See 'pynvme help <command>' or 'pynvme <command> --help' for more information on a sub-command")
    return 0

def _list():
    usage="usage: %prog list <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-o", "--output-format", type="choice", dest="output_format", action="store", choices=["normal",],default="normal",
        help="Output format: normal, default normal")

    (options, args) = parser.parse_args()
    ##
    print_format = "%-20s %-20s %-40s %-9s %-26s %-16s %-8s"
    print (print_format % ("Node", "SN", "Model", "Namespace", "Usage", "Format", "FW Rev"))
    print (print_format % ("-"*20, "-"*20, "-"*40, "-"*9, "-"*26, "-"*16, "-"*8))
    from pydiskcmd.pydiskhealthd.all_device import scan_device,os_type
    scsi_ba_to_int = nvme_format_print.scsi_ba_to_int
    ##
    for dev_context in scan_device(debug=False):
        if dev_context.device_type == "nvme":
            sn = dev_context.Serial
            mn = dev_context.Model
            fw = dev_context.fw
            #
            if os_type == 'Linux':
                from pydiskcmd.system.lin_os_tool import NVMeController
                dev_name = dev_context.dev_path.strip("/dev/")
                ctrl_info = NVMeController(dev_name)
                for ns_info in ctrl_info.retrieve_ns():
                    node = ns_info.dev_path
                    ns_id = ns_info.ns_id
                    ## Get information now!
                    ## send identify controller and identify namespace
                    with NVMe(init_device(ctrl_info.dev_path, open_t='nvme')) as d:
                        cmd_id_ns = d.id_ns(ns_info.ns_id)
                    ## para data
                    result = nvme_format_print.nvme_id_ns_decode(cmd_id_ns.data)
                    #
                    lbaf = result.get("LBAF").get(scsi_ba_to_int(result.get("FLBAS"), 'little'))
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
                node= dev_context.dev_path
                ns_id = 1  # always 1 in windows now!
                ## Get information now!
                ## send identify controller and identify namespace
                with NVMe(init_device(node, open_t='nvme')) as d:
                    cmd_id_ns = d.id_ns(ns_id)
                ## para data
                result = nvme_format_print.nvme_id_ns_decode(cmd_id_ns.data)
                #
                lbaf = result.get("LBAF").get(scsi_ba_to_int(result.get("FLBAS"), 'little'))
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
                raise RuntimeError("OS %s Not support" % os_type)

def smart_log():
    usage="usage: %prog smart-log <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-o", "--output-format", type="choice", dest="output_format", action="store", choices=["normal", "hex", "raw", "json"],default="normal",
        help="Output format: normal|hex|raw|json, default normal")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        if not check_device_exist(dev):
            raise RuntimeError("Device not support!")
        ##
        with NVMe(init_device(dev, open_t='nvme')) as d:
            cmd = d.smart_log()
        cmd.check_return_status()
        ##
        nvme_format_print.format_print_smart_log(cmd.data, print_type=options.output_format)
    else:
        parser.print_help()

def id_ctrl():
    usage="usage: %prog id-ctrl <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-o", "--output-format", type="choice", dest="output_format", action="store", choices=["normal", "hex", "raw", "json"],default="normal",
        help="Output format: normal|hex|raw|json, default normal")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        if not check_device_exist(dev):
            raise RuntimeError("Device not support!")
        ##
        with NVMe(init_device(dev, open_t='nvme')) as d:
            cmd = d.id_ctrl()
        cmd.check_return_status()
        nvme_format_print.format_print_id_ctrl(cmd.data, print_type=options.output_format)
    else:
        parser.print_help()

def id_ns():
    usage="usage: %prog id-ns <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-n", "--namespace-id", type="int", dest="namespace_id", action="store",default=1,
        help="identifier of desired namespace. Default 1")
    parser.add_option("-o", "--output-format", type="choice", dest="output_format", action="store", choices=["normal", "hex", "raw", "json"],default="normal",
        help="Output format: normal|hex|raw|json, default normal")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        if not check_device_exist(dev):
            raise RuntimeError("Device not support!")
        ## check namespace
        if not isinstance(options.namespace_id, int) or options.namespace_id < 1:
            parser.error("namespace id input error.")
            return
        ##
        with NVMe(init_device(dev, open_t='nvme')) as d:
            cmd = d.id_ns(options.namespace_id)
        cmd.check_return_status()
        ##
        nvme_format_print.format_print_id_ns(cmd.data, print_type=options.output_format)
    else:
        parser.print_help()

def error_log():
    usage="usage: %prog error-log <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-o", "--output-format", type="choice", dest="output_format", action="store", choices=["normal", "hex", "raw", "json"],default="normal",
        help="Output format: normal|hex|raw|json, default normal")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        if not check_device_exist(dev):
            raise RuntimeError("Device not support!")
        ##
        with NVMe(init_device(dev, open_t='nvme')) as d:
            cmd = d.error_log_entry()
        cmd.check_return_status()
        ##
        nvme_format_print.format_print_error_log(cmd.data, dev=dev, print_type=options.output_format)
    else:
        parser.print_help()

def fw_log():
    usage="usage: %prog fw-log <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-o", "--output-format", type="choice", dest="output_format", action="store", choices=["normal", "hex", "raw", "json"],default="normal",
        help="Output format: normal|hex|raw|json, default normal")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        if not check_device_exist(dev):
            raise RuntimeError("Device not support!")
        ##
        with NVMe(init_device(dev, open_t='nvme')) as d:
            cmd = d.fw_slot_info()
        cmd.check_return_status()
        ##
        nvme_format_print.format_print_fw_log(cmd.data, dev=d.device.device_name, print_type=options.output_format)
    else:
        parser.print_help()

def sanitize_log():
    usage="usage: %prog sanitize-log <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-o", "--output-format", type="choice", dest="output_format", action="store", choices=["normal", "hex", "raw", "json"],default="normal",
        help="Output format: normal|hex|raw|json, default normal")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        if not check_device_exist(dev):
            raise RuntimeError("Device not support!")
        ##
        with NVMe(init_device(dev, open_t='nvme')) as d:
            cmd = d.sanitize_log(127, lpol=0, lpou=0)
        cmd.check_return_status()
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

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        if not check_device_exist(dev):
            raise RuntimeError("Device not support!")
        if not options.output_file:
            raise RuntimeError("Need an input file by -o/--output-file")
        ##
        if options.controller_init: # Gather report generated by the controller
            with NVMe(init_device(dev, open_t='nvme')) as d:
                ## Get first 512 bytes log
                cmd = d.telemetry_ctrl_log(127)
                cmd.check_return_status()
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
                        cmd = d.telemetry_ctrl_log(127, lpol=lpol, lpou=lpou)
                        f.write(cmd.data)
        else: # Gather report generated by the host
            with NVMe(init_device(dev, open_t='nvme')) as d:
                ## Get first 512 bytes log
                cmd = d.telemetry_host_log(127)
                cmd.check_return_status()
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
                        cmd = d.telemetry_host_log(127, lpol=lpol, lpou=lpou)
                        f.write(cmd.data)
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
        if not check_device_exist(dev):
            raise RuntimeError("Device not support!")
        ## check namespace
        if not os.path.exists(options.fw_path):
            parser.error("No Firmware File provided")
            return
        ##
        with NVMe(init_device(dev, open_t='nvme')) as d:
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
        if not check_device_exist(dev):
            raise RuntimeError("Device not support!")
        ##
        smud = False
        with NVMe(init_device(dev, open_t='nvme')) as d:
            # get nvme ver
            smud = True if (d.ctrl_identify_info[260] & 0x20) else False
            #
            cmd = d.nvme_fw_commit(options.slot, options.action)
        cmd.check_return_status(True, False)
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
    parser.add_option("-p", "--pil", type="int", dest="pil", action="store", default=1,
        help="[0-1]: protection info location, last/first 8 bytes of metadata")
    parser.add_option("-m", "--ms", type="int", dest="ms", action="store", default=0,
        help="[0-1]: extended format off/on")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        if not check_device_exist(dev):
            raise RuntimeError("Device not support!")
        if options.lbaf < 0:
            parser.error("You need give the lbaf.")
        ##
        with NVMe(init_device(dev, open_t='nvme')) as d:
            cmd = d.nvme_format(options.lbaf, nsid=options.namespace_id, mset=options.ms, pi=options.pi, pil=options.pil, ses=options.ses)
        cmd.check_return_status()
    else:
        parser.print_help()

def persistent_event_log():
    usage="usage: %prog persistent_event_log <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-a", "--action", type="int", dest="action", action="store", default=3,
        help="action of get persistent event log, 0: open, 1: read, 2: close, 3: check status")
    parser.add_option("-o", "--output-format", type="choice", dest="output_format", action="store", choices=["normal", "hex", "raw", "json"],default="normal",
        help="Output format: normal|hex|raw|json, default normal")
    parser.add_option("-f", "--filter", type="str", dest="filter", action="store", default='',
        help="Show the event of the specified event type when --action=normal, split with comma(ex. 2,3)")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        if not check_device_exist(dev):
            raise RuntimeError("Device not support!")
        # check options.filter
        _filter = []
        if options.filter:
            try:
                _filter = [int(i) for i in options.filter.split(',')]
            except ValueError:
                parser.error("int type is need with -f/--filter")
        ##
        with NVMe(init_device(dev, open_t='nvme')) as d:
            ret = d.get_persistent_event_log(options.action)
        if ret == 6:
            print ("Device Not support Persistent Event log.")
        elif ret == 7:
            print ("data buffer for persistent event log need >= 16KiB")
        elif ret == 8:
            print ("Action should be 0|1|2|3.")
        else:
            if options.action == 3:
                if ret == 0:
                    print ("Context Not Established!")
                elif ret == 1:
                    print ("Context Established!")
                else:
                    print ("Command failed.")
            elif options.action == 0:
                if ret == 0:
                    print ("Context is established.")
                else:
                    print ("Other errors, error code: %s." % ret)
            elif options.action == 1:
                if ret == 3:
                    print ("Command failed in get persistent event log")
                    return
                if not ret:
                    print ("No avaliable data, please check if support persistent event log Or if open the context")
                    return
                nvme_format_print.format_print_event_log(ret, dev=d.device.device_name, print_type=options.output_format, event_filter=_filter)
            elif isinstance(ret, int):
                if ret == 0:
                    print ("Command success.")
                else:
                    print ("Command failed.")
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
        if not check_device_exist(dev):
            raise RuntimeError("Device not support!")
        # 
        if options.test_code not in (1, 2, 0xe, 0xf):
            parser.error("-s/--self-test-code not match")
        ##
        with NVMe(init_device(dev, open_t='nvme')) as d:
            cmd = d.self_test(options.test_code, ns_id=options.namespace_id)
        if cmd.cq_status == 0x1D:
            print ("The controller or NVM subsystem already has a device self-test operation in process.")
        else:
            print ("Command Specific Status ValuesL: %#x" % cmd.cq_status)
    else:
        parser.print_help()

def self_test_log():
    usage="usage: %prog self-test-log <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-o", "--output-format", type="choice", dest="output_format", action="store", choices=["normal", "hex", "raw", "json"],default="normal",
        help="Output format: normal|hex|raw|json, default normal")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        if not check_device_exist(dev):
            raise RuntimeError("Device not support!")
        ##
        with NVMe(init_device(dev, open_t='nvme')) as d:
            cmd = d.self_test_log()
        cmd.check_return_status()
        ##
        nvme_format_print.format_print_self_test_log(cmd.data, dev=d.device.device_name, print_type=options.output_format)
    else:
        parser.print_help()

def commands_supported_and_effects():
    usage="usage: %prog commands-se-log <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-o", "--output-format", type="choice", dest="output_format", action="store", choices=["normal", "hex", "raw", "json"],default="normal",
        help="Output format: normal|hex|raw|json, default normal")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        if not check_device_exist(dev):
            raise RuntimeError("Device not support!")
        ##
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
    parser.add_option("-o", "--output-format", type="choice", dest="output_format", action="store", choices=["normal", "binary", "raw"],default="normal",
        help="Output format: normal|binary|raw, default normal")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        if not check_device_exist(dev):
            raise RuntimeError("Device not support!")
        #
        if options.feature_id < 1:
            parser.error("You should give a valid feature id")
        ##
        result = {}
        with NVMe(init_device(dev, open_t='nvme')) as d:
            if options.feature_id == 2:
                cmd = _get_feature_power_management(d, options)
                result = nvme_format_print.nvme_power_management_cq_decode(cmd.cq_cmd_spec)
            elif options.feature_id == 3:
                cmd = _get_feature_lba_range_type(d, options)
            else:
                cmd = d.get_feature(options.feature_id,
                                    ns_id=options.namespace_id,
                                    sel=options.sel,
                                    cdw11=options.cdw11,
                                    data_len=options.data_len)
        cmd.check_return_status()
        ##
        if options.output_format == "binary":
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
        if not check_device_exist(dev):
            raise RuntimeError("Device not support!")
        #
        if options.feature_id < 1:
            parser.error("You should give a valid feature id")
        if options.value < 0:
            parser.error("You should give a valid value")
        if options.save:
            options.save = 1
        else:
            options.save = 0
        raw_data = None
        if options.file:
            if os.path.isfile(options.file):
                with open(options.file, 'rb') as f:
                    raw_data = f.read()
            else:
                parser.error("Data file not exists")
        ##
        with NVMe(init_device(dev, open_t='nvme')) as d:
            cmd = d.set_feature(options.feature_id,
                                ns_id=options.namespace_id,
                                sv=options.save,
                                cdw11=options.value,
                                cdw12=options.cdw12,
                                data_in=raw_data)
        cmd.check_return_status(success_hint=True, fail_hint=True)
    else:
        parser.print_help()

def nvme_create_ns():
    usage="usage: %prog nvme-create-ns <device> [OPTIONS]"
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

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        if not check_device_exist(dev):
            raise RuntimeError("Device not support!")
        #
        if options.nsze < 1:
            parser.error("namespace size should > 0")
        if options.ncap < 1:
            parser.error("namespace capacity should > 0")
        ##
        with NVMe(init_device(dev, open_t='nvme')) as d:
            cmd = d.ns_create(options.nsze,
                              options.ncap,
                              options.flbas,
                              options.dps,
                              options.nmic,
                              options.anagrpid,
                              options.nvmsetid,
                              csi=options.csi,
                              )
        sc,sct = cmd.check_return_status(success_hint=True, fail_hint=False)
        if sc == 0 and sct == 0:
            print ("Namespace Identifier is: %s" % cmd.cq_cmd_spec)
        ##
    else:
        parser.print_help()

def nvme_delete_ns():
    usage="usage: %prog nvme-delete-ns <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-n", "--namespace-id", type="int", dest="namespace_id", action="store", default=0,
        help="The namespace identifier to delete.")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        if not check_device_exist(dev):
            raise RuntimeError("Device not support!")
        #
        ##
        with NVMe(init_device(dev, open_t='nvme')) as d:
            cmd = d.ns_delete(options.namespace_id)
        ##
        cmd.check_return_status(success_hint=True, fail_hint=True)
    else:
        parser.print_help()

def nvme_attach_ns():
    usage="usage: %prog nvme-attach-ns <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-n", "--namespace-id", type="int", dest="namespace_id", action="store", default=0,
        help="The namespace identifier to attach.")
    parser.add_option("-c", "--controllers", dest="ctrl_list", action="store", default='',
        help="The comma separated list of controller identifiers to attach the namesapce too.")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        if not check_device_exist(dev):
            raise RuntimeError("Device not support!")
        #
        ctrl_list = []
        if options.ctrl_list:
            ctrl_list = options.ctrl_list.split(',')
            ctrl_list = [int(i.strip()) for i in ctrl_list]
        else:
            parser.error("give a ctrl_list")
        ##
        with NVMe(init_device(dev, open_t='nvme')) as d:
            cmd = d.ns_attachment(options.namespace_id, 0, ctrl_list)
        ##
        cmd.check_return_status(success_hint=True, fail_hint=True)
    else:
        parser.print_help()

def nvme_detach_ns():
    usage="usage: %prog nvme-detach-ns <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-n", "--namespace-id", type="int", dest="namespace_id", action="store", default=0,
        help="The namespace identifier to detach.")
    parser.add_option("-c", "--controllers", dest="ctrl_list", action="store", default='',
        help="The comma separated list of controller identifiers to detach the namesapce from.")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        if not check_device_exist(dev):
            raise RuntimeError("Device not support!")
        #
        ctrl_list = []
        if options.ctrl_list:
            ctrl_list = options.ctrl_list.split(',')
            ctrl_list = [int(i.strip()) for i in ctrl_list]
        else:
            parser.error("give a ctrl_list")
        ##
        with NVMe(init_device(dev, open_t='nvme')) as d:
            cmd = d.ns_attachment(options.namespace_id, 1, ctrl_list)
        ##
        cmd.check_return_status(success_hint=True, fail_hint=True)
    else:
        parser.print_help()

def list_ns():
    usage="usage: %prog list-ns <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-n", "--namespace-id", type="int", dest="namespace_id", action="store", default=0,
        help="first nsid returned list should start from(0 based value)")
    parser.add_option("-a", "--all", dest="all", action="store_true", default=False,
        help="show all namespaces in the subsystem, whether attached or inactive")
    parser.add_option("-o", "--output-format", type="choice", dest="output_format", action="store", choices=["normal", "hex", "raw", "json"],default="normal",
        help="Output format: normal|hex|raw|json, default normal")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        if not check_device_exist(dev):
            raise RuntimeError("Device not support!")
        #
        if options.all:
            with NVMe(init_device(dev, open_t='nvme')) as d:
                cmd = d.allocated_ns_ids(options.namespace_id)
        ##
        else:
            with NVMe(init_device(dev, open_t='nvme')) as d:
                cmd = d.active_ns_ids(options.namespace_id)
        cmd.check_return_status(success_hint=False, fail_hint=True)
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
    parser.add_option("-o", "--output-format", type="choice", dest="output_format", action="store", choices=["normal", "hex", "raw", "json"],default="normal",
        help="Output format: normal|hex|raw|json, default normal")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        if not check_device_exist(dev):
            raise RuntimeError("Device not support!")
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
        cmd.check_return_status(success_hint=False, fail_hint=True)
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

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        if not check_device_exist(dev):
            raise RuntimeError("Device not support!")
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
        cmd.check_return_status(success_hint=True, fail_hint=True)
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
    parser.add_option("-o", "--output-format", type="choice", dest="output_format", action="store", choices=["raw", "hex"],default="raw",
        help="Output format: raw|hex, default raw")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        if not check_device_exist(dev):
            raise RuntimeError("Device not support!")
        ##
        with NVMe(init_device(dev, open_t='nvme')) as d:
            cmd = d.read(options.namespace_id, options.start_block, options.block_count)
        cmd.check_return_status(success_hint=False, fail_hint=True)
        ##
        nvme_format_print.format_print_read_data(cmd.meta_data, cmd.data, dev=d.device.device_name, print_type=options.output_format)
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
        if not check_device_exist(dev):
            raise RuntimeError("Device not support!")
        ##
        with NVMe(init_device(dev, open_t='nvme')) as d:
            cmd = d.verify(options.namespace_id, options.start_block, options.block_count)
        cmd.check_return_status(success_hint=True, fail_hint=True)
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
        help="String containing the block to write")
    parser.add_option("-f", "--data-file", type="str", dest="dfile", action="store", default='',
        help="File(Read first) containing the block to write")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        if not check_device_exist(dev):
            raise RuntimeError("Device not exist!")
        ## check data
        temp_data = b''
        if options.data:
            temp_data = bytes(options.data, 'utf-8')
        elif options.dfile:
            if os.path.isfile(options.dfile):
                with open(options.dfile, 'rb') as f:
                    temp_data = f.read()
        if temp_data:
            data_l = len(temp_data)
            # now data is 512b aligned
            remainder = data_l % 512
            if remainder:
                data_l += (512-remainder) 
            data_buffer = DataBuffer(data_l)
            data_buffer.data_buffer = temp_data
        else:
            parser.error("Lack of input data")
            return
        ##
        with NVMe(init_device(dev, open_t='nvme')) as d:
            print ('issuing write command')
            print ("%s:" % d.device._file_name)
            print ('')
            cmd = d.write(options.namespace_id, options.start_block, options.block_count, data_buffer)
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
        if not check_device_exist(dev):
            raise RuntimeError("Device not support!")
        ##
        with NVMe(init_device(dev, open_t='nvme')) as d:
            cmd = d.flush(options.namespace_id)
        cmd.check_return_status(True)
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
    parser.add_option("-o", "--output-format", type="choice", dest="output_format", action="store", choices=["normal", "hex", "raw", "json"],default="normal",
        help="Output format: normal|hex|raw|json, default normal")
    parser.add_option("-t", "--timeout", type="int", dest="timeout", action="store", default=60000,
        help="timeout value, in milliseconds")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        if not check_device_exist(dev):
            raise RuntimeError("Device not support!")
        mndw = 2 + 4*options.entry_count - 1 # zero based
        ##
        with NVMe(init_device(dev, open_t='nvme')) as d:
            cmd = d.get_lba_status(options.namespace_id, # ns_id
                                   options.start_block,  # slba
                                   mndw,                 # mndw
                                   options.action_type,  # atype
                                   options.block_count,  # Range Length
                                   timeout=options.timeout, # timeout
                                   )
        SC,SCT = cmd.check_return_status(False)
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
        if not check_device_exist(dev):
            raise RuntimeError("Device not support!")
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

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        PCIePowerPath = "/sys/bus/pci/slots/%s/power"
        ##
        if options.power and options.power not in ("status", "on", "off"):
            parser.error("Check or set Pcie power should be in (status|on|off)")
        ## check device
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
        from pydiskcmd.pypci.pci_lib import map_pci_device
        from pydiskcmd.system.lin_os_tool import map_pcie_addr_by_nvme_ctrl_path
        ##
        bus_address = map_pcie_addr_by_nvme_ctrl_path(dev)
        if bus_address:
            pcie_context = map_pci_device(bus_address)
            if pcie_context:
                print ("Device %s mapped to pcie address %s" % (dev, pcie_context.device_name))
                print ('')
                if options.power:
                    pcie_parent = pcie_context.parent
                    if pcie_parent and pcie_parent.express_slot:
                        print ("Device Slot number is %s" % pcie_parent.express_slot.slot)
                        power_file = PCIePowerPath % pcie_parent.express_slot.slot
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
                    print ("Bus address: %s" % pcie_context.device_name)
                    print ("Location:    %s" % pcie_context.location)
                    print ("Device Type: %s" % pcie_context.express_type)
                    print ("Class ID:    %#x" % pcie_context.class_id)
                    print ("Device Name: %s" % pcie_context.name)
                    print ("")
                    print ("VID=%#x, DID=%#x, SSVID=%#x, SSDID=%#x" % (pcie_context.vendor_id, pcie_context.device_id,pcie_context.subsystem_vendor,pcie_context.subsystem_device))
                    if pcie_context.express_link:
                        print ("Speed is %s(capable %s), width is %s(capable %s)" % (pcie_context.express_link.cur_speed,
                                                                                     pcie_context.express_link.capable_speed,
                                                                                     pcie_context.express_link.cur_width,
                                                                                     pcie_context.express_link.capable_width)
                              )
                else:
                    pass
            else:
                parser.error("Cannot init pcie context, device %s: %s" % (dev, power_file))
        else:
            parser.error("You may need a device controller path, like /dev/nvme1")
    else:
        parser.print_help()

###########################
###########################
commands_dict = {"list": _list,
                 "list-ctrl": list_ctrl,
                 "list-ns": list_ns,
                 "smart-log": smart_log,
                 "id-ctrl": id_ctrl,
                 "id-ns": id_ns,
                 "get-log": get_log,
                 "error-log": error_log,
                 "fw-log": fw_log,
                 "telemetry-log": telemetry_log,
                 "sanitize-log": sanitize_log,
                 "fw-download": fw_download, 
                 "fw-commit": fw_commit, 
                 "nvme-create-ns": nvme_create_ns,
                 "nvme-delete-ns": nvme_delete_ns,
                 "nvme-attach-ns": nvme_attach_ns,
                 "nvme-detach-ns": nvme_detach_ns,
                 "get-feature": get_feature,
                 "set-feature": set_feature,
                 "format": nvme_format,
                 "sanitize": sanitize,
                 "persistent_event_log": persistent_event_log,
                 "device-self-test": device_self_test,
                 "self-test-log": self_test_log,
                 "commands-se-log": commands_supported_and_effects,
                 "pcie": pcie,
                 "flush": flush,
                 "read": read,
                 "verify": verify,
                 "write": write,
                 "get-lba-status":get_lba_status,
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
