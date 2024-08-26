# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import sys,os
import optparse
import binascii
from pydiskcmdlib.pysata.sata import SATA
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
from pydiskcmdlib.utils import init_device
from pydiskcmdcli.utils.format_print import format_dump_bytes,human_read_capacity
from pydiskcmdlib.exceptions import ExecuteCmdErr
from pydiskcmdcli.exceptions import (
    CommandSequenceError,
    CommandNotSupport,
    NonpydiskcmdError,
    UserDefinedError,
    FunctionNotImplementError,
)
from pydiskcmdcli import os_type
from pydiskcmdcli import version as Version
from pydiskcmdcli.plugins import ata_plugins
from . import parser_update,script_check

def _debug_info_print(cmd):
    print ("")
    if cmd.cdb:
        print ("Sending Command: %s" % ' '.join(["%x" % b for b in cmd.cdb]))
    if cmd.sense:
        print ("Return sense: %s" % ' '.join(["%x" % b for b in cmd.sense]))
    if cmd.raw_sense_data:
        print ("Return raw sense data: %s" % ' '.join(["%x" % b for b in cmd.raw_sense_data]))
    print ("")

def _sending_cmd_info(dev_path: str, cmd_name: str) -> None:
    print ('issuing %s command' % cmd_name)
    print ('Device: %s' % dev_path)
    print ('')

def version():
    print ("pysata version %s" % Version)

def print_help():
    if len(sys.argv) > 2 and sys.argv[2] in commands_dict:
        func_name,sys.argv[2] = sys.argv[2],"--help"
        commands_dict[func_name]()
    else:
        print ("pysata-%s" % Version)
        print ("usage: pysata <command> [<device>] [<args>]")
        print ("")
        print ("The '<device>' is usually a character device (ex: /dev/sdb or physicaldrive1).")
        print ("")
        print ("The following are all implemented sub-commands:")
        print ("  list                        List all SATA devices on machine")
        print ("  check-PowerMode             Check Disk Power Mode")
        print ("  accessible-MaxAddress       Send Accessible Max Address command")
        print ("  identify                    Get identify information")
        print ("  self-test                   Start a disk self test")
        print ("  set-feature                 Send set feature to device")
        print ("  trusted-receive             Send trusted receive to device")
        print ("  smart                       Get smart information")
        print ("  smart-return-status         Get the reliability status of the device")
        print ("  read-log                    Get the GPL Log and show it")
        print ("  write-log                   Send write log command")
        print ("  smart-read-log              Get the smart Log and show it")
        print ("  sanitize                    Send sanitize command")
        print ("  standby                     Send standby command")
        print ("  read                        Send a read command to disk")
        print ("  read-verify-sector          Send read verify sector(s) command")
        print ("  write                       Send a write command to disk") 
        print ("  write-uncorrectable         Send a write uncorrectable command to disk") 
        print ("  flush                       Send a flush command to disk")
        print ("  trim                        Send a trim command to disk")
        print ("  download-fw                 Download firmware to target disk")
        print ("  version                     Shows the program version")
        print ("  help                        Display this help")
        print ("")
        print ("The following are pysata cli management interface:")
        print ("  cli-info                    Shows pysata information")
        print ("  cli-autocmd                 Enable or Update the command completion")
        print ("")
        print ("See 'pysata help <command>' or 'pysata <command> --help' for more information on a sub-command")

def _list():
    usage="usage: %prog list <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser_update(parser, add_output=["normal",])

    (options, args) = parser.parse_args()
    ##
    script_check(options, admin_check=True)
    ##
    print_format = "%-20s %-20s %-40s %-26s %-16s %-8s"
    print (print_format % ("Node", "SN", "Model", "Capacity", "Format(L/P)", "FW Rev"))
    print (print_format % ("-"*20, "-"*20, "-"*40, "-"*26, "-"*16, "-"*8))
    from pydiskcmdlib.utils.converter import bytearray2string,translocate_bytearray
    dev_path_all = None
    if os_type == 'Linux':
        from pydiskcmdcli.system.lin_os_tool import get_block_devs
        dev_path_all = [i for i in get_block_devs(exclude=("nvme",))]
    elif os_type == 'Windows':
        from  pydiskcmdcli.system.win_os_tool import scan_all_physical_drive
        dev_path_all = sorted([i for i in scan_all_physical_drive()])
    if dev_path_all is not None:
        for dev_path in dev_path_all:
            try:
                with SATA(init_device(dev_path, open_t='ata'), 512) as d:
                    id_info = d.identify_raw
            except:
                continue
            # Get the information of device
            invalid_symbol = b'\x00'.decode()
            sn = bytearray2string(translocate_bytearray(id_info[20:40])).strip().strip(invalid_symbol)
            fw = bytearray2string(translocate_bytearray(id_info[46:54]))
            mn = bytearray2string(translocate_bytearray(id_info[54:94])).strip().strip(invalid_symbol)
            logical_sector_num = int(binascii.hexlify(translocate_bytearray(id_info[200:208], 2)),16)
            if id_info[213] & 0xC0 == 0x40: # word 106 valid
                if id_info[213] & 0x10:
                    logical_sector_size = int(binascii.hexlify(translocate_bytearray(id_info[234:238], 2)),16) * 2
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
            else:
                disk_format = "Unknown"
                cap = "Unknown"
            #
            if options.output_format == "normal":
                print (print_format % (dev_path, sn, mn, cap, disk_format, fw))
    else:
        raise RuntimeError("OS %s Not support command list" % os_type)

def check_power_mode():
    usage="usage: %prog check-PowerMode <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("", "--show_status", dest="show_status", action="store_true", default=False,
        help="Show status return value")
    parser_update(parser, add_debug=True)

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, admin_check=True)
        ##
        _sending_cmd_info(dev, "check power mode")
        with SATA(init_device(dev, open_t='ata'), 512) as d:
            cmd = d.check_power_mode()
            ##
            if options.debug:
                _debug_info_print(cmd)
            ##
            return_descriptor = cmd.ata_status_return_descriptor
            if options.show_status:
                _print_return_status(return_descriptor)
            sector_count = return_descriptor.get("sector_count")
            if return_descriptor.get("extend"):
                sector_count += (return_descriptor.get("sector_count_rsvd") << 8)
            ###
            count = sector_count&0xFF
            print ("Device is in the:")
            if count == 0xFF:
                print ("PM0:Active state or PM1:Idle state.")
            elif count == 0x00:
                print ("PM2:Standby state (see 4.15.4) and the EPC feature set (see 4.9) is not enabled;")
                print ("or")
                print ("PM2:Standby state, the EPC feature set is enabled, and the device is in the Standby_z power condition.")
            elif count == 0x01:
                print ("PM2:Standby state, the EPC feature set is enabled, and the device is in the Standby_y power condition.")
            elif count == 0x80:
                print ("PM1:Idle state (see 4.15.4) and EPC feature set is not supported.")
            elif count == 0x81:
                print ("PM1:Idle state, the EPC feature set is enable, and the device is in the Idle_a power condition.")
            elif count == 0x82:
                print ("PM1:Idle state, the EPC feature set is enabled, and the device is in the Idle_b power condition.")
            elif count == 0x83:
                print ("PM1:Idle state, the EPC feature set is enabled, and the device is in the Idle_c power condition.")
            else:
                print ("Other power state: state Reserved or Obsoleted.")
    else:
        parser.print_help()

def read_dma_ext():
    usage="usage: %prog read <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-s", "--start-block", type="int", dest="slba", action="store", default=0,
        help="Logical Block Address to write to. Default 0")
    parser.add_option("-c", "--block-count", type="int", dest="nlb", action="store", default=1,
        help="Transfer Length in blocks. Default 1")
    parser.add_option("-b", "--block-size", type="int", dest="bs", action="store", default=0,
        help="To fix the block size of the device. Default 0")
    parser.add_option("", "--show_status", dest="show_status", action="store_true", default=False,
        help="Show status return value")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, admin_check=True)
        ##
        _sending_cmd_info(dev, "read DMA EXT")
        with SATA(init_device(dev, open_t='ata'), blocksize=options.bs) as d:
            cmd = d.read_DMAEXT16(options.slba, options.nlb)
            cmd.check_return_status()
            if options.show_status:
                _print_return_status(cmd.ata_status_return_descriptor)
            print ('')
            print ('Data Out:')
            print ('len: %d' % (len(cmd.datain)))
            print (cmd.datain)
    else:
        parser.print_help()

def read_verify_sector():
    usage="usage: %prog read-verify-sector <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-s", "--start-block", type="int", dest="slba", action="store", default=0,
        help="Logical Block Address to write to. Default 0")
    parser.add_option("-c", "--block-count", type="int", dest="nlb", action="store", default=1,
        help="Transfer Length in blocks. Default 1")
    parser.add_option("-b", "--block-size", type="int", dest="bs", action="store", default=0,
        help="To fix the block size of the device. Default 0")
    parser.add_option("", "--show_status", dest="show_status", action="store_true", default=False,
        help="Show status return value")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, admin_check=True)
        ##
        _sending_cmd_info(dev, "read verify sector(s)")
        with SATA(init_device(dev, open_t='ata'), blocksize=options.bs) as d:
            cmd = d.read_verify_sector(options.slba, options.nlb)
            cmd.check_return_status(success_hint=True)
            if options.show_status:
                _print_return_status(cmd.ata_status_return_descriptor)
            print ('')
    else:
        parser.print_help()

def write_dma_ext():
    usage="usage: %prog write <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-s", "--start-block", type="int", dest="slba", action="store", default=0,
        help="Logical Block Address to write to. Default 0")
    parser.add_option("-c", "--block-count", type="int", dest="nlb", action="store", default=1,
        help="Transfer Length in blocks. Default 1")
    parser.add_option("-d", "--data", type="str", dest="data", action="store", default='',
        help="String containing the block to write")
    parser.add_option("-f", "--data-file", type="str", dest="dfile", action="store", default='',
        help="File(Read first) containing the block to write")
    parser.add_option("-b", "--block-size", type="int", dest="bs", action="store", default=0,
        help="To fix the block size of the device. Default 0")
    parser.add_option("", "--show_status", dest="show_status", action="store_true", default=False,
        help="Show status return value")
    parser_update(parser, add_force=True)

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, danger_check=True, admin_check=True)
        ##
        _sending_cmd_info(dev, "write DMA EXT")
        with SATA(init_device(dev, open_t='ata'), blocksize=options.bs) as d:
            # check data
            if options.data:
                options.data = bytearray(options.data, 'utf-8')
            elif options.dfile:
                if os.path.isfile(options.dfile):
                    with open(options.dfile, 'rb') as f:
                        data = f.read()
                    options.data = bytearray(data)
            if options.data:
                data_l = len(options.data)
                data_size = options.nlb * d.blocksize
                if data_size < data_l:
                    options.data = options.data[0:data_size]
                elif data_size > data_l:
                    options.data = options.data + bytearray(data_size-data_l)
                else:
                    pass
            else:
                parser.error("Lack of input data")
            # issue command
            cmd = d.write_DMAEXT16(options.slba, options.nlb, options.data)
            cmd.check_return_status()
            if options.show_status:
                _print_return_status(cmd.ata_status_return_descriptor)
    else:
        parser.print_help()

def write_log():
    usage="usage: %prog write-log <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-l", "--log-address", type="int", dest="log_address", action="store", default=0,
        help="Log address to read")
    parser.add_option("-p", "--page-number", type="int", dest="page_number", action="store", default=0,
        help="Page number offset in this log address")
    parser.add_option("-c", "--count", type="int", dest="count", action="store", default=1,
        help="Read log data transfer length, 512 Bytes per count")
    parser.add_option("-d", "--data", type="str", dest="data", action="store", default='',
        help="String containing the block to write")
    parser.add_option("-f", "--data-file", type="str", dest="dfile", action="store", default='',
        help="File(Read first) containing the block to write")
    parser.add_option("-b", "--block-size", type="int", dest="bs", action="store", default=0,
        help="To fix the block size of the device. Default 0")
    parser.add_option("", "--show_status", dest="show_status", action="store_true", default=False,
        help="Show status return value")
    parser_update(parser, add_force=True)

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, danger_check=True, admin_check=True)
        _sending_cmd_info(dev, "write log")
        with SATA(init_device(dev, open_t='ata'), blocksize=options.bs) as d:
            ## check data
            data = None
            if options.data:
                data = bytearray(options.data, 'utf-8')
            elif options.dfile:
                if os.path.isfile(options.dfile):
                    with open(options.dfile, 'rb') as f:
                        data = f.read()
                    data = bytearray(data)
            if data:
                data_l = len(data)
                data_size = options.nlb * d.blocksize
                if data_size < data_l:
                    data = data[0:data_size]
                elif data_size > data_l:
                    data = data + bytearray(data_size-data_l)
                else:
                    pass
            ##
            cmd = d.write_log(options.count, options.log_address, options.page_number, data)
            cmd.check_return_status()
            if options.show_status:
                _print_return_status(cmd.ata_status_return_descriptor)
    else:
        parser.print_help()

def flush():
    usage="usage: %prog flush <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("", "--show_status", dest="show_status", action="store_true", default=False,
        help="Show status return value")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, admin_check=True)
        ##
        _sending_cmd_info(dev, "flush")
        with SATA(init_device(dev, open_t='ata')) as d:
            cmd = d.flush()
            cmd.check_return_status()
            if options.show_status:
                _print_return_status(cmd.ata_status_return_descriptor)
    else:
        parser.print_help()

def accessible_max_address():
    usage="usage: %prog accessible-MaxAddress <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("", "--show_status", dest="show_status", action="store_true", default=False,
        help="Show status return value")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, admin_check=True)
        ##
        _sending_cmd_info(dev, "accessible max address")
        with SATA(init_device(dev, open_t='ata')) as d:
            cmd = d.getAccessibleMaxAddress()
            cmd.check_return_status()
            if options.show_status:
                _print_return_status(cmd.ata_status_return_descriptor)
        ##
        return_descriptor = cmd.ata_status_return_descriptor
        if return_descriptor:
            LBA_ordinal = bytearray(6)
            #
            LBA_ordinal[0] = return_descriptor.get("lba_low")
            LBA_ordinal[1] = return_descriptor.get("lba_mid")
            LBA_ordinal[2] = return_descriptor.get("lba_high")
            if return_descriptor.get("extend"):
                LBA_ordinal[3] = return_descriptor.get("lba_low_rsvd")  
                LBA_ordinal[4] = return_descriptor.get("lba_mid_rsvd")   
                LBA_ordinal[5] = return_descriptor.get("lba_high_rsvd")
            ##
            LBA_max = int.from_bytes(LBA_ordinal, byteorder='little', signed=False)
            print ("Max LBA address: %s" % LBA_max)
            print ("That will present total LBAs: %s" % (LBA_max+1))
            print ('')
        else:
            print ("No valid data")
    else:
        parser.print_help()

def identify():
    usage="usage: %prog identify <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("", "--show_status", dest="show_status", action="store_true", default=False,
        help="Show status return value")
    parser.add_option("", "--ignore_error", dest="ignore_error", action="store_true", default=False,
        help="Ignore error that was checked out and continue to show the result")
    parser_update(parser, add_output=["normal", "hex", "raw", "json"])

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, admin_check=True)
        ##
        if options.output_format != 'json':
            _sending_cmd_info(dev, "identify")
        with SATA(init_device(dev, open_t='ata')) as d:
            cmd = d.identify()
        cmd.check_return_status(raise_if_fail=not options.ignore_error)
        format_print_identify(cmd, print_type=options.output_format, show_status=options.show_status)
    else:
        parser.print_help()

def self_test():
    usage="usage: %prog self-test <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-t", "--test", type="choice", dest="self_test", action="store", choices=["short", "long"], default='short',
        help="Start a self test, short|long")
    parser.add_option("", "--show_status", dest="show_status", action="store_true", default=False,
        help="Show status return value")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, admin_check=True)
        ##
        with SATA(init_device(dev, open_t='ata')) as d:
            if options.self_test == "short":
                _sending_cmd_info(dev, "selftest command - short test")
                cmd = d.smart_read_data()
                cmd.check_return_status()
                data = cmd.result
                print ('ShortSelftestPollingTimeInMin: %s min' % data['ShortSelftestPollingTimeInMin'][0])
                print ('')
                cmd2 = d.smart_exe_offline_imm(0x01)
                cmd2.check_return_status()
            else:
                _sending_cmd_info(dev, "selftest command - long test")
                cmd = d.smart_read_data()
                cmd.check_return_status()
                data = cmd.result
                print ('longSelftestPollingTimeInMin: %s min' % data['longSelftestPollingTimeInMin'][0])
                print ('')
                cmd2 = d.smart_exe_offline_imm(0x02)
                cmd2.check_return_status()
            if options.show_status:
                _print_return_status(cmd2.ata_status_return_descriptor)
    else:
        parser.print_help()

def read_log():
    usage="usage: %prog read-log <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-l", "--log-address", type="int", dest="log_address", action="store", default=0,
        help="Log address to read")
    parser.add_option("-p", "--page-number", type="int", dest="page_number", action="store", default=0,
        help="Page number offset in this log address")
    parser.add_option("-c", "--count", type="int", dest="count", action="store", default=1,
        help="Read log data transfer length, 512 Bytes per count")
    parser.add_option("-f", "--feature", type="int", dest="feature", action="store", default=0,
        help="Specify a feature in read log")
    parser.add_option("", "--show_status", dest="show_status", action="store_true", default=False,
        help="Show status return value")
    parser_update(parser, add_output=["normal", "hex", "raw"])

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, admin_check=True)
        ##
        _sending_cmd_info(dev, "read-log")
        with SATA(init_device(dev, open_t='ata')) as d:
            cmd = d.read_log(options.log_address, options.count, page_number=options.page_number, feature=options.feature)
        cmd.check_return_status()
        if options.show_status:
            print ("CDB:", cmd.cdb)
            _print_return_status(cmd.ata_status_return_descriptor)
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

def set_feature():
    usage="usage: %prog set-feature <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-f", "--feature", type="int", dest="feature", action="store", default=0,
        help="Set feature subcommand field")
    parser.add_option("-c", "--count", type="int", dest="count", action="store", default=0,
        help="Subcommand specific in count field")
    parser.add_option("-l", "--lba", type="int", dest="lba", action="store", default=0,
        help="Subcommand specific in LBA field")
    parser.add_option("", "--guideline", dest="guideline", action="store_true", default=False,
        help="The guideline for set feature command")
    parser.add_option("", "--show_status", dest="show_status", action="store_true", default=False,
        help="Show status return value")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        if options.guideline:
            format_print_set_feature_guide()
            return
        ##
        script_check(options, admin_check=True)
        ## check device
        dev = sys.argv[2]
        ##
        _sending_cmd_info(dev, "set-feature")
        with SATA(init_device(dev, open_t='ata')) as d:
            cmd = d.set_feature(options.feature, options.count, options.lba)
        cmd.check_return_status()
        ##
        if options.show_status:
            print_ata_cmd_status(cmd)
    else:
        parser.print_help()

def smart_read_log():
    usage="usage: %prog smart-read-log <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-l", "--log-address", type="int", dest="log_address", action="store", default=0,
        help="Log address to read")
    parser.add_option("-c", "--count", type="int", dest="count", action="store", default=1,
        help="Read log data transfer length, 512 Bytes per count")
    parser.add_option("", "--show_status", dest="show_status", action="store_true", default=False,
        help="Show status return value")
    parser_update(parser, add_output=["normal", "hex", "raw"])

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, admin_check=True)
        ##
        _sending_cmd_info(dev, "smart-read-log")
        with SATA(init_device(dev, open_t='ata')) as d:
            cmd = d.smart_read_log(options.log_address, options.count)
        cmd.check_return_status()
        if options.show_status:
            print ("CDB:", bytes(cmd.cdb))
            print ('')
            _print_return_status(cmd.ata_status_return_descriptor)
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

def smart():
    usage="usage: %prog smart <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("", "--show_status", dest="show_status", action="store_true", default=False,
        help="Show status return value")
    parser_update(parser, add_output=["normal", "hex", "raw", "json"], add_debug=True)

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, admin_check=True)
        ##
        from pydiskcmdcli.sata_spec import SMART_KEY
        #
        if options.output_format != 'json':
            _sending_cmd_info(dev, "smart")
        with SATA(init_device(dev, open_t='ata')) as d:
            cmd_read_data = d.smart_read_data(SMART_KEY)
            cmd_read_data.check_return_status()
            ##
            if options.debug:
                _debug_info_print(cmd_read_data)
            cmd_thread = d.smart_read_thresh()
            cmd_thread.check_return_status()
            ##
            if options.debug:
                _debug_info_print(cmd_thread)
        ##
        format_print_smart(cmd_read_data, cmd_thread, print_type=options.output_format, show_status=options.show_status)
    else:
        parser.print_help()

def smart_return_status():
    usage="usage: %prog smart-return-status <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("", "--show_status", dest="show_status", action="store_true", default=False,
        help="Show status return value")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, admin_check=True)
        #
        _sending_cmd_info(dev, "smart-return-status")
        with SATA(init_device(dev, open_t='ata')) as d:
            cmd = d.smart_return_status()
        cmd.check_return_status()
        ##
        if not cmd.ata_status_return_descriptor["extend"]:
            lba = (cmd.ata_status_return_descriptor["lba_high"] << 16) + (cmd.ata_status_return_descriptor["lba_mid"] << 8) + (cmd.ata_status_return_descriptor["lba_low"])
            status = lba >> 8
            if status == 0xC24F:
                print ("The subcommand specified a captive self-test that has completed without error")
            elif status == 0x2CF4:
                print ("The device has detected a threshold exceeded condition")
            else:
                print ("Got Undefined Values %#X" % status)
        else:
            print (cmd.ata_status_return_descriptor)
    else:
        parser.print_help()


def standby_imm():
    usage="usage: %prog standby <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("", "--show_status", dest="show_status", action="store_true", default=False,
        help="Show status return value")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, admin_check=True)
        ##
        _sending_cmd_info(dev, "standby immediate")
        with SATA(init_device(dev, open_t='ata')) as d:
            cmd = d.standby_imm()
        cmd.check_return_status()
        if options.show_status:
            _print_return_status(cmd.ata_status_return_descriptor)
    else:
        parser.print_help()

def trim():
    usage="usage: %prog trim <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-r", "--block_range", type="str", dest="block_range", action="store", default='',
        help="Block range that need trim(format is startLBA:LBAlength,startLBA:LBAlength,...)")
    parser.add_option("", "--show_status", dest="show_status", action="store_true", default=False,
        help="Show status return value")
    parser_update(parser, add_force=True)

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, danger_check=True, admin_check=True, delay_act=True)
        ## check LBA format
        LBA_list = options.block_range.split(',')
        if 0 < len(LBA_list) < 65:
            lba_description = []
            for lba_des in LBA_list:
                lba_des_list = lba_des.split(':')
                if len(lba_des_list) != 2:
                    parser.error("lba description Format Error!")
                lba_des_tuple = (int(lba_des_list[0]), int(lba_des_list[1]))
                lba_description.append(lba_des_tuple)
        else:
            parser.error("lba description Format Error!")
        ##
        print ("Note: If you want trim command works, lba_description need 4k aligned!")
        print ('')
        _sending_cmd_info(dev, "data set management(known as trim)")
        with SATA(init_device(dev, open_t='ata')) as d:
            cmd = d.trim(lba_description)
        cmd.check_return_status()
        if options.show_status:
            _print_return_status(cmd.ata_status_return_descriptor)
    else:
        parser.print_help()

def download_fw():
    usage="usage: %prog download-fw <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-f", "--file", dest="fw_file", action="store", default='',
        help="The firmware file path.")
    parser.add_option("-c", "--code", type="choice", dest="code", action="store", choices=[0x03, 0x07, 0x0E, 0x0F], default=3,
        help="The subcommand code to use, default 3")
    parser.add_option("-x", "--xfer", type=int, dest="xfer", action="store", default=0x200,
        help="Transfer chunksize.")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, admin_check=True)
        if not os.path.isfile(options.fw_file):
            parser.error("Firmware file Not Exist.")
        ##
        _sending_cmd_info(dev, "download microcode")
        with SATA(init_device(dev, open_t='ata')) as d:
            rc = d.download_fw(options.fw_file, transfer_size=options.xfer, feature=options.code)
            if rc == 0:
                print ("Success to download firmware.")
            else:
                print ("Failed to download firmware. Return Code: %s" % rc)
    else:
        parser.print_help()

def trusted_receive():
    usage='''usage: %prog trusted-receive <device> [OPTIONS]

Note: This will be a limitted function, for only 255 blocks can be transferred,
      while blocks will be 1 byte or 512 bytes
Important: To use this command, libata.allow_tpm must be set to 1 in linux.
    '''
    parser = optparse.OptionParser(usage)
    parser.add_option("-p", "--protocol", type="int", dest="protocol", action="store", default=0,
        help="Specifies which security protocol to use")
    parser.add_option("-s", "--sp", type="int", dest="sp", action="store", default=0,
        help="Specific field in security protocol")
    parser.add_option("-i", "--INC_512", type="int", dest="INC_512", action="store", default=1,
        help="Set transfer size block size in step of 512 bytes")
    parser.add_option("-l", "--alloclen", type="int", dest="alloclen", action="store", default=1,
        help="Set transfer size block number")
    parser_update(parser, add_output=["hex", "raw"])

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, admin_check=True)
        ##
        _sending_cmd_info(dev, "trusted receive")
        with SATA(init_device(dev, open_t='ata')) as d:
            try:
                cmd = d.trusted_receive(options.protocol, options.alloclen, options.sp, INC_512=options.INC_512)
                cmd.check_return_status()
            except ExecuteCmdErr as e:
                print (e)
                if 'Check Condition: Illegal Request(0x05) ASC+Q:Invalid Field In CDB(0x2400)' in str(e):
                    print ("Important: You may need set libata.allow_tpm=1 when use this function.")
            else:
                if options.output_format == "hex":
                    format_dump_bytes(cmd.datain)
                else:
                    print (bytes(cmd.datain))
    else:
        parser.print_help()

def sanitize():
    usage="usage: %prog sanitize <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-f", "--feature", type="int", dest="feature", action="store", default=0,
        help="Sanitize Command field of Feature")
    ## valid in SANITIZE STATUS EXT
    parser.add_option("", "--clear-failed", dest="clear_failed", action="store_false", default=False,
        help="Clear sanitize failed, valid in SANITIZE STATUS EXT")
    ## valid in CRYPTO SCRAMBLE EXT,  BLOCK ERASE EXT
    parser.add_option("", "--failure-mode", dest="failure_mode", action="store_false", default=False,
        help="Failuer mode(default 0), valid in CRYPTO SCRAMBLE EXT, BLOCK ERASE EXT, OVERWRITE EXT")
    parser.add_option("", "--zoned-no-reset", dest="zoned_no_reset", action="store_false", default=False,
        help="Zoned no reset(default 0), valid in CRYPTO SCRAMBLE EXT, BLOCK ERASE EXT, OVERWRITE EXT")
    ## valid in OVERWRITE EXT
    parser.add_option("", "--invert", dest="invert", action="store_false", default=False,
        help="Invert pattern between overwrite passes(default 0), valid in OVERWRITE EXT")
    parser.add_option("", "--definitive", dest="definitive", action="store_false", default=False,
        help="Definitive ending pattern(default 0), valid in OVERWRITE EXT")
    parser.add_option("-n", "--owpass", type="int", dest="owpass", action="store", default=1,
        help="Overwrite pass count(default 1), valid in OVERWRITE EXT")
    parser.add_option("-p", "--ovrpat", type="int", dest="ovrpat", action="store", default=0,
        help="Overwrite pattern(default 0) in DWORD, valid in OVERWRITE EXT")
    parser_update(parser, add_force=True)

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, danger_check=True if options.feature in (0x0011, 0x0012, 0x0014) else False, admin_check=True)
        #
        count = 0
        if options.feature == 0x0012:
            lba = 0x4572 + (0x426B << 16)
            if options.failure_mode:
                count += (1 << 4)
            if options.zoned_no_reset:
                count += (1 << 15)
        elif options.feature == 0x0011:
            lba = 0x7970 + (0x4372 << 16)
            if options.failure_mode:
                count += (1 << 4)
            if options.zoned_no_reset:
                count += (1 << 15)
        elif options.feature == 0x0014 and options.ovrpat:
            lba = options.ovrpat + (0x4F57 << 32)
            if options.owpass < 16:
                count += options.owpass
            if options.failure_mode:
                count += (1 << 4)
            if options.definitive:
                count += (1 << 6)
            if options.invert:
                count += (1 << 7)
            if options.zoned_no_reset:
                count += (1 << 15)
        elif options.feature == 0x0040:
            lba = 0x7469 + (0x416E << 16)
            count = 0
        elif options.feature == 0x0020:
            lba = 0x4C6B + (0x4672 << 16)
            count = 0
        elif options.feature == 0:
            lba = 0
            count = 1 if options.clear_failed else 0
        else:
            raise RuntimeError("feature(%s) invalid" % options.feature)
        ##
        _sending_cmd_info(dev, "sanitize")
        with SATA(init_device(dev, open_t='ata')) as d:
            cmd = d.sanitize(options.feature, count, lba)
        cmd.check_return_status()
        return_descriptor = cmd.ata_status_return_descriptor
        if return_descriptor:
            print ("Command Error Bit: ", return_descriptor["status"] & 0x01)
            if (return_descriptor["status"] & 0x01): # error output
                if return_descriptor["lba_low"] == 0:
                    print ("Reason not reported or sanitize device command failed")
                elif return_descriptor["lba_low"] == 1:
                    print ("Sanitize Command Unsuccessful – The sanitize operation completed with physical sectors that are available to be allocated for user data that were not successfully sanitized.")
                elif return_descriptor["lba_low"] == 2:
                    print ("Invalid or unsupported value in the Sanitize Device FEATURE field")
                elif return_descriptor["lba_low"] == 3:
                    print ("Device is in the SD1: Sanitize Frozen state")
                elif return_descriptor["lba_low"] == 4:
                    print ("SANITIZE FREEZE LOCK command failed as a result of the Sanitize Antifreeze Lock value being set to one")
                else:
                    print ("Unknown reason: %d" % return_descriptor["lba_low"])
            else:    # normal output
                print ("Process: %s%%" % round(100 * (return_descriptor["lba_low"] + (return_descriptor["lba_mid"] << 8)) / 65535, 1))
                print ("SANITIZE ANTIFREEZE is %s" % ((return_descriptor["sector_count_rsvd"] & 0x10) > 0))
                print ("Sanitize Frozen state: %s" % ((return_descriptor["sector_count_rsvd"] & 0x20) > 0))
                print ("Sanitize in progress state: %s" % ((return_descriptor["sector_count_rsvd"] & 0x40) > 0))
                print ("Sanitize completed witout error: %s" % ((return_descriptor["sector_count_rsvd"] & 0x80) > 0))
        else:
            print ("No valid data to parse")
    else:
        parser.print_help()

def write_uncorrectable():
    usage="usage: %prog write-uncorrectable <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-f", "--feature", type=int, dest="feature", action="store", default=0xAA,
        help="Uncorrectable options to set. 0x55h: Create a pseudo-uncorrectable error with logging,\
0x5Ah: Vendor specific, \
0xA5h: Vendor specific, \
0xAAh: Create a flagged error without logging. Default is 0xAA")
    parser.add_option("-c", "--count", type=int, dest="count", action="store", default=8,
        help="The number of logical sectors to be marked. A value of 0000h indicates that 65 536 logical sectors, default is 8")
    parser.add_option("-l", "--lba", type=int, dest="lba", action="store", default=0,
        help="LBA of first logical sector to be marked.")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        #
        if options.feature not in (0x55, 0x5A, 0xA5, 0xAA):
            parser.error("Feature should be 0x55|0x5A|0xA5|0xAA")
        ##
        script_check(options, admin_check=True)
        ##
        _sending_cmd_info(dev, "write-uncorrectable")
        with SATA(init_device(dev, open_t='ata')) as d:
            cmd = d.write_uncorrectable_ext(options.feature, options.count, options.lba)
        cmd.check_return_status(success_hint=True, )
    else:
        parser.print_help()

#################################################
# Bellow is cli management interface 
#################################################
def cli_info():
    from pydiskcmdlib import version as lib_version
    from pydiskcmdlib.pysata import version as ata_version
    version()
    print ('')
    print ('pydiskcmdlib version: %s' % lib_version)
    print ('  - ata code version: %s' % ata_version)

def cli_autocmd():
    from pydiskcmdcli.system.bash_completion import enable_cmd_completion
    enable_cmd_completion()
#########
commands_dict = {"list": _list, 
                 "check-PowerMode": check_power_mode,
                 "accessible-MaxAddress": accessible_max_address,
                 "identify": identify, 
                 "self-test": self_test, 
                 "set-feature": set_feature,
                 "trusted-receive": trusted_receive,
                 "smart": smart, 
                 "smart-return-status": smart_return_status, 
                 "standby": standby_imm, 
                 "read-log": read_log,
                 "smart-read-log": smart_read_log,
                 "sanitize": sanitize,
                 "read": read_dma_ext,
                 "read-verify-sector": read_verify_sector,
                 "write": write_dma_ext,
                 "write-uncorrectable": write_uncorrectable,
                 "write-log": write_log,
                 "flush": flush,
                 "trim": trim,
                 "download-fw": download_fw,
                 "version": version,
                 "help": print_help,
                 "cli-info": cli_info,
                 "cli-autocmd": cli_autocmd,
                 }
commands_dict.update(ata_plugins)

def pysata():
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
                from pydiskcmdlib.exceptions import BaseError as lib_BaseError
                from pydiskcmdcli.exceptions import BaseError as cli_BaseError
                if not isinstance(e, (lib_BaseError, cli_BaseError)):
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
