# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from .ocp import ocp
from .parse_cmd import parse_cmd
from .vroc import win_nvme_vroc
from .lenovo import lenovo

nvme_plugins = { "ocp": ocp,
                 "vroc": win_nvme_vroc,}

ata_plugins = {}

scsi_plugins = {"parse-cmd": parse_cmd,
                }
