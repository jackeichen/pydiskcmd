# coding: utf-8
# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from abc import ABCMeta, abstractmethod


class DeviceBase(object):
    """
    This Class define the function that must be implemented by device function.
    """
    def __init__(self,
                 device: str,
                 readwrite: bool,
                 detect_replugged: bool):
        """
        initialize a  new instance of a DeviceBase
        :param device: the file descriptor
        :param readwrite: access type
        :param detect_replugged: detects device unplugged and plugged events and ensure executions will not fail
        silently due to replugged events
        """
        self._file_name = device
        self._read_write = readwrite
        self._detect_replugged = detect_replugged
        # The devcie type
        self._devicetype = None

    def __del__(self):
        self.close() 

    def __enter__(self):
        """
        :return: return the class itself
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

    @abstractmethod
    def _is_replugged(self):
        """ Methmod to detect if a devcie plugged. """

    @abstractmethod
    def open(self):
        """ Methmod to open a devcie. """

    @abstractmethod
    def close(self):
        """ Methmod to close a devcie. """

    @abstractmethod
    def execute(self, cmd):
        """ Methmod to execute a command to the devcie. """

    @property
    def opcodes(self):
        """
        This maybe unnecessary sometimes, to maintain consistency with pyscsi.pyscsi.scsi_device

        :return: the opcode used by command
        """
        return self._opcodes

    @opcodes.setter
    def opcodes(self, value):
        """
        Setting opcodes, maybe unnecessary sometimes, to maintain consistency with 
        pyscsi.pyscsi.scsi_device
        :param value: opcode instance that used by command

        :return:
        """
        self._opcodes = value

    @property
    def devicetype(self):
        """
        This maybe unnecessary sometimes, to maintain consistency with pyscsi.pyscsi.scsi_device

        :return: the devicetype of the device
        """
        return self._devicetype

    @devicetype.setter
    def devicetype(self, value):
        """
        Setting devicetype, maybe unnecessary sometimes, to maintain consistency with 
        pyscsi.pyscsi.scsi_device
        :param value: devicetype instance that used by device

        :return:
        """
        self._devicetype = value
