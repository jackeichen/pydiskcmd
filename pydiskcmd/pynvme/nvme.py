# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later

import os
from pydiskcmd.utils.converter import scsi_ba_to_int
from pydiskcmd.pynvme.nvme_spec import nvme_id_ns_decode,nvme_id_ctrl_decode,persistent_event_log_header_decode
from pydiskcmd.pynvme.cdb_identify import IDCtrl,IDNS,IDActiveNS,IDAllocatedNS,IDCtrlListInSubsystem,IDCtrlListAttachedToNS
from pydiskcmd.pynvme.cdb_set_feature import SetFeature
from pydiskcmd.pynvme.cdb_get_feature import GetFeature
from pydiskcmd.pynvme.cdb_get_feature import GetFeature
from pydiskcmd.pynvme.cdb_get_log_page import FWSlotInfo,ErrorLog,SmartLog,SelfTestLog,PersistentEventLog
from pydiskcmd.pynvme.cdb_fw_download import FWImageDownload
from pydiskcmd.pynvme.cdb_fw_commit import FWCommit
from pydiskcmd.pynvme.cdb_format import Format
from pydiskcmd.pynvme.cdb_self_test import SelfTest
from pydiskcmd.pynvme.cdb_ns_management import NSCreate,NSDelete
from pydiskcmd.pynvme.cdb_ns_attachment import NSAttachment
from pydiskcmd.exceptions import *

code_version = "0.1.1"

class NVMe(object):
    def __init__(self, dev):
        self.device = dev
        ## the identify information
        ret = self.id_ctrl()
        if max(ret.check_return_status()) > 0:
            raise ExecuteCmdErr("Identify Command failed!")
        self.__ctrl_identify_info = ret.data
        # self.__id_ns_info = {}
    
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

    def get_nvme_ver(self):
        '''
        Get the device support nvme version
        
        :return: a tuple, (MJR,MNR,TER)
        '''
        return self.__ctrl_identify_info[82],self.__ctrl_identify_info[81],self.__ctrl_identify_info[80]

    def execute(self, cmd):
        """
        wrapper method to call the NVMeDevice.execute method

        :param cmd: a nvme CmdStructure object
        :return: CommandDecoder type
        """
        try:
            self.device.execute(cmd)
        except Exception as e:
            raise e
        return cmd

    def id_ctrl(self):
        cmd = IDCtrl()
        self.execute(cmd)
        cmd.check_return_status()
        return cmd

    def id_ns(self, ns_id=1):
        cmd = IDNS(ns_id)
        self.execute(cmd)
        cmd.check_return_status()
        return cmd

    def active_ns_ids(self, ns_id=0, uuid_index=0):
        cmd = IDActiveNS(ns_id, uuid_index)
        self.execute(cmd)
        cmd.check_return_status()
        return cmd

    def allocated_ns_ids(self, ns_id=0):
        cmd = IDAllocatedNS(ns_id)
        self.execute(cmd)
        cmd.check_return_status()
        return cmd

    def cnt_ids(self, cnt_id=0):
        cmd = IDCtrlListInSubsystem(cnt_id)
        self.execute(cmd)
        cmd.check_return_status()
        return cmd

    def ns_attached_cnt_ids(self, ns_id, cnt_id=0):
        cmd = IDCtrlListAttachedToNS(ns_id, cnt_id)
        self.execute(cmd)
        cmd.check_return_status()
        return cmd

    def set_feature(self, feature_id, **kwargs):
        cmd = SetFeature(feature_id, **kwargs)
        self.execute(cmd)
        cmd.check_return_status()
        return cmd

    def get_feature(self, feature_id, **kwargs):
        cmd = GetFeature(feature_id, **kwargs)
        self.execute(cmd)
        cmd.check_return_status()
        return cmd

    def fw_slot_info(self):
        cmd = FWSlotInfo()
        self.execute(cmd)
        cmd.check_return_status()
        return cmd

    def error_log_entry(self):
        ## get the max number log entries
        max_number = self.__ctrl_identify_info[262] + 1
        cmd = ErrorLog(max_number)
        self.execute(cmd)
        cmd.check_return_status()
        return cmd

    def smart_log(self, data_buffer=None):
        cmd = SmartLog(data_buffer)
        self.execute(cmd)
        cmd.check_return_status()
        return cmd

    def get_persistent_event_log(self, action, data_buffer=None):
        '''
        action: 0-> Establish Context, 1 -> Read Log Data, 2 -> Release Context, 3 -> check if Establish Context.
        data_buffer: a data buffer object from pydiskcmd.pynvme.command_structure.DataBuffer
        '''
        ## by nvme spec 1.4a
        if not (self.__ctrl_identify_info[261] & 0x10):
            print ("Device Not support Persistent Event log.")
            return 6
        extend_cap = (self.__ctrl_identify_info[261] & 0x04)
        ##
        data_addr = None
        if data_buffer:
            data_addr = data_buffer.addr
            ## need check data_buffer is multiple of 4 kib
            if data_buffer.data_length < 16384:
                print ("data buffer for persistent_event_log need >= 16KiB")
                return 7
        event_log_size_max = scsi_ba_to_int(self.__ctrl_identify_info[352:356], 'little')  # 64Kib unit
        if action == 0:
            ## Establish Context and Read Log Data, first 512 Bytes(Persistent Event Log Header) to be read here, 
            ##  to determine the "Total Log Length"(TLL)
            # try to Establish Context and Read Log Data
            # build command
            # If extended data is not supported, then bits 27:16 of the Number of Dwords Lower field 
            # specify the Number of Dwords to transfer.
            # 0x0FFF is enough for 512 Bytes. we Do Not Need check the Log Page Attributes field
            cmd = PersistentEventLog(1, 127, data_addr=data_addr)
            self.execute(cmd)
            # if command abort, then Context is already established
            SC,SCT = cmd.check_return_status(False, False)
            if SCT == 0 and SC == 0:
                print ("Context is established.")
                return 0
            elif SCT == 0 and SC == 0x0C:
                print ("Context is already established by others.")
                return 0
            else:
                return 2
        elif action == 1:
            ## step 1. Read Log Data, first 512 Bytes(Persistent Event Log Header) to be read here, 
            ##  to determine the "Total Log Length"(TLL)
            # build command
            # If extended data is not supported, then bits 27:16 of the Number of Dwords Lower field 
            # specify the Number of Dwords to transfer.
            # 0x0FFF is enough for 512 Bytes. We Do Not Need check the Log Page Attributes field
            cmd = PersistentEventLog(0, 127, data_addr=data_addr)
            self.execute(cmd)
            SC,SCT = cmd.check_return_status(False, False)
            if SCT == 0 and SC == 0:
                if data_buffer:
                    ret_data = bytes(data_buffer._data_buf)
                else:
                    ret_data = cmd.data
                persistent_event_log_header = persistent_event_log_header_decode(ret_data)
                total_number_of_events = scsi_ba_to_int(persistent_event_log_header.get("TNEV"), 'little')
                total_log_length = scsi_ba_to_int(persistent_event_log_header.get("TLL"), 'little')
                ## here to 512B aligned
                if total_log_length % 512:
                    total_log_length = total_log_length + 512 - (total_log_length % 512)
                ## Read the log page, default 16kiB data to be read every time
                # check Log Page Attributes field page of extend capacity
                numd = int(total_log_length / 4)
                if extend_cap:
                    ret_data = b''
                    numd_mod = numd % 4096
                    numd_cycles = int((numd-numd_mod)/4096)
                    offset_by_byte = 0
                    for i in range(numd_cycles):
                        lpol = offset_by_byte & 0xFFFF
                        lpou = (offset_by_byte >> 32) & 0xFFFF
                        cmd = PersistentEventLog(0, 4095, lpol=lpol, lpou=lpou, data_addr=data_addr)
                        self.execute(cmd)
                        SC,SCT = cmd.check_return_status(False, False)
                        if SCT == 0 and SC == 0:
                            if data_buffer:
                                ret_data += bytes(data_buffer._data_buf)[0:16384]
                            else:
                                ret_data += cmd.data
                            offset_by_byte += 16384
                        else:
                            print ("Failed in cycle %s" % i)
                            return 3
                    if numd_mod:
                        lpol = offset_by_byte & 0xFFFF
                        lpou = (offset_by_byte >> 32) & 0xFFFF
                        cmd = PersistentEventLog(0, numd_mod-1, lpol=lpol, lpou=lpou, data_addr=data_addr)
                        self.execute(cmd)
                        SC,SCT = cmd.check_status()
                        if SCT == 0 and SC == 0:
                            if data_buffer:
                                ret_data += bytes(data_buffer._data_buf)[0:numd_mod*4]
                            else:
                                ret_data += cmd.data
                        else:
                            print ("Failed in cycle %s" % (i+1))
                            return 3
                    return ret_data
        elif action == 2:  ## Release Context
            cmd = PersistentEventLog(2, 0)
            self.execute(cmd)
            cmd.check_return_status(False, False)
            return 0
        elif action == 3:  ## Check if Context exist
            cmd = PersistentEventLog(0, 127, data_addr=data_addr)
            self.execute(cmd)
            SC,SCT = cmd.check_return_status(False, False)
            if SCT == 0 and SC == 0:  # can read, Context established
                return 1
            elif SCT == 0 and SC == 0x0C: # abort, Context Not established
                return 0
            else:
                return 5
        else:
            print ("Action should be 0|1|2|3.")
            return 6

    def self_test_log(self):
        cmd = SelfTestLog()
        self.execute(cmd)
        cmd.check_return_status()
        return cmd

    def nvme_fw_download(self, fw_path, xfer=0, offset=0):
        if not os.path.isfile(fw_path):
            print ("Not Exist Firmware File in %s" % fw_path)
            return 1
        ## Get FWUG
        fwug = self.__ctrl_identify_info[319] & 0xFF
        if fwug == 0 or fwug == 0xFF:
            fwug = 4096     # fwug 
        else:
            fwug = fwug * 4096  # fwug 
        # check numd
        if xfer == 0:
            xfer = fwug
        elif xfer and (xfer % fwug):
            xfer = fwug
        # check offset
        if (offset*4) % fwug != 0:
            print ("warning: offset is not matched with FWUG in Identify, it may failed with status of Invalid Field in Command.")
        ## Firmware Image Download
        RC = 0
        with open(fw_path, "rb") as f:
            ##
            while True:
                fw_data = f.read(xfer)
                if fw_data:
                    cmd = FWImageDownload(fw_data, offset)
                    self.execute(cmd)
                    sc,sct = cmd.check_return_status()
                    if sc:
                        print ("Firmware Download failed(SC=%s,SCT=%s)" % (sc,sct))
                        print ("Command specific status values is %#x" % cmd.cq_cmd_spec)
                        RC = 2
                        break
                else:
                    break
                offset += int(xfer/4)
        if RC == 0:
            print ("Firmware Download Success")
        return RC        

    def nvme_fw_commit(self, fw_slot, action, bpid=0):
        cmd = FWCommit(fw_slot, action, bpid)
        self.execute(cmd)
        cmd.check_return_status()
        return cmd

    def nvme_format(self, lbaf, nsid=0xFFFFFFFF, **kwargs):
        ### Check parameters
        
        if (not self.__ctrl_identify_info[524] & 0x01) and nsid == 0xFFFFFFFF:
            print ("The controller supports format on a per namespace basis.")
        if (not self.__ctrl_identify_info[524] & 0x02) and ses and nsid == 0xFFFFFFFF:
            print ("Any secure erase performed as part of a format results in a secure erase of the particular namespace specified")
        ###
        cmd = Format(lbaf, nsid=nsid, **kwargs)
        self.execute(cmd)
        cmd.check_return_status()
        return cmd

    def self_test(self, stc, ns_id=0xFFFFFFFF):
        cmd = SelfTest(stc, ns_id=ns_id)
        self.execute(cmd)
        return cmd

    def ns_create(self, ns_size, ns_cap, flbas, dps, nmic, anagrp_id, nvmeset_id, csi=0, vendor_spec_data=b''):
        cmd = NSCreate(ns_size, ns_cap, flbas, dps, nmic, anagrp_id, nvmeset_id, csi=csi, vendor_spec_data=vendor_spec_data)
        self.execute(cmd)
        cmd.check_return_status()
        return cmd

    def ns_delete(self, ns_id):
        cmd = NSDelete(ns_id)
        self.execute(cmd)
        cmd.check_return_status()
        return cmd

    def ns_attachment(self, ns_id, sel, ctrl_id_list):
        cmd = NSAttachment(ns_id, sel, ctrl_id_list)
        self.execute(cmd)
        cmd.check_return_status()
        return cmd

