# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import sys
import optparse
from pydiskcmdlib.pynvme.nvme import NVMe
from pydiskcmdcli import os_type
from pydiskcmdlib.utils import init_device
from pydiskcmdcli.utils import nvme_format_print
from pydiskcmdlib.utils.converter import scsi_ba_to_int
from pydiskcmdcli.utils.format_print import format_dump_bytes,human_read_capacity
from pydiskcmdcli.scripts import parser_update,script_check
from pydiskcmdcli.utils.string_utils import decode_bytes,string_strip
from .cdb_ocp_get_log_page import (SmartExtendedLog,
                                   ErrorRecoveryLog,
                                   LatencyMonitor,
                                   DeviceCapabilities,
                                   UnsupportedRequirements,
                                   HardwareComponent,
                                   TCGConfiguration,
                                   TelemetryStringLog,
                                   )

ocp_plugin = {"SmartExtendedLog": SmartExtendedLog,
              "ErrorRecoveryLog": ErrorRecoveryLog,
              "LatencyMonitor": LatencyMonitor,
              "DeviceCapabilities": DeviceCapabilities,
              "UnsupportedRequirements": UnsupportedRequirements,
              "HardwareComponent": HardwareComponent,
              "TCGConfiguration": TCGConfiguration,
              "TelemetryStringLog": TelemetryStringLog,
              }

def _ocp_print_help():
    if len(sys.argv) > 3 and sys.argv[3] in plugin_ocp_commands_dict:
        func_name,sys.argv[3] = sys.argv[3],"--help"
        plugin_ocp_commands_dict[func_name]()
    else:
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
        print ("  latency-monitor               Retrieve latency monitor log page")
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

def _ocp_latency_monitor():
    usage="usage: %prog ocp latency-monitor <device> [OPTIONS]"
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
            cmd = ocp_plugin["LatencyMonitor"]()
            d.execute(cmd)
        ##
        nvme_format_print.format_print_ocp_latency_monitor_log(cmd, options.output_format)
    else:
        parser.print_help()

plugin_ocp_commands_dict = {"ocp-check": _ocp_info_check,
                            "smart-add-log": _ocp_smart_extended_log,
                            "error-recovery-log": _ocp_error_recovery_log,
                            "latency-monitor": _ocp_latency_monitor,
                            "cloud-SSD-plugin-version": _ocp_print_ver,
                            "Help": _ocp_print_help,}


def ocp():
    if len(sys.argv) > 2:
        plugin_command = sys.argv[2]
        if plugin_command in plugin_ocp_commands_dict:
            plugin_ocp_commands_dict[plugin_command]()
            return
    _ocp_print_help()
