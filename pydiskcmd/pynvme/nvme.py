# SPDX-FileCopyrightText: 2014 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later

import os
from pydiskcmd.pynvme.command_structure import CmdStructure,DataBuffer,encode_data_buffer
from pydiskcmd.pynvme.nvme_device import NVMeDevice
from pydiskcmd.pynvme.nvme_command import build_command
from pydiskcmd.pynvme.nvme_spec import nvme_id_ns_decode,nvme_id_ctrl_decode,persistent_event_log_header_decode
from pydiskcmd.utils.converter import scsi_ba_to_int,encode_dict

code_version = "0.1.0"

class NVMe(object):
    def __init__(self, dev):
        self.device = dev
        ## the identify information
        ret = self.id_ctrl(False)
        self.__ctrl_identify_info = ret.data
        self.__id_ns_info = {}
    
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

    def _set_ba_value(self, ba, bit_mask, value):
        # bit_mask:
        # If the length is 2 we have the legacy notation [bitmask, offset]
        # Example: 'sync': [0x10, 7],
        pass

    def get_ns_info_by_ns_id(self, ns_id):
        if ns_id not in self.__id_ns_info:
            ret = self.id_ns(ns_id=ns_id)
            self.__id_ns_info[ns_id] = nvme_id_ns_decode(ret.data)
        return self.__id_ns_info.get(ns_id)

    @property
    def ctrl_identify_info(self):
        return self.__ctrl_identify_info

    def execute(self, cmd):
        """
        wrapper method to call the NVMeDevice.execute method

        :param cmd: a nvme CmdStructure object
        :return: CommandDecoder type
        """
        ret = None
        try:
            ret = self.device.execute(0, cmd)
        except Exception as e:
            raise e
        return ret

    def execute_io(self, cmd):
        """
        wrapper method to call the NVMeDevice.execute method

        :param cmd: a nvme CmdStructure object
        :return: CommandDecoder type
        """
        ret = None
        try:
            ret = self.device.execute(1, cmd)
        except Exception as e:
            raise e
        return ret

    def id_ctrl(self, check_status=True):
        ## build command
        cmd_struc = CmdStructure(opcode=0x06,
                                 data_len=4096,
                                 cdw10=0x01,)
        ##
        ret = self.execute(cmd_struc)
        if check_status:
            ret.check_status()
        return ret

    def id_ns(self, ns_id=1):
        ## build command
        cmd_struc = CmdStructure(opcode=0x06,
                                 nsid=ns_id,
                                 data_len=4096,
                                 cdw10=0x00,)
        ##
        ret = self.execute(cmd_struc)
        ret.check_status()
        return ret

    def active_ns_ids(self, ns_id=0, uuid_index=0):
        ### build command
        cdw10 = build_command({"CNS": (0xFF, 0, 0x02)})
        cdw14 = build_command({"UUID": (0x7F, 0, uuid_index),})
        ##
        cmd_struc = CmdStructure(opcode=0x06,
                                 nsid=ns_id,
                                 data_len=4096,
                                 cdw10=cdw10,
                                 cdw14=cdw14)
        ###
        ret = self.execute(cmd_struc)
        ret.check_status()
        return ret

    def allocated_ns_ids(self, ns_id=0):
        ### build command
        cdw10 = build_command({"CNS": (0xFF, 0, 0x10)})
        ##
        cmd_struc = CmdStructure(opcode=0x06,
                                 nsid=ns_id,
                                 data_len=4096,
                                 cdw10=cdw10)
        ###
        ret = self.execute(cmd_struc)
        ret.check_status()
        return ret

    def cnt_ids(self, cnt_id=0):
        ### build command
        cdw10 = build_command({"CNS": (0xFF, 0, 0x13),
                               "CNTID": (0xFFFF, 2, cnt_id)})
        ##
        cmd_struc = CmdStructure(opcode=0x06,
                                 data_len=4096,
                                 cdw10=cdw10)
        ###
        ret = self.execute(cmd_struc)
        ret.check_status()
        return ret

    def ns_attached_cnt_ids(self, ns_id, cnt_id=0):
        ### build command
        cdw10 = build_command({"CNS": (0xFF, 0, 0x12),
                               "CNTID": (0xFFFF, 2, cnt_id)})
        ##
        cmd_struc = CmdStructure(opcode=0x06,
                                 nsid=ns_id,
                                 data_len=4096,
                                 cdw10=cdw10)
        ###
        ret = self.execute(cmd_struc)
        ret.check_status()
        return ret

    def set_feature(self, feature_id, ns_id=0 ,sv=0, uuid_index=0, cdw11=0, cdw12=0, cdw13=0, cdw15=0, data_in=None):
        ### build command
        cdw10 = build_command({"FID": (0xFF, 0, feature_id),
                               "SV": (0x80, 3, sv)})
        cdw14 = build_command({"UUID": (0x7F, 0, uuid_index),})
        ##
        d_l = len(data_in) if data_in else 0
        cmd_struc = CmdStructure(opcode=0x09,
                                 nsid=ns_id,
                                 data_len=d_l,
                                 data_in=data_in,
                                 cdw10=cdw10,
                                 cdw11=cdw11,
                                 cdw12=cdw12,
                                 cdw13=cdw13,
                                 cdw14=cdw14,
                                 cdw15=cdw15,)
        ###
        ret = self.execute(cmd_struc)
        ret.check_status()
        return ret

    def get_feature(self, feature_id, ns_id=0, sel=0, uuid_index=0, cdw11=0, data_len=0):
        ### build command
        #
        cdw10 = build_command({"FID": (0xFF, 0, feature_id),
                               "SEL": (0x07, 1, sel)})
        cdw14 = build_command({"UUID": (0x7F, 0, uuid_index),})
        ##
        cmd_struc = CmdStructure(opcode=0x0A,
                                 nsid=ns_id,
                                 data_len=data_len,
                                 cdw10=cdw10,
                                 cdw11=cdw11,
                                 cdw14=cdw14)
        ###
        ret = self.execute(cmd_struc)
        ret.check_status()
        return ret

    def fw_slot_info(self):
        ### build command
        numdl = int(512 / 4) - 1
        cdw10 = build_command({"lid": (0xFF, 0, 0x03),
                               "numdl": (0x0FFF, 2, numdl),})
        ##
        cmd_struc = CmdStructure(opcode=0x02,
                                 data_len=512,
                                 cdw10=cdw10,)
        ###
        ret = self.execute(cmd_struc)
        ret.check_status()
        return ret

    def error_log_entry(self):
        ## get the max number log entries
        max_number = self.__ctrl_identify_info[262] + 1
        numbet_dw = max_number * 16 ## 16 = 64 / 4
        numd = numbet_dw - 1
        ## the numbet_dw <= 256*16= 4096,
        #  so 0x0FFF is enough for numd
        numdl = numd & 0x0FFF
        ### build command
        cdw10 = build_command({"lid": (0xFF, 0, 0x01),      # log id
                               "numdl": (0x0FFF, 2, numdl),})
        ##
        cmd_struc = CmdStructure(opcode=0x02,
                                 data_len=numbet_dw*4,
                                 cdw10=cdw10,)
        ###
        ret = self.execute(cmd_struc)
        ret.check_status()
        return ret

    def smart_log(self, data_buffer=None):
        ###
        data_addr = None
        if data_buffer:
            data_addr = data_buffer.addr
            ## need check data_buffer is multiple of 4 kib
            if data_buffer.data_length < 512:
                print ("data buffer for persistent_event_log need >= 512 bytes")
                return 7
        ### build command
        numdl = int(512 / 4) - 1
        cdw10 = build_command({"lid": (0xFF, 0, 0x02),      # log id
                               "numdl": (0x0FFF, 2, numdl),})
        ##
        cmd_struc = CmdStructure(opcode=0x02,
                                 nsid=0xFFFFFFFF,
                                 addr=data_addr,
                                 data_len=512,
                                 cdw10=cdw10,)
        ###
        ret = self.execute(cmd_struc)
        ret.check_status()
        if data_buffer:
            ret.data = bytes(data_buffer._data_buf)[0:512]
        return ret

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
            cycle = 0
            while True:
                fw_data = f.read(xfer)
                if fw_data:
                    ### build command
                    cdw10 = 0
                    cdw11 = 0
                    ##
                    cdw10 += int(((xfer / 4) - 1))
                    ##
                    cdw11 += int((offset + xfer*cycle/4))
                    ###
                    cmd_struc = CmdStructure(opcode=0x11,
                                             data_len=xfer,
                                             data_in=fw_data,
                                             cdw10=cdw10,
                                             cdw11=cdw11)
                    ##
                    ret = self.execute(cmd_struc)
                    sc,sct = ret.check_status(hint=False)
                    if sc:
                        print ("Firmware Download failed(SC=%s,SCT=%s)" % (sc,sct))
                        RC = 2
                        break
                else:
                    break
                cycle += 1
        if RC == 0:
            print ("Firmware Download Success")
        return RC

    def nvme_fw_commit(self, fw_slot, action, bpid=None):
        ### build command
        cdw10 = 0
        #
        if fw_slot in range(8):
            cdw10 += fw_slot          # Firmware Slot
        else:
            print ("fw_slot should be 0-7")
            return 1
        if action in range(8):
            cdw10 += (action << 3)    # Commit Action
        else:
            print ("action should be 0-7")
            return 1
        if bpid in (0,1):
            cdw10 += (bpid << 31)
        elif bpid is None:
            pass
        else:
            print ("bpid should be 0|1")
            return 1
        ##
        cmd_struc = CmdStructure(opcode=0x10,
                                 cdw10=cdw10)
        ###
        ret = self.execute(cmd_struc)
        ret.check_status()
        return ret

    def nvme_read(self, 
                  nsid,
                  start_lba, 
                  lba_count,
                  protection_info_field,
                  fua,
                  limit_retry,
                  dataset_management,
                  eilbrt,
                  elbat,
                  elbatm):
        ## get lba_format
        ns_info = self.get_ns_info_by_ns_id(nsid)
        index = ns_info.get("FLBAS") & 0x0F
        lbaf = ns_info.get("LBAF%s" % index)
        metadata_size = scsi_ba_to_int(lbaf.get("MS"), 'little')
        lbads = scsi_ba_to_int(lbaf.get("LBADS"), 'little')
        lba_size = pow(2, lbads)
        print (metadata_size, lba_size)
        return

    def nvme_format(self, lbaf, mset=0, pi=0, pil=1, ses=0, nsid=0xFFFFFFFF):
        ### Check parameters
        if (not self.__ctrl_identify_info[524] & 0x01) and nsid == 0xFFFFFFFF:
            print ("The controller supports format on a per namespace basis.")
        if (not self.__ctrl_identify_info[524] & 0x02) and ses and nsid == 0xFFFFFFFF:
            print ("Any secure erase performed as part of a format results in a secure erase of the particular namespace specified")
        ### build command
        cdw10 = build_command({"lbaf": (0x0F, 0, lbaf),
                               "mset": (0x10, 0 ,mset),
                               "pi": (0xE0, 0, pi),
                               "pil": (0x01, 1, pil),
                               "ses": (0x0E, 1, ses)})
        ###
        cmd_struc = CmdStructure(opcode=0x80,
                                 nsid=nsid,
                                 cdw10=cdw10,
                                 timeout_ms=600000)
        ###
        ###
        ret = self.execute(cmd_struc)
        ret.check_status()
        return ret

    def get_persistent_event_log(self, action, data_buffer=None):
        '''
        action: 0-> Establish Context, 1 -> Read Log Data, 2 -> Release Context.
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
            cdw10 = build_command({"lid": (0xFF, 0, 0x0D),
                                   "lsp": (0x0F, 1, 1),   # Establish Context and Read Log Data:
                                   "rae": (0x80, 1, 0),
                                   "numdl": (0x0FFF, 2, 127),})

            cmd_struc = CmdStructure(opcode=0x02,
                                     addr=data_addr,
                                     data_len=512,
                                     cdw10=cdw10,)
            # execute command
            ret = self.execute(cmd_struc)
            # if command abort, then Context is already established
            SC,SCT = ret.check_status()
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
            cdw10 = build_command({"lid": (0xFF, 0, 0x0D),
                                   "lsp": (0x0F, 1, 0),   # Read Log Data
                                   "rae": (0x80, 1, 0),
                                   "numdl": (0x0FFF, 2, 127),})

            cmd_struc = CmdStructure(opcode=0x02,
                                     addr=data_addr,
                                     data_len=512,
                                     cdw10=cdw10,)
            # execute command
            ret = self.execute(cmd_struc)
            # if command abort, then Context is already established
            SC,SCT = ret.check_status(fail_hint=False)
            if SCT == 0 and SC == 0:
                if data_buffer:
                    ret_data = bytes(data_buffer._data_buf)
                else:
                    ret_data = ret.data
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
                        cdw10 = build_command({"lid": (0xFF, 0, 0x0D),
                                               "lsp": (0x0F, 1, 0),   # Read Log Data
                                               "rae": (0x80, 1, 0),
                                               "numdl": (0x0FFF, 2, 4095),})
                        # cdw 12 Log Page Offset Lower (LPOL), cdw13 Log Page Offset Upper (LPOU)
                        lpol = offset_by_byte & 0xFFFF
                        lpou = (offset_by_byte >> 32) & 0xFFFF
                        cdw12 = build_command({"lpol": (0xFFFF, 0, lpol)})
                        cdw13 = build_command({"lpou": (0xFFFF, 0, lpou)})
                        #
                        cmd_struc = CmdStructure(opcode=0x02,
                                                 addr=data_addr,
                                                 data_len=16384,
                                                 cdw10=cdw10,
                                                 cdw12=cdw12,
                                                 cdw13=cdw13,)
                        # execute command
                        ret = self.execute(cmd_struc)
                        SC,SCT = ret.check_status()
                        if SCT == 0 and SC == 0:
                            if data_buffer:
                                ret_data += bytes(data_buffer._data_buf)[0:16384]
                            else:
                                ret_data += ret.data
                            offset_by_byte += 16384
                        else:
                            print ("Failed in cycle %s" % i)
                            return 3
                    if numd_mod:
                        ## build command
                        cdw10 = build_command({"lid": (0xFF, 0, 0x0D),
                                               "lsp": (0x0F, 1, 0),   # Read Log Data
                                               "rae": (0x80, 1, 0),
                                               "numdl": (0x0FFF, 2, numd_mod-1),})
                        # cdw 12 Log Page Offset Lower (LPOL), cdw13 Log Page Offset Upper (LPOU)
                        lpol = offset_by_byte & 0xFFFF
                        lpou = (offset_by_byte >> 32) & 0xFFFF
                        cdw12 = build_command({"lpol": (0xFFFF, 0, lpol)})
                        cdw13 = build_command({"lpou": (0xFFFF, 0, lpou)})
                        #
                        cmd_struc = CmdStructure(opcode=0x02,
                                                 addr=data_addr,
                                                 data_len=numd_mod*4,
                                                 cdw10=cdw10,
                                                 cdw12=cdw12,
                                                 cdw13=cdw13,)
                                    # execute command
                        ret = self.execute(cmd_struc)
                        SC,SCT = ret.check_status()
                        if SCT == 0 and SC == 0:
                            if data_buffer:
                                ret_data += bytes(data_buffer._data_buf)[0:numd_mod*4]
                            else:
                                ret_data += ret.data
                        else:
                            print ("Failed in cycle %s" % i)
                            return 3
                    return ret_data
                else:
                    numdl = min(numd-1, 0x0FFF)
                    # we only can read 16 KiB of data now, included persistent_event_log_header
                    cdw10 = build_command({"lid": (0xFF, 0, 0x0D),
                                           "lsp": (0x0F, 1, 0),   # Read Log Data
                                           "rae": (0x80, 1, 0),
                                           "numdl": (0x0FFF, 2, numdl),}) 
                    cmd_struc = CmdStructure(opcode=0x02,
                                             addr=data_addr,
                                             data_len=(numdl+1)*4,
                                             cdw10=cdw10,)

                    # execute command
                    ret = self.execute(cmd_struc)
                    SC,SCT = ret.check_status()
                    if SCT == 0 and SC == 0:
                        if data_buffer:
                            return bytes(data_buffer._data_buf)
                        else:
                            return ret.data
                    else:
                        return 3
            elif SCT == 0 and SC == 0x0C:
                print ("Need Establish Context first.")
                return 4
            else:
                print ("Other errors.")
                ret.check_status()
                return 5
        elif action == 2:  ## Release Context
            # build command
            cdw10 = build_command({"lid": (0xFF, 0, 0x0D),
                                   "lsp": (0x0F, 1, 2),   # Release Context:
                                   "rae": (0x80, 1, 0),
                                   "numdl": (0x0FFF, 2, 0),})
            cmd_struc = CmdStructure(opcode=0x02,
                                     cdw10=cdw10,)
            ret = self.execute(cmd_struc)
            ret.check_status()
            return 0
        elif action == 3:  ## Check if Context exist
            # build command
            # If extended data is not supported, then bits 27:16 of the Number of Dwords Lower field 
            # specify the Number of Dwords to transfer.
            # 0x0FFF is enough for 512 Bytes. we Do Not Need check the Log Page Attributes field
            cdw10 = build_command({"lid": (0xFF, 0, 0x0D),
                                   "lsp": (0x0F, 1, 0),   # Read Log Data
                                   "rae": (0x80, 1, 0),
                                   "numdl": (0x0FFF, 2, 127),})

            cmd_struc = CmdStructure(opcode=0x02,
                                     addr=data_addr,
                                     data_len=512,
                                     cdw10=cdw10,)
            # execute command
            ret = self.execute(cmd_struc)
            # if command abort, then Context is already established
            SC,SCT = ret.check_status(fail_hint=False)
            if SCT == 0 and SC == 0:  # can read, Context established
                return 1
            elif SCT == 0 and SC == 0x0C: # abort, Context Not established
                return 0
            else:
                return 5
        else:
            print ("Action should be 0|1|2|3.")
            return 6

    def self_test(self, stc, ns_id=0xFFFFFFFF,):
        ### build command
        cdw10 = build_command({"stc": (0x0F, 0, stc),})
        ###
        cmd_struc = CmdStructure(opcode=0x14,
                                 nsid=ns_id,
                                 cdw10=cdw10,
                                 timeout_ms=60000)
        ###
        ###
        ret = self.execute(cmd_struc)
        ret.check_status()
        return ret

    def self_test_log(self):
        ### build command
        numdl = int(564 / 4) - 1
        cdw10 = build_command({"lid": (0xFF, 0, 0x06),      # log id
                               "numdl": (0x0FFF, 2, numdl),})
        ##
        cmd_struc = CmdStructure(opcode=0x02,
                                 data_len=564,
                                 cdw10=cdw10,)
        ###
        ret = self.execute(cmd_struc)
        ret.check_status()
        return ret

    def ns_create(self, ns_size, ns_cap, flbas, dps, nmic, anagrp_id, nvmeset_id, vendor_spec_data=b''):
        ### build command
        cdw10 = build_command({"SEL": (0x0F, 0, 0x00),      # Select (SEL): This field selects the type of management operation to perform
                              })
        
        #
        data_dict = {"ns_size": ns_size,
                     "ns_cap": ns_cap,
                     "flbas": flbas,
                     "dps": dps,
                     "nmic": nmic,
                     "anagrp_id": anagrp_id,
                     "nvmeset_id": nvmeset_id,
                    }
        check_dict = {"ns_size": (0xFFFFFFFFFFFFFFFF, 0),
                      "ns_cap": (0xFFFFFFFFFFFFFFFF, 8),
                      "flbas": (0xFF, 26),
                      "dps": (0xFF, 29),
                      "nmic": (0xFF, 30),
                      "anagrp_id": (0xFFFFFFFF, 92),
                      "nvmeset_id": (0xFFFF, 100),
                     }
        #
        d = DataBuffer(4096)
        encode_data_buffer(data_dict, check_dict, d.data_buffer)
        # set vendor_spec_data
        if vendor_spec_data:
            cycles = min(len(vendor_spec_data), 3072)
            for i in range(cycles):
                d.data_buffer[1024+i] = vendor_spec_data[i]
        ##
        cmd_struc = CmdStructure(opcode=0x0D,
                                 nsid=0,         ## Create: The NSID field is reserved for this operation; host software clears this field to a value of 0h.
                                 data_len=4096,
                                 addr=d.addr,
                                 cdw10=cdw10,)
        ###
        ret = self.execute(cmd_struc)
        ret.check_status()
        return ret

    def ns_delete(self, ns_id):
        ### build command
        cdw10 = build_command({"SEL": (0x0F, 0, 0x01),      # Select (SEL): This field selects the type of management operation to perform
                              })
        ##
        cmd_struc = CmdStructure(opcode=0x0D,
                                 nsid=ns_id,
                                 cdw10=cdw10,)
        ###
        ret = self.execute(cmd_struc)
        ret.check_status()
        return ret

    def ns_attachment(self, ns_id, sel, ctrl_id_list):
        ### build command
        cdw10 = build_command({"SEL": (0x0F, 0, sel),      # Select (SEL):  This field selects the type of attachment to perform.
                              })
        ##
        id_num = len(ctrl_id_list)
        # id_num = min(len(ctrl_id_list), self.__ctrl_identify_info[338]+(self.__ctrl_identify_info[339] << 8))
        data_dict = {"id_number": id_num,}
        check_dict = {"id_number": (0xFFFF, 0),}
        for i in range(id_num):
            data_dict["id_%s" % i] = ctrl_id_list[i]
            check_dict["id_%s" % i] = (0xFFFF, 2+i*2)
        #
        d = DataBuffer(4096)
        encode_data_buffer(data_dict, check_dict, d.data_buffer)
        ##
        cmd_struc = CmdStructure(opcode=0x15,
                                 nsid=ns_id,
                                 data_len=4096,
                                 addr=d.addr,
                                 cdw10=cdw10,)
        ###
        ret = self.execute(cmd_struc)
        ret.check_status()
        return ret

    def sanitize(self, sanact, ause):
        pass
