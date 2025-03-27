# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import sys,os
import optparse
from pydiskcmdcli import os_type
from pydiskcmdlib.pyscsi.scsi import SCSI
from pydiskcmdcli.scsi_spec import LogSenseAttr,get_smart_simulate
from pydiskcmdlib.utils import init_device
from pydiskcmdcli.utils.format_print import format_dump_bytes,human_read_capacity,json_print
from pydiskcmdcli.plugins import scsi_plugins
from pyscsi.pyscsi.scsi_sense import SCSICheckCondition
from pyscsi.pyscsi import scsi_enum_inquiry as INQUIRY
from pyscsi.pyscsi.scsi_enum_getlbastatus import P_STATUS
from pydiskcmdcli import version as Version
from . import parser_update,script_check,func_debug_info
from pydiskcmdcli.exceptions import (
    CommandSequenceError,
    CommandNotSupport,
    NonpydiskcmdError,
    UserDefinedError,
    FunctionNotImplementError,
)
from pydiskcmdcli.scripts._scsi_common import (
    _inquiry_standard,
    _inquiry_supported_vpd_pages,
    _inquiry_block_limits,
    _inquiry_block_dev_char,
    _inquiry_logical_block_prov,
    _inquiry_unit_serial_number,
    _inquiry_device_identification,
    _inquiry_ata_information,
    _no_match_inq,
)
from pydiskcmdcli import log

def version():
    print ("pyscsi version %s" % Version)
    return 0

def print_help():
    if len(sys.argv) > 2 and sys.argv[2] in commands_dict:
        func_name,sys.argv[2] = sys.argv[2],"--help"
        commands_dict[func_name]()
    else:
        print ("pyscsi %s" % Version)
        print ("usage: pyscsi <sub-command> [<device>] [<args>]")
        print ("")
        print ("The '<device>' is usually a character device (ex: /dev/sdb or physicaldrive1).")
        print ("")
        print ("The following are all implemented sub-commands:")
        print ("  list                        List all SCSI devices on machine")
        print ("  inq                         Send scsi inquiry command")
        print ("  getlbastatus                Get LBA Status from target SCSI device")
        print ("  readcap                     Read capacity from target SCSI device")
        print ("  luns                        Send Report Luns commandc to target SCSI device")
        print ("  mode-sense                  Send Mode Sense command to target SCSI device")
        print ("  log-sense                   Send Log Sense command to target SCSI device")
        print ("  cdb-passthru                Submit an arbitrary SCSI command, return results")
        print ("  se-protocol-in              Submit SECURITY PROTOCOL IN command, return results")
        print ("  smart-simulate              Retrieve different logs, return simulate smart")
        print ("  sync                        Synchronize cache to non-volatile cache, as known as flush")
        print ("  read                        Send a read command to disk")
        print ("  write                       Send a write command to disk")
        print ("  version                     Shows the program version")
        print ("  help                        Display this help")
        print ("")
        print ("The following are all installed plugin extensions:")
        print ("  parse-cmd                   Parse the CDB and sense code")
        print ("  lenovo                      Lenovo disk plugin")
        print ("  csmi                        Common Storage Management Interface (CSMI) plugin")
        print ("  megaraid                    MegaRAID extensions")
        print ("")
        print ("The following are pyscsi cli management interface:")
        print ("  cli-info                   Shows pyscsi information")
        print ("  cli-autocmd                Enable or Update the command completion")
        print ("")  
        print ("See 'pyscsi help <command>' or 'pyscsi <command> --help' for more information on a sub-command")
    return 0

###################
@func_debug_info
def inq():
    usage="usage: %prog inq <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-p", "--page", type="int", dest="page_code", action="store", default=-1,
        help="Vital Product Data (VPD) page number or abbreviation")
    parser.add_option("-l", "--alloclen", type="int", dest="alloclen", action="store", default=96,
        help="Transfer data length, default 96")
    parser_update(parser, add_output=["normal", "hex", "raw"], add_debug=True)

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, admin_check=True)
        #
        evpd = 0
        if options.page_code >= 0:
            evpd = 1
        ##
        with SCSI(init_device(dev, open_t='scsi')) as d:
            print ('issuing inquiry command')
            print ("%s:" % d.device._file_name)
            try:
                d.testunitready()
                ##
                if not evpd:
                    _inquiry_standard(d, options)
                    return

                if options.page_code == INQUIRY.VPD.SUPPORTED_VPD_PAGES:
                    _inquiry_supported_vpd_pages(d, options)
                    return

                if options.page_code == INQUIRY.VPD.BLOCK_LIMITS:
                    _inquiry_block_limits(d, options)
                    return

                if options.page_code == INQUIRY.VPD.BLOCK_DEVICE_CHARACTERISTICS:
                    _inquiry_block_dev_char(d, options)
                    return

                if options.page_code == INQUIRY.VPD.LOGICAL_BLOCK_PROVISIONING:
                    _inquiry_logical_block_prov(d, options)
                    return

                if options.page_code == INQUIRY.VPD.UNIT_SERIAL_NUMBER:
                    _inquiry_unit_serial_number(d, options)
                    return

                if options.page_code == INQUIRY.VPD.DEVICE_IDENTIFICATION:
                    _inquiry_device_identification(d, options)
                    return

                if options.page_code == INQUIRY.VPD.ATA_INFORMATION:
                    _inquiry_ata_information(d, options)
                    return

                _no_match_inq(d, options)
            except SCSICheckCondition as ex:
                # if you want a print out of the sense data dict uncomment the next line
                #ex.show_data = True
                print(ex)
    else:
        parser.print_help()
############################ .decode(encoding="utf-8", errors="strict")
@func_debug_info
def _list():
    usage="usage: %prog list <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser_update(parser, add_output=["normal",])

    (options, args) = parser.parse_args()
    ##
    script_check(options, admin_check=True)
    ##
    print_format = "%-20s %-10s %-30s %-40s %-26s %-16s %-8s"
    print (print_format % ("Node", "Protocal", "SN", "Model", "Capacity", "Format(L/P)", "FW Rev"))
    print (print_format % ("-"*20, "-"*10, "-"*30, "-"*40, "-"*26, "-"*16, "-"*8))

    from pydiskcmdcli.utils.string_utils import decode_bytes,string_strip
    from pydiskcmdlib.pysata.sata import SATA
    dev_path_all = None
    if os_type == 'Linux':
        from pydiskcmdcli.system.lin_os_tool import get_block_devs
        dev_path_all = [i for i in get_block_devs(exclude=("nvme",))]
    elif os_type == 'Windows':
        from pydiskcmdcli.system.win_os_tool import scan_all_physical_drive
        dev_path_all = sorted([i for i in scan_all_physical_drive()])
    if dev_path_all is not None:
        for dev_path in dev_path_all:
            try:
                with SCSI(init_device(dev_path, open_t='scsi'), 512) as d:
                    serial_info = d.inquiry(evpd=1, page_code=INQUIRY.VPD.UNIT_SERIAL_NUMBER).result
                    inq_info = d.inquiry().result
                    cap = d.readcapacity16().result
            except:
                continue
            # device who can be here, will be scsi device
            # Then check if ATA device
            device_type = 'scsi'
            try:
                with SATA(init_device(dev_path, open_t='ata')) as d:
                    id_info = d.identify_raw
            except:
                pass
            else:
                device_type = 'ata'
            # Get the information of device
            serial = 'Unknown'
            model = 'Unknown'

            serial = string_strip(decode_bytes(serial_info.get('unit_serial_number')), b'\x00'.decode(), ' ')
            serial = serial if serial else 'Unknown'
            model = string_strip(decode_bytes(inq_info.get('product_identification')), b'\x00'.decode(), ' ')
            model = model if model else 'Unknown'
            fw = decode_bytes(inq_info.get('product_revision_level'))
            logical_sector_num = cap["returned_lba"]
            logical_sector_size = cap["block_length"]
            physical_sector_size = (2 ** cap["lbppbe"]) * logical_sector_size
            disk_format = "%s / %s" % (logical_sector_size, physical_sector_size)
            disk_cap = human_read_capacity(logical_sector_size * logical_sector_num)
            if options.output_format == "normal":
                print (print_format % (dev_path, device_type, serial, model, disk_cap, disk_format, fw))
    else:
        raise RuntimeError("OS %s Not support command list" % os_type)

def getlbastatus():
    usage="usage: %prog getlbastatus <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-l", "--lba", type="int", dest="lba", action="store", default=0,
        help="the lba to get status")
    parser_update(parser, add_output=["normal", "hex", "raw"])

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, admin_check=True)
        ##
        with SCSI(init_device(dev, open_t='scsi')) as d:
            print ('issuing getlbastatus command')
            print ("%s:" % d.device._file_name)
            ##
            r = d.readcapacity16().result
            if not r['lbpme']:
                print('LUN is fully provisioned.')
                return
            cmd = d.getlbastatus(options.lba)
        ##
        if options.output_format == "normal":
            r = cmd.result
            for i in range(len(r['lbas'])):
                print('LBA:%d-%d %s' % (
                    r['lbas'][i]['lba'],
                    r['lbas'][i]['lba'] + r['lbas'][i]['num_blocks'] - 1,
                    P_STATUS[r['lbas'][i]['p_status']]
                ))
        elif options.output_format == "hex":
            format_dump_bytes(cmd.datain)
        else:
            print (bytes(cmd.datain))
    else:
        parser.print_help()
############################
def readcap():
    usage="usage: %prog readcap <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser_update(parser, add_output=["normal", "hex", "raw"])

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, admin_check=True)
        ##
        with SCSI(init_device(dev, open_t='scsi')) as d:
            print ('issuing readcap command')
            print ("%s:" % d.device._file_name)
            print ("")
            ##
            cmd = d.readcapacity16()
            r = cmd.result
            if not r['lbpme']:
                print('LUN is fully provisioned.')
                print ("")
            ##
        if options.output_format == "normal":
            print ("Read Capacity results:")
            print ("  Last LBA=%d (%#x), Number of logical blocks=%d" % (r["returned_lba"], r["returned_lba"], r["returned_lba"]+1))
            print ("  Logical block length=%d bytes" % r["block_length"])
            if r["lbppbe"] == 0:
                print ("  Physical block length is One or more physical blocks per logical block")
            else:
                print ("  Physical block length=%d bytes" % (2 ** r["lbppbe"] * r["block_length"]))
        elif options.output_format == "hex":
            format_dump_bytes(cmd.datain)
        else:
            print (bytes(cmd.datain))
    else:
        parser.print_help()

def luns():
    usage="usage: %prog luns <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-s", "--select", type="int", dest="SR", action="store", default=0,
        help="select report field value")
    parser.add_option("", "--data_len", type="int", dest="data_len", action="store", default=96,
        help="the max number of bytes allocated for the data_in buffer")
    parser_update(parser, add_output=["normal", "hex", "raw"])

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, admin_check=True)
        ##
        with SCSI(init_device(dev, open_t='scsi')) as d:
            print ('issuing report luns command')
            print ("%s:" % d.device._file_name)
            print ("")
            ##
            cmd = d.reportluns(report=options.SR, alloclen=options.data_len)
            r = d.reportluns(report=options.SR, alloclen=options.data_len).result
        ##
        if options.output_format == "normal":
            r = cmd.result
            print ("Report luns [select_report=%#x]:" % options.SR)
            for i in r["luns"]:
                for k,v in i.items():
                    print ("  %-6s%x" % (k,v))
                print ('-'*20)
        elif options.output_format == "hex":
            format_dump_bytes(cmd.datain)
        else:
            print (bytes(cmd.datain))
    else:
        parser.print_help()

def mode_sense():
    usage="usage: %prog mode-sense <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-p", "--page", type="int", dest="page", action="store", default=0,
        help="select report field value")
    parser.add_option("-s", "--subpage", type="int", dest="subpage", action="store", default=0,
        help="select report field value")
    parser.add_option("-l", "--alloclen", type="int", dest="alloclen", action="store", default=96,
        help="Transfer data length, default 96")
    parser_update(parser, add_output=["normal", "hex", "raw"])

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, admin_check=True)
        ##
        with SCSI(init_device(dev, open_t='scsi')) as d:
            print ('issuing mode sense command')
            print ("%s:" % d.device._file_name)
            print ("")
            ##
            cmd = d.modesense10(options.page, sub_page_code=options.subpage, alloclen=options.alloclen)
        ##
        if options.output_format == "normal":
            for k,v in cmd.result.items():
                if k != "mode_pages":
                    print ("%-25s:%s" % (k,v))
                else:
                    print ("mode_pages:")
                    for i in range(len(v)):
                        temp = []
                        for _k,_v in v[i].items():
                            temp.append("%s=%s" % (_k,_v))
                        if i > 0:
                            print ('-'*30)
                        print ("  L%-3s  %s" % (i, ','.join(temp)))
        elif options.output_format == "hex":
            format_dump_bytes(cmd.datain)
        else:
            print (bytes(cmd.datain))
    else:
        parser.print_help()

def log_sense():
    usage="usage: %prog log-sense <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-p", "--page", type="int", dest="page", action="store", default=0,
        help="Select report field value")
    parser.add_option("-s", "--subpage", type="int", dest="subpage", action="store", default=0,
        help="Select report field value")
    parser.add_option("-c", "--pc", type="int", dest="page_ctrl", action="store", default=0,
        help="The page control value")
    parser.add_option("-l", "--alloclen", type="int", dest="alloclen", action="store", default=0,
        help="Transfer data length, default 0 means auto fix the length")
    parser_update(parser, add_output=["normal", "hex", "raw"], add_debug=True)

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, admin_check=True)
        # 
        if options.alloclen == 0:
            log_len = 96 # set a 96 length to get
        elif options.alloclen < 5:
            parser.error("alloclen need > 4") 
        else:
            log_len = options.alloclen
        ##
        with SCSI(init_device(dev, open_t='scsi')) as d:
            print ('issuing log sense command')
            print ("%s:" % d.device._file_name)
            print ("")
            ##
            cmd = d.logsense(options.page, sub_page_code=options.subpage, sp=0, pc=0, parameter=0, alloclen=log_len, control=0)
            if options.alloclen == 0: # auot fix 
                log_len = cmd.datain[3] + (cmd.datain[2] << 8) + 4
                if log_len > options.alloclen:
                    # Fixed the length to 
                    # print ("Fixed alloclen %s->%s" % (options.alloclen, log_len))
                    cmd = d.logsense(options.page, sub_page_code=options.subpage, sp=0, pc=options.page_ctrl, parameter=0, alloclen=log_len, control=0)
        ##
        if options.output_format == "normal":
            log_page = LogSenseAttr.get((options.page, options.subpage))
            if not log_page:
                log_page = LogSenseAttr.get("Unkonwn")
            log_page_decode = log_page.decode_value(cmd.datain)
            print ("%-14s: %s" % ("Log Page Name", log_page.log_page_name))
            for i in ("page_code", "subpage_code", "spf", "ds", "page_length"):
                print ("%-14s: %s" % (i, log_page_decode[i]))
            print ("%-14s:" % "Log Parameters")
            print ("")
            if options.page == 0:
                if options.subpage == 0:
                    print ("Supported log pages  [0x0]:")
                    subpage_code = 0
                    for page_code in log_page_decode["log_parameters"]:
                        temp = LogSenseAttr.get((page_code,subpage_code))
                        if not temp:
                            temp = LogSenseAttr.get("Unkonwn")
                        print ("  %-16s: %s" % ("%#x" % page_code, temp.log_page_name))
                elif options.subpage == 0xFF:
                    print ("Supported log pages and subpages  [0x0, 0xff]:")
                    for page_code,subpage_code in log_page_decode["log_parameters"]:
                        temp = LogSenseAttr.get((page_code,subpage_code))
                        if not temp:
                            temp = LogSenseAttr.get("Unkonwn")
                        print ("  %-16s: %s" % ("%#x,%#x" % (page_code,subpage_code), temp.log_page_name))
                else:
                    pass
            else:
                for i in log_page_decode["log_parameters"]:
                    for k in ("parameter_code", "ctrl_bit", "parameter_length", "parameter_value"):
                        print ("  %-16s: %s" % (k, i.get(k)))
                    print ("  %s" % ("-"*50))
        elif options.output_format == "hex":
            format_dump_bytes(cmd.datain)
        else:
            print (bytes(cmd.datain))
    else:
        parser.print_help()
############################
def sync():
    usage="usage: %prog sync <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-s", "--start-lba", type="int", dest="start_lba", action="store", default=0,
        help="The start LBA address to sync cache")
    parser.add_option("-c", "--block-count", type="int", dest="block_count", action="store", default=0,
        help="The number of LBAs to sync cache")
    parser.add_option("-i", "--immed", type="int", dest="immed", action="store", default=0,
        help="Whether wait the command finish or not, default 0: wait")
    parser.add_option("-g", "--group-number", type="int", dest="group_number", action="store", default=0,
        help="The group into which attributes associated with the command")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, admin_check=True)
        ##
        with SCSI(init_device(dev, open_t='scsi')) as d:
            print ('issuing SynchronizeCache16 command')
            print ("%s:" % d.device._file_name)
            print ("")
            ##
            cmd = d.synchronizecache16(options.start_lba, options.block_count, immed=options.immed, group_number=options.group_number)
    else:
        parser.print_help()

def read16():
    usage="usage: %prog read16 <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-s", "--start-block", type="int", dest="slba", action="store", default=0,
        help="Logical Block Address to write to. Default 0")
    parser.add_option("-c", "--block-count", type="int", dest="nlba", action="store", default=1,
        help="Transfer Length in blocks. Default 1")
    parser.add_option("-b", "--block-size", type="int", dest="bs", action="store", default=0,
        help="To fix the block size of the device. Default 0")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, admin_check=True)
        ##
        with SCSI(init_device(dev, open_t='scsi'), options.bs) as d:
            print ('issuing read16 command')
            print ("%s:" % d.device._file_name)
            data = d.read16(options.slba, options.nlba).datain
            print ("Data Length: %s" % len(data))
            print ("")
            print (data)
    else:
        parser.print_help()

def write16():
    usage="usage: %prog write16 <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-s", "--start-block", type="int", dest="slba", action="store", default=0,
        help="Logical Block Address to write to. Default 0")
    parser.add_option("-c", "--block-count", type="int", dest="nlba", action="store", default=1,
        help="Transfer Length in blocks. Default 1")
    parser.add_option("-d", "--data", type="str", dest="data", action="store", default='',
        help="String containing the block to write")
    parser.add_option("-f", "--data-file", type="str", dest="dfile", action="store", default='',
        help="File(Read first) containing the block to write")
    parser.add_option("-b", "--block-size", type="int", dest="bs", action="store", default=0,
        help="To fix the block size of the device. Default 0")
    parser_update(parser, add_force=True)

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, danger_check=True, admin_check=True)
        ##
        with SCSI(init_device(dev, open_t='scsi'), options.bs) as d:
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
                data_size = options.nlba * d.blocksize
                if data_size < data_l:
                    options.data = options.data[0:data_size]
                elif data_size > data_l:
                    options.data = options.data + bytearray(data_size-data_l)
                else:
                    pass
            else:
                parser.error("Lack of input data")
                return
            # issue command
            print ('issuing write16 command')
            print ("%s:" % d.device._file_name)
            cmd = d.write16(options.slba, options.nlba, options.data)
    else:
        parser.print_help()

def cdb_passthru():
    def get_raw_cdb(option, opt_str, value, parser):
        assert value is None
        value = []

        def floatable(str):
            try:
                float(str)
                return True
            except ValueError:
                return False

        for arg in parser.rargs:
            # stop on --foo like options
            if arg[:2] == "--" and len(arg) > 2:
                break
            # stop on -a, but not on -3 or -3.0
            if arg[:1] == "-" and len(arg) > 1 and not floatable(arg):
                break
            if arg.startswith('0x') or arg.endswith('h'):
                arg = arg.rstrip('h')
                # hexadecimal
                arg = int(arg, 16)
            elif arg.isdigit():
                arg = int(arg)
            else:
                raise RuntimeError("Invalid value in -r/--raw-cdb")
            if arg < 256:
                value.append(arg)
            else:
                raise RuntimeError("Invalid value in -r/--raw-cdb, one byte per value")

        del parser.rargs[:len(value)]
        setattr(parser.values, option.dest, value)
    ##
    usage="usage: %prog cdb-passthru <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-r", "--raw-cdb", dest="raw_cdb", action="callback", callback=get_raw_cdb,
        help="The Raw CDB you want to send")
    parser.add_option("-l", "--data-len", type="int", dest="data_len", action="store", default=0,
        help="Data length read or write from device, default 0 means no data transfer")
    parser.add_option("-f", "--data-file", type="str", dest="dfile", action="store", default='',
        help="File containing data that will send to device")
    parser.add_option("-d", "--direction", type="int", dest="direction", action="store", default=0,
        help="data transfer direction, 0: no data transfer, 1: data from device, 2: data to device")
    parser.add_option("-b", "--block-size", type="int", dest="bs", action="store", default=0,
        help="To fix the block size of the device. Default 512")
    parser_update(parser, add_output=["hex", "raw"])

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        ##
        script_check(options, admin_check=True)
        #
        if options.raw_cdb:
            raw_cdb = bytes(bytearray(options.raw_cdb))
        else:
            parser.error("Need raw CDB input")
        #
        if options.direction == 0:
            dataout = b''
            datain_alloclen = 0
        elif options.direction == 1:
            dataout = b''
            datain_alloclen = options.data_len
            if not datain_alloclen:
                parser.error("Need give -l/--data-len, when read data from device")
        else:
            if options.dfile and os.path.isfile(options.dfile):
                data_len = options.data_len if options.data_len > 0 else -1
                with open(options.dfile, 'rb') as f:
                    dataout = f.read(data_len)
                datain_alloclen = 0
            else:
                parser.error("Need give -f/--data-file, when write data to device")
        with SCSI(init_device(dev, open_t='scsi'), options.bs) as d:
            print ('issuing cdb-passthru command')
            print ("%s:" % d.device._file_name)
            cmd = d.cdb_passthru(raw_cdb, dataout=dataout, datain_alloclen=datain_alloclen)
        if options.direction == 1:
            if options.dfile:
                with open(options.dfile, 'wb') as f:
                    f.write(cmd.datain)
            else:
                if options.output_format == "hex":
                    format_dump_bytes(cmd.datain)
                else:
                    print (bytes(cmd.datain))
    else:
        parser.print_help()

def security_protocol_in():
    usage="usage: %prog se-protocol-in <device> [OPTIONS]"
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
        with SCSI(init_device(dev, open_t='scsi')) as d:
            print ('issuing security protocol in command')
            print ("%s:" % d.device._file_name)
            cmd = d.security_protocol_in(options.protocol, options.sp, options.alloclen, INC_512=options.INC_512)
        if options.output_format == "hex":
            format_dump_bytes(cmd.datain)
        else:
            print (bytes(cmd.datain))
    else:
        parser.print_help()

def smart_simulate():
    usage="usage: %prog smart-simulate <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser_update(parser, add_output=["normal", "json"], add_debug=True)

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        #
        script_check(options, admin_check=True)
        ##
        if options.output_format != 'json':
            print ('issuing smart simulate command')
            print ('Device: %s' % dev)
            print ('')
        with SCSI(init_device(dev, open_t='scsi')) as d:
            smart = get_smart_simulate(d)
        if options.output_format == 'normal':
            print_format = "%-25s %-15s %s"
            print (print_format % ("ATTRIBUTE_NAME", "THRESH", "VALUE"))
            for k,v in smart.items():
                if k == "Power On Minutes":
                    print (print_format % ("Power On Hours", "-" if v.Threshold is None else round(v.Threshold / 60, 2), round(v.Value / 60, 2)))
                elif k in ("Total Write", "Total Read"):
                    print (print_format % ("%s(GB)" % k, "-" if v.Threshold is None else round(v.Threshold / 10**9, 3), round(v.Value / 10**9, 3)))
                elif k in ("Percentage Used", "Available Spare"):
                    print (print_format % ("%s(%%)" % k, "-" if v.Threshold is None else v.Threshold, v.Value))
                elif k == "Workload Utilization":
                    print (print_format % ("%s(%%)" % k, "-" if v.Threshold is None else (v.Threshold / 100), (v.Value / 100)))
                else:
                    print (print_format % (k, "-" if v.Threshold is None else v.Threshold, v.Value))
        elif options.output_format == 'json':
            for k in smart.keys():
                smart[k] = {"AttributeName": k, "Threshold": smart[k].Threshold, "Value": smart[k].Value}
            json_print(smart)
        ##
        # format_print_smart()
    else:
        parser.print_help()
#################################################
# Bellow is cli management interface 
#################################################
def cli_info():
    from pydiskcmdlib import version as lib_version
    from pydiskcmdlib.pyscsi import version as scsi_version
    version()
    print ('')
    print ('pydiskcmdlib version : %s' % lib_version)
    print ('  - scsi code version: %s' % scsi_version)
    return 0

def cli_autocmd():
    from pydiskcmdcli.system.bash_completion import enable_cmd_completion
    enable_cmd_completion()
    return 0
#########
############################
############################
commands_dict = {"list": _list, 
                 "inq": inq,
                 "cdb-passthru": cdb_passthru,
                 "readcap": readcap,
                 "getlbastatus": getlbastatus,
                 "luns": luns,
                 "mode-sense": mode_sense,
                 "log-sense": log_sense,
                 "se-protocol-in": security_protocol_in,
                 "smart-simulate": smart_simulate,
                 "version": version,
                 "sync": sync,
                 "read": read16,
                 "write":write16,
                 "help": print_help,
                 "cli-info": cli_info,
                 "cli-autocmd": cli_autocmd,
                 }
commands_dict.update(scsi_plugins)

def pyscsi():
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
                import traceback
                log.debug(traceback.format_exc())
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
