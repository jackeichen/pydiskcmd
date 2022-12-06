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
    from pydiskcmd.common.device import DeviceBase
    from pydiskcmd.pyscsi.scsi_command import ctypes,SCSIPassThroughDirect,SCSIPassThroughDirectWithBuffer
    import pyscsi.pyscsi.scsi_enum_command as scsi_enum_command
    from pyscsi.pyscsi.scsi_sense import SCSICheckCondition

    class SCSIDevice(DeviceBase):
        def __init__(self, 
                     device,
                     readwrite=True,
                     detect_replugged=True):
            self._opcodes = scsi_enum_command.spc
            super(SCSIDevice, self).__init__(device, readwrite, detect_replugged)
            ##
            self.__kernel32 = None
            self._file = None
            ##
            self.open()

        def _is_replugged(self):
            #  type: (WinDevice) -> bool
            # TODO
            # always return False,
            return False

        def _kernel32(self):
            # Opens the Kernel32.dll, which can be quite a slow process, and
            # saves it for future use.
            if self.__kernel32 is None:
                self.__kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            return self.__kernel32

        def open(self):
            """

            :param dev:
            :param read_write:
            :return:
            """
            self._file = self._kernel32().CreateFileW(self._file_name,
                                                      0x80000000 | 0x40000000,  # GENERIC_READ | GENERIC_WRITE
                                                      0x00000001,  # FILE_SHARE_READ
                                                      None,
                                                      0x00000003,  # OPEN_EXISTING
                                                      0x00000080,  # FILE_ATTRIBUTE_NORMAL,
                                                      None
                                                     )
            if self._file == -1:
                raise ctypes.WinError(ctypes.get_last_error())

        def close(self):
            if self._file:
                self._kernel32().CloseHandle(self._file)
                self._file = None

        def execute(self, cmd, en_raw_sense=False):
            """
            execute a IOCTL command

            :param cmd: a Command Structure
            """
            if self._detect_replugged and self._is_replugged():
                try:
                    self.close()
                finally:
                    self.open()
            try:
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
                ## excute
                result = self._kernel32().DeviceIoControl(self._file, 
                                                          0x4D014, 
                                                          ctypes.pointer(header_with_buffer),
                                                          ctypes.sizeof(header_with_buffer),
                                                          ctypes.pointer(header_with_buffer),
                                                          ctypes.sizeof(header_with_buffer),
                                                          None,
                                                          None)
                if result == 0:
                    raise ctypes.WinError(ctypes.get_last_error())
                # After execute. reinit the datain,
                # for use the pyscsi command structure
                if cmd.datain: 
                    cmd.datain = bytearray(data_buffer)
                # SCSICheckCondition(bytearray(header_with_buffer.sense))
                if en_raw_sense:
                    cmd.raw_sense_data = bytearray(header_with_buffer.sense)
            except:
                traceback.print_exc()
            return cmd

        @property
        def opcodes(self):
            return self._opcodes

        @opcodes.setter
        def opcodes(self,
                    value):
            self._opcodes = value

        @property
        def devicetype(self):
            return self._devicetype

        @devicetype.setter
        def devicetype(self,
                       value):
            self._devicetype = value

elif os_type == "Linux":
    from pyscsi.pyscsi.scsi_device import SCSIDevice
