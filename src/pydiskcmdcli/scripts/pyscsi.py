# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import sys,os
import optparse
from pydiskcmdcli import os_type
from pydiskcmdlib.pyscsi.scsi import SCSI
from pydiskcmdcli.scsi_spec import LogSenseAttr
from pydiskcmdlib.utils import init_device
from pydiskcmdcli.utils.format_print import format_dump_bytes,human_read_capacity
from pyscsi.pyscsi.scsi_sense import SCSICheckCondition
from pyscsi.pyscsi import scsi_enum_inquiry as INQUIRY
from pyscsi.pyscsi.scsi_enum_getlbastatus import P_STATUS
from pydiskcmdcli.plugins import parse_cmd_plugin
from pydiskcmdcli import version as Version
from . import parser_update,script_check
from pydiskcmdcli.exceptions import (
    CommandSequenceError,
    CommandNotSupport,
    NonpydiskcmdError,
    UserDefinedError,
    FunctionNotImplementError,
)


def _debug_info_print(cmd):
    print ("")
    if cmd.cdb:
        print ("Sending Command: %s" % ' '.join(["%x" % b for b in cmd.cdb]))
    if cmd.sense:
        print ("Return sense: %s" % ' '.join(["%x" % b for b in cmd.sense]))
    if cmd.raw_sense_data:
        print ("Return raw sense data: %s" % ' '.join(["%x" % b for b in cmd.raw_sense_data]))
    print ("")

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
        print ("  sync                        Synchronize cache to non-volatile cache, as known as flush")
        print ("  read                        Send a read command to disk")
        print ("  write                       Send a write command to disk")
        print ("  version                     Shows the program version")
        print ("  help                        Display this help")
        print ("")
        print ("The following are all installed plugin extensions:")
        print ("  parse-cmd                   Parse the CDB and sense code")
        print ("")
        print ("The following are pyscsi cli management interface:")
        print ("  cli-info                   Shows pyscsi information")
        print ("  cli-autocmd                Enable or Update the command completion")
        print ("")  
        print ("See 'pyscsi help <command>' or 'pyscsi <command> --help' for more information on a sub-command")
    return 0

def _inquiry_standard(s, options):
    cmd = s.inquiry(alloclen=options.alloclen)
    if options.debug:
        _debug_info_print(cmd)
    if options.output_format == 'normal':
        i = cmd.result
        print('Standard INQUIRY')
        print('================')
        print('PQual=%d  Device_type=%d  RMB=%d  version=0x%02x  %s' % (
            i['peripheral_qualifier'],
            i['peripheral_device_type'],
            i['rmb'],
            i['version'],
            '[SPC3]' if i['version'] == 5 else ''))
        print('NormACA=%d  HiSUP=%d  Resp_data_format=%d' % (
            i['normaca'],
            i['hisup'],
            i['response_data_format']))
        print('SCCS=%d  ACC=%d  TPGS=%d  3PC=%d  Protect=%d' % (
            i['sccs'],
            i['acc'],
            i['tpgs'],
            i['3pc'],
            i['protect']))
        print('EncServ=%d  MultiP=%d  Addr16=%d' % (
            i['encserv'],
            i['multip'],
            i['addr16']))
        print('WBus16=%d  Sync=%d  CmdQue=%d' % (
            i['wbus16'],
            i['sync'],
            i['cmdque']))
        print('Clocking=%d  QAS=%d  IUS=%d' % (
            i['clocking'],
            i['qas'],
            i['ius']))
        print('  length=%d  Peripheral device type: %s' % (i['additional_length'] + 5,
                                                           cmd.DEVICE_TYPE[i['peripheral_device_type']]))
        print('Vendor identification:', i['t10_vendor_identification'][:32].decode(encoding="utf-8",
                                                                                   errors="strict"))
        print('Product identification:', i['product_identification'][:32].decode(encoding="utf-8",
                                                                                 errors="strict"))
        print('Product revision level:', i['product_revision_level'].decode(encoding="utf-8",
                                                                            errors="strict"))
    elif options.output_format == 'hex':
        format_dump_bytes(cmd.datain)
    else:
        print (cmd.datain)

def _inquiry_supported_vpd_pages(s, options):
    cmd = s.inquiry(evpd=1, page_code=INQUIRY.VPD.SUPPORTED_VPD_PAGES, alloclen=options.alloclen)
    if options.output_format == 'normal':
        i = cmd.result
        print('Supported VPD Pages, page_code=0x00')
        print('===================================')
        print('PQual=%d  Peripheral device type: %s' % (i['peripheral_qualifier'],
                                                        cmd.DEVICE_TYPE[i['peripheral_device_type']]))
        print('  Supported VPD pages:')
        for pg in i['vpd_pages']:
            print('    0x%02x: %s' % (pg, cmd.VPD[pg]))
    elif options.output_format == 'hex':
        format_dump_bytes(cmd.datain)
    else:
        print (cmd.datain)

def _inquiry_block_limits(s, options):
    cmd = s.inquiry(evpd=1, page_code=INQUIRY.VPD.BLOCK_LIMITS, alloclen=options.alloclen)
    if options.output_format == 'normal':
        i = cmd.result
        print('Block Limits, page_code=0xb0 (SBC)')
        print('==================================')
        print('  Maximum compare and write length:', i['max_caw_len'])
        print('  Optimal transfer length granularity:', i['opt_xfer_len_gran'])
        print('  Maximum transfer length:', i['max_xfer_len'])
        print('  Optimal transfer length:', i['opt_xfer_len'])
        print('  Maximum prefetch, xdread, xdwrite transfer length:', i['max_pfetch_len'])
        print('  Maximum unmap LBA count:', i['max_unmap_lba_count'])
        print('  Maximum unmap block descriptor count:', i['max_unmap_bd_count'])
        print('  Optimal unmap granularity:', i['opt_unmap_gran'])
        print('  Unmap granularity alignment valid:', i['ugavalid'])
        print('  Unmap granularity alignment:', i['unmap_gran_alignment'])
    elif options.output_format == 'hex':
        format_dump_bytes(cmd.datain)
    else:
        print (cmd.datain)

def _inquiry_block_dev_char(s, options):
    cmd = s.inquiry(evpd=1, page_code=INQUIRY.VPD.BLOCK_DEVICE_CHARACTERISTICS, alloclen=options.alloclen)
    if options.output_format == 'normal':
        i = cmd.result
        print('Block Device Characteristics, page_code=0xb1 (SBC)')
        print('==================================================')
        print('  Nominal rotation rate: %d rpm' % (i['medium_rotation_rate']))
        print('  Product type=%d' % (i['product_type']))
        print('  WABEREQ=%d' % (i['wabereq']))
        print('  WACEREQ=%d' % (i['wacereq']))
        print('  Nominal form factor %s inches' % (
            cmd.NOMINAL_FORM_FACTOR[i['nominal_form_factor']]))
        print('  VBULS=%d' % (i['vbuls']))
    elif options.output_format == 'hex':
        format_dump_bytes(cmd.datain)
    else:
        print (cmd.datain)

def _inquiry_logical_block_prov(s, options):
    cmd = s.inquiry(evpd=1, page_code=INQUIRY.VPD.LOGICAL_BLOCK_PROVISIONING, alloclen=options.alloclen)
    if options.output_format == 'normal':
        i = cmd.result
        print('Logical Block Provisioning, page_code=0xb2 (SBC)')
        print('================================================')
        print('  Threshold=%d blocks  [%s]' % (1 << i['threshold_exponent'],
                                               'NO LOGICAL BLOCK PROVISIONING SUPPORT' if not
                                               i['threshold_exponent'] else 'exponent=%d' % (
                                               i['threshold_exponent'])))
        print('  LBPU=%d  LBPWS=%d  LBPWS10=%d  LBPRZ=%d  ANC_SUP=%d  DP=%d' % (i['lbpu'],
                                                                                i['lpbws'],
                                                                                i['lbpws10'],
                                                                                i['lbprz'],
                                                                                i['anc_sup'],
                                                                                i['dp']))
        print('  Provisioning Type=%d  [%s]' % (i['provisioning_type'],
                                                cmd.PROVISIONING_TYPE[i['provisioning_type']]))
    elif options.output_format == 'hex':
        format_dump_bytes(cmd.datain)
    else:
        print (cmd.datain)

def _inquiry_unit_serial_number(s, options):
    cmd = s.inquiry(evpd=1, page_code=INQUIRY.VPD.UNIT_SERIAL_NUMBER, alloclen=options.alloclen)
    if options.output_format == 'normal':
        i = cmd.result
        print('Unit Serial Number, page_code=0x80')
        print('==================================')
        print('  Unit serial number: %s' % (i['unit_serial_number']))
    elif options.output_format == 'hex':
        format_dump_bytes(cmd.datain)
    else:
        print (cmd.datain)

def _inquiry_device_identification(s, options):
    cmd = s.inquiry(evpd=1, page_code=INQUIRY.VPD.DEVICE_IDENTIFICATION, alloclen=16383)
    if options.output_format == 'normal':
        i = cmd.result
        print('Device Identification, page_code=0x83')
        print('=====================================')
        _d = i['designator_descriptors']
        for idx in range(len(_d)):
            print('  Designation descriptor, descriptor length: %d' %
                  (_d[idx]['designator_length'] + 4))
            print('    designator type:%d [%s]  code set:%d [%s]' %
                  (_d[idx]['designator_type'],
                   cmd.DESIGNATOR[_d[idx]['designator_type']],
                   _d[idx]['code_set'],
                   cmd.CODE_SET[_d[idx]['code_set']]))
            print('    association:%d [%s]' % (_d[idx]['association'],
                                               cmd.ASSOCIATION[_d[idx]['association']]))
            for k, v in _d[idx]['designator'].items():
                print('      %s: %s' % (k, v))
    elif options.output_format == 'hex':
        format_dump_bytes(cmd.datain)
    else:
        print (cmd.datain)

def _inquiry_ata_information(s, options):
    specific_config = {
        14280: 'Device requires SET FEATURES subcommand to spin-up after power-up\n'
               'and IDENTIFY DEVICE data is incomplete',
        29640: 'Device requires SET FEATURES subcommand to spin-up after power-up\n'
               'and DEVICE data is complete',
        35955: 'Device does not require SET FEATURES subcommand to spin-up after power-up\n'
               'and IDENTIFY DEVICE data is incomplete',
        51255: 'Device does not require SET FEATURES subcommand to spin-up after power-up\n'
               'and IDENTIFY DEVICE data is complete',
    }
    print('ATA Information, page_code=0x89')
    print('=============================================\n')
    cmd = s.inquiry(evpd=1, page_code=INQUIRY.VPD.ATA_INFORMATION, alloclen=options.alloclen)
    if options.output_format == 'normal':
        i = cmd.result
        print('SAT Vendor Identification:', i['sat_vendor_identification'].decode(encoding="utf-8",
                                                                                  errors="strict"))
        print('SAT Product Identification:', i['sat_product_identification'].decode(encoding="utf-8",
                                                                                    errors="strict"))
        print('SAT Product Revisions Level:', i['sat_product_rev_lvl'].decode(encoding="utf-8",
                                                                              errors="strict"))
        if 'signature' in i.keys():
            sig = i['signature']
            print('Signature Information:')
            print('    Sector Count:', sig['sector_count'])
            print('    LBA low:', sig['lba_low'])
            print('    LBA mid/Byte Count low:', sig['lba_mid'])
            print('    LBA high/Byte Count high:', sig['lba_high'])
            print('    Device:', sig['device'])
        if 'identify' in i.keys():
            ident = i['identify']
            print('Identify Device or Identify Package Device Data:')
            print('    General Configuration:')
            print('        ATA Device:',
                  'yes' if ident['general_config']['ata_device'] == 0 else 'no')
            print('        Response incomplete:',
                  'yes' if ident['general_config']['ata_device'] == 2 else 'no')
            print('    Specific Configuration:')
            print('       ', (specific_config[ident['specific_config']]
                              if ident['specific_config'] in specific_config.keys() else 'reserved'))
            print('    Device Serial number: %s' % ident['serial_number'].decode(encoding="utf-8",
                                                                                 errors="replace"))
            print('    Firmware Revision:', ident['firmware_rev'].decode(encoding="utf-8",
                                                                         errors="replace"))
            print('    Model Number:', ident['model_number'].decode(encoding="utf-8",
                                                                    errors="replace"))
    elif options.output_format == 'hex':
        format_dump_bytes(cmd.datain)
    else:
        print (cmd.datain)

def _no_match_inq(s, options):
    print('No pretty print( for this page, page_code=0x%02x' % options.page_code)
    print('=============================================\n')
    cmd = s.inquiry(evpd=1, page_code=options.page_code, alloclen=options.alloclen)
    if options.output_format == 'normal':
        i = cmd.result
        for k, v in i.items():
            print('%s - %s' % (k, v))
    elif options.output_format == 'hex':
        format_dump_bytes(cmd.datain)
    else:
        print (cmd.datain)
###################
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
                    cmd = d.logsense(options.page, sub_page_code=options.subpage, sp=0, pc=0, parameter=0, alloclen=log_len, control=0)
        if options.debug:
            _debug_info_print(cmd)
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

#################################################
# Bellow is parse-cmd plugin 
#################################################
def _parse_cmd_print_help():
    print ("pyscsi-%s" % Version)
    print ("usage: pynvme parse-cmd <sub-command> [<device>] [<args>]")
    print ("")
    print ("Parse Command plugin")
    print ("")
    print ("The following are all implemented sub-commands:")
    print ("")
    print ("  cdb                     Parse the command CDB(in hex format), like A0 01 00 00 00 00")
    print ("  sense-code              Parse the return sense code(in hex format), sense-key/asc/ascq or asc/ascq")
    print ("  help                    Display this help")
    print ("")
    print ("See 'pyscsi parse-cmd help <command>' for more information on a specific command")
    return 0

def _parse_cmd_print_ver():
    print ("parse-cmd Plugin Version: %s" % "1.0")
    print ("")
    return 0

def _cdb():
    usage="usage: %prog parse-cmd cdb CDB0 CDB1 ..."
    parser = optparse.OptionParser(usage)
    if len(sys.argv[3:]) > 1:
        cdb_in_str = [i.strip() for i in sys.argv[3:]]
    else:
        temp = sys.argv[3].strip("0x")
        cdb_in_str = [temp[i:i+2] for i in range(0, len(temp), 2)]
    parsed_cdb = parse_cmd_plugin["cdb"]([int(i, 16) for i in cdb_in_str])
    print ("Command CDB:    %s" % ' '.join(cdb_in_str))
    print ("Command Opcode: 0x%s" % cdb_in_str[0])  # cdb[0] is usually the Opcode
    print ("")
    for spec_name,cdb_desp in parsed_cdb.items():
        print ("-"*30)
        print ("Command in Spec: %s" % spec_name)
        print ("Command Name:    %s" % cdb_desp['cdb_name'])
        print ("")
        for k,v in cdb_desp['cdb'].items():
            print ("%-20s: %s" % (k,v))
    return 0

def _sense_code():
    usage="usage: %prog parse-cmd sense-code sense-key/asc/ascq or asc/ascq"
    parser = optparse.OptionParser(usage)
    if len(sys.argv) < 4:
        parser.error("Please input the sense-code")
    if "/" in sys.argv[3]:
        args = [int(i.strip(), 16) for i in sys.argv[3].split("/")]
    elif ":" in sys.argv[3]:
        args = [int(i.strip(), 16) for i in sys.argv[3].split(":")]
    if len(args) == 3:
        res = parse_cmd_plugin["sense_code"](args[1], args[2], args[0])
        sense_key = "%X" % args[0]
        asc = "%X" % args[1]
        ascq = "%X" % args[2]
        print ("Sense Key=0x%s,      %s" % (sense_key.zfill(2), res[1]))
        print ("ASC=0x%s, ASCQ=0x%s, %s" % (asc.zfill(2), ascq.zfill(2), res[0] if res[0] else "NA"))
    elif len(args) == 2:
        res = parse_cmd_plugin["sense_code"](*args)
        asc = "%X" % args[0]
        ascq = "%X" % args[1]
        print ("ASC=0x%s, ASCQ=0x%s, %s" % (asc.zfill(2), ascq.zfill(2), res if res else "NA"))
    else:
        parser.error("sense-code should sense-key/asc/ascq or asc/ascq")
    return 0


plugin_parse_cmd_commands_dict = {"cdb": _cdb,
                                 "sense-code": _sense_code,
                                 "version": _parse_cmd_print_ver,
                                 "help": _parse_cmd_print_help,}


def parse_cmd():
    if len(sys.argv) > 2:
        plugin_command = sys.argv[2]
        if plugin_command in plugin_parse_cmd_commands_dict:
            plugin_parse_cmd_commands_dict[plugin_command]()
            return
    _parse_cmd_print_help()
    return 0

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
                 "version": version,
                 "sync": sync,
                 "read": read16,
                 "write":write16,
                 "help": print_help,
                 "cli-info": cli_info,
                 "cli-autocmd": cli_autocmd,
                 "parse-cmd": parse_cmd,
                 }

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
