# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import time
import argparse
from pydiskcmdlib.utils import init_device
from pydiskcmdlib.pynvme.nvme import NVMe
from pydiskcmdlib.pysata.sata import SATA
from pydiskcmdlib.utils.converter import scsi_ba_to_int

# This is a script to get nand-based SSD Write Amplification.
# Here is some examples:
#
# example 1. Get OCP NVMe SSD WA in 30 minutes, run command:
#   python3 WAFTool.py -i nvme -d /dev/nvme<X> -t 1800
#
# example 2. Get NVMe SSD WA with your custom command.
# Suppose the nand write in log ID 0xF0(log page size=4096B), nand write located in byte 16-23, 
# unit is GB, then run command:
#   python3 WAFTool.py -i nvme -d /dev/nvme<X> -nw 240,16,8 -nl 4096 -nf 1000000000


def get_nvme_write_factor(d, args):
    if args.host_write:
        host_write_log_id,host_write_offset,host_write_length = [int(i.strip()) for i in args.host_write.split(',')]
        cmd = d.get_log_page(0,                    # ns_id
                             host_write_log_id,    # log id
                             0,                    # lsp
                             0,
                             (args.host_log_length & 0xFFFF),
                             ((args.host_log_length >> 16) & 0xFFFF),
                             0,
                             0,
                             0,
                             0,
                             0,
                             0,
                             )
        host_write = scsi_ba_to_int(cmd.data[host_write_offset:host_write_offset+host_write_length], 'little') * args.host_factor
    else:
        cmd = d.smart_log()
        host_write = scsi_ba_to_int(cmd.data[48:64], 'little') * 512000
    ##
    if args.nand_write:
        nand_write_log_id,nand_write_offset,nand_write_length = [int(i.strip()) for i in args.nand_write.split(',')]
        cmd = d.get_log_page(0,                    # ns_id
                             nand_write_log_id,    # log id
                             0,                    # lsp
                             0,
                             (args.nand_log_length & 0xFFFF),
                             ((args.nand_log_length >> 16) & 0xFFFF),
                             0,
                             0,
                             0,
                             0,
                             0,
                             0,
                             )
        nand_write = scsi_ba_to_int(cmd.data[nand_write_offset:nand_write_offset+nand_write_length], 'little') * args.nand_factor
    elif d.ocp_support:
        from pydiskcmdcli.plugins import ocp_plugin
        cmd = ocp_plugin["SmartExtendedLog"]()
        d.execute(cmd)
        nand_write = scsi_ba_to_int(cmd.data[0:16], 'little')
    else:
        raise RuntimeError("Lack key value of Nand Write")
    return host_write,nand_write

def get_ata_write_factor(d, args):
    host_write = None
    nand_write = None
    if args.ata_smart_hw_id or args.ata_smart_nw_id:
        cmd = d.smart_read_data()
        for i in range(2, 362, 12):
            temp = cmd.datain[i:i+12]
            if args.ata_smart_hw_id and temp[0] == args.ata_smart_hw_id:
                host_write = scsi_ba_to_int(temp[5:11], 'little') * args.host_factor  # raw data used
            elif args.ata_smart_nw_id and temp[0] == args.ata_smart_nw_id:
                nand_write = scsi_ba_to_int(temp[5:11], 'little') * args.nand_factor  # raw data used
    else:
        raise RuntimeError("ATA SSD Only support smart type")
    if host_write is None:
        raise RuntimeError("Lack key value of Host Write")
    if nand_write is None:
        raise RuntimeError("Lack key value of Nand Write")
    return host_write,nand_write

def calculate_wa(host_write_start, nand_write_start, host_write_end, nand_write_end):
    host_write_total = host_write_end - host_write_start
    nand_write_total = nand_write_end - nand_write_start
    if host_write_total > 0:
        return nand_write_total/host_write_total
    else:
        raise RuntimeError("No host write!")

def main():
    parser = argparse.ArgumentParser(description='''Script to get the SSD Average WA over time.

Note: The host write should not include metadata. 
''')
    parser.add_argument('-i', '--interface', type=str, choices=['nvme', 'sata'], required=True,
                        help="Specify the SSD interface.")
    parser.add_argument('-d', '--device', type=str, required=True,
                        help="Specify the Disk path.")
    parser.add_argument('-hw', '--host_write', type=str, default='', 
                        help="Host write location, input log_id,data_offset,data_length")
    parser.add_argument('-hf', '--host_factor', type=int, default=1, 
                        help="Host write factor.")
    parser.add_argument('-hl', '--host_log_length', type=int, default=512,
                        help="Set Host write Log Length for -hw/-nw.")
    parser.add_argument('-nw', '--nand_write', type=str, default='', 
                        help="Nand write location, input log_id,data_offset,data_length")
    parser.add_argument('-nf', '--nand_factor', type=int, default=1, 
                        help="Nand write factor.")
    parser.add_argument('-nl', '--nand_log_length', type=int, default=512,
                        help="Set Log Length for -hw/-nw.")
    parser.add_argument('--ata_smart_hw_id', type=int, default=241,
                        help="Host write smart id for sata ssd, default 241")
    parser.add_argument('--ata_smart_nw_id', type=int, default=0,
                        help="Nand write smart id for sata ssd")
    parser.add_argument('-t', '--run_time', type=int, default=0,
                        help="Total time to check the WAF. Default 0, never exit until CTRL+C pressed.")

    args = parser.parse_args()
    ## process
    start_t = time.time()
    ## Get host_write,nand_write 
    if args.interface == "nvme":
        with NVMe(init_device(args.device, open_t='nvme')) as d:
            host_write_start,nand_write_start = get_nvme_write_factor(d, args)
    elif args.interface == "sata":
        with SATA(init_device(args.device, open_t='ata')) as d:
            host_write_start,nand_write_start = get_ata_write_factor(d, args)
    ## sleep 
    try:
        if args.run_time > 0:
            time.sleep(args.run_time)
        else:
            while True:
                time.sleep(3600)
    except KeyboardInterrupt:
        print ('Exiting by user.')
    print ('')
    ## Get host_write,nand_write again
    if args.interface == "nvme":
        with NVMe(init_device(args.device, open_t='nvme')) as d:
            host_write_end,nand_write_end = get_nvme_write_factor(d, args)
    elif args.interface == "sata":
        with SATA(init_device(args.device, open_t='ata')) as d:
           host_write_end,nand_write_end = get_ata_write_factor(d, args)
    ## calculate WAF
    end_t = time.time()
    wa = calculate_wa(host_write_start, nand_write_start, host_write_end, nand_write_end)
    print ("Total run time: %f seconds, the Write Amplification of disk is %f" % (end_t-start_t, wa))

if __name__ == '__main__':
    main()
