# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import os
import re
import socket
from typing import List
#####
PCIeMappingPath = "/sys/class/nvme/%s/address"
excluded_block_devices = ('sr', 'zram', 'dm-', 'md', 'loop')
#####

def map_pcie_addr_by_nvme_ctrl_path(dev_path):
    addr = None
    if check_nvme_if_ctrl_path(dev_path):
        path = PCIeMappingPath % dev_path.replace("/dev/", "")
        if os.path.exists(path):
            with open(path, 'r') as f:
                addr = f.read()
            addr = addr.strip()
    return addr

def check_nvme_if_ns_path(dev_path):
    g = re.match(r'/dev/nvme[0-9]+n[0-9]+', dev_path)
    return (g is not None)

def check_nvme_if_ctrl_path(dev_path):
    g = re.match(r'/dev/nvme[0-9]+', dev_path)
    return ((g is not None) and not check_nvme_if_ns_path(dev_path))

def get_block_devs(print_detail=True) -> List[str]:
    """Determine the list of block devices by looking at /sys/block"""
    devs = [dev for dev in os.listdir('/sys/block')
            if not dev.startswith(excluded_block_devices)]
    if print_detail:
        print (f'{len(devs)} devices detected')
    return sorted(devs)

def get_nvme_dev_info():
    """
    Return: a list that contain ctrl_id, like ["nvme0", "nvme1"]
    """
    if os.path.exists('/sys/class/nvme'):
        return sorted([dev for dev in os.listdir('/sys/class/nvme') if dev.startswith("nvme")])
    return []


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

def get_nvme_block_dev_by_ctrl_id(ctrl_id):
    """
    Return: a list that contain ns_id under ctrl_id, like ["nvme0n1", "nvme0n2"]
    """
    path = os.path.join('/sys/class/nvme', ctrl_id)
    return [dev for dev in os.listdir(path) if dev.startswith("nvme")]


class NVMeNS(object):
    base_dir_path = '/sys/class/block/'
    def __init__(self, ns_name, nvme_ctrl=None):
        self.__nvme_ctrl = nvme_ctrl
        self.ns_name = ns_name
        self._blk_path = os.path.join(NVMeNS.base_dir_path, self.ns_name)

    def _init(self):
        pass

    @property
    def nvme_ctrl(self):
        return self.__nvme_ctrl

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
    base_dir_path = '/sys/class/nvme'
    def __init__(self, ctrl_name, subsystem=None):
        self.ctrl_name = ctrl_name
        self.__subsystem = subsystem
        #
        self._ctrl_path = os.path.join(NVMeController.base_dir_path, self.ctrl_name)
        ## init information

    def _init(self):
        pass

    @property
    def subsystem(self):
        return self.__subsystem

    @property
    def dev_path(self):
        return "/dev/%s" % self.ctrl_name

    def _get_str_by_file(self, file_name):
        with open(os.path.join(self._ctrl_path, file_name), 'r') as f:
            temp = f.read()
        return temp.strip()

    @property
    def cntlid(self):
        return int(self._get_str_by_file('cntlid'))

    @property
    def address(self):
        return self._get_str_by_file('address')

    @property
    def state(self):
        return self._get_str_by_file('state')

    @property
    def transport(self):
        return self._get_str_by_file('transport')

    def retrieve_ns(self):
        for dir_name in os.listdir(self._ctrl_path):
            if dir_name.startswith("nvme"):
                yield NVMeNS(dir_name, nvme_ctrl=self)


def scan_nvme_system():
    ctrl_names = get_nvme_dev_info()
    all_info = {}
    for i in ctrl_names:
        all_info[i] = NVMeController(i)
    return all_info


class NVMeSubsystem(object):
    base_dir_path = '/sys/devices/virtual/nvme-subsystem/'
    def __init__(self, subsystem_name):
        self.__subsystem_name = subsystem_name
        self._current_dir_path = os.path.join(NVMeSubsystem.base_dir_path, self.__subsystem_name)

    @property
    def subsystem_name(self):
        return self.__subsystem_name

    def retrieve_ctrl(self):
        for dir_name in os.listdir(self._current_dir_path):
            if dir_name.startswith("nvme"):
                yield NVMeController(dir_name,subsystem=self)

    def get_ctrls(self):
        return {i.ctrl_name: i for i in self.retrieve_ctrl()}

    def _get_str_by_file(self, file_name):
        with open(os.path.join(self._current_dir_path, file_name), 'r') as f:
            temp = f.read()
        return temp.strip()

    @property
    def nqn(self):
        return self._get_str_by_file('subsysnqn')

    @property
    def model(self):
        return self._get_str_by_file('model')

    @property
    def firmware(self):
        return self._get_str_by_file('firmware_rev')

    @property
    def iopolicy(self):
        return self._get_str_by_file('iopolicy')

    @property
    def serial(self):
        return self._get_str_by_file('serial')


def scan_nvme_subsystem():
    all_info = {}
    for dir_name in os.listdir(NVMeSubsystem.base_dir_path):
        if dir_name.startswith("nvme-subsys"):
            all_info[dir_name] = NVMeSubsystem(dir_name)
    return all_info

