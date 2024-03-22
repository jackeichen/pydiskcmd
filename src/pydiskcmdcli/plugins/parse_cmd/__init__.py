# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from .parse_scsi_cdb import parse_cdb
from .parse_scsi_sense_code import parse_sense_code

parse_cmd_plugin = {"cdb": parse_cdb,
                    "sense_code": parse_sense_code,
                    }
