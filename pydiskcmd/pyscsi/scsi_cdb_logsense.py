# coding: utf-8
# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later

import pyscsi.pyscsi.scsi_enum_modesense as modesense_enums
from pyscsi.pyscsi.scsi_command import SCSICommand
from pyscsi.utils.converter import (
    decode_bits,
    encode_dict,
    scsi_ba_to_int,
    scsi_int_to_ba,
)

#
# SCSI LogSelect/LogSense command and definitions
#


class LogSense(SCSICommand):
    """
    A class to hold information from a LogSense command
    """

    _cdb_bits = {
        "opcode": [0xFF, 0],
        "sp": [0x01, 1],
        "page_code": [0x3F, 2],
        "pc": [0xC0, 2],
        "sub_page_code": [0xFF, 3],
        "parameter": [0xFFFF, 5],
        "alloc_len": [0xFFFF, 7],
        "control": [0xFF, 9],
    }

    def __init__(
        self, opcode, page_code, sub_page_code=0, sp=0, pc=0, parameter=0, alloclen=512, control=0
    ):
        """
        initialize a new instance

        :param opcode: a OpCode instance
        :param page_code: the page code for the vpd page
        :param sub_page_code: a integer representing a sub page code
        :param sp: a integer representing whether the device server shall save parameters to nonvolatile memory
        :param parameter: a integer representing the application client to request parameter data beginning
        :param pc: page control field, a value between 0 and 3
        :param alloclen: the max number of bytes allocated for the data_in buffer
        :param control: The CONTROL byte is defined in SAM-5
        """
        SCSICommand.__init__(self, opcode, 0, alloclen)
        self.cdb = self.build_cdb(
            opcode=self.opcode.value,
            page_code=page_code,
            sub_page_code=sub_page_code,
            sp=sp,
            parameter=parameter,
            pc=pc,
            control=control,
            alloc_len=alloclen,
        )

    @classmethod
    def unmarshall_datain(cls, data):
        """
        Unmarshall the ModeSense10 datain.

        :param data: a byte array
        :return result: a dict
        """
        pass

    @classmethod
    def marshall_datain(cls, data):
        """
        Marshall the ModeSense10 datain.

        :param data: a dict
        :return result: a byte array
        """
        pass


class LogSelect(SCSICommand):
    """
    A class to hold information from a LogSelect command
    """

    _cdb_bits = {
        "opcode": [0xFF, 0],
        "sp": [0x01, 1],
        "pcr": [0x02, 1],
        "page_code": [0x3F, 2],
        "pc": [0xC0, 2],
        "sub_page_code": [0xFF, 3],
        "parameter_list_length": [0xFFFF, 7],
        "control": [0xFF, 9],
    }

    def __init__(
        self, opcode, page_code, sub_page_code=0, sp=0, pcr=0, pc=0, parameter_list_length=96, control=0
    ):
        """
        initialize a new instance

        :param opcode: a OpCode instance
        :param page_code: the page code for the vpd page
        :param sub_page_code: a integer representing a sub page code
        :param sp: a integer representing whether the device server shall save parameters to nonvolatile memory
        :param pcr: a integer representing whether the device server shall set parameters to their vendor  specific default values
        :param pc: page control field, a value between 0 and 3
        :param parameter_list_length: the max number of bytes allocated for the data_in buffer
        :param control: The CONTROL byte is defined in SAM-5
        """
        raise NotImplementedError("LogSelect Not Implemented")

    @classmethod
    def unmarshall_datain(cls, data):
        """
        Unmarshall the ModeSense10 datain.

        :param data: a byte array
        :return result: a dict
        """
        pass

    @classmethod
    def marshall_datain(cls, data):
        """
        Marshall the ModeSense10 datain.

        :param data: a dict
        :return result: a byte array
        """
        pass

