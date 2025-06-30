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
from .scan_csmi_controller import (
    CSMIController,
    scan_csmi_controller,
)


def _win_csmi_print_help():
    if len(sys.argv) > 3 and sys.argv[3] in plugin_win_nvme_vroc_commands_dict:
        func_name,sys.argv[3] = sys.argv[3],"--help"
        plugin_win_nvme_vroc_commands_dict[func_name]()
    else:
        print ("usage: pyscsi csmi <command> [<device>] [<args>]")
        print ("")
        print (r"The '<device>' is a string(ex: \\.\Scsi0:/390) split by '/' that include")
        print (r"CSMI Controller(ex: \\.\Scsi0:) and CSMI Disk ID.")
        print ("")
        print ("Windows CSMI extensions")
        print ("")
        print ("The following are all implemented sub-commands:")
        print ("")
        print ("  list-ctrls                    List all CSMI Controllers")
        print ("  get-cntrl-status              Get CSMI Controller Status")
        print ("  get-driver-info               Get CSMI Controller Driver Info")
        print ("  get-raid-info                 Get CSMI Controller Raid Info")
        print ("  get-raid-config               Get CSMI Controller Raid Config")
        print ("  get-phy-info                  Get CSMI Controller Phy Info")
        print ("  version                       Shows Windows CSMI plugin version")
        print ("  help                          Display this help")
        print ("")
        print ("See 'pyscsi csmi help <command>' for more information on a specific command")

def _win_csmi_print_ver():
    print ("Windows CSMI Plugin Version: %s" % "0.1")
    print ("")

def _win_csmi_list_ctrls():
    usage="usage: %prog csmi list-ctrls"
    parser = optparse.OptionParser(usage)
    parser_update(parser, add_output=["normal"])

    (options, args) = parser.parse_args()
    ##
    script_check(options, admin_check=True)
    ##
    print_format = "%-15s %-10s %-8s %-10s %-20s %-40s"
    print (print_format % ("Node", "Status", "CSMIRev", "DriverRev", "Name", "Description"))
    print (print_format % ("-"*15, "-"*10, "-"*8, "-"*10, "-"*20, "-"*40))
    ## cmd.Information.usMajorRevision
    for csmi_ctrl in scan_csmi_controller():
        cmd = csmi_ctrl.get_cntlr_status()
        status = cmd.get_status_desp()
        #
        cmd = csmi_ctrl.get_driver_info()
        cmd.check_return_status(raise_if_fail=True)
        driver_rev = "%d.%d" % (cmd.cdb.Information.usMajorRevision,
                                cmd.cdb.Information.usMinorRevision,
                                )
        csmi_rev = "%d.%d" % (cmd.cdb.Information.usCSMIMajorRevision,
                              cmd.cdb.Information.usCSMIMinorRevision,
                              )
        name = string_strip(decode_bytes(bytes(cmd.cdb.Information.szName)), b'\x00'.decode(), ' ')
        des = string_strip(decode_bytes(bytes(cmd.cdb.Information.szDescription)), b'\x00'.decode(), ' ')
        if options.output_format == "normal":
            print (print_format % (csmi_ctrl.device._file_name, 
                                   status,
                                   csmi_rev,
                                   driver_rev,
                                   name,
                                   des,
                                   ))

def _win_csmi_get_driver_info():
    usage="usage: %prog csmi get-driver-info"
    parser = optparse.OptionParser(usage)
    parser_update(parser, add_output=["normal"])

    (options, args) = parser.parse_args()
    if len(sys.argv) > 3:
        #
        dev = sys.argv[3].strip()
        ##
        script_check(options, admin_check=True)
        ##
        with CSMIController(init_device(dev, open_t='csmi')) as d:
            cmd = d.get_driver_info()
            cmd.check_return_status(raise_if_fail=True)

        if options.output_format == "normal":
            print ("CSMI Get %s Driver Info:" % dev)
            print ("")
            print ("  Name:     %s" % string_strip(decode_bytes(bytes(cmd.cdb.Information.szName)), b'\x00'.decode(), ' '))
            print ("  Description: %s" % string_strip(decode_bytes(bytes(cmd.cdb.Information.szDescription)), b'\x00'.decode(), ' '))
            print ("  MajorRevision: %d" % cmd.cdb.Information.usMajorRevision)
            print ("  MinorRevision: %d" % cmd.cdb.Information.usMinorRevision)
            print ("  BuildRevsion: %d" % cmd.cdb.Information.usBuildRevision)
            print ("  ReleaseRevision: %d" % cmd.cdb.Information.usReleaseRevision)
            print ("  CSMIMajorRevision: %d" % cmd.cdb.Information.usCSMIMajorRevision)
            print ("  CSMIMinorRevision: %d" % cmd.cdb.Information.usCSMIMinorRevision)
    else:
        parser.print_help()

def _win_csmi_get_cntrl_status():
    usage="usage: %prog csmi get-cntrl-status"
    parser = optparse.OptionParser(usage)
    parser_update(parser, add_output=["normal"])

    (options, args) = parser.parse_args()
    if len(sys.argv) > 3:
        #
        dev = sys.argv[3].strip()
        ##
        script_check(options, admin_check=True)
        ##
        with CSMIController(init_device(dev, open_t='csmi')) as d:
            cmd = d.get_cntlr_status()
            cmd.check_return_status(raise_if_fail=True)

        if options.output_format == "normal":
            print ("CSMI Get %s CNTLR Status:" % dev)
            print ("")
            print ("  Current Status: %d" % cmd.cdb.Status.uStatus)
            print ("  Offline Reason: %d" % cmd.cdb.Status.uOfflineReason)
    else:
        parser.print_help()

def _win_csmi_get_raid_info():
    usage="usage: %prog csmi get-raid-info"
    parser = optparse.OptionParser(usage)
    parser_update(parser, add_output=["normal"])

    (options, args) = parser.parse_args()
    if len(sys.argv) > 3:
        #
        dev = sys.argv[3].strip()
        ##
        script_check(options, admin_check=True)
        ##
        with CSMIController(init_device(dev, open_t='csmi')) as d:
            cmd = d.get_raid_info()
            cmd.check_return_status(raise_if_fail=True)

        if options.output_format == "normal":
            print ("CSMI Get %s RAID Info:" % dev)
            print ("")
            print ("  NumRaidSets:     %d" % cmd.cdb.Information.uNumRaidSets)
            print ("  MaxDrivesPerSet: %d" % cmd.cdb.Information.uMaxDrivesPerSet)
    else:
        parser.print_help()

def _win_csmi_get_raid_config():
    usage="usage: %prog csmi get-raid-config"
    parser = optparse.OptionParser(usage)
    parser_update(parser, add_output=["normal"])

    (options, args) = parser.parse_args()
    if len(sys.argv) > 3:
        #
        dev = sys.argv[3].strip()
        ##
        script_check(options, admin_check=True)
        ##
        result = {}
        with CSMIController(init_device(dev, open_t='csmi')) as d:
            cmd = d.get_raid_info()
            cmd.check_return_status(raise_if_fail=True)
            num_raid_sets = cmd.cdb.Information.uNumRaidSets
            max_drives_per_set = cmd.cdb.Information.uMaxDrivesPerSet
            for raid_set_index in range(0, num_raid_sets):
                cmd = d.get_raid_config(raid_set_index, max_drives_per_set)
                cmd.check_return_status(raise_if_fail=True)
                result[raid_set_index] = {"RaidSetIndex": cmd.cdb.Configuration.uRaidSetIndex,
                                          "Capacity": cmd.cdb.Configuration.uCapacity,
                                          "StripeSize": cmd.cdb.Configuration.uStripeSize,
                                          "RaidType": cmd.cdb.Configuration.bRaidType,
                                          "Status": cmd.cdb.Configuration.bStatus,
                                          "Information": cmd.cdb.Configuration.bInformation,
                                          "DriveCount": cmd.cdb.Configuration.bDriveCount,
                                          "Drives": [],
                                          }
                for drive_index in range(result[raid_set_index]["DriveCount"]):
                    drive_info = cmd.cdb.Configuration.Drives[drive_index]
                    result[raid_set_index]["Drives"].append({"Model": bytes(drive_info.bModel),
                                                             "Firmware": bytes(drive_info.bFirmware),
                                                             "SerialNumber": bytes(drive_info.bSerialNumber),
                                                             "SASAddress": bytes(drive_info.bSASAddress),
                                                             "SASLun": bytes(drive_info.bSASLun),
                                                             "DriveStatus": drive_info.bDriveStatus,
                                                             "DriveUsage": drive_info.bDriveUsage,
                                                           })

        if options.output_format == "normal":
            print ("CSMI Get %s RAID Config:" % dev)
            print ("")
            if result:
                for raid_set_index,raid_info in result.items():
                    print ("  %s" % ("="*20))
                    print ("  RaidSetIndex: %d" % raid_info["RaidSetIndex"])
                    print ("  Capacity: %d" % raid_info["Capacity"])
                    print ("  StripeSize: %d" % raid_info["StripeSize"])
                    print ("  RaidType: %d" % raid_info["RaidType"])
                    print ("  Status: %d" % raid_info["Status"])
                    print ("  Information: %d" % raid_info["Information"])
                    print ("  DriveCount: %d" % raid_info["DriveCount"])
                    for drive_index,drive_info in enumerate(raid_info["Drives"]):
                        print ("    %s" % ("-"*18))
                        print ("    Drive[%d]:" % drive_index)
                        print ("      Model: %s" % drive_info["Model"])
                        print ("      Firmware: %s" % drive_info["Firmware"])
                        print ("      SerialNumber: %s" % drive_info["SerialNumber"])
                        print ("      SASAddress: %s" % drive_info["SASAddress"])
                        print ("      SASLun: %s" % drive_info["SASLun"])
                        print ("      DriveStatus: %d" % drive_info["DriveStatus"])
                        print ("      DriveUsage: %d" % drive_info["DriveUsage"])
            else:
                print ("No RAID Volume is configured.")
    else:
        parser.print_help()


def _win_csmi_get_phy_info():
    usage="usage: %prog csmi get-phy-info"
    parser = optparse.OptionParser(usage)
    parser_update(parser, add_output=["normal"])

    (options, args) = parser.parse_args()
    if len(sys.argv) > 3:
        #
        dev = sys.argv[3].strip()
        script_check(options, admin_check=True)
        #
        with CSMIController(init_device(dev, open_t='csmi')) as d:
            cmd = d.get_phy_info()
            cmd.check_return_status(raise_if_fail=True)
        ## print output
        if options.output_format == "normal":
            print ("CSMI Get %s Phy Info:" % dev)
            print ("  NumberOfPhys: %d" % cmd.cdb.Information.bNumberOfPhys)
            print ("")
            for i in range(cmd.cdb.Information.bNumberOfPhys):
                temp = cmd.cdb.Information.Phy[i]
                print ("  Phy[%d] Port %d:" % (i, temp.bPortIdentifier))
                print ("    CSMI_SAS_IDENTIFY:")
                print ("      DeviceType:            %#x" % temp.Identify.bDeviceType)
                print ("      InitiatorPortProtocol: %#x" % temp.Identify.bInitiatorPortProtocol)
                print ("      TargetPortProtocol:    %#x" % temp.Identify.bInitiatorPortProtocol)
                print ("      SASAddress:            %s" % ' '.join([("%X" % i).rjust(2, '0') for i in bytes(temp.Identify.bSASAddress)]))
                print ("      PhyIdentifier:         %d" % temp.Identify.bPhyIdentifier)
                print ("      SignalClass:           %#x" % temp.Identify.bSignalClass)
                print ("    PortIdentifier:        %d" % temp.bPortIdentifier)
                print ("    NegotiatedLinkRate:    %#x" % temp.bNegotiatedLinkRate)
                print ("    MinimumLinkRate:       %#x" % temp.bMinimumLinkRate)
                print ("    MaximumLinkRate:       %#x" % temp.bMaximumLinkRate)
                print ("    PhyChangeCount:        %#x" % temp.bPhyChangeCount)
                print ("    AutoDiscover:          %#x" % temp.bAutoDiscover)
                print ("    Attached:")
                print ("      DeviceType:            %#x" % temp.Attached.bDeviceType)
                print ("      InitiatorPortProtocol: %#x" % temp.Attached.bInitiatorPortProtocol)
                print ("      TargetPortProtocol:    %#x" % temp.Attached.bInitiatorPortProtocol)
                print ("      SASAddress:            %s" % ' '.join([("%X" % i).rjust(2, '0') for i in bytes(temp.Attached.bSASAddress)]))
                print ("      PhyIdentifier:         %d" % temp.Attached.bPhyIdentifier)
                print ("      SignalClass:           %#x" % temp.Attached.bSignalClass)
                print ("  ----------------------------")


plugin_win_nvme_vroc_commands_dict = {"list-ctrls": _win_csmi_list_ctrls,
                                      "get-cntrl-status": _win_csmi_get_cntrl_status,
                                      "get-driver-info": _win_csmi_get_driver_info,
                                      "get-raid-info": _win_csmi_get_raid_info,
                                      "get-raid-config": _win_csmi_get_raid_config,
                                      "get-phy-info": _win_csmi_get_phy_info,
                                      "version": _win_csmi_print_ver,
                                      "help": _win_csmi_print_help,}

def win_csmi():
    if os_type != 'Windows':
        raise NotImplementedError("Only Windows support CSMI for now")
    if len(sys.argv) > 2:
        plugin_command = sys.argv[2]
        if plugin_command in plugin_win_nvme_vroc_commands_dict:
            return plugin_win_nvme_vroc_commands_dict[plugin_command]()
    _win_csmi_print_help()
