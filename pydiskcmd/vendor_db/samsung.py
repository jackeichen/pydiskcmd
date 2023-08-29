# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmd.vendor_db.db_base import DiskInfo


class PM9A3(DiskInfo):
    extend_smart_decode_bit = {'Lifetime Program Fail Cnt ID': ('b', 0, 3),
                               'Lifetime Program Fail Cnt Normalized Value': ('b', 3, 2),
                               'Lifetime Program Fail Cnt Current Raw Value': ('b', 5, 7),
                               'Lifetime user writes': ('b', 264, 16),
                               'Lifetime NAND writes': ('b', 280, 16),
                               }
    
    
    def __init__(self):
        super(PM9A3, self).__init__('Samsung',
                                    'PM9A3',
                                    r'MZQL2.*',
                                    'nvme',
                                    models=('MZQL2960HCJR-00B7C',
                                            'MZQL21T9HCJR-00B7C',
                                            'MZQL23T8HCLS-00B7C',
                                            'MZQL27T6HBLA-00B7C'),
                                    )
        self.add_vs_log_page('Extended SMART Information Log',
                             0xCA,
                             512,
                             PM9A3.extend_smart_decode_bit)
