# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from .cdb_vroc_nvme_get_number_of_passthrough_disks import GetNumberOfPassthroughDisks
from .cdb_vroc_nvme_get_passthrough_disk_infomation import GetPassthroughDiskInformation
from .cdb_vroc_nvme_get_number_of_spare_disks import GetNumberOfSpareDisks
from .cdb_vroc_nvme_get_spare_disk_infomation import GetSpareDiskInformation
from .cdb_vroc_nvme_get_number_of_journaling_disks import GetNumberOfJournalingDisks
from .cdb_vroc_nvme_get_journaling_disk_infomation import GetJournalingDiskInformation
from .cdb_vroc_nvme_get_number_of_raid_volumes import GetNumberOfRaidVolumes
from .cdb_vroc_nvme_get_raid_infomation import GetRaidInformation
from .cdb_vroc_nvme_get_raid_configuration import GetRaidConfiguration
from .win_ioctl import NVME_MEMBER_DISK_INFORMATION,sizeof
from .cdb_vroc_nvme_identify import IDCtrl,IDNS
from .cdb_vroc_nvme_get_feature import GetFeature
from .cdb_vroc_nvme_set_feature import SetFeature
from .cdb_vroc_nvme_get_log_page import (
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
from .cdb_vroc_nvme_fw_commit import FWCommit
from .cdb_vroc_nvme_device_self_test import SelfTest
from .cdb_vroc_nvme_flush import Flush

class NVMeDisk(object):
    def __init__(self, dev, vrocDiskID: int):
        self.device = dev
        self._vrocDiskID = vrocDiskID

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

    def id_ctrl(self, uuid=0):
        cmd = IDCtrl(self._vrocDiskID, uuid=uuid)
        self.execute(cmd)
        return cmd

    def id_ns(self, ns_id=1, uuid=0):
        cmd = IDNS(self._vrocDiskID, ns_id, uuid=uuid)
        self.execute(cmd)
        return cmd

    def set_feature(self, feature_id, **kwargs):
        cmd = SetFeature(self._vrocDiskID, feature_id, **kwargs)
        self.execute(cmd)
        return cmd

    def get_feature(self, feature_id, **kwargs):
        cmd = GetFeature(self._vrocDiskID, feature_id, **kwargs)
        self.execute(cmd)
        return cmd

    def get_log_page(self, *args, **kwargs):
        cmd = GetLogPage(self._vrocDiskID, *args, **kwargs)
        self.execute(cmd)
        return cmd

    def fw_slot_info(self):
        cmd = FWSlotInfo(self._vrocDiskID)
        self.execute(cmd)
        return cmd

    def error_log_entry(self, lpol=0, lpou=0):
        ## get the max number log entries
        max_number = self.__ctrl_identify_info[262] + 1
        cmd = ErrorLog(self._vrocDiskID, max_number, lpol=lpol, lpou=lpou)
        self.execute(cmd)
        return cmd

    def smart_log(self):
        cmd = SmartLog(self._vrocDiskID)
        self.execute(cmd)
        return cmd

    def get_persistent_event_log(self, action, numd, lpo, data_buffer=None, uuid=0):
        '''
        action: 0-> Establish Context, 1 -> Read Log Data, 2 -> Release Context, 3 -> check if Establish Context.
        data_buffer: a data buffer object from pydiskcmdlib.pynvme.data_buffer.DataBuffer
        '''
        ##
        cmd = PersistentEventLog(self._vrocDiskID, 
                                 action, 
                                 numd & 0xFFFF, 
                                 numdu=(numd >> 16) & 0xFFFF,
                                 lpol=lpo & 0xFFFFFFFF,
                                 lpou=(lpo >> 32) & 0xFFFFFFFF,
                                 uuid=uuid,
                                 data_buffer=data_buffer)
        self.execute(cmd)
        return cmd

    def self_test_log(self, uuid=0):
        cmd = SelfTestLog(self._vrocDiskID, uuid=uuid)
        self.execute(cmd)
        return cmd

    def commands_supported_and_effects_log(self):
        cmd = CommandsSupportedAndEffectsLog(self._vrocDiskID)
        self.execute(cmd)
        return cmd

    def telemetry_host_log(self, numdl, create_telemetry=0, lpol=0, lpou=0, uuid=0):
        cmd = TelemetryHostInitiatedLog(self._vrocDiskID, create_telemetry, numdl, lpol=lpol, lpou=lpou, uuid=uuid)
        self.execute(cmd)
        return cmd

    def telemetry_ctrl_log(self, numdl, lpol=0, lpou=0, uuid=0):
        cmd = TelemetryControllerInitiatedLog(self._vrocDiskID, numdl, lpol=lpol, lpou=lpou, uuid=uuid)
        self.execute(cmd)
        return cmd

    def nvme_fw_commit(self, fw_slot, action, bpid=0):
        cmd = FWCommit(self._vrocDiskID, fw_slot, action, bpid)
        self.execute(cmd)
        return cmd

    def self_test(self, stc, ns_id=0xFFFFFFFF):
        cmd = SelfTest(self._vrocDiskID, stc, nsid=ns_id)
        self.execute(cmd)
        return cmd

    def flush(self, ns_id):
        cmd = Flush(self._vrocDiskID, ns_id)
        self.execute(cmd)
        return cmd


class RaidVolumes(object):
    def __init__(self, dev, indexOfRaidVolume):
        self.device = dev
        self._indexOfRaidVolume = indexOfRaidVolume

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

    def raid_information(self):
        cmd = GetRaidInformation(self._indexOfRaidVolume)
        self.execute(cmd)
        return cmd

    def raid_configuration(self):
        cmd = self.raid_information()
        ## It is a strange behavior, I have to init more memory to stoare
        #  the data although it is big enough.
        disk_number = cmd.cdb.numberOfMemberDisks + 1
        cmd = GetRaidConfiguration(self._indexOfRaidVolume, disk_number)
        self.execute(cmd)
        return cmd

    def get_disk(self):
        cmd = self.raid_configuration()
        length = sizeof(NVME_MEMBER_DISK_INFORMATION)
        offset = -length
        while True:
            offset += length
            temp_data = cmd.data[offset:offset+length]
            if len(temp_data) != length:
                break
            temp = NVME_MEMBER_DISK_INFORMATION.from_buffer(bytearray(temp_data))
            # filter the invalid disk
            if temp.vrocDiskID == 0:
                continue
            yield NVMeDisk(self.device, temp.vrocDiskID)
        return


class RaidController(object):
    def __init__(self, dev):
        self.device = dev
        ## first try a GetNumberOfRaidVolumes command
        #  to check if RaidController
        cmd = self.get_number_of_raid_volumes()

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

    def get_number_of_raid_volumes(self):
        cmd = GetNumberOfRaidVolumes()
        self.execute(cmd)
        return cmd

    def get_number_of_passthrough_disks(self):
        cmd = GetNumberOfPassthroughDisks()
        self.execute(cmd)
        return cmd

    def get_number_of_spare_disks(self):
        cmd = GetNumberOfSpareDisks()
        self.execute(cmd)
        return cmd

    def get_number_of_journaling_disks(self):
        cmd = GetNumberOfJournalingDisks()
        self.execute(cmd)
        return cmd

    def get_raid_volumes(self):
        cmd = self.get_number_of_raid_volumes()
        number_of_raid_volumes = cmd.cdb.numberOfDevices
        if number_of_raid_volumes > 0:
            for i in range(1, number_of_raid_volumes+1):
                yield RaidVolumes(self.device, i)
        return

    def get_passthrough_disks(self):
        cmd = self.get_number_of_passthrough_disks()
        number_of_disks = cmd.cdb.numberOfDevices
        if number_of_disks > 0:
            ##
            cmd = GetPassthroughDiskInformation(number_of_disks+1)
            self.execute(cmd)
            ##
            length = sizeof(NVME_MEMBER_DISK_INFORMATION)
            offset = -length
            while True:
                offset += length
                temp_data = cmd.data[offset:offset+length]
                if len(temp_data) != length:
                    break
                # filter the invalid disk
                temp = NVME_MEMBER_DISK_INFORMATION.from_buffer(bytearray(temp_data))
                if temp.vrocDiskID == 0:
                    continue
                yield NVMeDisk(self.device, temp.vrocDiskID)
        return

    def get_spare_disks(self):
        cmd = self.get_number_of_spare_disks()
        number_of_disks = cmd.cdb.numberOfDevices
        if number_of_disks > 0:
            ##
            cmd = GetSpareDiskInformation(number_of_disks+1)
            self.execute(cmd)
            ##
            length = sizeof(NVME_MEMBER_DISK_INFORMATION)
            offset = -length
            while True:
                offset += length
                temp_data = cmd.data[offset:offset+length]
                if len(temp_data) != length:
                    break
                # filter the invalid disk
                temp = NVME_MEMBER_DISK_INFORMATION.from_buffer(bytearray(temp_data))
                if temp.vrocDiskID == 0:
                    continue
                yield NVMeDisk(self.device, temp.vrocDiskID)
        return

    def get_journaling_disks(self):
        cmd = self.get_number_of_journaling_disks()
        number_of_disks = cmd.cdb.numberOfDevices
        if number_of_disks > 0:
            ##
            cmd = GetJournalingDiskInformation(number_of_disks+1)
            self.execute(cmd)
            ##
            length = sizeof(NVME_MEMBER_DISK_INFORMATION)
            offset = -length
            while True:
                offset += length
                temp_data = cmd.data[offset:offset+length]
                if len(temp_data) != length:
                    break
                # filter the invalid disk
                temp = NVME_MEMBER_DISK_INFORMATION.from_buffer(bytearray(temp_data))
                if temp.vrocDiskID == 0:
                    continue
                yield NVMeDisk(self.device, temp.vrocDiskID)
        return
