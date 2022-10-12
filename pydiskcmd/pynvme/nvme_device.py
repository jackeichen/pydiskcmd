# coding: utf-8
# SPDX-FileCopyrightText: 2014 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later

import os
import traceback
from pydiskcmd.pynvme.linux_nvme import execute_admin_cmd,execute_io_cmd


def get_inode(file):
    #  type: (str) -> int
    return os.stat(file).st_ino


class NVMeDevice(object):
    def __init__(self,
                 device,
                 readwrite=False,
                 detect_replugged=True):
        self._file_name = device
        self._read_write = readwrite
        self._file = None
        self._ino = None
        self._detect_replugged = detect_replugged

    def __enter__(self):
        """

        :return:
        """
        return self

    def __exit__(self,
                 exc_type,
                 exc_val,
                 exc_tb):
        """

        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        """
        self.close()

    def __repr__(self):
        """

        :return:
        """
        return self.__class__.__name__

    def _is_replugged(self):
        #  type: (NVMeDevice) -> bool
        ino = get_inode(self._file_name)
        return ino != self._ino

    def open(self):
        """

        :param dev:
        :param read_write:
        :return: None
        """
        self._file = open(self._file_name,
                          'w+b' if self._read_write else 'rb')
        self._ino = get_inode(self._file_name)

    def close(self):
        if self._file:
            self._file.close()

    def execute(self, cmd_t, cmd):
        """
        execute a nvme command (admin, IO)

        :param cmd_t: cmd type, 0-> admin cmd, 1-> io cmd
        :param cmd: a NVMe Command Structure
        :return: CommandDecoder type
        """
        if self._detect_replugged and self._is_replugged():
            try:
                self.close()
            finally:
                self.open()
        ret = None
        try:
            if cmd_t == 0:
                ret = execute_admin_cmd(self._file, cmd)
            else:
                ret = execute_io_cmd(self._file, cmd)
        except:
            traceback.print_exc()
        return ret
