# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import os,sys
import optparse
from pydiskcmdlib.utils import init_device
from pydiskcmdlib.pynvme.nvme import NVMe
from pydiskcmdcli.scripts import parser_update,script_check
from pydiskcmdcli.utils.format_print import format_dump_bytes,json_print,format_print_pyobj
from pydiskcmdcli.nvme_spec import decode_commands_supported_and_effects,decode_mi_commands_supported_and_effects,get_nvme_mi_command_name
from .mi_decode import decode_subsys_health_status
from pydiskcmdlib.exceptions import CommandReturnDataError,CommandReturnStatusError


def _nvme_mi_print_help():
    if len(sys.argv) > 3 and sys.argv[3] in plugin_nvme_mi_commands_dict:
        func_name,sys.argv[3] = sys.argv[3],"--help"
        plugin_nvme_mi_commands_dict[func_name]()
    else:
        print ("usage: pynvme mi <command> [<device>] [<args>]")
        print ("")
        print (r"The '<device>' is a string(ex: /dev/nvme0)")
        print ("")
        print ("NVMe-MI extensions")
        print ("")
        print ("The following are all implemented sub-commands:")
        print ("")
        print ("  check-support                 Check device if support NVMe MI commands")
        print ("  mi-data                       Read NVMe-MI Data Structure")
        print ("  subsys-health                 Get Subsystem Health Status")
        print ("  vpd-read                      Read VPD page")
        print ("  ib-send                       In-Band NVMe-MI Send Command passthrough")
        print ("  ib-recv                       In-Band NVMe-MI Receive Command passthrough")
        print ("  version                       Shows Windows NVMe VROC plugin version")
        print ("  help                          Display this help")
        print ("")
        print ("See 'pynvme mi help <command>' for more information on a specific command")
    return 0

def _nvme_mi_print_ver():
    print ("NVMe-MI Plugin Version: %s" % "1.0")
    print ("")
    return 0

def _check_support():
    usage="usage: %prog mi check-support <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser_update(parser)
    if len(sys.argv) > 3:
        (options, args) = parser.parse_args(sys.argv[3:])
        ##
        script_check(options, admin_check=True)
        ## check device
        from pydiskcmdlib.pynvme.nvme_command import AdminCommandOpcode
        dev = sys.argv[3].strip()
        mi_send_support = "Unkown"
        mi_recv_support = "Unkown"
        mi_cmds = []
        with NVMe(init_device(dev, open_t='nvme')) as d:
            # First check commands supported and effects log
            cmd = d.commands_supported_and_effects_log()
            SC,SCT = cmd.check_return_status(fail_hint=False)
            if SC == 0 and SCT == 0:
                admin_cmd,_ = decode_commands_supported_and_effects(cmd.data)
                mi_send_support = "No"
                mi_recv_support = "No"
                for i in admin_cmd:
                    if i["opcode"] == AdminCommandOpcode.NVMeMISend.value:
                        mi_send_support = "Yes"
                    if i["opcode"] == AdminCommandOpcode.NVMeMIReceive.value:
                        mi_recv_support = "Yes"
                ##
                cmd = d.mi_commands_supported_and_effects_log()
                SC,SCT = cmd.check_return_status(fail_hint=False)
                if SC == 0 and SCT == 0:
                    mi_cmd = decode_mi_commands_supported_and_effects(cmd.data)
                    for opcode,_ in mi_cmd.items():
                        mi_cmds.append((opcode, get_nvme_mi_command_name(opcode)))
        print ("NVMe-Mi Send Command Support   : %s" % mi_send_support)
        print ("NVMe-Mi Receive Command Support: %s" % mi_recv_support)
        if mi_cmds:
            print_format = "  %-10s %s"
            print ('')
            print ('NVMe-Mi Commands:')
            print (print_format % ("Opcode", "Command Name"))
            for i in mi_cmds:
                print (print_format % i)
    else:
        parser.print_help()

def _ib_send():
    usage="usage: %prog mi ib-send <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-O", "--opcode", type="int", dest="opcode", default=-1,
        help="opcode (required).")
    parser.add_option("-0", "--nmd0", type="int", dest="nmd0", default=0,
        help="nvme management dword 0 value")
    parser.add_option("-1", "--nmd1", type="int", dest="nmd1", default=0,
        help="nvme management dword 1 value")
    parser.add_option("-i", "--input-file", type="str", dest="input_file", default="",
        help="data input file.")
    parser_update(parser, add_output=["hex", "raw"])

    if len(sys.argv) > 3:
        (options, args) = parser.parse_args(sys.argv[3:])
        ##
        script_check(options, admin_check=True)
        ## check device
        dev = sys.argv[3].strip()
        ##
        if os.path.isfile(options.input_file):
            with open(options.input_file, "rb") as f:
                raw_data = f.read()
        else:
            raise FileNotFoundError("input file not found: %s" % options.input_file)
        with NVMe(init_device(dev, open_t='nvme')) as d:
            cmd = d.nvme_mi_send(options.opcode, options.nmd0, options.nmd1, data=raw_data)
        cmd.check_return_status(raise_if_fail=True)
        #
        print ("Tunneled Status: %#x" % (cmd.cq_cmd_spec & 0xFF))
        print ("Tunneled NVMe Management Response: %#x" % (cmd.cq_cmd_spec >> 8))
    else:
        parser.print_help()

def _ib_recv():
    usage="usage: %prog mi ib-recv <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-O", "--opcode", type="int", dest="opcode", default=-1,
        help="opcode (required).")
    parser.add_option("-0", "--nmd0", type="int", dest="nmd0", default=0,
        help="nvme management dword 0 value")
    parser.add_option("-1", "--nmd1", type="int", dest="nmd1", default=0,
        help="nvme management dword 1 value")
    parser.add_option("-l", "--data-len", type="int", dest="data_len", default=0,
        help="The length of Request Data field.")
    parser_update(parser, add_output=["hex", "raw"])

    if len(sys.argv) > 3:
        (options, args) = parser.parse_args(sys.argv[3:])
        ##
        script_check(options, admin_check=True)
        ## check device
        dev = sys.argv[3].strip()
        ##
        with NVMe(init_device(dev, open_t='nvme')) as d:
            cmd = d.nvme_mi_recv(options.opcode, options.nmd0, options.nmd1, data_len=options.data_len)
        cmd.check_return_status(raise_if_fail=True)
        #
        print ("Tunneled Status: %#x" % (cmd.cq_cmd_spec & 0xFF))
        print ("Tunneled NVMe Management Response: %#x" % (cmd.cq_cmd_spec >> 8))
        if options.data_len > 0:
            print ("Response Data:")
            print ("")
            if options.output_format == "hex":
                format_dump_bytes(cmd.data, byteorder="obverse")
            else:
                print(cmd.data)
    else:
        parser.print_help()

def _read_nvme_mi_data():
    usage="usage: %prog mi mi-data <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-c", "--ctrl-id", type="int", dest="ctrl_id", default=0,
        help="Controller Identifier in the NVM Subsystem to request. Default 0")
    parser.add_option("-p", "--port-id", type="int", dest="port_id", default=0,
        help="Port Identifier to request. Default 0")
    parser.add_option("-t", "--type", type="int", dest="type", default=0,
        help="Data Structure Type to request. Default 0")
    parser.add_option("-i", "--iocsi", type="int", dest="iocsi", default=0,
        help="I/O Command Set Identifier. Default 0")
    parser.add_option("-l", "--data-len", type="int", dest="data_len", default=32,
        help="The length of Request Data field. Default 32")
    parser.add_option("-m", "--servicing-mode", type="choice", dest="servicing_mode", action="store", choices=["ib", "vdm", "smbus", "i2c"], default="ib",
        help="Message Servicing Mode, In-Band(ib) or Out-Of-Band(vdm/smbus/i2c). Default ib")
    parser_update(parser, add_output=["hex", "raw"])

    if len(sys.argv) > 3:
        (options, args) = parser.parse_args(sys.argv[3:])
        ##
        script_check(options, admin_check=True)
        ## check device
        dev = sys.argv[3].strip()
        ##
        numd0 = options.ctrl_id + (options.port_id << 16) + (options.type << 24)
        nmd1 = options.iocsi
        if options.servicing_mode == 'ib':
            with NVMe(init_device(dev, open_t='nvme')) as d:
                cmd = d.nvme_mi_recv(0x00, numd0, nmd1, data_len=options.data_len)
            cmd.check_return_status(raise_if_fail=True)
            # check the Tunneled Status
            if cmd.cq_cmd_spec & 0xFF:
                raise CommandReturnStatusError("Tunneled Status code is %#x" % (cmd.cq_cmd_spec & 0xFF))
            # check the request data
            if options.data_len > 0 and ((cmd.cq_cmd_spec >> 8) & 0xFFFF == 0x00):
                raise CommandReturnDataError("Return Data Length is 0")
        else:
            raise NotImplementedError("Out-Of-Band Message Servicing Mode(%s) is not implemented now" % options.servicing_mode)
        # check the request data
        if options.output_format == "hex":
            format_dump_bytes(cmd.data, byteorder="obverse")
        else:
            print(cmd.data)
    else:
        parser.print_help()

def _nvm_subsys_health_status():
    usage="usage: %prog mi subsys-health <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-c", "--clear-status", dest="clear_status", action="store_true",default=False,
        help="Clear the state of reported Composite Controller Status. Default False")
    parser.add_option("-m", "--servicing-mode", type="choice", dest="servicing_mode", action="store", choices=["ib", "vdm", "smbus", "i2c"], default="ib",
        help="Message Servicing Mode, In-Band(ib) or Out-Of-Band(vdm/smbus/i2c). Default ib")
    parser_update(parser, add_output=["normal", "hex", "raw", "json"])

    if len(sys.argv) > 3:
        (options, args) = parser.parse_args(sys.argv[3:])
        ##
        script_check(options, admin_check=True)
        ## check device
        dev = sys.argv[3].strip()
        ##
        if options.clear_status:
            nmd1 = 0x8000
        else:
            nmd1 = 0
        if options.servicing_mode == 'ib':
            with NVMe(init_device(dev, open_t='nvme')) as d:
                cmd = d.nvme_mi_recv(0x01, 0, nmd1, data_len=8)
            cmd.check_return_status(raise_if_fail=True)
        else:
            raise NotImplementedError("Out-Of-Band Message Servicing Mode(%s) is not implemented now" % options.servicing_mode)
        ##
        if options.output_format == "normal":
            result = decode_subsys_health_status(cmd.data)
            format_print_pyobj(result)
        elif options.output_format == "json":
            result = decode_subsys_health_status(cmd.data)
            json_print(result)
        elif options.output_format == "hex":
            format_dump_bytes(cmd.data, byteorder="obverse")
        else:
            print(cmd.data)
    else:
        parser.print_help()

def _vpd_read():
    usage="usage: %prog mi vpd-read <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-l", "--dlen", type="int", dest="data_len", action="store",default=8,
        help="Data length in bytes to read from the VPD page. Default 8")
    parser.add_option("-L", "--dofst", type="int", dest="data_offset", action="store",default=0,
        help="Starting offset in bytes to read the VPD data. Default 0")
    parser.add_option("-m", "--servicing-mode", type="choice", dest="servicing_mode", action="store", choices=["ib", "vdm", "smbus", "i2c"], default="ib",
        help="Message Servicing Mode, In-Band(ib) or Out-Of-Band(vdm/smbus/i2c). Default ib")
    parser_update(parser, add_output=["hex", "raw"])

    if len(sys.argv) > 3:
        (options, args) = parser.parse_args(sys.argv[3:])
        ##
        script_check(options, admin_check=True)
        ## check device
        dev = sys.argv[3].strip()
        ##
        nmd0 = options.data_offset
        nmd1 = options.data_len
        if options.servicing_mode == 'ib':
            with NVMe(init_device(dev, open_t='nvme')) as d:
                cmd = d.nvme_mi_recv(0x05, nmd0, nmd1, data_len=options.data_len)
            cmd.check_return_status(raise_if_fail=True)
        else:
            raise NotImplementedError("Out-Of-Band Message Servicing Mode(%s) is not implemented now" % options.servicing_mode)
        ##
        if options.output_format == "hex":
            format_dump_bytes(cmd.data, byteorder="obverse")
        else:
            print(cmd.data)
    else:
        parser.print_help()


plugin_nvme_mi_commands_dict = {
    "check-support": _check_support,
    "mi-data": _read_nvme_mi_data,
    "subsys-health": _nvm_subsys_health_status,
    "vpd-read": _vpd_read,
    "ib-send": _ib_send,
    "ib-recv": _ib_recv,
    "version": _nvme_mi_print_ver,
    "help": _nvme_mi_print_help,
}

def nvme_mi():
    if len(sys.argv) > 2:
        plugin_command = sys.argv[2]
        if plugin_command in plugin_nvme_mi_commands_dict:
            plugin_nvme_mi_commands_dict[plugin_command]()
            return
    _nvme_mi_print_help()
