# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmdlib.csmi.csmi_controller import CSMIController
from .cdb_rst_nvme_get_log_page import (
    GetLogPage,
    ErrorLog,
    SmartLog,
    FWSlotInfo,
    ChangedNamespaceList,
    CommandsSupportedAndEffectsLog,
    SelfTestLog,
    TelemetryHostInitiatedLog,
    TelemetryControllerInitiatedLog,
    PersistentEventLog,
    SanitizeStatus,
)
from .cdb_rst_nvme_identify import ( 
    IDCtrl,
    IDNS,
    Identify,
)
from .cdb_rst_ata_smart import (
    SmartReadData,
    SmartReadThresh,
)
from .cdb_rst_ata_identify import Identify16

from pydiskcmdlib.exceptions import *

class RSTNVMe(object):
    def __init__(self, dev, path_id: int):
        self.device = dev
        self._path_id = path_id
        ## the identify information
        # will raise if command failed, which
        # standards for not a NVMe ssd
        ret = self.id_ctrl()
        if ret.check_return_status():
            raise ExecuteCmdErr("Identify Command failed!")
        self.__ctrl_identify_info = bytes(ret.cdb.DataBuffer)
        ## OCP info here
        self.__ocp_support = None
        self.__ocp_version = []

    def __enter__(self):
        return self

    def __exit__(self,
                 exc_type,
                 exc_val,
                 exc_tb):
        self.device.close()

    @property
    def dev_node(self):
        return self._path_id

    def ctrl_identify_info(self):
        return self.__ctrl_identify_info

    def execute(self, cmd, check_return_status=False):
        """
        wrapper method to call the NVMeDevice.execute method

        :param cmd: a nvme CmdStructure object
        :return: CommandDecoder type
        """
        try:
            self.device.execute(cmd)
            if check_return_status:
                cmd.check_return_status(raise_if_fail=True)
        except Exception as e:
            raise e
        return cmd 

    def id_ctrl(self, uuid=0):
        cmd = IDCtrl(self._path_id, uuid=uuid)
        self.execute(cmd)
        return cmd

    def get_smart_log(self):
        cmd = SmartLog(self._path_id)
        return self.execute(cmd)


class RSTATA(object):
    def __init__(self, dev, phy_id, port_id, sas_addr):
        self.device = dev
        self._phy_id = phy_id
        self._port_id = port_id
        self._sas_addr = sas_addr

    def __enter__(self):
        return self

    def __exit__(self,
                 exc_type,
                 exc_val,
                 exc_tb):
        self.device.close()

    def execute(self, cmd, check_return_status=False):
        """
        wrapper method to call the NVMeDevice.execute method

        :param cmd: a nvme CmdStructure object
        :return: CommandDecoder type
        """
        try:
            self.device.execute(cmd)
            if check_return_status:
                cmd.check_return_status(raise_if_fail=True)
        except Exception as e:
            raise e
        return cmd 

    @property
    def dev_node(self):
        return self._phy_id

    def smart_read_data(self, smart_key=None):
        cmd = SmartReadData(self._phy_id, self._port_id, self._sas_addr, smart_key)
        self.execute(cmd)
        cmd.unmarshall()
        return cmd

    def smart_read_thresh(self):
        cmd = SmartReadThresh(self._phy_id, self._port_id, self._sas_addr)
        self.execute(cmd)
        return cmd

    def identify(self):
        cmd = Identify16(self._phy_id, self._port_id, self._sas_addr)
        self.execute(cmd)
        return cmd


class RSTController(CSMIController):
    def __init__(self, dev):
        super(RSTController, self).__init__(dev)
        ## first try a get_driver_info command
        #  to check if RST controller
        cmd = self.get_driver_info()
        if not (bytes(cmd.cdb.Information.szName).startswith(b'iaStor') and 
                bytes(cmd.cdb.Information.szDescription).startswith(b'Intel(R) Rapid Storage Technology')):
            raise DeviceTypeError("Not a RST Controller.")

    def __call__(self,
                 dev):
        """
        call the instance again with new device

        :param dev: a NVMeDevice object
        """
        self.device = dev

    def __enter__(self):
        return self

    def __exit__(self,
                 exc_type,
                 exc_val,
                 exc_tb):
        self.device.close()

    def get_nvme_disks(self):
        """
        Retrieves a list of NVMe devices.

        This function scans the system for available NVMe devices and returns a list of their identifiers.

        yield:
            NVMe device RSTNVMe object
        """
        # TODO
        raise NotImplementedError("Get nvme disks is not implemented yet.")

    def get_sata_disks(self):
        """
        Retrieves a list of SATA devices.

        This function scans the system for available SATA devices and returns a list of their identifiers.

        yield:
            NVMe device RSTATA object
        """
        # TODO
        try:
            cmd = self.get_phy_info()
            cmd.check_return_status(raise_if_fail=True)
            for i in range(cmd.cdb.Information.bNumberOfPhys):
                temp = cmd.cdb.Information.Phy[i]
                if temp.Attached.bDeviceType == 0x10:
                    # print ("Phy: %d, Port: %d, SASAddress: %s" % (i,
                    #                                               temp.bPortIdentifier,
                    #                                               ' '.join([("%X" % i).rjust(2, '0') for i in bytes(temp.Attached.bSASAddress)]),
                    #                                               ))
                    yield RSTATA(self.device, i, temp.bPortIdentifier, bytes(temp.Attached.bSASAddress))
        except:
            pass
