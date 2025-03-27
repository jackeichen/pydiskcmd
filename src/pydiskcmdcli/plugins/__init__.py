# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from .ocp import ocp
from .parse_cmd import parse_cmd
from .vroc import win_nvme_vroc
from .csmi import win_csmi
from .broadcom import meraraid_sata
from .broadcom import meraraid_scsi

nvme_plugins = { "ocp": ocp,
                 "vroc": win_nvme_vroc,}

ata_plugins = {"megaraid": meraraid_sata}

scsi_plugins = {"parse-cmd": parse_cmd,
                "csmi": win_csmi,
                "megaraid": meraraid_scsi,}
