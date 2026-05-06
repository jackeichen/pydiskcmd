# coding: utf-8
# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later

from pyscsi.pyscsi.scsi_command import SCSICommand
#
# SCSI SynchronizeCache command and definitions
#


class Sanitize(SCSICommand):
    """
    A class to hold information from a Sanitize command to a scsi device
    """

    _cdb_bits = {
        "opcode": [0xFF, 0],
        "service_action": [0x1F, 1],
        "ause": [0x20, 1],
        "znr": [0x40, 1],
        "immed": [0x80, 1],
        "para_list_len": [0xFFFF, 7],
        "control": [0xFF, 9],
    }

    def __init__(
        self, opcode, service_action, ause, znr, immed, para_list_len, control=0, data=None,
    ):
        """
        initialize a new instance

        :param opcode: a OpCode instance
        :param service_action: a integer representing Service action
        :param ause: a integer representing Allow unrestricted sanitize exit
        :param znr: a integer representing ZNR
        :param immed: a integer representing Immediate
        :param para_list_len: a integer representing Parameter list length
        :param control: The CONTROL byte is defined in SAM-5
        :param data: a byte array with data
        """
        if data is not None:
            SCSICommand.__init__(self, opcode, len(data), 0)
            self.dataout = data
        else:
            SCSICommand.__init__(self, opcode, 0, 0)
        self.cdb = self.build_cdb(
            opcode=self.opcode.value,
            service_action=service_action,
            ause=ause,
            znr=znr,
            immed=immed,
            para_list_len=para_list_len,
            control=control,
        )
