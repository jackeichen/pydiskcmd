# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pyscsi.pyscsi.scsi_sense import sense_key_dict,sense_ascq_dict
sense_ascq_dict[0x0000] = "NO ADDITIONAL SENSE INFORMATION"

def parse_sense_code(asc, ascq, sense_key=None):
    index = (asc << 8) + ascq
    if sense_key is None:
        return sense_ascq_dict.get(index)
    else:
        return sense_ascq_dict.get(index),sense_key_dict.get(sense_key)
