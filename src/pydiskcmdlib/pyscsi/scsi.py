# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pyscsi.pyscsi.scsi import SCSI as _SCSI
from pydiskcmdlib.pyscsi.scsi_cdb_logsense import LogSense
from pydiskcmdlib.pyscsi.scsi_cdb_synchronizecache import SynchronizeCache10,SynchronizeCache16
from pydiskcmdlib.pyscsi.scsi_cdb_SecurityProtocolIn import SecurityProtocolIn
from pydiskcmdlib.pyscsi.scsi_cdb_passthru import CDBPassthru
from pydiskcmdlib.pyscsi.scsi_cdb_receivediagnosticresults import ReceiveDiagnosticResults # noqa
from pydiskcmdlib.pyscsi.scsi_cdb_writebuffer import WriteBuffer
from pydiskcmdlib.pyscsi.scsi_cdb_sanitize import Sanitize
from pydiskcmdlib.exceptions import ProtocolSettingError
from pyscsi.utils.converter import encode_dict


class SCSI(_SCSI):
    def __init__(self, 
                 dev,
                 blocksize=0):
        super(SCSI, self).__init__(dev, blocksize=blocksize)
        # auto detect blocksize
        if self._blocksize == 0:
            cap = self.readcapacity16().result
            self._blocksize = cap["block_length"]

    def __del__(self):
        if self.device:
            self.device.close()

    def cdb_passthru(self, raw_cdb, dataout=b'', datain_alloclen=0):
        """
        Returns a CDBPassthru Instance
        
        :param raw_cdb: a CDB Format bytes
        :param dataout_alloclen: the data_out buffer
        :param datain_alloclen: integer representing the size of the data_in buffer
        """
        cmd = CDBPassthru(raw_cdb, dataout=dataout, datain_alloclen=datain_alloclen)
        self.execute(cmd)
        return cmd

    def logsense(self, page_code, **kwargs):
        """
        Returns a LogSense Instance

        :param page_code:  The page requested
        :param kwargs: a dict with key/value pairs
                       sub_page_code = 0, Requested subpage
                       sp = 0, 
                       pc = 0, 
                       parameter = 0, 
                       alloclen = 512, 
                       control = 0
        :return: a LogSense instance
        """
        opcode = self.device.opcodes.LOG_SENSE
        cmd = LogSense(opcode, page_code, **kwargs)
        self.execute(cmd)
        cmd.unmarshall()
        return cmd

    def synchronizecache10(self, lba, block_number, **kwargs):
        """
        Returns a synchronizecache10 Instance

        :param lba:  The target LBA address
        :param block_number:  LBA length to sync cache
        :param kwargs: a dict with key/value pairs
                       passthrough to scsi_cdb_synchronizecache.SynchronizeCache10
        :return: a synchronizecache10 instance
        """
        opcode = self.device.opcodes.SYNCHRONIZE_CACHE_10
        cmd = SynchronizeCache10(opcode, lba, block_number, **kwargs)
        self.execute(cmd)
        return cmd

    def synchronizecache16(self, lba, block_number, **kwargs):
        """
        Returns a synchronizecache16 Instance

        :param lba:  The target LBA address
        :param block_number:  LBA length to sync cache
        :param kwargs: a dict with key/value pairs
                       passthrough to scsi_cdb_synchronizecache.SynchronizeCache16
        :return: a synchronizecache10 instance
        """
        opcode = self.device.opcodes.SYNCHRONIZE_CACHE_16
        cmd = SynchronizeCache16(opcode, lba, block_number, **kwargs)
        self.execute(cmd)
        return cmd

    def security_protocol_in(self, security_protocol, security_protocol_sp, alloc, **kwargs):
        """
        Returns a LogSense Instance

        :param security_protocol: a blocksize
        :param security_protocol_sp: Logical Block Address
        :param alloc: number of block
        :param kwargs: a dict with key/value pairs
                       passthrough to scsi_cdb_SecurityProtocolIn.SecurityProtocolIn
        :return: a security_protocol_in instance
        """
        opcode = self.device.opcodes.SECURITY_PROTOCOL_IN
        cmd = SecurityProtocolIn(opcode, security_protocol, security_protocol_sp, alloc, **kwargs)
        self.execute(cmd)
        return cmd

    def write_buffer(self, mode, mode_spec, buffer_id, buffer_offset, para_list_length, data=None, control=0):
        opcode = self.device.opcodes.WRITE_BUFFER
        cmd = WriteBuffer(opcode, mode, mode_spec, buffer_id, buffer_offset, para_list_length, data=data, control=control)
        self.execute(cmd)
        return cmd

    def sanitize(self, service_action: int, ause: int, znr: int, immed: int, control: int = 0, **kwargs):
        """
        Returns a Sanitize Instance

        :param service_action: a integer representing Service action
        :param ause: a integer representing Allow unrestricted sanitize exit
        :param znr: a integer representing ZNR
        :param immed: a integer representing Immediate
        :param control: The CONTROL byte is defined in SAM-5
        :param kwargs: a dict with key/value pairs, for Performing a sanitize overwrite operation
                    Key  
                    overwrite_count
                    test
                    invert
                    pattern
        :return: a Sanitize instance
        """
        opcode = self.device.opcodes.SANITIZE
        data_ba =None
        if service_action in (0x02, 0x03, 0x1F):
            para_list_len = 0
            if kwargs:
                raise ProtocolSettingError("data is not allowed for service action 0x%x" % service_action)
        elif service_action == 0x01:
            if not kwargs:
                raise ProtocolSettingError("kwargs is required for service action 0x%x" % service_action)
            para_list_len = len(kwargs.get("pattern")) + 4
            if not (4 < para_list_len < (self._blocksize + 5)):
                raise ProtocolSettingError("Your data length must be between 4 and %d" % (self._blocksize + 5))
            data_ba = bytearray(para_list_len)
            overwrite_para_list_bits = {
                "overwrite_count": [0x1F, 0],
                "test": [0x60, 0],
                "invert": [0x80, 0],
                "pattern_length": [0xFFFF, 2],
                "pattern": ('b', 4, len(kwargs.get("pattern"))),
            }
            encode_dict(kwargs, overwrite_para_list_bits, data_ba)
        else:
            # this will be Reserved field
            raise ProtocolSettingError("service action 0x%x is reserved" % service_action)
        cmd = Sanitize(opcode, service_action, ause, znr, immed, para_list_len, control=control, data=data_ba)
        self.execute(cmd)
        return cmd
