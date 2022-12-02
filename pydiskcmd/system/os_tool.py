# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later

import os
import time
import socket
from typing import List
from pydiskcmd.system.env_var import os_type

###
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
    if os.path.exists('/sys/class/nvme'):
        return [dev for dev in os.listdir('/sys/class/nvme') if dev.startswith("nvme")]
    return []

def get_nvme_block_dev_by_ctrl_id(ctrl_id):
    """
    Return: a list that contain ns_id under ctrl_id, like ["nvme0n1", "nvme0n2"]
    """
    path = os.path.join('/sys/class/nvme', ctrl_id)
    return [dev for dev in os.listdir(path) if dev.startswith("nvme")]


class NVMeNS(object):
    def __init__(self, nvme_ctrl, ns_name):
        self.nvme_ctrl = nvme_ctrl
        self.ns_name = ns_name
        self._blk_path = os.path.join('/sys/class/nvme', self.nvme_ctrl.ctrl_name, self.ns_name)

    def _init(self):
        pass

    @property
    def dev_path(self):
        return "/dev/%s" % self.ns_name

    @property
    def ns_id(self):
        nsid = None
        with open(os.path.join(self._blk_path, 'nsid'), 'r') as f:
            nsid = int(f.read().strip())
        return nsid


class NVMeController(object):
    def __init__(self, ctrl_name):
        self.ctrl_name = ctrl_name
        #
        self._ctrl_path = os.path.join('/sys/class/nvme', self.ctrl_name)
        ## init information

    def _init(self):
        pass

    @property
    def dev_path(self):
        return "/dev/%s" % self.ctrl_name

    @property
    def cntlid(self):
        cntlid = None
        with open(os.path.join(self._ctrl_path, 'cntlid'), 'r') as f:
            cntlid = int(f.read().strip())
        return cntlid

    def retrieve_ns(self):
        for dir_name in os.listdir(self._ctrl_path):
            if dir_name.startswith("nvme"):
                yield NVMeNS(self, dir_name)


def scan_nvme_system():
    ctrl_names = get_nvme_dev_info()
    all_info = {}
    for i in ctrl_names:
        all_info[i] = NVMeController(i)
    return all_info


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
