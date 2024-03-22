# coding: utf-8
# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later

from pyscsi.pyscsi.scsi_command import SCSICommand
from pyscsi.pyscsi.scsi_opcode import OpCode
from pydiskcmdlib.exceptions import BuildSCSICommandError

#
# SCSI SynchronizeCache command and definitions
#

class CDBPassthru(SCSICommand):
    """
    A class to hold information from a CDBPassthru command to a scsi device
    """

    _cdb_bits = {
        "opcode": [0xFF, 0],
    }

    def __init__(
        self, raw_cdb, dataout=b'', datain_alloclen=0
    ):
        """
        initialize a new instance

        :param raw_cdb: a CDB Format bytes
        :param dataout: the data_out buffer
        :param datain_alloclen: integer representing the size of the data_in buffer
        """
        dataout_alloclen = len(dataout)
        ## OPCode is usally in the first byte
        opcode = OpCode("", raw_cdb[0], {})
        SCSICommand.__init__(self, opcode, dataout_alloclen, datain_alloclen)
        if dataout:
            self.dataout = dataout
        # check the legality of CDB format 
        if len(SCSICommand._cdb) == len(raw_cdb):
            self.cdb = bytearray(raw_cdb)
        else:
            raise BuildSCSICommandError("Illegal CDB Format building Passthru CDB")
