# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import ctypes
from pydiskcmdlib.device.device import DeviceBase
from pydiskcmdlib import log

class BytesReturnedStruc(ctypes.Structure):
    _fields_ = [("return_bytes", ctypes.c_uint32),]
    _pack_ = 1

    def __init__(self, return_bytes: int =0):
        self.return_bytes = return_bytes


class WinIOCTLDevice(DeviceBase):
    """
    The IOCTL device class for Windows.
    
    Initialize a new instance of a WinIOCTLDevice.

    :param device: The file descriptor representing the device.
    :param readwrite: Boolean indicating the access type. True for read-write, False for read-only.
    :param detect_replugged: Boolean to enable detection of device unplugged and plugged events.
                             If True, ensures that executions will not fail silently due to replugged events.
    :param share_mode: The file sharing mode, default is FILE_SHARE_READ (0x00000001).
    :param flags_and_attributes: The file attributes, default is FILE_ATTRIBUTE_NORMAL (0x00000080).
    See https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilea for details.
    """
    DevIDCount = 0
    def __init__(self, 
                 device,
                 readwrite=True,
                 detect_replugged=True,
                 share_mode=0x00000001, # FILE_SHARE_READ
                 flags_and_attributes=0x00000080, # FILE_ATTRIBUTE_NORMAL
                 ):
        """
        initialize a new instance of a WinIOCTLDevice
        :param device: the file descriptor
        :param readwrite: access type
        :param detect_replugged: detects device unplugged and plugged events and ensure executions will not fail
        silently due to replugged events
        """
        super(WinIOCTLDevice, self).__init__(device, readwrite, detect_replugged)
        self._share_mode = share_mode
        self._flags_and_attributes = flags_and_attributes
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
        return False

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
        log.debug("Opening Windows device[%s], readwrite=%s, detect_replugged=%s, share_mode=%#x, flags_and_attributes=%#x" % (self._file_name,
                                                                                                                               self._read_write,
                                                                                                                               self._detect_replugged,
                                                                                                                               self._share_mode,
                                                                                                                               self._flags_and_attributes,
                                                                                                                               ))
        self._file = self._kernel32().CreateFileW(self._file_name,
                                                  (0x80000000 | 0x40000000) if self._read_write else 0x80000000,  # GENERIC_READ | GENERIC_WRITE
                                                  self._share_mode,  # FILE_SHARE_Mode
                                                  None,
                                                  0x00000003,  # OPEN_EXISTING
                                                  self._flags_and_attributes,  # FILE_ATTRIBUTE,
                                                  None
                                                 )
        log.debug("CreateFileW return %s" % self._file)
        if self._file == -1:
            raise ctypes.WinError(ctypes.get_last_error())
        WinIOCTLDevice.DevIDCount += 1

    def close(self):
        """
        close the device if the device is opened.

        :return: None
        """
        if self._file:
            log.debug("Closing Windows device[%s], file=%s" % (self._file_name, self._file))
            self._kernel32().CloseHandle(self._file)
            self._file = None
            WinIOCTLDevice.DevIDCount -= 1

    def execute(self, IoControlCode, InBuffer, OutBuffer, BytesReturned=None, Overlapped=None, raise_if_fail=True):
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
            if result == 0 and raise_if_fail:
                log.debug("Execute Command failed: %s" % ctypes.get_last_error())
                raise ctypes.WinError(ctypes.get_last_error())
        else:
            log.debug("Open device first!")
            raise RuntimeError("Open device first!")
        return result
