# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import os
from pydiskcmd.common.device import DeviceBase

def get_inode(file):
    #  type: (str) -> int
    return os.stat(file).st_ino


class LinDevice(DeviceBase):
    def __init__(self, 
                 device,
                 readwrite=True,
                 detect_replugged=True):
        super(LinDevice, self).__init__(device, readwrite, detect_replugged)
        ##
        from fcntl import ioctl
        self._ioctl = ioctl
        #
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
        if self._file:
            self.close()
        self._file = open(self._file_name,
                          'w+b' if self._read_write else 'rb')
        self._ino = get_inode(self._file_name)

    def close(self):
        self._file.close()
        self._ino = None

    def execute(self, op, cdb):
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

        ##
        result = self._ioctl(self._file.fileno(), 
                             op, 
                             cdb)
        return result
