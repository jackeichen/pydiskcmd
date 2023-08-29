# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmd.exceptions import ProtocolSettingError

class VendorSpecLogPageStruc(object):
    def __init__(self, 
                 name,
                 lid,
                 length,
                 decode_bit_mask=None):
        self.name = name
        self.lid = lid
        self.length = length
        self.decode_bit_mask = decode_bit_mask
        self.command = None


class DiskInfo(object):
    def __init__(self,
                 manufacturer,
                 product_name,
                 model_match,
                 disk_protocol,
                 models=None,):
        ##
        self.__disk_protocol = None
        self.models = []                 # model number list
        ##
        self.manufacturer = manufacturer # manufacturer, i.e. samsung
        self.product = product_name      # product name, i.e. PM9A3
        self.model_match = model_match   # model match
        self.disk_protocol = disk_protocol
        self.add_model(models)
        ##
        self.vs_log_page = {}            # store VendorSpecLogPageStruc info: key is VendorSpecLogPageStruc.name

    @property
    def disk_protocol(self):
        return self.__disk_protocol

    @disk_protocol.setter
    def disk_protocol(self, value):
        if value in ('sata','sas','nvme'):
            self.__disk_protocol = value
        else:
            raise ProtocolSettingError("Disk Protocal shouldbe sata|sas|nvme, but not %s" % value)

    @property
    def match_id(self):
        return (self.model_match, None)

    @property
    def family_description(self):
        return "%s family %s series" % (self.manufacturer,self.product)

    def add_vs_log_page(self, *args, **kwargs):
        obj = VendorSpecLogPageStruc(*args, **kwargs)
        self.vs_log_page[obj.lid] = obj

    def add_model(self, *args):
        if args:
            for m in args:
                self.models.append(m)
