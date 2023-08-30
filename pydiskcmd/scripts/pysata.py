# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import sys,os
import optparse
import binascii
from pydiskcmd.pysata.sata import SATA
from pydiskcmd.utils.ata_format_print import (
    _print_return_status,
    print_ata_cmd_status,
    read_log_format_print_set,
    smart_read_log_format_print_set,
    read_log_decode_set,
    format_print_identify,
    format_print_smart,
    format_print_set_feature_guide,
    )
from pydiskcmd.utils import init_device
from pydiskcmd.utils.format_print import format_dump_bytes,human_read_capacity
from pydiskcmd.system.os_tool import check_device_exist

Version = '0.2.0'

def version():
    print ("pysata version %s" % Version)
    return 0

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
        print ("  list                        List all SCSI devices on machine")
        print ("  check-PowerMode             Check Disk Power Mode")
        print ("  accessible-MaxAddress       Send Accessible Max Address command")
        print ("  identify                    Get identify information")
        print ("  self-test                   Start a disk self test")
        print ("  set-feature                 Send set feature to device")
        print ("  smart                       Get smart information")
        print ("  read-log                    Get the GPL Log and show it")
        print ("  smart-read-log              Get the smart Log and show it")
        print ("  standby                     Send standby command")
        print ("  read                        Send a read command to disk")
        print ("  write                       Send a write command to disk")
        print ("  flush                       Send a flush command to disk")
        print ("  trim                        Send a trim command to disk")
        print ("  download_fw                 Download firmware to target disk")
        print ("  version                     Shows the program version")
        print ("  help                        Display this help")
        print ("")
        print ("See 'pysata help <command>' or 'pysata <command> --help' for more information on a sub-command")
    return 0

def _list():
    usage="usage: %prog list <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-o", "--output-format", type="choice", dest="output_format", action="store", choices=["normal",],default="normal",
        help="Output format: normal, default normal")

    (options, args) = parser.parse_args()
    ##
    print_format = "%-20s %-20s %-40s %-26s %-16s %-8s"
    print (print_format % ("Node", "SN", "Model", "Capacity", "Format(L/P)", "FW Rev"))
    print (print_format % ("-"*20, "-"*20, "-"*40, "-"*26, "-"*16, "-"*8))
    from pydiskcmd.pydiskhealthd.all_device import scan_device
    from pydiskcmd.utils.converter import bytearray2string,translocate_bytearray
    for dev_context in scan_device(debug=False):
        ## check ATA device
        if dev_context.device_type == "ata":
            sn = bytearray2string(translocate_bytearray(dev_context.id_info[20:40])).strip()
            fw = bytearray2string(translocate_bytearray(dev_context.id_info[46:54]))
            mn = bytearray2string(translocate_bytearray(dev_context.id_info[54:94])).strip()
            logical_sector_num = int(binascii.hexlify(translocate_bytearray(dev_context.id_info[200:208], 2)),16)
            if dev_context.id_info[213] & 0xC0 == 0x40: # word 106 valid
                if dev_context.id_info[213] & 0x10:
                    logical_sector_size = int(binascii.hexlify(translocate_bytearray(dev_context.id_info[234:238], 2)),16) * 2
                else:
                    logical_sector_size = 512
                if dev_context.id_info[213] & 0x20:
                    relationship = 2 ** (dev_context.id_info[212] & 0x0F)
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
                print (print_format % (dev_context.dev_path, sn, mn, cap, disk_format, fw))

def check_power_mode():
    usage="usage: %prog check-PowerMode <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("", "--show_status", dest="show_status", action="store_true", default=False,
        help="Show status return value")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        if not check_device_exist(dev):
            raise ("Device %s not exist!" % dev)
        ##
        with SATA(init_device(dev, open_t='ata'), 512) as d:
            print ('issuing check power mode command')
            print ("%s:" % d.device._file_name)
            cmd = d.check_power_mode()
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
    parser.add_option("-b", "--block-size", type="int", dest="bs", action="store", default=512,
        help="To fix the block size of the device. Default 512")
    parser.add_option("", "--show_status", dest="show_status", action="store_true", default=False,
        help="Show status return value")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        if not check_device_exist(dev):
            raise RuntimeError("Device %s not exist!" % dev)
        ##
        print ('issuing read DMA EXT command.')
        with SATA(init_device(dev, open_t='ata'), 512) as d:
            print ("%s:" % d.device._file_name)
            cmd = d.read_DMAEXT16(options.slba, options.nlb)
            return_descriptor = cmd.ata_status_return_descriptor
            if options.show_status:
                _print_return_status(return_descriptor)
            print ('')
            print ('status error bit: ', return_descriptor.get("status") & 0x01)
            print ('')
            print ('Data Out:')
            print ('len: %d' % (len(cmd.datain)))
            print (cmd.datain)
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
    parser.add_option("-b", "--block-size", type="int", dest="bs", action="store", default=512,
        help="To fix the block size of the device. Default 512")
    parser.add_option("", "--show_status", dest="show_status", action="store_true", default=False,
        help="Show status return value")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        if not check_device_exist(dev):
            raise RuntimeError("Device not exist!")
        ## check data
        if options.data:
            options.data = bytearray(options.data, 'utf-8')
        elif options.dfile:
            if os.path.isfile(options.dfile):
                with open(options.dfile, 'rb') as f:
                    data = f.read()
                options.data = bytearray(data)
        if options.data:
            data_l = len(options.data)
            data_size = options.nlb * options.bs
            if data_size < data_l:
                options.data = options.data[0:data_size]
            elif data_size > data_l:
                options.data = options.data + bytearray(data_size-data_l)
            else:
                pass
        else:
            parser.error("Lack of input data")
            return
        ##
        with SATA(init_device(dev, open_t='ata'), 512) as d:
            print ('issuing write DMA EXT command')
            print ("%s:" % d.device._file_name)
            print ('')
            cmd = d.write_DMAEXT16(options.slba, options.nlb, options.data)
            return_descriptor = cmd.ata_status_return_descriptor
            if options.show_status:
                _print_return_status(return_descriptor)
            print ('status error bit: ', return_descriptor.get("status") & 0x01)
            print ('')
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
        if not check_device_exist(dev):
            raise RuntimeError("Device not exist!")
        ##
        with SATA(init_device(dev, open_t='ata'), 512) as d:
            print ('issuing flush command')
            print ("%s:" % d.device._file_name)
            cmd = d.flush()
            return_descriptor = cmd.ata_status_return_descriptor
            if options.show_status:
                _print_return_status(return_descriptor)
            print ('')
            print ('status err_bit:', return_descriptor.get("status") & 0x01)
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
        if not check_device_exist(dev):
            raise RuntimeError("Device not exist!")
        ##
        with SATA(init_device(dev, open_t='ata'), 512) as d:
            print ('issuing accessible max address command')
            print ("%s:" % d.device._file_name)
            cmd = d.getAccessibleMaxAddress()
            return_descriptor = cmd.ata_status_return_descriptor
            if options.show_status:
                _print_return_status(return_descriptor)
            print ('')
            print ('status err_bit:', return_descriptor.get("status") & 0x01)
            print ('')
        ##
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
        parser.print_help()

def identify():
    usage="usage: %prog identify <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-o", "--output-format", type="choice", dest="output_format", action="store", choices=["normal", "hex", "raw", "json"],default="normal",
        help="Output format: normal|hex|raw|json, default normal")
    parser.add_option("", "--show_status", dest="show_status", action="store_true", default=False,
        help="Show status return value")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        if not check_device_exist(dev):
            raise RuntimeError("Device not exist!")
        ##
        if options.output_format != 'json':
            print ('issuing identify command')
            print ('Device: %s' % dev)
            print ('')
        with SATA(init_device(dev, open_t='ata'), 512) as d:
            cmd = d.identify()
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
        if not check_device_exist(dev):
            raise RuntimeError("Device not exist!")
        ##
        with SATA(init_device(dev, open_t='ata'), 512) as d:
            if options.self_test == "short":
                print ('issuing selftest command - short test')
                print ("%s:" % d.device._file_name)
                print ('')
                cmd = d.smart_read_data()
                data = cmd.result
                print ('ShortSelftestPollingTimeInMin: %s min' % data['ShortSelftestPollingTimeInMin'][0])
                print ('')
                cmd2 = d.smart_exe_offline_imm(0x01)
                return_descriptor = cmd2.ata_status_return_descriptor
                if options.show_status:
                    _print_return_status(return_descriptor)
                print ('status error bit:', return_descriptor.get("status") & 0x01)
                print ('')
            else:
                print ('issuing selftest command - long test')
                print ("%s:" % d.device._file_name)
                print ('')
                cmd = d.smart_read_data()
                data = cmd.result
                print ('longSelftestPollingTimeInMin: %s min' % data['longSelftestPollingTimeInMin'][0])
                print ('')
                cmd2 = d.smart_exe_offline_imm(0x02)
                return_descriptor = cmd2.ata_status_return_descriptor
                if options.show_status:
                    _print_return_status(return_descriptor)
                print ('status error bit:', return_descriptor.get("status") & 0x01)
                print ('')
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
    parser.add_option("-o", "--output-format", type="choice", dest="output_format", action="store", choices=["normal", "binary", "raw"],default="normal",
        help="Output format: normal|binary|raw, default normal")
    parser.add_option("", "--show_status", dest="show_status", action="store_true", default=False,
        help="Show status return value")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        if not check_device_exist(dev):
            raise RuntimeError("Device not exist!")
        ##
        with SATA(init_device(dev, open_t='ata'), 512) as d:
            print ('issuing read-log command')
            print ("%s:" % d.device._file_name)
            print ('')
            cmd = d.read_log(options.log_address, options.count, page_number=options.page_number, feature=options.feature)
            return_descriptor = cmd.ata_status_return_descriptor
            if options.show_status:
                print ("CDB:", cmd.cdb)
                _print_return_status(return_descriptor)
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
            return 0
        ## check device
        dev = sys.argv[2]
        if not check_device_exist(dev):
            raise RuntimeError("Device not exist!")
        ##
        print ('issuing set-feature command')
        print ('Device: %s' % dev)
        print ('')
        with SATA(init_device(dev, open_t='ata'), 512) as d:
            cmd = d.set_feature(options.feature, options.count, options.lba)
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
    parser.add_option("-o", "--output-format", type="choice", dest="output_format", action="store", choices=["normal", "binary", "raw"],default="normal",
        help="Output format: normal|binary|raw, default normal")
    parser.add_option("", "--show_status", dest="show_status", action="store_true", default=False,
        help="Show status return value")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        if not check_device_exist(dev):
            raise RuntimeError("Device not exist!")
        ##
        with SATA(init_device(dev, open_t='ata'), 512) as d:
            print ('issuing smart-read-log command')
            print ("%s:" % d.device._file_name)
            print ('')
            cmd = d.smart_read_log(options.log_address, options.count)
            return_descriptor = cmd.ata_status_return_descriptor
            if options.show_status:
                print ("CDB:", bytes(cmd.cdb))
                print ('')
                _print_return_status(return_descriptor)
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
    parser.add_option("-o", "--output-format", type="choice", dest="output_format", action="store", choices=["normal", "hex", "raw", "json"],default="normal",
        help="Output format: normal|hex|raw|json, default normal")
    parser.add_option("", "--show_status", dest="show_status", action="store_true", default=False,
        help="Show status return value")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        if not check_device_exist(dev):
            raise RuntimeError("Device not exist!")
        ##
        from pydiskcmd.pysata.sata_spec import SMART_KEY
        #
        if options.output_format != 'json':
            print ('issuing smart command')
            print ('Device: %s' % dev)
            print ('')
        with SATA(init_device(dev, open_t='ata'), 512) as d:
            cmd_read_data = d.smart_read_data(SMART_KEY)
            cmd_thread = d.smart_read_thresh()
        ##
        format_print_smart(cmd_read_data, cmd_thread, print_type=options.output_format, show_status=options.show_status)
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
        if not check_device_exist(dev):
            raise RuntimeError("Device not exist!")
        ##
        with SATA(init_device(dev, open_t='ata'), 512) as d:
            print ('issuing standby immediate command')
            print ("%s:" % d.device._file_name)
            cmd = d.standby_imm()
            return_descriptor = cmd.ata_status_return_descriptor
            if options.show_status:
                _print_return_status(return_descriptor)
            print ('')
            print ('status err_bit:', return_descriptor.get("status") & 0x01)
    else:
        parser.print_help()

def trim():
    usage="usage: %prog trim <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-r", "--block_range", type="str", dest="block_range", action="store", default='',
        help="Block range that need trim(format is startLBA:LBAlength,startLBA:LBAlength,...)")
    parser.add_option("", "--show_status", dest="show_status", action="store_true", default=False,
        help="Show status return value")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        if not check_device_exist(dev):
            raise RuntimeError("Device not exist!")
        ## check LBA format
        LBA_list = options.block_range.split(',')
        if 0 < len(LBA_list) < 65:
            lba_description = []
            for lba_des in LBA_list:
                lba_des_list = lba_des.split(':')
                if len(lba_des_list) != 2:
                    parser.error("lba description Format Error!")
                    return
                lba_des_tuple = (int(lba_des_list[0]), int(lba_des_list[1]))
                lba_description.append(lba_des_tuple)
        else:
            parser.error("lba description Format Error!")
            return 
        ##
        print ("Note: If you want trim command works, lba_description need 4k aligned!")
        print ('')
        with SATA(init_device(dev, open_t='ata'), 512) as d:
            print ('issuing data set management(known as trim) command')
            print ("%s:" % d.device._file_name)
            cmd = d.trim(lba_description)
            return_descriptor = cmd.ata_status_return_descriptor
            if options.show_status:
                _print_return_status(return_descriptor)
            print ('')
            print ('status err_bit:', return_descriptor.get("status") & 0x01)
    else:
        parser.print_help()

def download_fw():
    usage="usage: %prog standby <device> [OPTIONS]"
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
        if not check_device_exist(dev):
            raise RuntimeError("Device not exist!")
        if not os.path.isfile(options.fw_file):
            parser.error("Firmware file Not Exist.")
        ##
        with SATA(init_device(dev, open_t='ata'), 512) as d:
            print ('issuing download microcode command')
            print ("%s:" % d.device._file_name)
            rc = d.download_fw(options.fw_file, transfer_size=options.xfer, feature=options.code)
            if rc == 0:
                print ("Success to download firmware.")
            else:
                print ("Failed to download firmware. Return Code: %s" % rc)
    else:
        parser.print_help()


commands_dict = {"list": _list, 
                 "check-PowerMode": check_power_mode,
                 "accessible-MaxAddress": accessible_max_address,
                 "identify": identify, 
                 "self-test": self_test, 
                 "set-feature": set_feature,
                 "smart": smart, 
                 "standby": standby_imm, 
                 "read-log": read_log,
                 "smart-read-log": smart_read_log,
                 "read": read_dma_ext,
                 "write": write_dma_ext,
                 "flush": flush,
                 "trim": trim,
                 "download_fw": download_fw,
                 "version": version,
                 "help": print_help}

def pysata():
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command in commands_dict:
            commands_dict[command]()
        else:
            print_help()
    else:
        print_help()
