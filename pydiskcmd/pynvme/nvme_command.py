# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from abc import abstractmethod
from pydiskcmd.exceptions import *
from pydiskcmd.pynvme.linux_nvme_command import CmdStructure,DataBuffer,encode_data_buffer,build_int_by_bitmap
##

class CommandBase(object):
    '''
    :param req_id:  req_id used by IOCTL.
    '''
    def __init__(self, req_id):
        self.req_id = req_id 
        self.cdb = None
        ##
        self._cq_status_field = None

    @abstractmethod
    def build_command(self, **kwargs):
        '''Methmod to build command'''

    @property
    def cdb_raw(self):
        if self.cdb:
            return bytes(self.cdb)

    @property
    def cdb_struc(self):
        if self.cdb:
            return print(self.cdb.dump_element())

    @property
    def cq_status(self):
        return self._cq_status_field

    @cq_status.setter
    def cq_status(self, value):
        self._cq_status_field = value

    @property
    def cq_cmd_spec(self):
        return self.cdb.result

    @property
    def data(self):
        if self.cdb._data_buf:
            return bytes(self.cdb._data_buf)

    @property
    def meta_data(self):
        if self.cdb._metadata_buf:
            return bytes(self.cdb._metadata_buf)

    def check_return_status(self, success_hint=False, fail_hint=True):
        SC = (self.cq_status & 0xFF)
        SCT = ((self.cq_status >> 8) & 0x07)
        CRD = ((self.cq_status >> 11) & 0x03)
        More = (self.cq_status >> 13 & 0x01)
        DNR = (self.cq_status >> 14 & 0x01)
        if SCT == 0 and SC == 0:
            if success_hint:
                print ("Command Success")
                print ('')
        elif fail_hint:
            print ("Command failed, and details bellow.")
            format_string = "%-15s%-20s%-8s%s"
            print (format_string % ("Status Code", "Status Code Type", "More", "Do Not Retry"))
            print (format_string % (SC, SCT, More, DNR))
            print ('')
        return SC,SCT

class LinCommand(CommandBase):
    linux_req = {"NVME_IOCTL_ADMIN_CMD": 0xC0484E41,
                 "NVME_IOCTL_IO_CMD": 0xC0484E43}

    def __init__(self, req_id):
        super(LinCommand, self).__init__(req_id)

    def build_command(self, **kwargs):
        self.__kwargs = kwargs
        self.cdb = CmdStructure(**kwargs)
        return self.cdb


class WinCommand(CommandBase):
    win_req = {"IOCTL_STORAGE_QUERY_PROPERTY": 0x2D1400,
               "IOCTL_STORAGE_PROTOCOL_COMMAND": 0x2DD3C0,
               "IOCTL_STORAGE_FIRMWARE_DOWNLOAD": 0x2DDC04,
               "IOCTL_STORAGE_FIRMWARE_ACTIVATE": 0x2DDC08,
               "IOCTL_STORAGE_SET_TEMPERATURE_THRESHOLD": 0x2DD200,
               "IOCTL_STORAGE_SET_PROPERTY": 0x2D93FC,
               "IOCTL_STORAGE_MANAGE_DATA_SET_ATTRIBUTES": 0x2D9404,
               }

    def __init__(self, req_id):
        super(WinCommand, self).__init__(req_id)

    def build_command(self, **kwargs):
        self.__kwargs = kwargs
        return

