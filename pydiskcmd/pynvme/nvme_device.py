# coding: utf-8
# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later

import os
import traceback
from pydiskcmd.system.os_tool import os_type
from pydiskcmd.common.device import DeviceBase


def get_inode(file):
    #  type: (str) -> int
    return os.stat(file).st_ino

if os_type == "Linux":
    from fcntl import ioctl
    ## Linux device
    class NVMeDevice(DeviceBase):
        def __init__(self, 
                     device,
                     readwrite=False,
                     detect_replugged=True):
            super(NVMeDevice, self).__init__(device, readwrite, detect_replugged)
            ##
            self._file = None
            self._ino = None
            ## open device
            self.open()

        def _is_replugged(self):
            #  type: (LinuxIOCTLDevice) -> bool
            ino = get_inode(self._file_name)
            return ino != self._ino

        def open(self):
            """
            :param dev:
            :param read_write:
            :return:
            """
            self._file = open(self._file_name,
                              'w+b' if self._read_write else 'rb')
            self._ino = get_inode(self._file_name)

        def close(self):
            self._file.close()
    
        def execute(self, cmd):
            """
            execute a nvme command (admin, IO)

            :param cmd: a NVMe Command Object
            :return: a NVMe Command Object
            """
            if self._detect_replugged and self._is_replugged():
                try:
                    self.close()
                finally:
                    self.open()

            try:
                cmd.cq_status = ioctl(self._file.fileno(), 
                                      cmd.req_id, 
                                      cmd.cdb)
            except:
                traceback.print_exc()
            return cmd

elif os_type == "Windows":
    import win32file
    class NVMeDevice(DeviceBase):
        def __init__(self, 
                     device,
                     readwrite=True,
                     detect_replugged=True):
            super(NVMeDevice, self).__init__(device, readwrite, detect_replugged)
            ##
            self._file = None
            self._ino = None
            ##
            self.open()

        def _is_replugged(self):
            #  type: (WinDevice) -> bool
            ino = get_inode(self._file_name)
            return ino != self._ino

        def open(self):
            """

            :param dev:
            :param read_write:
            :return:
            """
            open_t = (win32file.GENERIC_READ | win32file.GENERIC_WRITE) if self._read_write else (win32file.GENERIC_READ)
            share_t = (win32file.FILE_SHARE_READ | win32file.FILE_SHARE_WRITE) if self._read_write else (win32file.FILE_SHARE_READ)
            self._file = win32file.CreateFile(self._file_name,
                                              win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                                              win32file.FILE_SHARE_READ|win32file.FILE_SHARE_WRITE,
                                              None,
                                              win32file.OPEN_EXISTING,
                                              0,
                                              None)
            self._ino = get_inode(self._file_name)

        def close(self):
            if self._file:
                win32file.CloseHandle(self._file)
                self._file = None

        def execute(self, cmd):
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
                cmd.cq_status = win32file.DeviceIoControl(self._file,  # file
                                                          cmd.req_id,      # IOControl Code to use, from winioctlcon
                                                          cmd.cdb,      # datain
                                                          cmd.cdb,      # dataout
                                                          None)
            except:
                traceback.print_exc()
            return cmd
else:
    raise NotImplementedError("%s not support" % os_type)
