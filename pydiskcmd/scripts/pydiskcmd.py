# SPDX-FileCopyrightText: 2014 The python-scsi Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import optparse
##
from pydiskcmd.pynvme.nvme import code_version as nvme_version
from pydiskcmd.pysata.sata import code_version as ata_version
from pydiskcmd.pyscsi.scsi import code_version as scsi_version
from pydiskcmd.utils.bash_completion import update_pydiskcmd_completion


ToolVersion = "0.1.1"

def pydiskcmd():
    usage="usage: %prog [OPTION] [args...]"
    parser = optparse.OptionParser(usage,version="pydiskcmd " + ToolVersion)
    parser.add_option("", "--en_completion", dest="enable_completion", action="store_true", default=False,
        help="Enable pynvme/pysata bash completion")
    parser.add_option("", "--en_smartd_systemctl", dest="enable_smartd_systemctl", action="store_true", default=False,
        help="Enable pysmartd systemctl ")
    parser.add_option("", "--code_version", dest="code_version", action="store",default="pydiskcmd",
        help="Check code version: pydiskcmd|nvme|ata|scsi, default pydiskcmd")

    (options, args) = parser.parse_args()
    ##
    if options.enable_completion:
        update_pydiskcmd_completion()
    elif options.enable_smartd_systemctl:
        print ("Not support now!")
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
