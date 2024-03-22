# coding: utf-8

# Copyright (C) 2014 by Ronnie Sahlberg<ronniesahlberg@gmail.com>
# SPDX-FileCopyrightText: 2014 The python-scsi Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later

from pyscsi.pyscsi.scsi_command import SCSICommand

#
# SCSI SecurityProtocolIn command and definitions
#


class SecurityProtocolIn(SCSICommand):
    """
    A class to send a SecurityProtocolIn command to a scsi device
    """

    _cdb_bits = {
        "opcode": [0xFF, 0],
        "security_protocol": [0xFF, 1],
        "security_protocol_sp": [0xFFFF, 2],
        "INC_512": [0x80, 4],
        "alloc": [0xFFFFFFFF, 6],
        "control": [0xFF, 11],
    }

    def __init__(
        self, opcode, security_protocol, security_protocol_sp, alloc, INC_512=1, control=0,
    ):
        """
        initialize a new instance

        :param opcode: a OpCode instance
        :param security_protocol: a blocksize
        :param security_protocol_sp: Logical Block Address
        :param alloc: number of block
        :param INC_512=1: transfer block size setting, 0: 1 byte, 1: 512 bytes 
        :param control=0: The CONTROL byte is defined in SAM-5
        
        Note:
        libata-scsi.c write:
         * Filter TPM commands by default. These provide an
         * essentially uncontrolled encrypted "back door" between
         * applications and the disk. Set libata.allow_tpm=1 if you
         * have a real reason for wanting to use them. This ensures
         * that installed software cannot easily mess stuff up without
         * user intent. DVR type users will probably ship with this enabled
         * for movie content management.
         *
         * Note that for ATA8 we can issue a DCS change and DCS freeze lock
         * for this and should do in future but that it is not sufficient as
         * DCS is an optional feature set. Thus we also do the software filter
         * so that we comply with the TC consortium stated goal that the user
         * can turn off TC features of their system.
        """
        SCSICommand.__init__(self, opcode, 0, (alloc * INC_512 * 512) if INC_512 > 0 else alloc)

        self.cdb = self.build_cdb(
            opcode=self.opcode.value,
            security_protocol=security_protocol,
            security_protocol_sp=security_protocol_sp,
            INC_512=INC_512,
            alloc=alloc,
            control=control,
        )
