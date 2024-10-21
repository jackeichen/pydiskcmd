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
        pass
