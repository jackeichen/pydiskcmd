# SPDX-FileCopyrightText: 2014 The python-scsi Authors
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

@timeit
def get_block_devs() -> List[str]:
    """Determine the list of block devices by looking at /sys/block"""
    devs = [dev for dev in os.listdir('/sys/block')
            if not dev.startswith(excluded_block_devices)]
    print (f'{len(devs)} devices detected')
    return devs


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
