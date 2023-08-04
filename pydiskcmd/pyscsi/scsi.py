# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pyscsi.pyscsi.scsi import SCSI as _SCSI
from pydiskcmd.pyscsi.scsi_cdb_logsense import LogSense
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

    def logsense(self, page_code, **kwargs):
        """
        Returns a LogSense Instance

        :param page_code:  The page requested
        :param kwargs: a dict with key/value pairs
                       sub_page_code = 0, Requested subpage
                       sp = 0, 
                       pc = 0, 
                       parameter = 0, 
                       alloclen = 512, 
                       control = 0
        :return: a LogSense instance
        """
        opcode = self.device.opcodes.LOG_SENSE
        cmd = LogSense(opcode, page_code, **kwargs)
        self.execute(cmd)
        cmd.unmarshall()
        return cmd
