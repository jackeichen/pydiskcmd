# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later

import os
import time
import socket
from typing import List

excluded_block_devices = ('sr', 'zram', 'dm-', 'md', 'loop')

def timeit(func):
    def wrap(*args, **kwargs):
        start_time = time.time()
        print (f'{func.__name__} starting')
        result = func(*args, **kwargs)
        elapsed = time.time() - start_time
        print (f'{func.__name__} complete. Runtime {elapsed:.10f} secs')
        return result
    return wrap

def get_block_devs(print_detail=True) -> List[str]:
    """Determine the list of block devices by looking at /sys/block"""
    devs = [dev for dev in os.listdir('/sys/block')
            if not dev.startswith(excluded_block_devices)]
    if print_detail:
        print (f'{len(devs)} devices detected')
    return devs 

def get_nvme_dev_info():
    """
    Return: a list that contain ctrl_id, like ["nvme0", "nvme1"]
    """
    return [dev for dev in os.listdir('/sys/class/nvme') if dev.startswith("nvme")]

def get_nvme_block_dev_by_ctrl_id(ctrl_id):
    """
    Return: a list that contain ns_id under ctrl_id, like ["nvme0n1", "nvme0n2"]
    """
    path = os.path.join('/sys/class/nvme', ctrl_id)
    return [dev for dev in os.listdir(path) if dev.startswith("nvme")]


class SystemdNotify(object):
    def __init__(self):
        self.path = os.environ.get("NOTIFY_SOCKET")
        if self.path:
            if self.path[0] == "@":
                self.path = "\0" + self.path[1:]
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        else:
            raise RuntimeError("No NOTIFY_SOCKET Address.")

    def notify(self, **kwargs):
        arg_list = []
        for k,v in kwargs.items():
            arg_list.append("%s=%s" % (k,v))
        arg = "\n".join(arg_list)
        self.sock.sendto(arg.encode("utf-8"), self.path)
