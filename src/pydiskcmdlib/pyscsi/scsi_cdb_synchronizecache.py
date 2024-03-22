# coding: utf-8
# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later

from pyscsi.pyscsi.scsi_command import SCSICommand
#
# SCSI SynchronizeCache command and definitions
#

class SynchronizeCache10(SCSICommand):
    """
    A class to hold information from a SynchronizeCache10 command to a scsi device
    """

    _cdb_bits = {
        "opcode": [0xFF, 0],
        "immed": [0x02, 1],
        "lba": [0xFFFFFFFF, 2],
        "group_number": [0x1F, 6],
        "block_number": [0xFFFF, 7],
        "control": [0xFF, 9],
    }

    def __init__(
        self, opcode, lba, block_number, immed=0, group_number=0, control=0
    ):
        """
        initialize a new instance

        :param opcode: a OpCode instance
        :param lba: the LOGICAL BLOCK ADDRESS field
        :param block_number: a integer representing NUMBER OF BLOCKS
        :param immed: a integer representing Immediate
        :param group_number: the group into which attributes associated with the command should be collected
        :param control: The CONTROL byte is defined in SAM-5
        """
        SCSICommand.__init__(self, opcode, 0, 0)
        self.cdb = self.build_cdb(
            opcode=self.opcode.value,
            lba=lba,
            block_number=block_number,
            immed=immed,
            group_number=group_number,
            control=control,
        )


class SynchronizeCache16(SCSICommand):
    """
    A class to hold information from a SynchronizeCache16 command to a scsi device
    """

    _cdb_bits = {
        "opcode": [0xFF, 0],
        "immed": [0x02, 1],
        "lba": [0xFFFFFFFFFFFFFFFF, 2],
        "block_number": [0xFFFFFFFF, 10],
        "group_number": [0x1F, 14],
        "control": [0xFF, 15],
    }

    def __init__(
        self, opcode, lba, block_number, immed=0, group_number=0, control=0
    ):
        """
        initialize a new instance

        :param opcode: a OpCode instance
        :param lba: the LOGICAL BLOCK ADDRESS field
        :param block_number: a integer representing NUMBER OF BLOCKS
        :param immed: a integer representing Immediate
        :param group_number: the group into which attributes associated with the command should be collected
        :param control: The CONTROL byte is defined in SAM-5
        """
        SCSICommand.__init__(self, opcode, 0, 0)
        self.cdb = self.build_cdb(
            opcode=self.opcode.value,
            lba=lba,
            block_number=block_number,
            immed=immed,
            group_number=group_number,
            control=control,
        )
