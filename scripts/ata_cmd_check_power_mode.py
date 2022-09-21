#!/usr/bin/env python
# coding: utf-8
import sys
import pydiskcmd.pysata.sata
import pydiskcmd.utils


def usage():
    print('Usage: check_power_mode.py <device>')
    print ('')

def main(device):
    r = None
    with pydiskcmd.pysata.sata.SATA(device,512) as s:
        print ('issuing check power mode command')
        print ("%s:" % device._file_name)
        cmd = s.check_power_mode()
        return_descriptor = cmd.ata_status_return_descriptor
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
    print ('')
    return

if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(pydiskcmd.utils.init_device(sys.argv[1]))
    else:
        usage()
