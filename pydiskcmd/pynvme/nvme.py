# SPDX-FileCopyrightText: 2014 The python-scsi Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import os
from pydiskcmd.pynvme.command_structure import CmdStructure
from pydiskcmd.pynvme.nvme_device import NVMeDevice
from pydiskcmd.pynvme.nvme_spec import nvme_id_ns_decode,nvme_id_ctrl_decode
from pydiskcmd.utils.converter import scsi_ba_to_int

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

    def get_feature(self, feature_id, sel=0):
        ### build command
        cdw10 = 0
        cdw14 = 0
        #
        cdw10 += feature_id
        cdw10 += (sel << 8)
        ##
        cmd_struc = CmdStructure(opcode=0x0A,
                                 cdw10=cdw10,)
        ###
        ret = self.execute(cmd_struc)
        ret.check_status()
        return ret

    def fw_slot_info(self):
        ### build command
        cdw10 = 0
        cdw11 = 0
        cdw12 = 0
        cdw13 = 0
        #
        cdw10 += 3  # Log ID
        cdw10 += (127 << 16)
        ##
        cmd_struc = CmdStructure(opcode=0x02,
                                 data_len=512,
                                 cdw10=cdw10,
                                 cdw11=cdw11,
                                 cdw12=cdw12,
                                 cdw13=cdw13,)
        ###
        ret = self.execute(cmd_struc)
        ret.check_status()
        return ret

    def error_log_entry(self):
        ## get the max number log entries
        max_number = self.__ctrl_identify_info[262] + 1
        number_bytes = max_number * 64
        NUMDL = number_bytes & 0xFFFF
        NUMDU = (number_bytes >> 16) & 0xFFFF
        ### build command
        cdw10 = 0
        cdw11 = 0
        cdw12 = 0
        cdw13 = 0
        #
        cdw10 += 1  # Log ID
        NUMDL = number_bytes & 0xFFFF
        cdw10 += (NUMDL << 16)
        #
        cdw11 += NUMDU
        ##
        cmd_struc = CmdStructure(opcode=0x02,
                                 data_len=number_bytes,
                                 cdw10=cdw10,
                                 cdw11=cdw11,
                                 cdw12=cdw12,
                                 cdw13=cdw13,)
        ###
        ret = self.execute(cmd_struc)
        ret.check_status()
        return ret

    def smart_log(self):
        ### build command
        cdw10 = 0
        cdw11 = 0
        cdw12 = 0
        cdw13 = 0
        #
        cdw10 += 2  # Log ID
        cdw10 += (512 << 16)
        ##
        cmd_struc = CmdStructure(opcode=0x02,
                                 nsid=0xFFFFFFFF,
                                 data_len=4096,
                                 cdw10=cdw10,
                                 cdw11=cdw11,
                                 cdw12=cdw12,
                                 cdw13=cdw13,)
        ###
        ret = self.execute(cmd_struc)
        ret.check_status()
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
        ### build command
        cdw10 = 0
        cdw11 = 0
        cdw12 = 0
        cdw13 = 0
        #
        cdw10 += 2  # Log ID
        cdw10 += (512 << 16)
        ##
        cmd_struc = CmdStructure(opcode=0x02,
                                 nsid=nsid,
                                 data_len=4096,
                                 cdw10=cdw10,
                                 cdw11=cdw11,
                                 cdw12=cdw12,
                                 cdw13=cdw13,)
        ###
        ret = self.execute_io(cmd_struc)
        ret.check_status()
        return ret
