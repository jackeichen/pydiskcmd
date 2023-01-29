# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import sys,os
import optparse
from pydiskcmd.pyscsi.scsi import SCSI
from pydiskcmd.utils import init_device
from pydiskcmd.utils.format_print import format_dump_bytes
from pydiskcmd.system.os_tool import check_device_exist
# import from python-scsi
from pyscsi.pyscsi.scsi_sense import SCSICheckCondition
from pyscsi.pyscsi import scsi_enum_inquiry as INQUIRY
from pyscsi.pyscsi.scsi_enum_getlbastatus import P_STATUS
from pyscsi.pyscsi import scsi_enum_modesense as MODESENSE6
from pyscsi.pyscsi import scsi_enum_readelementstatus as READELEMENTSTATUS



Version = '0.2.0'

def version():
    print ("pyscsi version %s" % Version)
    return 0

def print_help():
    if len(sys.argv) > 2 and sys.argv[2] in commands_dict:
        func_name,sys.argv[2] = sys.argv[2],"--help"
        commands_dict[func_name]()
    else:
        print ("pyscsi %s" % Version)
        print ("usage: pyscsi <command> [<device>] [<args>]")
        print ("")
        print ("The '<device>' is usually an sd character device (ex: /dev/sdb or physicaldrive1).")
        print ("")
        print ("The following are all implemented sub-commands:")
        print ("  inq                         Send scsi inquiry command")
        print ("  getlbastatus                Get LBA Status from target SCSI device")
        print ("  read                        Send a read command to disk")
        print ("  write                       Send a write command to disk")
        print ("  version                     Shows the program version")
        print ("  help                        Display this help")
        print ("")
        print ("See 'pyscsi help <command>' or 'pyscsi <command> --help' for more information on a sub-command")
    return 0

def _inquiry_standard(s, options):
    cmd = s.inquiry()
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
    elif options.output_format == 'binary':
        format_dump_bytes(cmd.datain)
    else:
        print (cmd.datain)

def _inquiry_supported_vpd_pages(s, options):
    cmd = s.inquiry(evpd=1, page_code=INQUIRY.VPD.SUPPORTED_VPD_PAGES)
    if options.output_format == 'normal':
        i = cmd.result
        print('Supported VPD Pages, page_code=0x00')
        print('===================================')
        print('PQual=%d  Peripheral device type: %s' % (i['peripheral_qualifier'],
                                                        cmd.DEVICE_TYPE[i['peripheral_device_type']]))
        print('  Supported VPD pages:')
        for pg in i['vpd_pages']:
            print('    0x%02x: %s' % (pg, cmd.VPD[pg]))
    elif options.output_format == 'binary':
        format_dump_bytes(cmd.datain)
    else:
        print (cmd.datain)

def _inquiry_block_limits(s, options):
    cmd = s.inquiry(evpd=1, page_code=INQUIRY.VPD.BLOCK_LIMITS)
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
    elif options.output_format == 'binary':
        format_dump_bytes(cmd.datain)
    else:
        print (cmd.datain)

def _inquiry_block_dev_char(s, options):
    cmd = s.inquiry(evpd=1, page_code=INQUIRY.VPD.BLOCK_DEVICE_CHARACTERISTICS)
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
    elif options.output_format == 'binary':
        format_dump_bytes(cmd.datain)
    else:
        print (cmd.datain)

def _inquiry_logical_block_prov(s, options):
    cmd = s.inquiry(evpd=1, page_code=INQUIRY.VPD.LOGICAL_BLOCK_PROVISIONING)
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
    elif options.output_format == 'binary':
        format_dump_bytes(cmd.datain)
    else:
        print (cmd.datain)

def _inquiry_unit_serial_number(s, options):
    cmd = s.inquiry(evpd=1, page_code=INQUIRY.VPD.UNIT_SERIAL_NUMBER)
    if options.output_format == 'normal':
        i = cmd.result
        print('Unit Serial Number, page_code=0x80')
        print('==================================')
        print('  Unit serial number: %s' % (i['unit_serial_number']))
    elif options.output_format == 'binary':
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
    elif options.output_format == 'binary':
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
    cmd = s.inquiry(evpd=1, page_code=INQUIRY.VPD.ATA_INFORMATION)
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
    elif options.output_format == 'binary':
        format_dump_bytes(cmd.datain)
    else:
        print (cmd.datain)
###################
def inq():
    usage="usage: %prog inq <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-p", "--page", type="int", dest="page_code", action="store", default=-1,
        help="Vital Product Data (VPD) page number or abbreviation")
    parser.add_option("-o", "--output-format", type="choice", dest="output_format", action="store", choices=["normal", "binary", "raw"],default="normal",
        help="Output format: normal|binary|raw, default normal")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        if not check_device_exist(dev):
            raise RuntimeError("Device not exist!")
        #
        evpd = 0
        if options.page_code >= 0:
            evpd = 1
        ##
        with SCSI(init_device(dev, open_t='scsi'), 512) as d:
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

                print('No pretty print( for this page, page_code=0x%02x' % options.page_code)
                print('=============================================\n')
                cmd = d.inquiry(evpd=1, page_code=options.page_code)
                i = cmd.result
                for k, v in i.items():
                    print('%s - %s' % (k, v))
            except SCSICheckCondition as ex:
                # if you want a print out of the sense data dict uncomment the next line
                #ex.show_data = True
                print(ex)
    else:
        parser.print_help()
############################

def getlbastatus():
    usage="usage: %prog getlbastatus <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-l", "--lba", type="int", dest="lba", action="store", default=0,
        help="the lba to get status")
    parser.add_option("-o", "--output-format", type="choice", dest="output_format", action="store", choices=["normal", "binary", "raw"],default="normal",
        help="Output format: normal|binary|raw, default normal")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        if not check_device_exist(dev):
            raise RuntimeError("Device not exist!")
        ##
        with SCSI(init_device(dev, open_t='scsi'), 512) as d:
            print ('issuing getlbastatus command')
            print ("%s:" % d.device._file_name)
            ##
            r = d.readcapacity16().result
            if not r['lbpme']:
                print('LUN is fully provisioned.')
                return
            ##
            r = d.getlbastatus(options.lba).result
            for i in range(len(r['lbas'])):
                print('LBA:%d-%d %s' % (
                    r['lbas'][i]['lba'],
                    r['lbas'][i]['lba'] + r['lbas'][i]['num_blocks'] - 1,
                    P_STATUS[r['lbas'][i]['p_status']]
                ))
############################

def read16():
    usage="usage: %prog read16 <device> [OPTIONS]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-s", "--start-block", type="int", dest="slba", action="store", default=0,
        help="Logical Block Address to write to. Default 0")
    parser.add_option("-c", "--block-count", type="int", dest="nlba", action="store", default=1,
        help="Transfer Length in blocks. Default 1")
    parser.add_option("-b", "--block-size", type="int", dest="bs", action="store", default=512,
        help="To fix the block size of the device. Default 512")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        if not check_device_exist(dev):
            raise RuntimeError("Device %s not exist!" % dev)
        ##
        with SCSI(init_device(dev, open_t='scsi'), options.bs) as d:
            print ('issuing read16 command')
            print ("%s:" % d.device._file_name)
            data = d.read16(options.slba, options.nlba).datain
            print ("Data Length: %s" % len(data))
            print ("")
            print (data)

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
    parser.add_option("-b", "--block-size", type="int", dest="bs", action="store", default=512,
        help="To fix the block size of the device. Default 512")

    if len(sys.argv) > 2:
        (options, args) = parser.parse_args(sys.argv[2:])
        ## check device
        dev = sys.argv[2]
        if not check_device_exist(dev):
            raise RuntimeError("Device %s not exist!" % dev)
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
            data_size = options.nlba * options.bs
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
        with SCSI(init_device(dev, open_t='scsi'), options.bs) as d:
            print ('issuing write16 command')
            print ("%s:" % d.device._file_name)
            cmd = d.write16(options.slba, options.nlba, options.data)

############################
############################

commands_dict = {"inq": inq,
                 "getlbastatus": getlbastatus,
                 "version": version,
                 "read": read16,
                 "write":write16,
                 "help": print_help}

def pyscsi():
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command in commands_dict:
            commands_dict[command]()
        else:
            print_help()
    else:
        print_help()
