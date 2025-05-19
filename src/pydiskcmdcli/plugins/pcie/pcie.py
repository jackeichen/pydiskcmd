# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
"""pcie.py"""
import os,sys
import optparse

from pydiskcmdcli import os_type
from pydiskcmdcli.utils import nvme_format_print
from pydiskcmdcli.utils.format_print import format_dump_bytes,json_print
from pydiskcmdcli.scripts import parser_update,script_check,func_debug_info
from pydiskcmdcli import log

##
Version="0.1"
#
PCIePowerPath = "/sys/bus/pci/slots/%s/power"
##
def _pci_print_help():
    if len(sys.argv) > 3 and sys.argv[3] in plugin_pci_commands_dict:
        func_name,sys.argv[3] = sys.argv[3],"--help"
        plugin_pci_commands_dict[func_name]()
    else:
        print ("usage: pynvme pci <command> [<device>] [<args>]")
        print ("")
        print (r"The '<device>' is a string, like /dev/nvme0")
        print ("")
        print ("Linux PCI extensions")
        print ("")
        print ("The following are all implemented sub-commands:")
        print ("")
        print ("  config-get                    Get information from PCIe Configuration Space")
        print ("  power                         Get/Set Pcie power status")
        print ("  update-pci-ids                Update the pci.ids online")
        print ("  version                       Shows Linux PCIe plugin version")
        print ("  help                          Display this help")
        print ("")
        print ("See 'pynvme pci help <command>' for more information on a specific command")

def _pci_print_ver():
    print ("Linux PCIe Plugin for PCIe SSD Version: %s" % Version)
    print ("")

def _pci_update_pci_ids():
    usage="usage: %prog pci update-pci-ids"
    parser = optparse.OptionParser(usage)
    parser_update(parser)
    (options, args) = parser.parse_args()
    script_check(options)
    #
    from pydiskcmdcli.utils.update_pci_ids import update_pci_ids_online
    return update_pci_ids_online()

def _pci_power():
    usage="usage: %prog pci power <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-s", "--set", type="choice", dest="SET", action="store", choices=["on", "off", ""], default="",
        help="Set Pcie power status(on|off), combine with -s/--slot_num if set power on.")
    parser.add_option("-g", "--get", type="choice", dest="GET", action="store", choices=["status", ""], default="",
        help="Get Pcie power information(status)")
    parser.add_option("-n", "--slot_num", type="int", dest="slot_num", action="store", default=-1,
        help="Combine with other options")
    parser_update(parser)
    #
    if len(sys.argv) > 3:
        (options, args) = parser.parse_args(sys.argv[3:])
        script_check(options)
        ##
        from pydiskcmdcli.system.os_tool import check_device_exist
        dev = sys.argv[3]
        if not check_device_exist(dev):
            if options.SET == "on":
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
            elif options.GET == "status":
                print ("Device is offline")
                print ("")
            else:
                print ("Device is offline")
                print ("")
            return
        #
        from pydiskcmdlib.pynvme.nvme_pcie_lib import NVMePCIe
        #
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
            pcie_parent = pcie_dev.get_parent()
            if pcie_parent and pcie_parent.pcie_cap:
                slot = pcie_parent.pcie_cap.slot_cap.decode_data["PhysicalSlotNumber"]
                print ("Device Slot number is %d" % slot)
                power_file = PCIePowerPath % slot
                if os.path.isfile(power_file):
                    if options.GET == "status":
                        with open(power_file, 'r') as f:
                            status = f.read().strip()
                        print ("Current PCIe power status: on")
                    if options.SET == "off":
                        print ("Powering off device")
                        with open(power_file, 'w') as f:
                            f.write("0")
                    elif options.SET == "on":
                        print ("No need power on, device is online")
                else:
                    parser.error("Cannot find power file, device %s: %s" % (dev, bus_address))
            else:
                print ("Cannot find upstream device slot information.")
    else:
        parser.print_help()

def _pci_config_get():
    usage="usage: %prog pci config-get <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-a", dest="all", action="store_true", default=False,
        help="Show the detail pcie configuration space information. Default is False.")
    parser_update(parser, add_output=["normal", "hex", "raw", "json"])
    #
    if len(sys.argv) > 3:
        (options, args) = parser.parse_args(sys.argv[3:])
        script_check(options)
        ##
        from pydiskcmdcli.system.os_tool import check_device_exist
        from pydiskcmdlib.pynvme.nvme_pcie_lib import NVMePCIe
        #
        dev = sys.argv[3]
        if check_device_exist(dev):
            try:
                pcie_dev = NVMePCIe(dev)
            except FileNotFoundError as e:
                parser.error("Cannot init pcie context, device %s, %s \nYou may need a device controller path, like /dev/nvme1, but not /dev/nvme1n1" % (dev, str(e)))
            except Exception as e:
                print (str(e))
            else:
                if options.output_format != "json":
                    print ("Device %s mapped to pcie address %s" % (dev, pcie_dev.address))
                    print ("")
                if not options.all:
                    if options.output_format == "normal":
                        pcie_dev.simple_info_print()
                    elif options.output_format == 'json':
                        pcie_info = {"device": {"name": dev, "pcie_address": pcie_dev.address},
                                        }
                        pcie_info.update(pcie_dev.dump_simple_info())
                        json_print(pcie_info)
                    else:
                        print ("Only support normal and json format @ simple show.")
                else:
                    if options.output_format == "normal":
                        pcie_dev.detail_info_print()
                    elif options.output_format == 'json':
                        pcie_info = {"device": {"name": dev, "pcie_address": pcie_dev.address},
                                        }
                        pcie_info.update(pcie_dev.dump_detail_info())
                        json_print(pcie_info)
                    elif options.output_format == 'hex':
                        nvme_format_print.format_dump_bytes(pcie_dev.raw_data, byteorder='obverse')
                    else:
                        print (bytes(pcie_dev.raw_data))
                return 0
        else:
            print ("Device is offline")
            print ("")
    else:
        parser.print_help()
    return 1

plugin_pci_commands_dict = {"update-pci-ids": _pci_update_pci_ids,
                            "power": _pci_power,
                            "config-get": _pci_config_get,
                            "version": _pci_print_ver,
                            "help": _pci_print_help,}



def pci():
    if os_type != 'Linux':
        raise NotImplementedError("Only Linux support")
    if len(sys.argv) > 2:
        plugin_command = sys.argv[2]
        if plugin_command in plugin_pci_commands_dict:
            plugin_pci_commands_dict[plugin_command]()
            return
    _pci_print_help()