# SPDX-FileCopyrightText: 2020 The python-scsi Authors
#
# SPDX-License-Identifier: MIT
import sys,os
from pydiskcmd.utils import init_device
from pydiskcmd.pynvme.nvme import NVMe
from pydiskcmd.utils.format_print import format_dump_bytes
from pydiskcmd.utils.converter import scsi_ba_to_int,ba_to_ascii_string
##
from pydiskcmd.pynvme.nvme_spec import *
from pydiskcmd.pynvme.command_structure import DataBuffer


def test():
    dev = sys.argv[1]
    data_buffer = DataBuffer(16384)
    with NVMe(init_device(dev)) as d:
        ## first check if open, open if not
        we_open = False
        ret = d.get_persistent_event_log(3, data_buffer=data_buffer)
        if ret == 0:
            d.get_persistent_event_log(0, data_buffer=data_buffer)
            we_open = True
        ## read
        ret_0 = d.get_persistent_event_log(1)
        
        ret_1 = d.get_persistent_event_log(1, data_buffer=data_buffer)
        if ret_0[512:] == ret_1[512:]:
            print ("success!")
        else:
            print ("failed!")
        #para
        pass
        ## 
        if we_open:
            ret = d.get_persistent_event_log(2, data_buffer=data_buffer)

test()