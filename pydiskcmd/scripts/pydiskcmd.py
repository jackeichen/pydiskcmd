# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import optparse
##
from pydiskcmd.pynvme.nvme import code_version as nvme_version
from pydiskcmd.pysata.sata import code_version as ata_version
from pydiskcmd.pyscsi.scsi import code_version as scsi_version
from pydiskcmd.system.bash_completion import update_pydiskcmd_completion
from pydiskcmd.system.pydiskhealth_daemon import enable_systemd_pydiskhealthd
from pydiskcmd.__version__ import version as ToolVersion

def pydiskcmd():
    usage="usage: %prog [OPTION] [args...]"
    parser = optparse.OptionParser(usage,version="pydiskcmd " + ToolVersion)
    parser.add_option("", "--en_completion", dest="enable_completion", action="store_true", default=False,
        help="Enable pynvme/pysata bash completion")
    parser.add_option("", "--en_diskhealth_daemon", dest="en_diskhealth_daemon", action="store_true", default=False,
        help="Enable pysmartd systemctl diskhealth daemon")
    parser.add_option("", "--show_temperature", dest="show_temperature", action="store_true", default=False,
        help="Show the history of disk temperature")
    parser.add_option("", "--code_version", dest="code_version", action="store",default="pydiskcmd",
        help="Check code version: pydiskcmd|nvme|ata|scsi, default pydiskcmd")

    (options, args) = parser.parse_args()
    ##
    if options.enable_completion:
        update_pydiskcmd_completion()
    elif options.en_diskhealth_daemon:
        enable_systemd_pydiskhealthd()
    elif options.show_temperature:
        from pydiskcmd.pydiskhealthd.DB import disk_trace_pool
        for disk_id,table in disk_trace_pool.disk_trace_pool.items():
            pass
    elif options.code_version:
        if options.code_version == "pydiskcmd":
            print ('')
            print ('pydiskcmd version: %s' % ToolVersion)
            print ('')
        elif options.code_version == "nvme":
            print ('')
            print ('NVMe code version: %s' % nvme_version)
            print ('')
        elif options.code_version == "ata":
            print ('')
            print ('ATA code version: %s' % ata_version)
            print ('')
        elif options.code_version == "scsi":
            print ('')
            print ('SCSI code version: %s' % scsi_version)
            print ('')
        else:
            parser.error("Args of check code version should be one of pydiskcmd|nvme|ata|scsi")
    else:
        parser.print_help()
