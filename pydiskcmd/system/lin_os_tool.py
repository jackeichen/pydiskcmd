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
    return (dev_path.startswith("/dev/") and get_nvme_device_type(dev_path) == 1)

def check_nvme_if_ctrl_path(dev_path):
    return (dev_path.startswith("/dev/") and get_nvme_device_type(dev_path) == 0)

def get_nvme_dev_info():
    """
    Return: a list that contain ctrl_id, like ["nvme0", "nvme1"]
    """
    if os.path.exists('/sys/class/nvme'):
        return sorted([dev for dev in os.listdir('/sys/class/nvme') if dev.startswith("nvme")])
    return []

def get_nvme_device_type(name):
    '''
    Return:
      0: controller path, like nvme0
      1: Namespace path, like nvme0n1
      2: Partation path, like nvme0n1p1
      3: Alias Namespace path, like nvme0c1n1
    '''
    name = name.strip("/dev/")
    for index,pattern in enumerate([r'^nvme[0-9]+$', 
                                    r'^nvme[0-9]+n[0-9]+$',
                                    r'^nvme[0-9]+n[0-9]+p[0-9]+$',
                                    r'^nvme[0-9]+c[0-9]+n[0-9]+$',
                                    ]):
        if re.match(pattern, name):
            return index

def get_block_devs(print_detail=True) -> List[str]:
    """Determine the list of block devices by looking at /sys/block"""
    devs = [dev for dev in os.listdir('/sys/block')
            if not dev.startswith(excluded_block_devices)]
    if print_detail:
        print (f'{len(devs)} devices detected')
    return sorted(devs)

def get_nvme_block_devs_path():
    devs = ["/dev/%s" % dev for dev in os.listdir('/sys/block')
            if get_nvme_device_type(dev) == 1]
    return sorted(devs)

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


class NVMeNS(object):
    base_dir_path = '/sys/block/'
    def __init__(self, 
                 ns_name, 
                 nvme_ctrl=None,
                 path_prefix=None,
                 ):
        self.__nvme_ctrl = nvme_ctrl
        self.ns_name = ns_name
        if path_prefix is not None:
            self.__path_prefix = path_prefix
        elif nvme_ctrl:
            self.__path_prefix = nvme_ctrl._ctrl_path
        else:
            self.__path_prefix = NVMeNS.base_dir_path
        ##
        self._blk_path = os.path.join(self.__path_prefix, self.ns_name)

    def _init(self):
        pass

    def _get_ns_id(self, path):
        def _get_file_content(file):
            temp = os.path.join(NVMeNS.base_dir_path, path, file)
            if os.path.exists(temp):
                with open(temp, 'r') as f:
                    return f.read().strip()
        return _get_file_content('uuid'),_get_file_content('wwid'),_get_file_content('nguid')

    @property
    def nvme_ctrl(self):
        return self.__nvme_ctrl

    @property
    def path_prefix(self):
        return self.__path_prefix

    @property
    def dev_path(self):
        if get_nvme_device_type(self.ns_name) == 1:
            return "/dev/%s" % self.ns_name
        elif get_nvme_device_type(self.ns_name) == 3:
            ## Get nvme device type 1
            _id = self._get_ns_id(self.ns_name)
            for dev in os.listdir(NVMeNS.base_dir_path):
                if get_nvme_device_type(dev) == 1 and os.path.exists(os.path.join(NVMeNS.base_dir_path,dev)):
                    if self._get_ns_id(dev) == _id:
                        return "/dev/%s" % dev

    @property
    def ns_id(self):
        nsid = None
        with open(os.path.join(self._blk_path, 'nsid'), 'r') as f:
            nsid = int(f.read().strip())
        return nsid

    @property
    def wwid(self):
        wwid = None
        with open(os.path.join(self._blk_path, 'wwid'), 'r') as f:
            wwid = f.read().strip()
        return wwid

def scan_nvme_namespaces():
    all_info = {}
    if os.path.exists(NVMeNS.base_dir_path):
        for i in sorted([dev for dev in os.listdir(NVMeNS.base_dir_path) if get_nvme_device_type(dev) == 1 and os.path.exists(os.path.join(NVMeNS.base_dir_path,dev))]):
            all_info[i] = NVMeNS(i)
    return all_info


class NVMeController(object):
    base_dir_path = '/sys/class/nvme'
    def __init__(self, 
                 ctrl_name, 
                 subsystem=None,
                 path_prefix=None,
                 ):
        self.ctrl_name = ctrl_name
        self.__subsystem = subsystem
        if path_prefix is not None:
            self.__path_prefix = path_prefix
        elif subsystem:
            self.__path_prefix = subsystem._current_dir_path
        else:
            self.__path_prefix = NVMeController.base_dir_path
        #
        self._ctrl_path = os.path.join(self.__path_prefix, self.ctrl_name)
        ## init information

    def _init(self):
        pass

    @property
    def subsystem(self):
        return self.__subsystem

    @property
    def path_prefix(self):
        return self.__path_prefix

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
            if get_nvme_device_type(dir_name) in (1,3) and os.path.exists(os.path.join(self._ctrl_path,dir_name)):
                yield NVMeNS(dir_name, nvme_ctrl=self)

    def get_namespaces(self):
        return {i.ns_name: i for i in self.retrieve_ns()}


def scan_nvme_system():
    ctrl_names = get_nvme_dev_info()
    all_info = {}
    for i in ctrl_names:
        all_info[i] = NVMeController(i)
    return all_info


class NVMeSubsystem(object):
    base_dir_path = '/sys/devices/virtual/nvme-subsystem/'
    def __init__(self, 
                 subsystem_name,
                 path_prefix=None,
                 ):
        self.__path_prefix = NVMeSubsystem.base_dir_path if path_prefix is None else path_prefix
        self.__subsystem_name = subsystem_name
        self._current_dir_path = os.path.join(self.__path_prefix, self.__subsystem_name)

    @property
    def subsystem_name(self):
        return self.__subsystem_name

    @property
    def path_prefix(self):
        return self.__path_prefix

    def retrieve_ctrl(self):
        for dir_name in os.listdir(self._current_dir_path):
            if get_nvme_device_type(dir_name) == 0 and os.path.exists(os.path.join(self._current_dir_path,dir_name)):
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
    if os.path.exists(NVMeSubsystem.base_dir_path):
        for dir_name in os.listdir(NVMeSubsystem.base_dir_path):
            if dir_name.startswith("nvme-subsys") and os.path.exists(os.path.join(NVMeSubsystem.base_dir_path,dir_name)):
                all_info[dir_name] = NVMeSubsystem(dir_name)
    return all_info
