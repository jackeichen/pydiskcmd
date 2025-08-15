# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later

from pydiskcmdlib.pynvme.cdb_identify import IDCtrl,IDNS,IDActiveNS,IDAllocatedNS,IDCtrlListInSubsystem,IDCtrlListAttachedToNS,UUIDList
from pydiskcmdlib.pynvme.cdb_set_feature import SetFeature
from pydiskcmdlib.pynvme.cdb_get_feature import GetFeature
from pydiskcmdlib.pynvme.cdb_get_feature import GetFeature
from pydiskcmdlib.pynvme.cdb_get_log_page import (
    GetLogPage,
    FWSlotInfo,
    ErrorLog,
    SmartLog,
    SelfTestLog,
    PersistentEventLog,
    TelemetryHostInitiatedLog,
    TelemetryControllerInitiatedLog,
    SanitizeStatus,
    CommandsSupportedAndEffectsLog,
    MICommandsSupportedAndEffectsLog,
    )
from pydiskcmdlib.pynvme.cdb_fw_download import FWImageDownload
from pydiskcmdlib.pynvme.cdb_fw_commit import FWCommit
from pydiskcmdlib.pynvme.cdb_format import Format
from pydiskcmdlib.pynvme.cdb_nvme_sanitize import Sanitize
from pydiskcmdlib.pynvme.cdb_self_test import SelfTest
from pydiskcmdlib.pynvme.cdb_ns_management import NSCreate,NSDelete
from pydiskcmdlib.pynvme.cdb_ns_attachment import NSAttachment
from pydiskcmdlib.pynvme.cdb_nvme_read import Read
from pydiskcmdlib.pynvme.cdb_nvme_verify import Verify
from pydiskcmdlib.pynvme.cdb_nvme_write import Write
from pydiskcmdlib.pynvme.cdb_nvme_flush import Flush
from pydiskcmdlib.pynvme.cdb_nvme_compare import Compare
from pydiskcmdlib.pynvme.cdb_nvme_write_unc import WriteUncorrectable
from pydiskcmdlib.pynvme.cdb_nvme_write_zeroes import WriteZeroes
from pydiskcmdlib.pynvme.cdb_nvme_dataset_management import DatasetManagement
from pydiskcmdlib.pynvme.cdb_nvme_get_lba_status import GetLBAStatus
from pydiskcmdlib.pynvme.cdb_nvme_reset import Reset
from pydiskcmdlib.pynvme.cdb_nvme_subsys_reset import SubsysReset
from pydiskcmdlib.pynvme.cdb_nvme_mi import NVMeMISend, NVMeMIRecv
from pydiskcmdlib.exceptions import *
from pydiskcmdlib.pynvme.data_buffer import DataBuffer
from pydiskcmdlib import log

class NVMe(object):
    def __init__(self, dev):
        self.device = dev
        ## the identify information
        ret = self.id_ctrl()
        if max(ret.check_return_status()) > 0:
            raise ExecuteCmdErr("Identify Command failed!")
        self.__ctrl_identify_info = ret.data
        # self.__id_ns_info = {}
        ## OCP info here
        self.__ocp_support = None
        self.__ocp_version = []
    
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

    @property
    def ctrl_identify_info(self):
        return self.__ctrl_identify_info

    def _ocp_info_check(self):
        cmd = self.get_log_page(0, 0xC0, 0, 0, 127, 0, 0, 0, 0, 0, 0, 0)
        smart_extend = bytes(cmd.data)
        if smart_extend[496:512] == b'\xc5\xaf\x10(\xea\xbf\xf2\xa4\x9cOo|\xc9\x14\xd5\xaf':
            self.__ocp_support = True
            Major = smart_extend[103]
            Minor = None
            if Major == 0:
                Major = 1
            else:
                Minor = smart_extend[101] + (smart_extend[102] << 8)
            self.__ocp_version = [Major, Minor]
        else:
            self.__ocp_support = False

    @property
    def ocp_support(self):
        if self.__ocp_support is None:
            self._ocp_info_check()
        return self.__ocp_support

    @property
    def ocp_ver(self):
        if self.__ocp_support is None:
            self._ocp_info_check()
        return self.__ocp_version

    def get_nvme_ver(self):
        '''
        Get the device support nvme version
        
        :return: a tuple, (MJR,MNR,TER)
        '''
        return self.__ctrl_identify_info[82],self.__ctrl_identify_info[81],self.__ctrl_identify_info[80]

    def execute(self, cmd, check_return_status=False):
        """
        wrapper method to call the NVMeDevice.execute method

        :param cmd: a nvme CmdStructure object
        :return: CommandDecoder type
        """
        try:
            log.debug("Sending NVMe %s: %s" % ("command" if cmd.cdb_struc else "Request",
                                               " ".join(["%X" % i for i in cmd.cdb_struc]) if cmd.cdb_struc else cmd.req_id,
                                              ))
            self.device.execute(cmd)
            if (cmd.cq_status is not None) and (cmd.cq_cmd_spec is not None):
                log.debug("Completion Queue Status: %X, Command Specific Data: %X" % (cmd.cq_status, cmd.cq_cmd_spec))
            if check_return_status:
                cmd.check_return_status()
        except Exception as e:
            raise e
        return cmd

    def reset_ctrl(self):
        cmd = Reset()
        self.execute(cmd, check_return_status=False)
        return cmd

    def subsystem_reset(self):
        cmd = SubsysReset()
        self.execute(cmd, check_return_status=False)
        return cmd

    def id_ctrl(self, uuid=0):
        cmd = IDCtrl(uuid=uuid)
        self.execute(cmd)
        return cmd

    def id_ns(self, ns_id=1, uuid=0):
        cmd = IDNS(ns_id, uuid=uuid)
        self.execute(cmd)
        return cmd

    def active_ns_ids(self, ns_id=0):
        cmd = IDActiveNS(ns_id)
        self.execute(cmd)
        return cmd

    def allocated_ns_ids(self, ns_id=0):
        cmd = IDAllocatedNS(ns_id)
        self.execute(cmd)
        return cmd

    def cnt_ids(self, cnt_id=0):
        cmd = IDCtrlListInSubsystem(cnt_id)
        self.execute(cmd)
        return cmd

    def ns_attached_cnt_ids(self, ns_id, cnt_id=0):
        cmd = IDCtrlListAttachedToNS(ns_id, cnt_id)
        self.execute(cmd)
        return cmd

    def uuid_list(self):
        cmd = UUIDList()
        self.execute(cmd)
        return cmd

    def set_feature(self, feature_id, **kwargs):
        cmd = SetFeature(feature_id, **kwargs)
        self.execute(cmd)
        return cmd

    def get_feature(self, feature_id, **kwargs):
        cmd = GetFeature(feature_id, **kwargs)
        self.execute(cmd)
        return cmd

    def get_log_page(self, *args, **kwargs):
        cmd = GetLogPage(*args, **kwargs)
        self.execute(cmd)
        return cmd

    def fw_slot_info(self):
        cmd = FWSlotInfo()
        self.execute(cmd)
        return cmd

    def error_log_entry(self, lpol=0, lpou=0):
        ## get the max number log entries
        max_number = self.__ctrl_identify_info[262] + 1
        cmd = ErrorLog(max_number, lpol=lpol, lpou=lpou)
        self.execute(cmd)
        return cmd

    def smart_log(self):
        cmd = SmartLog()
        self.execute(cmd)
        return cmd

    def get_persistent_event_log(self, action, numd, lpo, data_buffer=None, uuid=0):
        '''
        action: 0-> Establish Context, 1 -> Read Log Data, 2 -> Release Context, 3 -> check if Establish Context.
        data_buffer: a data buffer object from pydiskcmdlib.pynvme.data_buffer.DataBuffer
        '''
        ##
        cmd = PersistentEventLog(action, 
                                 numd & 0xFFFF, 
                                 numdu=(numd >> 16) & 0xFFFF,
                                 lpol=lpo & 0xFFFFFFFF,
                                 lpou=(lpo >> 32) & 0xFFFFFFFF,
                                 uuid=uuid,
                                 data_buffer=data_buffer)
        self.execute(cmd)
        return cmd

    def self_test_log(self, uuid=0):
        cmd = SelfTestLog(uuid=uuid)
        self.execute(cmd)
        return cmd

    def commands_supported_and_effects_log(self):
        cmd = CommandsSupportedAndEffectsLog()
        self.execute(cmd)
        return cmd

    def mi_commands_supported_and_effects_log(self, numdl=1023, lpol=0):
        cmd = MICommandsSupportedAndEffectsLog(numdl=numdl, lpol=lpol)
        self.execute(cmd)
        return cmd

    def telemetry_host_log(self, numdl, create_telemetry=0, lpol=0, lpou=0, uuid=0):
        cmd = TelemetryHostInitiatedLog(create_telemetry, numdl, lpol=lpol, lpou=lpou, uuid=uuid)
        self.execute(cmd)
        return cmd

    def telemetry_ctrl_log(self, numdl, lpol=0, lpou=0, uuid=0):
        cmd = TelemetryControllerInitiatedLog(numdl, lpol=lpol, lpou=lpou, uuid=uuid)
        self.execute(cmd)
        return cmd

    def nvme_fw_download(self, fw_data, offset):
        cmd = FWImageDownload(fw_data, offset)
        self.execute(cmd)
        return cmd     

    def nvme_fw_commit(self, fw_slot, action, bpid=0):
        cmd = FWCommit(fw_slot, action, bpid)
        self.execute(cmd)
        return cmd

    def nvme_format(self, lbaf, nsid=0xFFFFFFFF, mset=0, pi=0, pil=0, ses=0, timeout=600000):
        ###
        cmd = Format(lbaf, nsid=nsid, mset=mset, pi=pi, pil=pil, ses=ses, timeout=timeout)
        self.execute(cmd)
        return cmd

    def sanitize(self, action, ause, owpass, oipbp, no_deallocate, ovrpat=0):
        cmd = Sanitize(action, ause, owpass, oipbp, no_deallocate, ovrpat=ovrpat)
        self.execute(cmd)
        return cmd

    def sanitize_log(self, numdl, lpol=0):
        cmd = SanitizeStatus(numdl, lpol=lpol)
        self.execute(cmd)
        return cmd

    def self_test(self, stc, ns_id=0xFFFFFFFF):
        cmd = SelfTest(stc, nsid=ns_id)
        self.execute(cmd)
        return cmd

    def ns_create(self, ns_size, ns_cap, flbas, dps, nmic, anagrp_id, nvmeset_id, csi=0, vendor_spec_data=b''):
        cmd = NSCreate(ns_size=ns_size, ns_cap=ns_cap, flbas=flbas, dps=dps, nmic=nmic, anagrp_id=anagrp_id, nvmeset_id=nvmeset_id, csi=csi, vendor_spec_data=vendor_spec_data)
        self.execute(cmd)
        return cmd

    def ns_delete(self, ns_id):
        cmd = NSDelete(ns_id)
        self.execute(cmd)
        return cmd

    def ns_attachment(self, ns_id, sel, ctrl_id_list):
        cmd = NSAttachment(ns_id, sel, ctrl_id_list)
        self.execute(cmd)
        return cmd

    def nvme_mi_send(self, opcode, nmd0, nmd1, data=None):
        cmd = NVMeMISend(opcode, nmd0, nmd1, data=data)
        self.execute(cmd)
        return cmd

    def nvme_mi_recv(self, opcode, nmd0, nmd1, data_len=0):
        cmd = NVMeMIRecv(opcode, nmd0, nmd1, data_len=data_len)
        self.execute(cmd)
        return cmd

    def flush(self, ns_id):
        cmd = Flush(ns_id)
        self.execute(cmd)
        return cmd

    def read(self, ns_id, slba, nlba, **kwargs):
        ## first get the lbaf
        cmd = self.id_ns(ns_id=ns_id)
        # 
        flbaf = cmd.data[26] & 0x0F
        start_labf_des = 128 + flbaf * 4
        lbaf_ms = cmd.data[start_labf_des] + (cmd.data[start_labf_des+1] << 8)
        lbaf_lbads = 2 ** (cmd.data[start_labf_des+2])
        # get the data length
        data_len = (nlba + 1) * lbaf_lbads
        metadata_len = (nlba + 1) * lbaf_ms
        if lbaf_ms > 0:
            if (cmd.data[27] & 0x01): # extended data LBA
                data_len += metadata_len
                metadata_len = 0
            elif (cmd.data[27] & 0x02):
                pass
            else:
                metadata_len = 0
        else:
            metadata_len = 0
        ##
        cmd = Read(ns_id, slba, nlba, data_len=data_len, metadata_len=metadata_len, **kwargs)
        self.execute(cmd)
        return cmd

    def verify(self, ns_id, slba, nlba):
        cmd = Verify(ns_id, slba, nlba)
        self.execute(cmd)
        return cmd

    def write(self, ns_id, slba, nlba, raw_data, raw_metadata):
        cmd = Write(ns_id, slba, nlba, raw_data=raw_data, raw_metadata=raw_metadata)
        self.execute(cmd)
        return cmd

    def get_lba_status(self, ns_id, slba, mndw, atype, rl, timeout=60000):
        cmd = GetLBAStatus(ns_id, slba, mndw, atype, rl, timeout=60000)
        self.execute(cmd)
        return cmd

    def compare(self, ns_id, slba, nlba, data, metadata=None, **kwargs):
        ## first get the lbaf
        cmd = self.id_ns(ns_id=ns_id)
        # 
        flbaf = cmd.data[26] & 0x0F
        start_labf_des = 128 + flbaf * 4
        lbaf_ms = cmd.data[start_labf_des] + (cmd.data[start_labf_des+1] << 8)
        lbaf_lbads = 2 ** (cmd.data[start_labf_des+2])
        # get the data length
        data_len = (nlba + 1) * lbaf_lbads
        metadata_len = (nlba + 1) * lbaf_ms
        if lbaf_ms > 0:
            if (cmd.data[27] & 0x01): # extended data LBA
                data_len += metadata_len
                metadata_len = 0
            elif (cmd.data[27] & 0x02):
                pass
            else:
                metadata_len = 0
        else:
            metadata_len = 0
        ##
        cmd = Compare(ns_id, 
                      slba, 
                      nlba, 
                      data=data, 
                      data_len=data_len, 
                      metadata=metadata, 
                      metadata_len=metadata_len if metadata else 0,
                      **kwargs)
        self.execute(cmd)
        return cmd

    def write_uncorrectable(self, nsid, slba, nlba):
        cmd = WriteUncorrectable(nsid, slba, nlba)
        self.execute(cmd)
        return cmd

    def write_zeroes(self, nsid, slba, nlba, **kwargs):
        cmd = WriteZeroes(nsid, slba, nlba, **kwargs)
        self.execute(cmd)
        return cmd

    def dataset_management(self, nsid, nr, idr, idw, ad, data):
        cmd = DatasetManagement(nsid, nr, idr, idw, ad, data)
        self.execute(cmd)
        return cmd
