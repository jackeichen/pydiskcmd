# SPDX-FileCopyrightText: 2014 The python-scsi Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmd.pynvme.command_structure import CmdStructure
from pydiskcmd.pynvme.nvme_device import NVMeDevice


class NVMe(object):
    def __init__(self, dev):
        self.device = dev
    
    def __call__(self,
                 dev):
        """
        call the instance again with new device

        :param dev: a SCSIDevice or ISCSIDevice object
        """
        self.device = dev

    def __enter__(self):
        return self

    def __exit__(self,
                 exc_type,
                 exc_val,
                 exc_tb):
        self.device.close()

    def execute(self, cmd):
        """
        wrapper method to call the SCSIDevice.execute method

        :param cmd: a SCSICommand object
        """
        ret = None
        try:
            ret = self.device.execute(0, cmd)
        except Exception as e:
            raise e
        return ret
    
    def id_ctrl(self):
        ## build command
        cmd_struc = CmdStructure(opcode=0x06,
                                 data_len=4096,
                                 cdw10=0x01,)
        ##
        ret = self.execute(cmd_struc)
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


