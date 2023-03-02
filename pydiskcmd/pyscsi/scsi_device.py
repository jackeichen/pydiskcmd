# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import traceback
from pydiskcmd.system.os_tool import os_type

if os_type == "Windows":
    ########################################
    # Some code is from smartie, project in: 
    # https://github.com/TkTech/smartie
    # Author: Tyler Kennedy
    ########################################
    from pydiskcmd.common.win_device import WinDevice,ctypes
    from pydiskcmd.pyscsi.scsi_command import SCSIPassThroughDirect,SCSIPassThroughDirectWithBuffer
    import pyscsi.pyscsi.scsi_enum_command as scsi_enum_command
    from pyscsi.pyscsi.scsi_sense import SCSICheckCondition

    class SCSIDevice(WinDevice):
        def __init__(self, 
                     device,
                     readwrite=True,
                     detect_replugged=True):
            self._opcodes = scsi_enum_command.spc
            super(SCSIDevice, self).__init__(device, readwrite, detect_replugged)

        def execute(self, cmd, en_raw_sense=False):
            """
            execute a IOCTL command

            :param cmd: a Command Structure
            """
            ## create SCSIPassThroughDirect Or SCSIPassThroughDirectWithBuffer
            # will transfer SCSICommand to windows mode
            cdb = (ctypes.c_ubyte * 16).from_buffer_copy(
                cmd.cdb.ljust(16, b'\x00')  # noqa
            )

            if cmd.datain:
                direction = 1     ## read from device
                data_transfer_length = len(cmd.datain)
                data_buffer = ctypes.create_string_buffer(data_transfer_length)
            elif cmd.dataout:
                direction = 0     ## write to device
                data_transfer_length = len(cmd.dataout)
                data_buffer = ctypes.create_string_buffer(bytes(cmd.dataout), data_transfer_length)
            else:
                direction = 0
                data_transfer_length = 0
                data_buffer = ctypes.create_string_buffer(b'', 0)
            timeout = 18000
            ## create SCSIPassThroughDirect
            header_sptd = SCSIPassThroughDirect(
                length=ctypes.sizeof(SCSIPassThroughDirect),
                data_in=direction,
                data_transfer_length=data_transfer_length,
                data_buffer=ctypes.addressof(data_buffer),
                cdb_length=len(cmd.cdb),
                cdb=cdb,
                timeout_value=timeout,
                sense_info_length=(
                    SCSIPassThroughDirectWithBuffer.sense.size
                ),
                sense_info_offset=(
                    SCSIPassThroughDirectWithBuffer.sense.offset
                )
            )
            # create SCSIPassThroughDirectWithBuffer
            header_with_buffer = SCSIPassThroughDirectWithBuffer(sptd=header_sptd)
            ## execute
            result = WinDevice.execute(self, 
                                       0x4D014,
                                       header_with_buffer,
                                       header_with_buffer)
            ## After execute. will transfer result to Command Structure
            if cmd.datain: 
                cmd.datain = bytearray(data_buffer)
            # SCSICheckCondition(bytearray(header_with_buffer.sense))
            if en_raw_sense:
                cmd.raw_sense_data = bytearray(header_with_buffer.sense)
            return cmd

elif os_type == "Linux":
    from pyscsi.pyscsi.scsi_device import SCSIDevice
