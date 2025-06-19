# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from .cdb_csmi_sas_get_driver_info import CSMI_SAS_GET_DRIVER_INFO
from .cdb_csmi_sas_get_raid_info import CSMI_SAS_GET_RAID_INFO
from .cdb_csmi_sas_get_raid_config import CSMI_SAS_GET_RAID_CONFIG
from .cdb_csmi_sas_get_phy_info import CSMI_SAS_GET_PHY_INFO
from .cdb_csmi_sas_get_cntlr_status import CSMI_SAS_GET_CNTLR_STATUS

class CSMIController(object):
    def __init__(self, dev):
        self.device = dev
        ## first try a get_driver_info command
        #  to check if CSMI support
        # cmd = self.get_driver_info()

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

    def execute(self, cmd, check_return_status=False):
        """
        wrapper method to call the NVMeDevice.execute method

        :param cmd: a nvme CmdStructure object
        :return: CommandDecoder type
        """
        try:
            self.device.execute(cmd)
            if check_return_status:
                cmd.check_return_status()
        except Exception as e:
            raise e
        return cmd

    def get_driver_info(self):
        cmd = CSMI_SAS_GET_DRIVER_INFO()
        return self.execute(cmd)

    def get_raid_info(self):
        cmd = CSMI_SAS_GET_RAID_INFO()
        return self.execute(cmd)

    def get_raid_config(self, raid_set_index, MaxDrivesPerSet):
        cmd = CSMI_SAS_GET_RAID_CONFIG(raid_set_index, MaxDrivesPerSet)
        return self.execute(cmd)

    def get_phy_info(self):
        cmd = CSMI_SAS_GET_PHY_INFO()
        return self.execute(cmd)

    def get_cntlr_status(self):
        cmd = CSMI_SAS_GET_CNTLR_STATUS()
        return self.execute(cmd)
