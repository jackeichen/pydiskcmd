# coding: utf-8
# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from abc import ABCMeta, abstractmethod


class DeviceBase(object):
    '''
    This Class define the function that must be implemented by device function.
    '''
    def __init__(self,
                 device,
                 readwrite,
                 detect_replugged):
        self._file_name = device
        self._read_write = readwrite
        self._detect_replugged = detect_replugged
        # The devcie type
        self._devicetype = None

    def __del__(self):
        self.close() 

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

    @abstractmethod
    def _is_replugged(self):
        """ Methmod to detect a devcie plugged. """

    @abstractmethod
    def open(self):
        """ Methmod to open a devcie. """

    @abstractmethod
    def close(self):
        """ Methmod to close a devcie. """

    @abstractmethod
    def execute(self, cmd):
        """ Methmod to execute a command to devcie. """

    @property
    def opcodes(self):
        return self._opcodes

    @opcodes.setter
    def opcodes(self, value):
        self._opcodes = value

    @property
    def devicetype(self):
        return self._devicetype

    @devicetype.setter
    def devicetype(self,
                   value):
        self._devicetype = value
