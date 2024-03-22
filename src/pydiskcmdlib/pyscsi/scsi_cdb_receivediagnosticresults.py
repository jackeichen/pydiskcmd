# coding: utf-8
# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later

from pyscsi.pyscsi.scsi_command import SCSICommand
#
# SCSI SynchronizeCache command and definitions
#

class ReceiveDiagnosticResults(SCSICommand):
    """
    A class to hold information from a SynchronizeCache10 command to a scsi device
    """

    _cdb_bits = {
        "opcode": [0xFF, 0],
        "page_code": [0xFF, 2],
        "alloc_length": [0xFFFF, 3],
        "control": [0xFF, 5],
    }

    def __init__(
        self, opcode, blocksize, page_code, alloc_length, control=0
    ):
        """
        initialize a new instance

        :param opcode: a OpCode instance
        :param blocksize: a blocksize
        :param page_code: the page code
        :param alloc_length: 
        :param control: The CONTROL byte is defined in SAM-5
        """
        if blocksize == 0:
            raise SCSICommand.MissingBlocksizeException

        SCSICommand.__init__(self, opcode, 0, blocksize*alloc_length)
        self.cdb = self.build_cdb(
            opcode=self.opcode.value,
            page_code=page_code,
            alloc_length=alloc_length,
            control=control,
        )
