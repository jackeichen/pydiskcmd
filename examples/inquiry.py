#!/usr/bin/env python

# SPDX-FileCopyrightText: 2014 The python-scsi Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later

# coding: utf-8
import sys

from pyscsi.pyscsi.scsi_sense import SCSICheckCondition
from pydiskcmdlib.pyscsi.scsi import SCSI
from pydiskcmdlib.utils import init_device


def main():
    ## check device
    dev = sys.argv[1]
    ##
    with SCSI(init_device(dev, open_t='scsi')) as d:
        print ('issuing inquiry command')
        print ("%s:" % d.device._file_name)
        try:
            d.testunitready()
            ##
            cmd = d.inquiry(alloclen=96)
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
        except SCSICheckCondition as ex:
            # if you want a print out of the sense data dict uncomment the next line
            #ex.show_data = True
            print(ex)

if __name__ == "__main__":
    main()
