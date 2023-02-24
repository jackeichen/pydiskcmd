# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
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


class DiskInfo(object):
    def __init__(self,
                 manufacturer,
                 product_name,
                 model_match):
        self.manufacturer = manufacturer # manufacturer, i.e. samsung
        self.product = product_name      # product name, i.e. PM9A3
        self.models = []                 # model number list
        self.model_match = model_match   # model match
        ##
        self.vs_log_page = {}            # store VendorSpecLogPageStruc info: key is VendorSpecLogPageStruc.name

    @property
    def match_id(self):
        return (self.model_match, None)

    def add_vs_log_page(self, *args, **kwargs):
        obj = VendorSpecLogPageStruc(*args, **kwargs)
        self.vs_log_page[obj.name] = obj

    def add_model(self, *args):
        for m in args:
            self.models.append(m)
