# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import ctypes
from pydiskcmd.common.device import DeviceBase

class WinDevice(DeviceBase):
    def __init__(self, 
                 device,
                 readwrite=True,
                 detect_replugged=True):
        super(WinDevice, self).__init__(device, readwrite, detect_replugged)
        ##
        self.__kernel32 = None
        self._file = None
        ##
        self.open()

    def _is_replugged(self):
        # type: (WinDevice) -> bool
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
        if self._file:
            self.close()
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

    def execute(self, IoControlCode, InBuffer, OutBuffer, BytesReturned=None, Overlapped=None):
        """
        execute a IOCTL command

        :param cmd: a Command Structure
        """
        if self._detect_replugged and self._is_replugged():
            try:
                self.close()
            finally:
                self.open()
        ##
        result = None
        if self._file:
            # excute
            result = self._kernel32().DeviceIoControl(self._file, 
                                                      IoControlCode, 
                                                      ctypes.pointer(InBuffer),
                                                      ctypes.sizeof(InBuffer),
                                                      ctypes.pointer(OutBuffer),
                                                      ctypes.sizeof(OutBuffer),
                                                      BytesReturned,
                                                      Overlapped)
            if result == 0:
                raise ctypes.WinError(ctypes.get_last_error())
        else:
            raise RuntimeError("Open device first!")
        return result
