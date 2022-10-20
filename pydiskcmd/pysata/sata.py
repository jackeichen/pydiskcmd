# coding: utf-8

# Copyright (C) 2021 by Eric Gao<Eric-1128@outlook.com>
# SPDX-FileCopyrightText: 2014 The python-scsi Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmd.pyscsi.scsi_enum_command import spc, sbc, smc, ssc, mmc
from pydiskcmd.utils.converter import get_opcode
from pydiskcmd.pyscsi.scsi_cdb_inquiry import Inquiry
## cover before
from pydiskcmd.pysata.ata_cdb_AccessibleMaxAddress import AccessibleMaxAddressCfg
from pydiskcmd.pysata.ata_cdb_smart import SmartReadData,SmartReadThresh,SmartExeOffLineImm
from pydiskcmd.pysata.ata_cdb_readDMAEXT16 import ReadDMAEXT16
from pydiskcmd.pysata.ata_cdb_writeDMAEXT16 import WriteDMAEXT16
from pydiskcmd.pysata.ata_cdb_dsm import DSM
from pydiskcmd.pysata.ata_cdb_identify import Identify
from pydiskcmd.pysata.ata_cdb_flush import Flush
from pydiskcmd.pysata.ata_cdb_checkpowermode import CheckPowerMode
from pydiskcmd.pysata.ata_cdb_standbyImm import StandbyImm
from pydiskcmd.pysata.ata_cdb_hardreset import Hardreset
from pydiskcmd.pysata.ata_cdb_softreset import SoftReset
from pydiskcmd.pysata.ata_cdb_DeviceReset import DeviceReset
from pydiskcmd.pysata.ata_cdb_executeDeviceDiagnostic import ExecuteDeviceDiagnostic
from pydiskcmd.pysata.ata_cdb_downloadmicrocode import DownloadMicrocode,ActivateMicrocode


code_version = "0.1.0"

class SATA(object):
    """
    The interface to  the specialized scsi classes
    """
    def __init__(self,
                 dev,
                 blocksize=0):
        """
        initialize a new instance

        :param dev: a SCSIDevice object
        :param blocksize:  integer defining a blocksize
        """
        self.device = dev
        self._blocksize = blocksize
        self.__init_opcode()

    def __call__(self,
                 dev):
        """
        call the instance again with new device

        :param dev: a SCSIDevice or ISCSIDevice object
        """
        self.device = dev
        self.__init_opcode()

    def __enter__(self):
        return self

    def __exit__(self,
                 exc_type,
                 exc_val,
                 exc_tb):
        self.device.close()

    def __init_opcode(self):
        """
        Small helper method to terminate the type of
        the scsi device and assigning a proper opcode
        mapper.
        """
        if self.device is not None:
            self.device.devicetype = self.inquiry().result['peripheral_device_type']
            if self.device.devicetype in (0x00, 0x04, 0x07, ):  # sbc
                self.device.opcodes = sbc
            elif self.device.devicetype in (0x01, 0x02, 0x09):  # ssc
                self.device.opcodes = ssc
            elif self.device.devicetype in (0x03,):  # spc
                self.device.opcodes = spc
            elif self.device.devicetype in (0x08,):  # smc
                self.device.opcodes = smc
            elif self.device.devicetype in (0x05,):  # mmc
                self.device.opcodes = mmc

    def _execute(self, cmd):
        """
        wrapper method to call the SCSIDevice._execute method

        :param cmd: a SCSICommand object
        """
        self.device.execute(cmd)

    def execute(self, cmd):
        """
        wrapper method to call the SCSIDevice.execute method

        :param cmd: a SCSICommand object
        """
        try:
            self._execute(cmd)
            cmd.decode_sense()
        except Exception as e:
            raise e

    @property
    def blocksize(self):
        """
        getter method of the blocksize property

        :return: blocksize in bytes
        """
        return self._blocksize

    @blocksize.setter
    def blocksize(self,
                  value):
        """
        setter method of the blocksize property

        :param: blocksize in bytes
        """
        self._blocksize = value

    def inquiry(self,
                evpd=0,
                page_code=0,
                alloclen=96):
        """
        Returns a Inquiry Instance

        :param evpd: a byte indicating if vital product data is supported
        :param page_code: a byte representing a page code for vpd
        :param alloclen: the size of the data_in buffer
        :return: a Inquiry instance
        """
        opcode = self.device.opcodes.INQUIRY
        cmd = Inquiry(opcode,
                      evpd=evpd,
                      page_code=page_code,
                      alloclen=alloclen)
        try:
            self._execute(cmd)
        except Exception as e:
            raise e
        cmd.unmarshall(evpd=evpd)
        return cmd

    def getAccessibleMaxAddress(self):
        opcode = self.device.opcodes.PASS_THROUGH_16
        cmd = AccessibleMaxAddressCfg(opcode, self.blocksize, 0)
        self.execute(cmd)   # information need be reported in sense data
        return cmd

    def smart_read_data(self, smart_key=None):
        opcode = self.device.opcodes.PASS_THROUGH_16
        cmd = SmartReadData(opcode, self.blocksize, smart_key)
        self.execute(cmd)
        cmd.unmarshall()
        return cmd

    def smart_read_thresh(self):
        opcode = self.device.opcodes.PASS_THROUGH_16
        cmd = SmartReadThresh(opcode, self.blocksize)
        self.execute(cmd)
        return cmd

    def smart_exe_offline_imm(self, subcommand):
        opcode = self.device.opcodes.PASS_THROUGH_16
        cmd = SmartExeOffLineImm(opcode, self.blocksize, subcommand)
        self.execute(cmd)
        return cmd

    def read_DMAEXT16(self, 
                      lba,
                      tl,):
        """
        Returns a Read16 Instance

        :param lba: Logical Block Address to write to
        :param tl: Transfer Length in blocks
        
        :return: a read16 instance
        """
        opcode = self.device.opcodes.PASS_THROUGH_16
        cmd = ReadDMAEXT16(opcode, self.blocksize, lba, tl)
        self.execute(cmd)
        return cmd

    def write_DMAEXT16(self,
                       lba,
                       tl,
                       data):
        opcode = self.device.opcodes.PASS_THROUGH_16
        cmd = WriteDMAEXT16(opcode, self.blocksize, lba, tl, data)
        self.execute(cmd)
        return cmd

    def dsm(self,
            lba_description,
            fetures=1):
        '''
        lba_description = [[lba_start0,lba_length0], [lba_start1,lba_length1], ..., [lba_start63,lba_length63]]
            lba_description length more than 0 and less than 65
        '''
        ## check lba_description
        if 0 < len(lba_description) < 65:
            pass
        else:
            raise RuntimeError("lba_description format error!")
        ##
        data = bytearray(512)
        data_index = 0
        for lba_group in lba_description:
            lba_start,lba_length = lba_group
            #
            data[data_index] = (lba_start & 0xFF)
            data_index += 1
            data[data_index] = (lba_start & 0xFF00) >> 8
            data_index += 1
            data[data_index] = (lba_start & 0xFF0000) >> 16
            data_index += 1
            data[data_index] = (lba_start & 0xFF000000) >> 24
            data_index += 1
            data[data_index] = (lba_start & 0xFF00000000) >> 32
            data_index += 1
            data[data_index] = (lba_start & 0xFF00000000) >> 40
            data_index += 1
            data[data_index] = (lba_length & 0xFF)
            data_index += 1
            data[data_index] = (lba_length & 0xFF00) >> 8
            data_index += 1
        ##
        opcode = self.device.opcodes.PASS_THROUGH_16
        cmd = DSM(opcode, self.blocksize, fetures, data)
        self.execute(cmd)
        return cmd

    def trim(self, *args, **kwargs):
        return self.dsm(*args, **kwargs)

    def trimall(self,LBAS,fetures=1):
        single_cmd_num = 64
        single_cmd_unit_lbas = 4624
        LBAS = int(LBAS)
        single_cmd_lbas = single_cmd_num * single_cmd_unit_lbas
        #
        data = bytearray(512)
        for i in range(0,LBAS,single_cmd_lbas):
            lba_description = []
            for k in range(64):
                start_lba = i+k*single_cmd_unit_lbas
                if (start_lba+single_cmd_unit_lbas) <= LBAS:
                    lba_description.append((start_lba, single_cmd_unit_lbas))
                else:
                    lba_description.append((start_lba, LBAS-start_lba))
                    break
            #
            data_index = 0
            for lba_group in lba_description:
                lba_start,lba_length = lba_group
                data[data_index] = (lba_start & 0xFF)
                data_index += 1
                data[data_index] = (lba_start & 0xFF00) >> 8
                data_index += 1
                data[data_index] = (lba_start & 0xFF0000) >> 16
                data_index += 1
                data[data_index] = (lba_start & 0xFF000000) >> 24
                data_index += 1
                data[data_index] = (lba_start & 0xFF00000000) >> 32
                data_index += 1
                data[data_index] = (lba_start & 0xFF00000000) >> 40
                data_index += 1
                data[data_index] = (lba_length & 0xFF)
                data_index += 1
                data[data_index] = (lba_length & 0xFF00) >> 8
                data_index += 1
            # the rest data should be cleared 0 in the last value set
            for i in (data_index,512):
                data[i] = 0
            #
            opcode = self.device.opcodes.PASS_THROUGH_16
            cmd = DSM(opcode, self.blocksize, fetures, data)
            self.execute(cmd)
        return cmd

    def identify(self):
        opcode = self.device.opcodes.PASS_THROUGH_16
        cmd = Identify(opcode, self.blocksize)
        self.execute(cmd)
        cmd.unmarshall()
        return cmd

    def flush(self):
        opcode = self.device.opcodes.PASS_THROUGH_16
        cmd = Flush(opcode, self.blocksize)
        self.execute(cmd)
        return cmd
    
    def check_power_mode(self):
        opcode = self.device.opcodes.PASS_THROUGH_16
        cmd = CheckPowerMode(opcode, self.blocksize)
        self.execute(cmd)
        return cmd

    def standby_imm(self):
        opcode = self.device.opcodes.PASS_THROUGH_16
        cmd = StandbyImm(opcode, self.blocksize)
        self.execute(cmd)
        return cmd

    def hard_reset(self):
        opcode = self.device.opcodes.PASS_THROUGH_16
        cmd = Hardreset(opcode, self.blocksize)
        self.execute(cmd)
        return cmd

    def soft_reset(self):
        opcode = self.device.opcodes.PASS_THROUGH_16
        cmd = SoftReset(opcode, self.blocksize)
        self.execute(cmd)
        return cmd

    def device_reset(self):
        opcode = self.device.opcodes.PASS_THROUGH_16
        cmd = DeviceReset(opcode, self.blocksize)
        self.execute(cmd)
        return cmd

    def execute_device_diagnostic(self):
        opcode = self.device.opcodes.PASS_THROUGH_16
        cmd = ExecuteDeviceDiagnostic(opcode, self.blocksize)
        self.execute(cmd)
        return cmd

    def download_microcode(self,
                           feature,
                           lba,
                           tl,
                           data):
        opcode = self.device.opcodes.PASS_THROUGH_16
        cmd = DownloadMicrocode(opcode, self.blocksize, lba, tl, data, feature=feature)
        self.execute(cmd)
        return cmd

    def active_delayed_microcode(self):
        opcode = self.device.opcodes.PASS_THROUGH_16
        cmd = ActivateMicrocode(opcode, self.blocksize)
        self.execute(cmd)
        return cmd

    def download_fw(self, fw_path, transfer_size=0x200, feature=0x03):
        '''
        transfer_data_size = (transfer_size * 512), in every transfer, <transfer_data_size> blocks to transfer.
        '''
        ## read fw data
        with open(fw_path, 'rb') as fp:
            data = fp.read()
        ## check fw if multiple of 512
        res = len(data) % 512
        if res != 0:
            data += (b'\x00'*(512-re)) # need to be multiple of 512 Bytes, otherwise refill it.
        #dataview = memoryview(data)
        lba = 0
        length = len(data) / 512  # length=how many sectors(512 Bytes) of data
        ##
        if feature == 0x03 or feature == 0x0E:
            quotients = int(length / transfer_size) # 
            remainders = int(length % transfer_size)
            ##
            data_size = 512*transfer_size
            ##
            for i in range(0, quotients):
                cmd = self.download_microcode(feature, lba, transfer_size, data[i*data_size:(i+1)*data_size])
                ## first check sense data
                return_descriptor = cmd.ata_status_return_descriptor
                if return_descriptor:
                    if return_descriptor.get("error") != 0:
                        print ("Cycle: %s,Error: %s, status: %s" % (i, return_descriptor.get("error"), return_descriptor.get("status")))
                        return 1
                elif cmd.ata_sense_data_condition:  # something may be wrong here, check!
                    print ("Cycle: %s, Descrption: %s" % (i, cmd.ata_sense_data_condition._describe_ascq()))
                    print ('')
                    print (cmd.ata_sense_data_condition.data)
                    return 2
                lba += transfer_size
            if remainders != 0:
                cmd = self.download_microcode(feature, lba, remainders, data[quotients*data_size:])
                ##
                ## first check sense data
                return_descriptor = cmd.ata_status_return_descriptor
                if return_descriptor:
                    if return_descriptor.get("error") != 0:
                        print ("Cycle: %s, Error: %s, status: %s" % (i+1, return_descriptor.get("error"), return_descriptor.get("status")))
                elif cmd.ata_sense_data_condition:  # something may be wrong here, check!
                    print ("Cycle: %s, Descrption: %s" % (i+1, cmd.ata_sense_data_condition._describe_ascq()))
                    print ('')
                    print (cmd.ata_sense_data_condition.data)
        elif feature == 0x07:
            length = 0
            cmd = self.download_microcode(feature, lba, length, data)
            ## first check sense data
            return_descriptor = cmd.ata_status_return_descriptor
            if return_descriptor:
                if return_descriptor.get("error") != 0:
                    print ("Error: %s, status: %s" % (return_descriptor.get("error"), return_descriptor.get("status")))
                    return 1
            elif cmd.ata_sense_data_condition:  # something may be wrong here, check!
                print (cmd.ata_sense_data_condition._describe_ascq())
                print ('')
                print (cmd.ata_sense_data_condition.data)
                return 2
        else:
            return 3
        return 0
