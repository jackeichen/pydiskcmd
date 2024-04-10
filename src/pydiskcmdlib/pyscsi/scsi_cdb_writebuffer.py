# coding: utf-8

# Copyright (C) 2014 by Ronnie Sahlberg<ronniesahlberg@gmail.com>
# SPDX-FileCopyrightText: 2014 The python-scsi Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later

from pyscsi.pyscsi.scsi_command import SCSICommand

#
# SCSI Write10 command and definitions
#


class WriteBuffer(SCSICommand):
    """
    A class to send a Write Buffer command to a scsi device
    """

    _cdb_bits = {
        "opcode": [0xFF, 0],
        "mode": [0x1F, 1],
        "mode_spec": [0xE0, 1],
        "bufer_id": [0xFF, 2],
        "bufer_offset": [0xFFFFFF, 3],
        "para_list_length": [0xFFFFFF, 6],
        "control": [0xFF, 9],
    }

    def __init__(
        self, opcode, mode, mode_spec, bufer_id, bufer_offset, para_list_length, data=None, control=0,
    ):
        """
        initialize a new instance

        :param opcode: an OpCode instance
        :param mode: mode
        :param mode_spec: mode specific
        :param bufer_id: buffer ID
        :param bufer_offset: buffer offset
        :param para_list_length: parameter list length
        :param data: a byte array with data
        :param control=0: control bit, see SAM-5
        """
        if data is None:
            data = bytearray(0)
        if data and not isinstance(data, bytearray):
            data = bytearray(data)
        SCSICommand.__init__(self, opcode, len(data), 0)
        self.dataout = data
        self.cdb = self.build_cdb(
            opcode=self.opcode.value,
            mode=mode,
            mode_spec=mode_spec,
            bufer_id=bufer_id,
            bufer_offset=bufer_offset,
            para_list_length=para_list_length,
            control=control,
        )
