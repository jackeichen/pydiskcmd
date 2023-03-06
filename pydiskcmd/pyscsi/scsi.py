# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pyscsi.pyscsi.scsi import SCSI as _SCSI
###
code_version = "0.0.1"
###


class SCSI(_SCSI):
    def __init__(self, 
                 dev,
                 blocksize=0):
        super(SCSI, self).__init__(dev, blocksize=blocksize)

    def __del__(self):
        if self.device:
            self.device.close()
