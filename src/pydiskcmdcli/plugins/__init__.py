# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from .ocp import ocp
from .parse_cmd import parse_cmd
from .vroc import win_nvme_vroc
from .csmi import win_csmi
from .broadcom import meraraid_sata
from .broadcom import meraraid_scsi
from .pcie import pci
from .rst import win_sata_rst
from .nvme_mi import nvme_mi
try:
    from .lenovo import lenovo
except:
    def lenovo():
        raise RuntimeError("Function Not in Public release!")

nvme_plugins = { "ocp": ocp,
                 "vroc": win_nvme_vroc,
                 "pci":pci,
                 "mi": nvme_mi,
                 }

ata_plugins = {"megaraid": meraraid_sata,
               "rst": win_sata_rst,
               }

scsi_plugins = {"parse-cmd": parse_cmd,
                "lenovo": lenovo,
                "csmi": win_csmi,
                "megaraid": meraraid_scsi,}
