# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmdlib.device.device import DeviceBase
from pyscsi.pyscsi import scsi_device
from pyscsi.pyscsi.scsi_device import SCSIDevice,get_inode
from pydiskcmdlib import log
# cython-sgio is not the only choise, if it is not installed,
# and then python-sgio will be imported(locate in pydiskcmdlib)
# The Source Code is from https://github.com/goodes/python-sgio
# Thanks to the author: goodes
if scsi_device._has_sgio:
    class LinSGIODevice(SCSIDevice):
        """
        The scsi SGIO device class for Linux.
        See pyscsi.pyscsi.scsi_device for more detail.
        """
        def __init__(self, *args, **kwargs):
            SCSIDevice.__init__(self, *args, **kwargs)

        @property
        def device_name(self):
            return self._file_name.replace("/dev/", "")
else:
    try:
        from pydiskcmdlib import sgio
        scsi_device.sgio = sgio
        scsi_device._has_sgio = True
    except ImportError as e:
        scsi_device._has_sgio = False
    ##
    class LinSGIODevice(SCSIDevice):
        """
        The scsi SGIO device class for Linux.
        See pyscsi.pyscsi.scsi_device for more detail.
        
        If cython-sgio is not installed, the local sgio will be imported:
        Import the sgio from cython-sgio OR python-sgio
        """
        def __init__(self, *args, **kwargs):
            log.debug("Opening SCSi device %s, read write flag is %s, detect replugged is %s" % (args[0], 
                                                                                                 kwargs.get("readwrite"), 
                                                                                                 kwargs.get("detect_replugged")))
            SCSIDevice.__init__(self, *args, **kwargs)

        @property
        def device_name(self):
            return self._file_name.replace("/dev/", "")

        def execute(self, cmd, en_raw_sense=False):
            """
            execute a scsi command

            :param cmd: a SCSICommand
            """
            if self._detect_replugged and self._is_replugged():
                try:
                    self.close()
                finally:
                    self.open()
            log.debug("Sending SCSi Command: %s" % " ".join(["%X" % i for i in cmd.cdb]))
            result = sgio.execute(self._file, cmd.cdb, cmd.dataout, cmd.datain, return_sense_buffer=en_raw_sense)
            if en_raw_sense:
                resid,cmd.raw_sense_data = result
            else:
                resid = result
            log.debug("Sense Data: %s" % " ".join(["%X" % i for i in cmd.raw_sense_data]) if cmd.raw_sense_data else 'NA')
            return resid


class LinIOCTLDevice(DeviceBase):
    """
    The IOCTL device class for Linux
    A basic workflow for using a device would be:
        - try to open the device passed by the device arg
        - before execute the command, check the replugge event, reopen the device if necessary.
        - execute the command
        - close the device after all the commands.
    """
    def __init__(self, 
                 device,
                 readwrite=True,
                 detect_replugged=True):
        """
        initialize a new instance of a LinIOCTLDevice
        :param device: the file descriptor
        :param readwrite: access type
        :param detect_replugged: detects device unplugged and plugged events and ensure executions will not fail
        silently due to replugged events
        """
        super(LinIOCTLDevice, self).__init__(device, readwrite, detect_replugged)
        ## init the ioctl engine
        from fcntl import ioctl
        self._ioctl = ioctl
        ##
        self._file = None
        self._ino = None
        ## open device
        self.open()

    def _is_replugged(self):
        """
        check if the devide is replugged

        :return: True or False
        """
        ino = get_inode(self._file_name)
        return ino != self._ino

    @property
    def device_name(self):
        """
        get the device name

        :return: device name, string like sdb or nvme1
        """
        return self._file_name.replace("/dev/", "")

    def open(self):
        """
        open the device, it will close the device if the device is opened.

        :return: None
        """
        if self._file:
            self.close()
        self._file = open(self._file_name,
                          'w+b' if self._read_write else 'rb')
        self._ino = get_inode(self._file_name)

    def close(self):
        """
        close the device if the device is opened.

        :return: None
        """
        if self._file:
            self._file.close()
            self._file = None
            self._ino = None

    def execute(self, op: int, cdb):
        """
        execute a command (admin, IO)

        :param op: a operation code used by cdb
        :param cdb: a 
        :return: a ioctl return code
        """
        if self._detect_replugged and self._is_replugged():
            try:
                self.close()
            finally:
                self.open()

        ##
        result = None
        result = self._ioctl(self._file.fileno(), 
                             op, 
                             cdb if cdb else 0)
        return result
