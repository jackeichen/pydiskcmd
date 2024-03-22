# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import ctypes
from pydiskcmdlib.device.device import DeviceBase

class BytesReturnedStruc(ctypes.Structure):
    _fields_ = [("return_bytes", ctypes.c_uint64),]
    _pack_ = 1

    def __init__(self, return_bytes: int =0):
        self.return_bytes = return_bytes


class WinIOCTLDevice(DeviceBase):
    """
    The IOCTL device class for Windows.
    """
    def __init__(self, 
                 device,
                 readwrite=True,
                 detect_replugged=True):
        """
        initialize a new instance of a WinIOCTLDevice
        :param device: the file descriptor
        :param readwrite: access type
        :param detect_replugged: detects device unplugged and plugged events and ensure executions will not fail
        silently due to replugged events
        """
        super(WinIOCTLDevice, self).__init__(device, readwrite, detect_replugged)
        ##
        self.__kernel32 = None
        self._file = None
        ##
        self.open()

    def _is_replugged(self):
        """
        check if the devide is replugged.

        :return: always true for now
        """
        # TODO
        return True

    @property
    def device_name(self):
        """
        get the device name

        :return: device name, string like PHYSICALDRIVE1
        """
        return self._file_name.replace("\\\\.\\", "")

    def _kernel32(self):
        # Opens the Kernel32.dll, which can be quite a slow process, and
        # saves it for future use.
        """
        Opens the Kernel32.dll, which can be quite a slow process, and
        saves it for future use.

        :return: windows kernel32
        """
        if self.__kernel32 is None:
            self.__kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        return self.__kernel32

    def open(self):
        """
        open the device, it will close the device if the device is opened.

        :return: None
        :raise: ctypes.WinError if close file failed
        """
        if self._file:
            self.close()
        self._file = self._kernel32().CreateFileW(self._file_name,
                                                  (0x80000000 | 0x40000000) if self._read_write else 0x80000000,  # GENERIC_READ | GENERIC_WRITE
                                                  0x00000001,  # FILE_SHARE_READ
                                                  None,
                                                  0x00000003,  # OPEN_EXISTING
                                                  0x00000080,  # FILE_ATTRIBUTE_NORMAL,
                                                  None
                                                 )
        if self._file == -1:
            raise ctypes.WinError(ctypes.get_last_error())

    def close(self):
        """
        close the device if the device is opened.

        :return: None
        """
        if self._file:
            self._kernel32().CloseHandle(self._file)
            self._file = None

    def execute(self, IoControlCode, InBuffer, OutBuffer, BytesReturned=None, Overlapped=None):
        """
        execute a IOCTL command

        :param IoControlCode: a Command IoControlCode
        :param InBuffer: a Command InBuffer
        :param OutBuffer: a Command OutBuffer
        :param BytesReturned: a Command BytesReturned
        :param Overlapped: a Command Overlapped
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
                                                      ctypes.pointer(InBuffer) if InBuffer else None,
                                                      ctypes.sizeof(InBuffer) if InBuffer else 0,
                                                      ctypes.pointer(OutBuffer) if OutBuffer else None,
                                                      ctypes.sizeof(OutBuffer) if OutBuffer else 0,
                                                      ctypes.pointer(BytesReturned) if BytesReturned else None,
                                                      Overlapped)
            if result == 0:
                raise ctypes.WinError(ctypes.get_last_error())
        else:
            raise RuntimeError("Open device first!")
        return result
