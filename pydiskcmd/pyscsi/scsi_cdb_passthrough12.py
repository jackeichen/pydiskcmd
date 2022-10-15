# coding: utf-8

# Copyright (C) 2014 by Ronnie Sahlberg<ronniesahlberg@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 2.1 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
from pydiskcmd.pyscsi.scsi_command import SCSICommand
from pydiskcmd.utils.byte_converter import byteconvert2
from pydiskcmd.pyscsi.scsi_sense import SCSICheckCondition,decode_bits
#
# SCSI pass-through command and definitions
#

class ATACheckReturnDescriptorCondition(SCSICheckCondition):

    _extend_ata_status_return_descriptor=         {'descriptor_code': [0xff, 0],
                                                   'additional_descriptor_length': [0xff, 1],
                                                   'extend': [0x01, 2],
                                                   'error': [0xff, 3],
                                                   'sector_count_rsvd': [0xff, 4],
                                                   'sector_count': [0xff, 5],
                                                   'lba_low_rsvd': [0xff, 6],
                                                   'lba_low': [0xff, 7],
                                                   'lba_mid_rsvd': [0xff, 8],
                                                   'lba_mid': [0xff, 9],
                                                   'lba_high_rsvd': [0xff, 10],
                                                   'lba_high': [0xff, 11],
                                                   'device': [0xff, 12],
                                                   'status': [0xff, 13], }        

    def __init__(self,
                 sense,
                 print_data=False):
        super(ATACheckReturnDescriptorCondition, self).__init__(sense, print_data=print_data)
        ##
        if self.asc == 0 and self.ascq == 29: ## ATA PASS THROUGH INFORMATION AVAILABLE
            self.data['ata_pass_thr_return_descriptor'] = self.unmarshall_extend_ata_status_return_descriptor_data(sense[8:22])

    @property
    def ata_pass_thr_return_descriptor(self):
        return self.data.get("ata_pass_thr_return_descriptor")

    @staticmethod
    def unmarshall_extend_ata_status_return_descriptor_data(data):
        result = {}
        decode_bits(data,
                    ATACheckReturnDescriptorCondition._extend_ata_status_return_descriptor,
                    result)
        return result



class PassThrough12(SCSICommand):
    """
    A class to send a PassThrough16 command to a scsi device
    """
    _cdb_bits = {'opcode': [0xff, 0],
                 'mul_count':[0xE0,1],
                 'protocal':[0x1E,1],
                 'extend':[0x01,1],
                 'off_line':[0xC0,2],
                 'ck_cond':[0x20,2],
                 'reserved2':[0x10,2],
                 't_dir':[0x08,2],
                 'byte_block':[0x04,2],
                 't_lenght':[0x03,2],
                 'fetures':[0xff,3],
                 'sector_count':[0xff,4],
                 'lba':[0xffffff,5],
                 'device':[0xff,8],
                 'command':[0xff,9],
                 'reserved10':[0xff,10],
                 'control':[0xff,11],}

    def __init__(self,
                 opcode,
                 blocksize,
                 lba,
                 protocal,
                 t_lenght,
                 t_dir,
                 fetures,
                 sector_count,
                 command,
                 extend=0,
                 mul_count=0,
                 byte_block=1,
                 ck_cond=0,
                 off_line=0,
                 device=0x00,
                 control=0,
                 reserved2=0,
                 reserved10=0x00,
                 dataout=None
                 ):
        """
        initialize a new instance
        ## wait to change
        :param opcode: a OpCode instance
        :param blocksize: a blocksize
        :param lba: Logical Block Address
        :param tl: transfer length
        :param rdprotect=0:
        :param dpo=0:
        :param fua=0:
        :param rarc=0:
        :param group=0:
        """
        if blocksize == 0:
            raise SCSICommand.MissingBlocksizeException

        if t_lenght == 1:
            count = fetures
        elif t_lenght == 2:
            count = sector_count
        else:
            count = 1
        
        if t_dir == 0:
            args = (opcode, blocksize * count, 0)
        else:
            args = (opcode, 0, blocksize * count)
        SCSICommand.__init__(self, *args)
        self.check_sense = ck_cond
        self.dataout = dataout

        self.cdb = self.build_cdb(
                       opcode=self.opcode.value,
                       protocal=protocal,
                       t_lenght=t_lenght,
                       extend=extend,
                       t_dir=t_dir,
                       fetures=fetures,
                       sector_count=sector_count,
                       lba=byteconvert2(lba),
                       command=command,
                       mul_count=mul_count,
                       byte_block=byte_block,
                       ck_cond=ck_cond,
                       off_line=off_line,
                       device=device,
                       control=control,
                       )
        ###
        self.ata_sense_data_condition = None
        self.ata_sense_data = {}

    @property
    def ata_status_return_descriptor(self):
        if not self.ata_sense_data:
            self.ata_sense_data_condition = ATACheckReturnDescriptorCondition(self.sense)
            self.ata_sense_data = self.ata_sense_data_condition.data
        return self.ata_sense_data.get("ata_pass_thr_return_descriptor")
