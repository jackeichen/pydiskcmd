# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import os
from mmap import mmap, PROT_READ, PROT_WRITE, PAGESIZE
from struct import pack, unpack
##
from pydiskcmd.pypci.pci_decode import PCIConfigSpace,scsi_ba_to_int,get_pci_descriptation

################
pci_ids_locations = [
        "/usr/share/hwdata/pci.ids",
        "/usr/share/misc/pci.ids",
    ]

CLASS_ALIASES = {  # noqa
    'nvme': 0x010802,
    'ethernet': 0x020000,
    'raid': 0x010400,
    'gpu': 0x030200,
}

CLASSCODE_NAME = {value: name for name,value in CLASS_ALIASES.items()}

EXPRESS_TYPES = {
    0x0: 'endpoint',
    0x1: 'legacy_endpoint',
    0x4: 'root_port',
    0x5: 'upstream_port',
    0x6: 'downstream_port',
    0x7: 'pci_bridge',
    0x8: 'pcie_bridge',
    0x9: 'root_complex_endpoint',
    0xa: 'root_complex_event_collector',
}

EXPRESS_SPEED = {
    1: "2.5GT/s",
    2: "5GT/s",
    3: "8GT/s",
    4: "16GT/s",
    5: "32GT/s",
    6: "64GT/s",
}

PCI_EXP_SLOT_CTL_ATTN_LED_VALUES = {
    0x00: 'reserved',
    0x00c0: 'off',
    0x0080: 'blink',
    0x0040: 'on',
}

################
def valid_pcie_bus_addr(bus_addr):
    temp = bus_addr.split(":")
    if len(temp) not in (2,3):
        return False
    for i in temp[:-1]:
        if not i.isdigit():
            return False
    temp = temp[-1].split(".")
    if len(temp) == 2 and temp[0].isdigit() and temp[1].isdigit():
        return True
    return False

def dump_pcie_aer(path):
    result = {}
    for file_name in ("aer_dev_correctable", "aer_dev_fatal", "aer_dev_nonfatal"):
        result[file_name] = {}
        file = os.path.join(path, file_name)
        if os.path.isfile(file):
            with open(file, 'r') as f:
                while True:
                    temp = f.readline()
                    if not temp:
                        break
                    temp = temp.split(" ")
                    result[file_name][temp[0].strip()] = int(temp[1].strip())
    return result
################
class PCIeConfig(object):
    def __init__(self, config_path):
        self.__config_path = config_path
        self._pcie_config_space = None
        ##
        self.init_data()

    def init_data(self):
        if os.path.isfile(self.__config_path):
            with open(self.__config_path, 'rb') as f:
                raw_data = f.read()
            self._pcie_config_space = PCIConfigSpace(raw_data)
        else:
            raise FileNotFoundError("%s Not Found" % self.__config_path)

    @property
    def raw_data(self):
        return self._pcie_config_space.raw_data

    @property
    def config_path(self):
        return self.__config_path

    @property
    def size(self):
        return len(self.raw_data)

    @property
    def pci_header(self):
        return self._pcie_config_space.PCIConfigHeader

    @property
    def pci_cap(self):
        return self._pcie_config_space.PCICap

    @property
    def pcie_cap(self):
        return self._pcie_config_space.PCICap.pci_cap_deocde.get(0x10)

    @property
    def pcie_extend_cap(self):
        return self._pcie_config_space.PCIeExtendCap

    def read(self, offset, data_len=2):
        return self.raw_data[offset:offset+data_len]

    def get_parent(self):
        temp = os.path.realpath(os.path.dirname(self.config_path))
        config_path = None
        while temp.strip('/'):
            temp = os.path.dirname(temp)
            config_path = os.path.join(temp, 'config')
            if os.path.exists(config_path):
                break
        if config_path:
            return PCIeConfig(config_path)


class PCIExpressLink(object):
    def __init__(self, 
                 cur_speed, 
                 cur_width,
                 capable_speed, 
                 capable_width):
        self.cur_speed = cur_speed
        self.cur_width = cur_width
        self.capable_speed = capable_speed
        self.capable_width = capable_width


class NVMePCIe(PCIeConfig):
    PCIeBasePath = '/sys/class/nvme/%s/'
    PCIeConfigPath = os.path.join(PCIeBasePath, 'device', 'config')
    def __init__(self, ctrl_name):
        if ctrl_name.startswith("/dev/"):
            ctrl_name = ctrl_name.strip("/dev/")
        self.__ctrl_name = ctrl_name
        config_path = NVMePCIe.PCIeConfigPath % self.__ctrl_name
        super(NVMePCIe, self).__init__(config_path)

    def re_init_config_data(self):
        ## Re-read config data
        self.init_data()

    @property
    def ctrl_name(self):
        return self.__ctrl_name

    @property
    def address(self):
        with open(os.path.join(NVMePCIe.PCIeBasePath % self.__ctrl_name, 'address'), 'r') as f:
            address = f.read()
        return address.strip()

    @property
    def express_aer(self):
        return {'device': dump_pcie_aer(os.path.join(NVMePCIe.PCIeBasePath % self.__ctrl_name, 'device')),}

    @property
    def express_link(self):
        '''
        For compatibility of pydiskhealthd
        '''
        return PCIExpressLink(EXPRESS_SPEED.get(self.pcie_cap.link_status.decode_data["LinkSpeed"]), self.pcie_cap.link_status.decode_data["LinkWidth"],
                              EXPRESS_SPEED.get(self.pcie_cap.link_cap.decode_data["MaxLinkSpeed"]), self.pcie_cap.link_cap.decode_data["MaxLinkWidth"],
                              )

    def simple_info_print(self):
        print ("%-11s: %s" % ("Bus address", self.address))
        ## slot is parent physical slot number
        parent = self.get_parent()
        slot = "Unknown"
        up_dev_type = 'Unknown'
        if parent and parent.pcie_cap:
            slot = parent.pcie_cap.slot_cap.decode_data["PhysicalSlotNumber"]
            up_dev_type  = EXPRESS_TYPES.get(parent.pcie_cap.cap_reg.decode_data["DevOrPortType"])
        print ("%-11s: slot %d, %s" % ("Locate To", slot, up_dev_type))
        print ("%-11s: %s" % ("Device Type", EXPRESS_TYPES.get(self.pcie_cap.cap_reg.decode_data["DevOrPortType"])))
        print ("%-11s: %#x (%s)" % ("Class ID", scsi_ba_to_int(self.pci_header.decode_data["ClassCode"], byteorder='little'), CLASSCODE_NAME.get(scsi_ba_to_int(self.pci_header.decode_data["ClassCode"], byteorder='little'))))
        vendor_id = scsi_ba_to_int(self.pci_header.decode_data["VendorID"], byteorder='little')
        device_id = scsi_ba_to_int(self.pci_header.decode_data["DeviceID"], byteorder='little')
        subvendor_id = scsi_ba_to_int(self.pci_header.decode_data["SubsystemVendorID"], byteorder='little')
        subdevice_id = scsi_ba_to_int(self.pci_header.decode_data["SubsystemDeviceID"], byteorder='little')
        dev_name = 'Unknown'
        for f in pci_ids_locations:
            if os.path.isfile(f):
                dev_name = ", ".join(get_pci_descriptation(f, "%x" % vendor_id, device_id="%x" % device_id, subvd_id=("%x" % subvendor_id,"%x" % subdevice_id)))
        print ("%-11s: %s" % ("Device Name", dev_name))
        print ("")
        print ("VID=%#x, DID=%#x, SSVID=%#x, SSDID=%#x" % (vendor_id,device_id,subvendor_id,subdevice_id))
        print ("Speed is %s(capable %s), width is %d(capable %d)" % (EXPRESS_SPEED.get(self.pcie_cap.link_status.decode_data["LinkSpeed"]), 
                                                                     EXPRESS_SPEED.get(self.pcie_cap.link_cap.decode_data["MaxLinkSpeed"]),
                                                                     self.pcie_cap.link_status.decode_data["LinkWidth"],
                                                                     self.pcie_cap.link_cap.decode_data["MaxLinkWidth"],
                                                                     ))


class PCIeBar(object):
    def __init__(self, bar_path):
        self.__context = None
        self.__stat = None
        ##
        self.__bar_path = bar_path
        ##
        self.open()

    def open(self):
        if os.path.isfile(self.__bar_path):
            self.__stat = os.stat(self.__bar_path)
            fd = os.open(self.__bar_path, os.O_RDONLY)
            self.__context = mmap(fd, 0, prot=PROT_READ)
            os.close(fd)
        else:
            raise

    def close(self):
        if self.__context:
            self.__context.close()
            self.__context = None
            self.__stat = None

    def __del__(self):
        self.close()

    def read(self, offset, data_len=4):
        _offset = offset
        _data_len = data_len
        if offset % 4:
            _offset = offset - (offset % 4)
            _data_len += offset % 4
        if _data_len % 4:
            _data_len += (4 - (data_len % 4))
        temp = b''
        index = 0
        while (index < _data_len):
            temp += self.__context[_offset+index:_offset+index+4]
            index += 4
        return temp[(offset%4):data_len]

    @property
    def size(self):
        return self.__stat.st_size


class PCIeNVMeBar(PCIeBar):
    BarConfigPath = '/sys/class/nvme/%s/device/resource0'
    def __init__(self, ctrl_name):
        if ctrl_name.startswith("/dev/"):
            ctrl_name = ctrl_name.strip("/dev/")
        self.__ctrl_name = ctrl_name
        config_path = PCIeNVMeBar.BarConfigPath % self.__ctrl_name
        super(PCIeNVMeBar, self).__init__(config_path)

    @property
    def ctrl_name(self):
        return self.__ctrl_name

