# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmd.vendor_db.db_base import DiskInfo


class P5Series(DiskInfo):
    extend_smart_decode_bit = {'Lifetime NAND writes': ('b', 0x84, 5),
                               'Lifetime user writes': ('b', 0x90, 5),
                               }
    
    
    def __init__(self):
        super(PM9A3, self).__init__('Solidigm',
                                    'P5520/P5620',
                                    r'SSDPF2K.*',
                                    'nvme',
                                    models=('INTEL SSDPF2KX038T1N1',
                                            'INTEL SSDPF2KX019T1N1',
                                            'INTEL SSDPF2KX076T1N1',
                                            'INTEL SSDPF2KE064T1N1',
                                            'INTEL SSDPF2KE032T1N1',
                                            'INTEL SSDPF2KE016T1N1',
                                            ),
                                    )
        self.add_vs_log_page('Extended SMART Information Log',
                             0xCA,
                             512,
                             PM9A3.extend_smart_decode_bit)

    def getWA(self, raw_data):
        
