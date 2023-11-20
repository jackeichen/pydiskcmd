# # SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmd.utils.converter import decode_bits,scsi_ba_to_int


class PCIConfigHeader(object):
    ## Heander common bitmap locates in DWrod 0 ~ 5
    HeaderCommonBitmask = {"VendorID": ('b', 0, 2),
                           "DeviceID": ('b', 2, 2),
                           "Command": ('b', 4, 2),
                           "Status": ('b', 6, 2),
                           "RevisionID": ('b', 8, 1),
                           "ClassCode": ('b', 9, 3),
                           "CacheLineSize": ('b', 12, 1),
                           "LatTimer": ('b', 13, 1),
                           "HeaderType": ('b', 14, 1),
                           "BIST": ('b', 15, 1),
                           "CapPointer": ('b', 52, 1),
                           "InterruptLine": ('b', 60, 1),
                           "InterruptPin": ('b', 61, 1),
                           }
    ## Type 0 self bitmap, DWrod 6 ~ 15
    T0Bitmask = {"BaseAddr_0": ('b', 16, 4),
                 "BaseAddr_1": ('b', 20, 4),
                 "BaseAddr_2": ('b', 24, 4),
                 "BaseAddr_3": ('b', 28, 4),
                 "BaseAddr_4": ('b', 32, 4),
                 "BaseAddr_5": ('b', 36, 4),
                 "CardBusCISPointer": ('b', 40, 4),
                 "SubsystemVendorID": ('b', 44, 2),
                 "SubsystemDeviceID": ('b', 46, 2),
                 "ExpROMBaseAddr": ('b', 48, 4),
                 "MinGnt": ('b', 62, 1),
                 "MaxLat": ('b', 63, 1),
                 }
    ## Type 1 self bitmap, DWrod 6 ~ 15
    T1Bitmask = {"BaseAddr_0": ('b', 16, 4),
                 "BaseAddr_1": ('b', 20, 4),
                 "PriBusNum": ('b', 24, 1),
                 "SecBusNum": ('b', 25, 1),
                 "SubBusNum": ('b', 26, 1),
                 "SecLatTimer": ('b', 27, 1),
                 "IOBase": ('b', 28, 1),
                 "IOLimit": ('b', 29, 1),
                 "SecStatus": ('b', 30, 2),
                 "MemoryBase": ('b', 32, 2),
                 "MemoryLimit": ('b', 34, 2),
                 "PrefetchableMemBase": ('b', 36, 2),
                 "PrefetchableMemLimit": ('b', 38, 2),
                 "PrefetchableBaseU": ('b', 40, 4),
                 "PrefetchableLimitU": ('b', 44, 4),
                 "IOBaseU": ('b', 48, 2),
                 "IOLimitU": ('b', 50, 2),
                 "ExpROMBaseAddr": ('b', 56, 4),
                 "BridgeControl": ('b', 62, 2),
                 }
    def __init__(self, raw_data):
        self.__raw_data = raw_data
        self.__pci_config_header = {}
        decode_bits(raw_data, PCIConfigHeader.HeaderCommonBitmask, self.__pci_config_header)
        if self.header_type & 0x7F == 0:
            decode_bits(raw_data, PCIConfigHeader.T0Bitmask, self.__pci_config_header)
        elif self.header_type & 0x7F == 1:
            decode_bits(raw_data, PCIConfigHeader.T1Bitmask, self.__pci_config_header)
        else:
            raise

    @property
    def raw_data(self):
        return self.__raw_data

    @property
    def decode_data(self):
        return self.__pci_config_header

    @property
    def header_type(self):
        return self.__pci_config_header["HeaderType"][0]


class PCIeCapRegister(object):
    CapRegisterBitMap = {"CapabilityVersion": ('bb', 0, 4),
                         "DevOrPortType": ('bb', 4, 4),
                         "SlotImplemented": ('bb', 8, 1),
                         "InterruptMessageNumber": ('bb', 9, 5),
                         # "Undefined": ('bb', 14, 1)  # Leave it, different in different version spec.
                         }
    def __init__(self, raw_data):
        self.__raw_data = raw_data
        self.__cap_reg = {}
        decode_bits(raw_data, PCIeCapRegister.CapRegisterBitMap, self.__cap_reg)

    @property
    def raw_data(self):
        return self.__raw_data

    @property
    def decode_data(self):
        return self.__cap_reg


class PCIeLinkCap(object):
    LinkCapBitMap = {"MaxLinkSpeed": ('bb', 0, 4),
                     "MaxLinkWidth": ('bb', 4, 6),
                     "ASPMSupport": ('bb', 10, 2),
                     "L0sExitLat": ('bb', 12, 3),
                     "L1ExitLat": ('bb', 15, 3),
                     "ClockPowerManagement": ('bb', 18, 1),
                     "SurpriseDownErrReportingCap": ('bb', 19, 1),
                     "DataLinkLayerLinkActiveReportingCap": ('bb', 20, 1),
                     "LinkBWNotificationCap": ('bb', 21, 1),
                     "ASPMOptionalityCompliance": ('bb', 22, 1),
                     "PortNumber": ('bb', 24, 8),
                     }
    def __init__(self, raw_data):
        self.__raw_data = raw_data
        self.__link_cap = {}
        decode_bits(raw_data, PCIeLinkCap.LinkCapBitMap, self.__link_cap)

    @property
    def raw_data(self):
        return self.__raw_data

    @property
    def decode_data(self):
        return self.__link_cap


class PCIeLinkStatus(object):
    LinkStatusBitMap = {"LinkSpeed": ('bb', 0, 4),
                        "LinkWidth": ('bb', 4, 6),
                        "LinkTraining": ('bb', 10, 1),
                        "SlotClockConfig": ('bb', 11, 1),
                        "DataLinkLayerLinkActive": ('bb', 12, 1),
                        "LinkBWManagementStatus": ('bb', 13, 1),
                        "LinkAutonomousBWStatus": ('bb', 14, 1),
                        }
    def __init__(self, raw_data):
        self.__raw_data = raw_data
        self.__link_status = {}
        decode_bits(raw_data, PCIeLinkStatus.LinkStatusBitMap, self.__link_status)

    @property
    def raw_data(self):
        return self.__raw_data

    @property
    def decode_data(self):
        return self.__link_status


class PCIeSlotCap(object):
    SlotCapBitMap = {"AttentionButtonPresent": ('bb', 0, 1),
                     "PowerCtrlPresent": ('bb', 1, 1),
                     "MRLSensorPresent": ('bb', 2, 1),
                     "AttentionIndicatorPresent": ('bb', 3, 1),
                     "PowerIndicatorPresent": ('bb', 4, 1),
                     "Hot-PlugSurprise": ('bb', 5, 1),
                     "Hot-PlugCapable": ('bb', 6, 1),
                     "SlotPowerLimitValue": ('bb', 7, 8),
                     "SlotPowerLimitScale": ('bb', 15, 2),
                     "ElectInterlockPresent": ('bb', 17, 1),
                     "NoCommandCompletedSupport": ('bb', 18, 1),
                     "PhysicalSlotNumber": ('bb', 19, 13),
                     }
    def __init__(self, raw_data):
        self.__raw_data = raw_data
        self.__slot_cap = {}
        decode_bits(raw_data, PCIeSlotCap.SlotCapBitMap, self.__slot_cap)

    @property
    def raw_data(self):
        return self.__raw_data

    @property
    def decode_data(self):
        return self.__slot_cap


class PCIeCap(object):
    PCIeCapBitMap = {"PCIeCapID": ('b', 0, 1),
                     "NextCapPointer": ('b', 1, 1),
                     "PCIeCapRegister": ('b', 2, 2),
                     "DeviceCap": ('b', 4, 4),
                     "DeviceControl": ('b', 8, 2),
                     "DeviceStatus": ('b', 10, 2),
                     "LinkCap": ('b', 12, 4),
                     "LinkControl": ('b', 16, 2),
                     "LinkStatus": ('b', 18, 2),
                     "SlotCap": ('b', 20, 4),
                     "SlotControl": ('b', 24, 2),
                     "SlotStatus": ('b', 26, 2),
                     "RootControl": ('b', 28, 2),
                     "RootCap": ('b', 30, 2),
                     "RootStatus": ('b', 32, 4),
                     "DeviceCap2": ('b', 36, 4),
                     "DeviceControl2": ('b', 40, 2),
                     "DeviceStatus2": ('b', 42, 2),
                     "LinkCap2": ('b', 44, 4),
                     "LinkControl2": ('b', 48, 2),
                     "LinkStatus2": ('b', 50, 2),
                     "SlotCap2": ('b', 52, 4),
                     "SlotControl2": ('b', 56, 2),
                     "SlotStatus2": ('b', 58, 2),
                     }
    def __init__(self, raw_data):
        self.__raw_data = raw_data
        self.__pcie_cap = {}
        decode_bits(raw_data, PCIeCap.PCIeCapBitMap, self.__pcie_cap)
        if self.__pcie_cap["NextCapPointer"][0] > 0: # TODO
            pass
    @property
    def raw_data(self):
        return self.__raw_data

    @property
    def decode_data(self):
        return self.__pcie_cap

    @property
    def slot_cap(self):
        return PCIeSlotCap(self.__pcie_cap.get("SlotCap"))

    @property
    def link_cap(self):
        return PCIeLinkCap(self.__pcie_cap.get("LinkCap"))

    @property
    def link_status(self):
        return PCIeLinkStatus(self.__pcie_cap.get("LinkStatus"))

    @property
    def cap_reg(self):
        return PCIeCapRegister(self.__pcie_cap.get("PCIeCapRegister"))


class PCIeExtendCap(object):  # TODO
    def __init__(self, raw_data):
        self.__raw_data = raw_data
        self.__pcie_extend_cap = {}
        
    @property
    def raw_data(self):
        return self.__raw_data

    @property
    def decode_data(self):
        return self.__pcie_extend_cap


def get_pci_descriptation(pci_ids_path, vendor_id, start=0, end=None, device_id=None, subvd_id=None):
    if subvd_id:
        subvd_id = " ".join(subvd_id)
    ##
    vendor_desp = ''
    device_desp = ''
    subvd_desp = ''
    with open(pci_ids_path, 'r') as f:
        f.seek(start)
        while True:
            temp = f.readline()
            if not temp: # read reach the file end.
                break
            if temp.startswith("#"):  #  invalid loop and skip annotation
                continue
            ## first 
            if not vendor_desp:  # first search the vendor id
                if not temp.startswith("\t"):
                    temp = temp.strip()
                    index = temp.find("  ")
                    if index > 0 and temp[0:index] == vendor_id:
                        vendor_desp = temp[index+1:].strip()
            elif device_id and (not device_desp):  # then search the device id 
                if (temp.startswith("\t")) and (not temp.startswith("\t\t")):
                    temp = temp.strip("\t").strip()
                    index = temp.find("  ")
                    if index > 0 and temp[0:index] == device_id:
                        device_desp = temp[index+1:].strip()
            elif device_id and subvd_id and (not subvd_desp): # at last search the subvendor subdevice
                if temp.startswith("\t\t"):
                    temp = temp.strip("\t\t").strip()
                    index = temp.find("  ")
                    if index > 0 and temp[0:index] == subvd_id:
                        subvd_desp = temp[index+1:].strip()
            else:
                break  # could exit the search in the second valid loop after finish the search
            if end and f.tell() >= end:
                break  # search done in the condition
    result = [vendor_desp,]
    if device_id:
        result.append(device_desp)
        if subvd_id:
            result.append(subvd_desp)
    return result
