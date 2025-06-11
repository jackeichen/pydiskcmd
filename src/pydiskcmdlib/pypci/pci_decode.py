# # SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from enum import Enum
from pydiskcmdlib.utils.converter import (
    decode_bits,
    scsi_ba_to_int,
    decode_bits_iterative,
)
from pydiskcmdlib import log
# Layout of the Configuration Space and format of individual configuration registers are depicted following the
# little-endian convention.
#
# Code by PCIe Spec NCB-PCI_Express_Base_6.3
#

class PCIConfigHeader(object):
    ## Heander common bitmap locates in DWrod 0 ~ 5
    HeaderCommonBitmask = {"VendorID": [0xFFFF, 0],
                           "DeviceID": [0xFFFF, 2],
                           "Command": {
                               "IOSpaceEnable": [0x01, 4],
                               "MemorySpaceEnable": [0x02, 4],
                               "BusMasterEnable": [0x04, 4],
                               "SpecialCycleEnable": [0x08, 4],
                               "MemoryWriteAndInvalidate": [0x10, 4],
                               "VGAPaletteSnoop": [0x20, 4],
                               "ParityErrorResponse": [0x40, 4],
                               "IDSELSteppingWaitCycleControl": [0x80, 4],
                               "SERR#Enable": [0x01, 5],
                               "FastBack-to-BackTransactionsEnable": [0x02, 5],
                               "InterruptDisable": [0x04, 5],
                           },
                           "Status": {
                               "ImmediateReadiness": [0x01, 6],
                               "InterruptStatus": [0x08, 6],
                               "CapabilitiesList": [0x10, 6],
                               "66MHzCapable": [0x20, 6],   # only for PCI
                               "FastBack-to-BackTransactionsCapable": [0x80, 6],
                               "MasterDataParityError": [0x01, 7],
                               "DEVSELTiming": [0x06, 7],          # only for PCI
                               "SignaledTargetAbort": [0x08, 7],  
                               "ReceivedTargetAbort": [0x10, 7],  
                               "ReceivedMasterAbort": [0x20, 7],   
                               "SignaledSystemError": [0x40, 7], 
                               "DetectedParityError": [0x80, 7], 
                           },
                           "RevisionID": [0xFF, 8],
                           "ClassCode": [0xFFFFFF, 9],
                           "CacheLineSize": [0xFF, 12],
                           "LatTimer": [0xFF, 13],
                           "HeaderType": {
                               "HeaderLayout":[0x7F, 14],
                               "Multi-FunctionDevice":[0x80, 14],
                           },
                           "BIST": {
                               "CompletionCode": [0x0F, 15],
                               "StartBIST": [0x40, 15],
                               "BISTCapable": [0x80, 15],
                           },
                           "CapPointer": [0xFF, 52],
                           "InterruptLine": [0xFF, 60],
                           "InterruptPin": [0xFF, 61],
                           }
    ## Type 0 self bitmap, DWrod 6 ~ 15
    T0Bitmask = {"BaseAddr_0": [0xFFFFFFFF, 16],
                 "BaseAddr_1": [0xFFFFFFFF, 20],
                 "BaseAddr_2": [0xFFFFFFFF, 24],
                 "BaseAddr_3": [0xFFFFFFFF, 28],
                 "BaseAddr_4": [0xFFFFFFFF, 32],
                 "BaseAddr_5": [0xFFFFFFFF, 36],
                 "CardBusCISPointer": [0xFFFFFFFF, 40],
                 "SubsystemVendorID": [0xFFFF, 44],
                 "SubsystemDeviceID": [0xFFFF, 46],
                 "ExpROMBaseAddr": {
                     "ExpansionROMEnable": [0x01, 48],
                     "ExpansionROMValidationStatus": [0x0E, 48],
                     "ExpansionROMValidationDetails": [0xF0, 48],
                     "ExpansionROMBaseAddress": [0xFFFFF8, 49],
                 },
                 "MinGnt": [0xFF, 62],
                 "MaxLat": [0xFF, 63],
                 }
    ## Type 1 self bitmap, DWrod 6 ~ 15
    T1Bitmask = {"BaseAddr_0": [0xFFFFFFFF, 16],
                 "BaseAddr_1": [0xFFFFFFFF, 20],
                 "PriBusNum": [0xFF, 24],
                 "SecBusNum": [0xFF, 25],
                 "SubBusNum": [0xFF, 26],
                 "SecLatTimer": [0xFF, 27],
                 "IOBase": [0xFF, 28],
                 "IOLimit": [0xFF, 29],
                 "SecStatus": {
                               "66MHzCapable": [0x20, 30],   # only for PCI
                               "FastBack-to-BackTransactionsCapable": [0x80, 30],
                               "MasterDataParityError": [0x01, 31],
                               "DEVSELTiming": [0x06, 31],          # only for PCI
                               "SignaledTargetAbort": [0x08, 31],  
                               "ReceivedTargetAbort": [0x10, 31],  
                               "ReceivedMasterAbort": [0x20, 31],   
                               "SignaledSystemError": [0x40, 31], 
                               "DetectedParityError": [0x80, 31], 
                 },
                 "MemoryBase": [0xFFFF, 32],
                 "MemoryLimit": [0xFFFF, 34],
                 "PrefetchableMemBase": [0xFFFF, 36],
                 "PrefetchableMemLimit": [0xFFFF, 38],
                 "PrefetchableBaseU": [0xFFFFFFFF, 40],
                 "PrefetchableLimitU": [0xFFFFFFFF, 44],
                 "IOBaseU": [0xFFFF, 48],
                 "IOLimitU": [0xFFFF, 50],
                 "ExpROMBaseAddr": [0xFFFFFFFF, 56],
                 "BridgeControl": {
                     "ParityErrorResponseEnable": [0x01, 62],
                     "SERR#Enable": [0x02, 62],
                     "ISAEnable": [0x04, 62],
                     "VGAEnable": [0x08, 62],
                     "VGA16-bitDecode": [0x10, 62],
                     "MasterAbortMode": [0x20, 62],
                     "SecondaryBusReset": [0x40, 62],
                     "Fast Back-to-BackTransactionsEnable": [0x80, 62],
                     "PrimaryDiscardTimer": [0x01, 63],
                     "SecondaryDiscardTimer": [0x02, 63],
                     "DiscardTimerStatus": [0x04, 63],
                     "DiscardTimerSERR#Enable": [0x08, 63],
                 },
                 }
    name = "PCIConfigHeader"
    length = 64
    def __init__(self, raw_data):
        self.__raw_data = raw_data
        self.__pci_config_header = {}
        decode_bits_iterative(raw_data, PCIConfigHeader.HeaderCommonBitmask, self.__pci_config_header, byteorder='little')
        if self.header_type["HeaderLayout"] == 0:
            decode_bits_iterative(raw_data, PCIConfigHeader.T0Bitmask, self.__pci_config_header, byteorder='little')
        elif self.header_type["HeaderLayout"] == 1:
            decode_bits_iterative(raw_data, PCIConfigHeader.T1Bitmask, self.__pci_config_header, byteorder='little')
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
        return self.__pci_config_header["HeaderType"]

################ Capabilities Data Property ########################
# Capability lists 
class PCI_CAP_ID(Enum):
    PCI_CAP_ID_Null = 0x00              # No Capability
    PCI_CAP_ID_PM = 0x01     # Power Management
    PCI_CAP_ID_AGP = 0x02    # Accelerated Graphics Port
    PCI_CAP_ID_VPD = 0x03    # Vital Product Data
    PCI_CAP_ID_SLOTID = 0x04 # Slot Identification
    PCI_CAP_ID_MSI = 0x05    # Message Signalled Interrupts
    PCI_CAP_ID_CHSWP = 0x06  # CompactPCI HotSwap
    PCI_CAP_ID_PCIX = 0x07   # PCI-X
    PCI_CAP_ID_HT = 0x08     # HyperTransport
    PCI_CAP_ID_VNDR = 0x09   # Vendor-Specific
    PCI_CAP_ID_DBG = 0x0A    # Debug port
    PCI_CAP_ID_CCRC = 0x0B   # CompactPCI Central Resource Control
    PCI_CAP_ID_SHPC = 0x0C   # PCI Standard Hot-Plug Controller
    PCI_CAP_ID_SSVID = 0x0D  # Bridge subsystem vendor/device ID
    PCI_CAP_ID_AGP3 = 0x0E   # AGP Target PCI-PCI bridge
    PCI_CAP_ID_SECDEV = 0x0F # Secure Device
    PCI_CAP_ID_EXP = 0x10    # PCI Express
    PCI_CAP_ID_MSIX = 0x11   # MSI-X
    PCI_CAP_ID_SATA = 0x12   # SATA Data/Index Conf.
    PCI_CAP_ID_AF = 0x13     # PCI Advanced Features
    PCI_CAP_ID_EA = 0x14     # PCI Enhanced Allocation
    PCI_CAP_ID_FPB = 0x15    # PCI Flattening Portal Bridge

# Extended Capabilities (PCI-X 2.0 and Express)
class PCI_EXT_CAP_ID(Enum):
    PCI_EXT_CAP_ID_Null = 0x00                   # No Capability
    PCI_EXT_CAP_ID_ERR = 0x01     # Advanced Error Reporting
    PCI_EXT_CAP_ID_VC = 0x02      # Virtual Channel Capability
    PCI_EXT_CAP_ID_DSN = 0x03     # Device Serial Number
    PCI_EXT_CAP_ID_PWR = 0x04     # Power Budgeting
    PCI_EXT_CAP_ID_RCLD = 0x05    # Root Complex Link Declaration
    PCI_EXT_CAP_ID_RCILC = 0x06   # Root Complex Internal Link Control
    PCI_EXT_CAP_ID_RCEC = 0x07    # Root Complex Event Collector
    PCI_EXT_CAP_ID_MFVC = 0x08    # Multi-Function VC Capability
    PCI_EXT_CAP_ID_VC9 = 0x09     # same as _VC
    PCI_EXT_CAP_ID_RCRB = 0x0A    # Root Complex RB?
    PCI_EXT_CAP_ID_VNDR = 0x0B    # Vendor-Specific
    PCI_EXT_CAP_ID_CAC = 0x0C     # Config Access - obsolete
    PCI_EXT_CAP_ID_ACS = 0x0D     # Access Control Services
    PCI_EXT_CAP_ID_ARI = 0x0E     # Alternate Routing ID
    PCI_EXT_CAP_ID_ATS = 0x0F     # Address Translation Services
    PCI_EXT_CAP_ID_SRIOV = 0x10   # Single Root I/O Virtualization
    PCI_EXT_CAP_ID_MRIOV = 0x11   # Multi Root I/O Virtualization
    PCI_EXT_CAP_ID_MCAST = 0x12   # Multicast
    PCI_EXT_CAP_ID_PRI = 0x13     # Page Request Interface
    PCI_EXT_CAP_ID_AMD_XXX = 0x14 # Reserved for AMD
    PCI_EXT_CAP_ID_REBAR = 0x15   # Resizable BAR
    PCI_EXT_CAP_ID_DPA = 0x16     # Dynamic Power Allocation
    PCI_EXT_CAP_ID_TPH = 0x17     # TPH Requester
    PCI_EXT_CAP_ID_LTR = 0x18     # Latency Tolerance Reporting
    PCI_EXT_CAP_ID_SECPCI = 0x19  # Secondary PCIe Capability
    PCI_EXT_CAP_ID_PMUX = 0x1A    # Protocol Multiplexing
    PCI_EXT_CAP_ID_PASID = 0x1B   # Process Address Space ID
    PCI_EXT_CAP_ID_DPC = 0x1D     # Downstream Port Containment
    PCI_EXT_CAP_ID_L1SS = 0x1E    # L1 PM Substates
    PCI_EXT_CAP_ID_PTM = 0x1F     # Precision Time Measurement
    PCI_EXT_CAP_ID_DVSEC = 0x23   # Designated Vendor-Specific
    PCI_EXT_CAP_ID_DLF = 0x25     # Data Link Feature
    PCI_EXT_CAP_ID_PL_16GT = 0x26 # Physical Layer 16.0 GT/s
    PCI_EXT_CAP_ID_NPEM = 0x29    # Native PCIe Enclosure Management
    PCI_EXT_CAP_ID_PL_32GT = 0x2A # Physical Layer 32.0 GT/s
    PCI_EXT_CAP_ID_DOE = 0x2E     # Data Object Exchange
    PCI_EXT_CAP_ID_PL_64GT = 0x31 # Physical Layer 64.0 GT/s


class CapDataBase(object):
    BitMap = {}
    length = 0
    name = "Unsupported"
    cap_id = 0x00
    def __init__(self, raw_data, offset=None):
        self.__raw_data = raw_data
        self.__offset = offset
        #
        self.__cap_data_decode = {}
        decode_bits_iterative(raw_data, self.BitMap, self.__cap_data_decode, byteorder='little')

    @property
    def raw_data(self):
        return self.__raw_data

    @property
    def locate_offset(self):
        return self.__offset

    @raw_data.setter
    def raw_data(self, raw_data: bytes):
        self.__raw_data = raw_data

    @property
    def decode_data(self):
        return self.__cap_data_decode

    @property
    def data_len(self):
        return len(self.__raw_data)
################ PCI and PCIe Capabilities Start#########################
class PCICapID(CapDataBase):
    BitMap = {"CapabilityID": [0xFF, 0],
              "NextCapabilityPointer": [0xFF, 1],
              }
    length = 4
    def __init__(self, raw_data, offset):
        super(PCICapID, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class NullCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFF, 0],
              "NextCapabilityPointer": [0xFF, 1],
              }
    length = 2
    cap_id = PCI_CAP_ID.PCI_CAP_ID_Null.value
    name = "Null Capability"
    def __init__(self, raw_data, offset):
        super(NullCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class PCIeCapRegister(CapDataBase):
    BitMap = {"CapabilityVersion": ('bb', 0, 4),
              "DevOrPortType": ('bb', 4, 4),
              "SlotImplemented": ('bb', 8, 1),
              "InterruptMessageNumber": ('bb', 9, 5),
              # "Undefined": ('bb', 14, 1)  # Leave it, different in different version spec.
              }
    def __init__(self, raw_data):
        super(PCIeCapRegister, self).__init__(raw_data)

class PCIeLinkCap(CapDataBase):
    BitMap = {"MaxLinkSpeed": ('bb', 0, 4),
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
        super(PCIeLinkCap, self).__init__(raw_data)

class PCIeLinkStatus(CapDataBase):
    BitMap = {"LinkSpeed": ('bb', 0, 4),
              "LinkWidth": ('bb', 4, 6),
              "LinkTraining": ('bb', 10, 1),
              "SlotClockConfig": ('bb', 11, 1),
              "DataLinkLayerLinkActive": ('bb', 12, 1),
              "LinkBWManagementStatus": ('bb', 13, 1),
              "LinkAutonomousBWStatus": ('bb', 14, 1),
              }
    def __init__(self, raw_data):
        super(PCIeLinkStatus, self).__init__(raw_data)


class PCIeSlotCap(CapDataBase):
    BitMap = {"AttentionButtonPresent": ('bb', 0, 1),
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
        super(PCIeSlotCap, self).__init__(raw_data)


class PCIeCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFF, 0],
              "NextCapabilityPointer": [0xFF, 1],
              "PCIeCapRegister": {
                  "CapabilityVersion": [0x0F, 2],
                  "DPType": [0xF0, 2],
                  "SlotImp": [0x01, 3],
                  "INTMsgNum": [0x3E, 3],
                  "Undefined": [0x40, 3],
                  "RsvdP": [0x80, 3],
              },
              "PCIeCapRegister_raw": ('b', 2, 2),
              "DevCap": {
                  "MaxPayload": [0x07, 4],
                  "PhantFunc": [0x18, 4],
                  "ExtTag": [0x20, 4],
                  "EPL0sLat": [0x1C0, 4],
                  "EPL1Lat": [0x0E, 5],
                  "RBE": [0x80, 5],
                  "ERR_COR Subclass": [0x01, 6],
                  "SlotPowerLimitValue": [0x3FC, 6],
                  "SlotPowerLimitScale": [0x0C, 7],
                  "FLReset": [0x10, 7],
              },
              "DevCtl": {
                  "CorrErr": [0x01, 8],
                  "NonFatalErr": [0x02, 8],
                  "FatalErr": [0x04, 8],
                  "UnsupReq": [0x08, 8],
                  "RlxdOrd": [0x10, 8],
                  "MaxPayload": [0xE0, 8],
                  "ExtTag": [0x01, 9],
                  "PhantFunc": [0x02, 9],
                  "AuxPwr": [0x04, 9],
                  "NoSnoop": [0x08, 9],
                  "MaxReadReq": [0x70, 9],
                  "FLReset": [0x80, 9],
              },
              "DevSta": {
                  "CorrErr": [0x01, 10],
                  "NonFatalErr": [0x02, 10],
                  "FatalErr": [0x04, 10],
                  "UnsupReq": [0x08, 10],
                  "AuxPwr": [0x10, 10],
                  "TransPend": [0x20, 10],
                  "EmerPwr": [0x40, 10],
              },
              "LnkCap": {
                  "MaxLinkSpeed": [0x0F, 12],
                  "MaxLinkWidth": [0x3F0, 12],
                  "ASPM": [0x0C, 13],
                  "L0sExtLat": [0x70, 13],
                  "L1ExtLat": [0x380, 13],
                  "ClockPM": [0x04, 14],
                  "SPDownErrRptg": [0x08, 14],
                  "DLLLnkActRptg": [0x10, 14],
                  "LnkBWNotif": [0x20, 14],
                  "ASPMOptCo": [0x40, 14],
                  "PortNum": [0xFF, 15],
              },
              "LnkCap_raw": ('b', 12, 4),
              "LnkCtl": {
                  "ASPMCtrl": [0x03, 16],
                  "RdCtBdy": [0x08, 16],
                  "LnkDisable": [0x10, 16],
                  "RetrainLnk": [0x20, 16],
                  "ComClkConf": [0x40, 16],
                  "ExtdSynch": [0x80, 16],
                  "ClockPM": [0x01, 17],
                  "AutWidDis": [0x02, 17],
                  "BWInt": [0x04, 17],
                  "AutBWInt": [0x08, 17],
                  "DRSSig": [0xC0, 17],
              },
              "LnkSta": {
                  "Speed": [0x0F, 18],
                  "Width": [0x3F0, 18],
                  "Train": [0x08, 19],
                  "SlotClk": [0x10, 19],
                  "DLActive": [0x20, 19],
                  "BWMgmt": [0x40, 19],
                  "ABWMgmt": [0x80, 19],
              },
              "LnkSta_raw": ('b', 18, 2),
              "SltCap": {
                  "AttnBtn": [0x01, 20],
                  "PwrCtrl": [0x02, 20],
                  "MRL": [0x04, 20],
                  "AttnInd": [0x08, 20],
                  "PwrInd": [0x10, 20],
                  "Surprise": [0x20, 20],
                  "HotPlug": [0x40, 20],
                  "PowerLimitValue": [0x7F80, 20],
                  "PowerLimitScale": [0x180, 21],
                  "Interlock": [0x02, 22],
                  "NoCompl": [0x04, 22],
                  "PhysicalSlotNum": [0xFFF8, 22],
              },
              "SltCap_raw": ('b', 20, 4),
              "SltCtl": {
                  "AttnBtn": [0x01, 24],
                  "PwrFlt": [0x02, 24],
                  "MRL": [0x04, 24],
                  "PresDet": [0x08, 24],
                  "CmdCplt": [0x10, 24],
                  "HPIrq": [0x20, 24],
                  "AttnIndCtrl": [0xC0, 24],
                  "PwrIndCtrl": [0x03, 25],
                  "PwrControllerCtrl": [0x04, 25],
                  "Interlock": [0x08, 25],
                  "DLLStaChanged": [0x10, 25],
                  "AutoSltPwrLimitDis": [0x20, 25],
                  "IBPDDis": [0x40, 25],
              },
              "SltSta": {
                  "AttnBtn": [0x01, 26],
                  "PwrFlt": [0x02, 26],
                  "MRLChg": [0x04, 26],
                  "PresDetChg": [0x08, 26],
                  "CmdCplt": [0x10, 26],
                  "MRLSta": [0x20, 26],
                  "PresDetSta": [0x40, 26],
                  "Interlock": [0x80, 26],
                  "DLLStaChanged": [0x01, 27],
              },
              "RootCtl": {
                  "ErrCorrectable": [0x01, 28],
                  "ErrNon-Fatal": [0x02, 28],
                  "ErrFatal": [0x04, 28],
                  "PMEIntEna": [0x08, 28],
                  "CRSVisible": [0x10, 28],
              },
              "RootCap": {
                  "CRSVisible": [0x01, 30],
              },
              "RootSta": {
                  "PMEReqID": [0xFFFF, 32],
                  "PMESta": [0x01, 32],
                  "PMEPending": [0x02, 32],
              },
              "DevCap2": {
                  "CompletionTimeoutRange": [0x0F, 36],
                  "CompletionTimeoutDis": [0x10, 36],
                  "ARIForwarding": [0x20, 36],
                  "AtomOpRouting": [0x40, 36],
                  "32b_AtomOpCplt": [0x80, 36],
                  "64b_AtomOpCplt": [0x01, 37],
                  "128b_CASCplt": [0x02, 37],
                  "NROPrPrP": [0x04, 37],
                  "LTR": [0x08, 37],
                  "TPH": [0x30, 37],
                  "LNSystemCLS": [0xC0, 37],
                  "10BitTagComp": [0x01, 38],
                  "10BitTagReq": [0x02, 38],
                  "OBFF": [0x0C, 38],
                  "ExtFmt": [0x10, 38],
                  "EETLPPrefix": [0x20, 38],
                  "MaxEETLPPrefixes": [0xC0, 38],
                  "EmergencyPowerReduction": [0x03, 39],
                  "EmergencyPowerReductionInit": [0x04, 39],
                  "FRS": [0x80, 39],
              },
              "DevCtl2": {
                  "CompletionTimeoutValue": [0x0F, 40],
                  "TimeoutDis": [0x10, 40],
                  "ARIForwarding": [0x20, 40],
                  "AtomOpRequester": [0x40, 40],
                  "AtomOpEgressBlk": [0x80, 40],
                  "IDORequest": [0x01, 41],
                  "IDOCompletion": [0x02, 41],
                  "LTR": [0x04, 41],
                  "EmergencyPwrRR": [0x08, 41],
                  "10B_TagRequester": [0x10, 41],
                  "OBFF": [0x60, 41],
                  "EETLPPrefixBlk": [0x80, 41],
              },
              "DevSta2": [0xFFFF, 42],
              "LnkCap2": {
                  "Supported Link Speeds": [0xFE, 44],
                  "Crosslink": [0x01, 45],
                  "LowerSKPOSGenSSVec": [0xFE, 45],
                  "LowerSKPOSRecSSVec": [0xEF, 46],
                  "Retimer": [0x80, 46],
                  "2Retimers": [0x01, 47],
                  "DRS": [0x80, 47],
              },
              "LnkCtl2": {
                  "Target Link Speed": [0x0F, 48],
                  "EnterCompliance": [0x10, 48],
                  "SpeedDis": [0x20, 48],
                  "Selectable De-emphasis": [0x40, 48],
                  "Transmit Margin": [0x380, 48],
                  "EnterModifiedCompliance": [0x04, 49],
                  "ComplianceSOS": [0x08, 49],
                  "Compliance Preset/De-emphasis": [0xF0, 49],
              },
              "LnkSta2": {
                  "Current De-emphasis Level": [0x01, 50],
                  "EqualizationComplete": [0x02, 50],
                  "EqualizationPhase1": [0x04, 50],
                  "EqualizationPhase2": [0x08, 50],
                  "EqualizationPhase3": [0x10, 50],
                  "LinkEqualizationRequest": [0x20, 50],
                  "Retimer": [0x40, 50],
                  "2Retimers": [0x80, 50],
                  "CrosslinkRes": [0x03, 51],
                  "DownstreamComponentPresence": [0x70, 51],
                  "DRSMsgReceived": [0x80, 51],
              },
              "SlotCap2": {
                  "IBPDDis": [0x01, 52],
              },
              "SlotControl2": [0xFFFF, 56],
              "SlotStatus2": [0xFFFF, 58],
              }
    name = "PCIExpressCap"
    cap_id = PCI_CAP_ID.PCI_CAP_ID_EXP.value
    length = 60
    def __init__(self, raw_data, offset):
        super(PCIeCap, self).__init__(raw_data, offset=offset)

    @property
    def slot_cap(self):
        return PCIeSlotCap(self.decode_data.get("SltCap_raw"))

    @property
    def link_cap(self):
        return PCIeLinkCap(self.decode_data.get("LnkCap_raw"))

    @property
    def link_status(self):
        return PCIeLinkStatus(self.decode_data.get("LnkSta_raw"))

    @property
    def cap_reg(self):
        return PCIeCapRegister(self.decode_data.get("PCIeCapRegister_raw"))


class PowerManagementCap(CapDataBase):
    length = 8
    cap_id = PCI_CAP_ID.PCI_CAP_ID_PM.value
    BitMap = {"CapabilityID": [0xFF, 0],
              "NextCapabilityPointer": [0xFF, 1],
              # Power Management Capabilities
              "PMC": {"Version": [0x07, 2],
                      "PMEClock": [0x08, 2],
                      "Immediate_Readiness_on_Return_to_D0": [0x10, 2],
                      "DeviceSpecificInitialization": [0x20, 2],
                      "Aux_Current": [0x01C0, 2],
                      "D1_Support": [0x02, 3],
                      "D2_Support": [0x04, 3],
                      "PME_Support": [0xF8, 3],
                      },
              # Power Management Control/Status (PMCSR)
              "PMCSR": {"PowerState": [0x03, 4],
                        "No_Soft_Reset": [0x08, 4],
                        "PME_En": [0x01, 5],
                        "Data_Select": [0x1E, 5],
                        "Data_Scale": [0x60, 5],
                        "PME_Status": [0x80, 5],
                        "Undefined": [0xC0, 6],
                        },
              "Data": ("b", 7, 1),
              }
    name = "PowerManagementCap"
    def __init__(self, raw_data, offset):
        super(PowerManagementCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class MSICap(CapDataBase):
    length = 24  # Give a max length
    cap_id = PCI_CAP_ID.PCI_CAP_ID_MSI.value
    name = "MSICapability"
    BitMap = {"CapabilityID": [0xFF, 0],
              "NextCapabilityPointer": [0xFF, 1],
              "MessageControl": {"MSIEnable": [0x01, 2],
                                 "MultipleMessageCapable": [0x0E, 2],
                                 "MultipleMessageEnable": [0x70, 2],
                                 "64-bitAddressCapable": [0x80, 2],
                                 "Per-VectorMaskingCapable": [0x01, 3],
                                 "ExtendedMessageDataCapable": [0x02, 3],
                                 "ExtendedMessageDataEnable": [0x04, 3],
                                 },
              #"raw_MessageControl": ("b", 2, 2),
              "MessageAddress": ("b", 4, 4),
              }  # Common bitmap for all MSI Capability
    def __init__(self, raw_data, offset):
        super(MSICap, self).__init__(raw_data, offset=offset)
        ##
        message_address_64b = self.decode_data["MessageControl"]["64-bitAddressCapable"]
        pvm_enable = self.decode_data["MessageControl"]["Per-VectorMaskingCapable"]
        ##
        bit_map = MSICap.BitMap.copy()
        if message_address_64b:
            bit_map.update({"MessageUpperAddress": ("b", 8, 4),
                            "MessageData": ("b", 12, 2),
                            "ExtendMessageData": ("b", 14, 2),
                            })
            length = 16
        else:
            bit_map.update({"MessageData": ("b", 8, 2),
                            "ExtendMessageData": ("b", 10, 2),
                            })
            length = 12
        if pvm_enable:
            bit_map.update({"MaskBits": ("b", length, 4),
                            "PendingBits": ("b", length+4, 4),
                           })
            length += 8
        self.raw_data = raw_data[:length]  # Update raw data
        decode_bits_iterative(self.raw_data, bit_map, self.decode_data, byteorder='little')  # Second decode

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class MSIXCap(CapDataBase):
    length = 12 
    cap_id = PCI_CAP_ID.PCI_CAP_ID_MSIX.value
    name = "MSI-X Capability and Table Structure"
    BitMap = {"CapabilityID": [0xFF, 0],
              "NextCapabilityPointer": [0xFF, 1],
              "MsgCtrl": {"TableSize": [0x7FF, 2],
                          "FuncMask": [0x40, 3],
                          "MSIX_En": [0x80, 3],
                          },
              "TableBIR": [0x07, 4],
              "TableOffset": [0xFFFFFFF8, 4],
              "PBABIR": [0x07, 8],
              "PBAOffset": [0xFFFFFFF8, 8],
              }
    def __init__(self, raw_data, offset):
        super(MSIXCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class SubIDCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFF, 0],
              "NextCapabilityPointer": [0xFF, 1],
              "SSVID": [0xFFFF, 4],
              "SSID": [0xFFFF, 6],
              }
    length = 8
    cap_id = PCI_CAP_ID.PCI_CAP_ID_SSVID.value
    name = "Subsystem ID and Sybsystem Vendor ID Capability"
    def __init__(self, raw_data, offset):
        super(SubIDCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class FPBCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFF, 0],
              "NextCapabilityPointer": [0xFF, 1],
              "Cap": [0xFFFFFFFF, 4],
              "RIDCtl1": [0xFFFFFFFF, 8],
              "RIDCtl2": [0xFFFFFFFF, 12],
              "MemLowCtl": [0xFFFFFFFF, 16],
              "MemHighCtl1": [0xFFFFFFFF, 20],
              "MemHighCtl2": [0xFFFFFFFF, 24],
              "VecAccessCtl": [0xFFFFFFFF, 28],
              "VecAccessData": [0xFFFFFFFF, 32],
              }
    length = 36
    cap_id = PCI_CAP_ID.PCI_CAP_ID_FPB.value
    name = "FPB Capability"
    def __init__(self, raw_data, offset):
        super(FPBCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class EnhancedAllocCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFF, 0],
              "NextCapabilityPointer": [0xFF, 1],
              "NumEntries": [0x3F, 2],
              }
    length = 4
    cap_id = PCI_CAP_ID.PCI_CAP_ID_EA.value
    name = "Enhanced Allocation Capability"
    def __init__(self, raw_data, offset):
        super(EnhancedAllocCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class VenorSpecCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFF, 0],
              "NextCapabilityPointer": [0xFF, 1],
              "Len": [0xFF, 2],
              "VSReg": ('b', 3, 13),
    }
    length = 16
    name = 'Vendor-Specific Capability'
    cap_id = PCI_CAP_ID.PCI_CAP_ID_VNDR.value
    def __init__(self, raw_data, offset):
        super(VenorSpecCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class VPDCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFF, 0],
              "NextCapabilityPointer": [0xFF, 1],
              "VPDAddress": [0xFFFF, 2],
              "VPDData": [0xFFFFFFFF, 4],
              }
    length = 8
    cap_id = PCI_CAP_ID.PCI_CAP_ID_VPD.value
    name = "Vital Product Data Capability"
    def __init__(self, raw_data, offset):
        super(VPDCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class PCICap(object):
    PCICapTable = {PowerManagementCap.cap_id: PowerManagementCap,
                   PCIeCap.cap_id: PCIeCap,
                   MSICap.cap_id: MSICap,
                   SubIDCap.cap_id: SubIDCap,
                   MSIXCap.cap_id: MSIXCap,
                   EnhancedAllocCap.cap_id: EnhancedAllocCap,
                   FPBCap.cap_id: FPBCap,
                   VenorSpecCap.cap_id: VenorSpecCap,
                   NullCap.cap_id: NullCap,
                   VPDCap.cap_id: VPDCap,
                   }
    locate_offset = 64
    def __init__(self, raw_data, pci_config_header: PCIConfigHeader):
        self.__raw_data = raw_data
        self.__pci_config_header = pci_config_header
        self.__pci_cap_decode = {}
        self.read_config()

    @property
    def raw_data(self):
        return self.__raw_data

    @property
    def pci_cap_decode(self):
        return self.__pci_cap_decode

    @property
    def decode_data(self):
        return self.__pci_cap_decode

    @staticmethod
    def _get_self_locate(offset):
        return offset - PCICap.locate_offset

    def read_config(self):
        """
        Read the pci cap data
        """
        offset = self.__pci_config_header.decode_data.get("CapPointer")
        for i in range(48):
            # check offset
            if 0x3F < offset < 0xFF:
                #
                _self_locate = self._get_self_locate(offset)
                pci_cap_id = PCICapID(self.__raw_data[_self_locate:_self_locate+PCICapID.length], offset)
                if pci_cap_id.CapabilityID in PCICap.PCICapTable:
                    func = PCICap.PCICapTable.get(pci_cap_id.CapabilityID)
                    self.__pci_cap_decode[pci_cap_id.CapabilityID] = func(self.__raw_data[_self_locate:_self_locate+func.length], offset)
                else:
                    self.__pci_cap_decode[pci_cap_id.CapabilityID] = pci_cap_id  # Unknown Capability
                ## no other items
                if pci_cap_id.NextCapabilityPointer == 0:
                    break
                ## Get next cap
                offset = pci_cap_id.NextCapabilityPointer
            else:
                raise ValueError("Incorrect PCI Capabilities Data offset(%#x)." % offset)
        else:
            raise ValueError("Incorrect PCI Capabilities Data.")

################ PCI and PCIe Capabilities End #########################
################ PCIe Extend Capabilities Start#########################

class PCIeExtendCapID(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              }
    length = 4
    def __init__(self, raw_data, offset):
        super(PCIeExtendCapID, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class NullExtendCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              }
    length = 4
    name = 'Null Extended Capability'
    cap_id = PCI_EXT_CAP_ID.PCI_EXT_CAP_ID_Null.value
    def __init__(self, raw_data, offset):
        super(NullExtendCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class AERCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              "UESta":{
                  "DLP": [0x10, 4],
                  "SDES": [0x20, 4],
                  "TLP": [0x10, 5],
                  "FCP": [0x20, 5],
                  "CmpltTO": [0x40, 5],
                  "CmpltAbrt": [0x80, 5],
                  "UnxCmplt": [0x01, 6],
                  "RxOF": [0x02, 6],
                  "MalfTLP": [0x04, 6],
                  "ECRC": [0x08, 6],
                  "UnsupReq": [0x10, 6],
                  "ACSViol": [0x20, 6],
                  "UncIntErr": [0x40, 6],
                  "MCBlkTLP": [0x80, 6],
                  "AtomOpEgBlk": [0x01, 7],
                  "TLPPrefixBlkErr": [0x02, 7],
                  "PosTLPEgBlk": [0x04, 7],
              },
              "UEMsk":{
                  "DLP": [0x10, 8],
                  "SDES": [0x20, 8],
                  "TLP": [0x10, 9],
                  "FCP": [0x20, 9],
                  "CmpltTO": [0x40, 9],
                  "CmpltAbrt": [0x80, 9],
                  "UnxCmplt": [0x01, 10],
                  "RxOF": [0x02, 10],
                  "MalfTLP": [0x04, 10],
                  "ECRC": [0x08, 10],
                  "UnsupReq": [0x10, 10],
                  "ACSViol": [0x20, 10],
                  "UncIntErr": [0x40, 10],
                  "MCBlkTLP": [0x80, 10],
                  "AtomOpEgBlk": [0x01, 11],
                  "TLPPrefixBlkErr": [0x02, 11],
                  "PosTLPEgBlk": [0x04, 11],
              },
              "UESvrt": {
                  "DLP": [0x10, 12],
                  "SDES": [0x20, 12],
                  "TLP": [0x10, 13],
                  "FCP": [0x20, 13],
                  "CmpltTO": [0x40, 13],
                  "CmpltAbrt": [0x80, 13],
                  "UnxCmplt": [0x01, 14],
                  "RxOF": [0x02, 14],
                  "MalfTLP": [0x04, 14],
                  "ECRC": [0x08, 14],
                  "UnsupReq": [0x10, 14],
                  "ACSViol": [0x20, 14],
                  "UncIntErr": [0x40, 14],
                  "MCBlkTLP": [0x80, 14],
                  "AtomOpEgBlk": [0x01, 15],
                  "TLPPrefixBlkErr": [0x02, 15],
                  "PosTLPEgBlk": [0x04, 15],
              },
              "CESta": {
                  "RxErr": [0x01, 16],
                  "BadTLP": [0x40, 16],
                  "BadDLLP": [0x80, 16],
                  "Rollover": [0x01, 17],
                  "Timeout": [0x10, 17],
                  "AdvNonFatalErr": [0x20, 17],
                  "CIE": [0x40, 17],
                  "HeaderLog": [0x80, 17],
              },
              "CEMsk": {
                  "RxErr": [0x01, 20],
                  "BadTLP": [0x40, 20],
                  "BadDLLP": [0x80, 20],
                  "Rollover": [0x01, 21],
                  "Timeout": [0x10, 21],
                  "AdvNonFatalErr": [0x20, 21],
                  "CIE": [0x40, 21],
                  "HeaderLog": [0x80, 21],
              },
              "AERCap": {
                  "First Error Pointer": [0x1F, 24],
                  "ECRCGenCap": [0x20, 24],
                  "ECRCGenEn": [0x40, 24],
                  "ECRCChkCap": [0x80, 24],
                  "ECRCChkEn": [0x01, 25],
                  "MultHdrRecCap": [0x02, 25],
                  "MultHdrRecEn": [0x04, 25],
                  "TLPPfxPres": [0x08, 25],
                  "HdrLogCap": [0x10, 25],
              },
              "HeaderLog": {
                  "1st": [0xFFFFFFFF, 28],
                  "2nd": [0xFFFFFFFF, 32],
                  "3rd": [0xFFFFFFFF, 36],
                  "4th": [0xFFFFFFFF, 40],
              },
              "RootCmd": {
                  "CERptEn": [0x01, 44],
                  "NFERptEn": [0x02, 44],
                  "FERptEn": [0x04, 44],
              },
              "RootSta": {
                  "CERcvd": [0x01, 48],
                  "MultCERcvd": [0x02, 48],
                  "UERcvd": [0x04, 48],
                  "MultUERcvd": [0x08, 48],
                  "FirstFatal": [0x10, 48],
                  "NonFatalMsg": [0x20, 48],
                  "FatalMsg": [0x40, 48],
                  "ERR_COR Subclass": [0x0180, 48],
                  "IntMsg": [0xF8, 51],
              },
              "ErrorSrc": {
                  "ERR_COR": [0xFFFF, 52],
                  "ERR_FATAL/NONFATAL": [0xFFFF, 54],
              },
              "TLPPrefixLogReg": {
                  "1st": [0xFFFFFFFF, 56],
                  "2nd": [0xFFFFFFFF, 60],
                  "3rd": [0xFFFFFFFF, 64],
                  "4th": [0xFFFFFFFF, 68],
              },
    }
    length = 72
    name = 'AER Capability'
    cap_id = PCI_EXT_CAP_ID.PCI_EXT_CAP_ID_ERR.value
    def __init__(self, raw_data, offset):
        super(AERCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")

class SRIOVCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              "SRIOVCap": {
                  "VFMigCap": [0x01, 4],
                  "ARI": [0x02, 4],
                  "VF_10B_Tag": [0x04, 4],
                  "VFMigIntMsgNum": [0xFFE0, 6],
              },
              "SRIOVCtrl": {
                  "VFEn": [0x01, 8],
                  "VFMigEn": [0x02, 8],
                  "VFMigIntEn": [0x04, 8],
                  "VF MSE": [0x08, 8],
                  "ARICap": [0x10, 8],
                  "VF_10B_Tag": [0x20, 8],
              },
              "SRIOVSta": {
                  "VFMigSta": [0x01, 10],
              },
              "InitialVFs": [0xFFFF, 12],
              "TotalVFs": [0xFFFF, 14],
              "NumVFs": [0xFFFF, 16],
              "FunDepLink": [0xFF, 18],
              "FirstVFOffset": [0xFFFF, 20],
              "VFStride": [0xFFFF, 22],
              "VFDeviceID": [0xFFFF, 26],
              "SupportedPageSizes": [0xFFFFFFFF, 28],
              "SystemPageSize": [0xFFFFFFFF, 32],
              "VFBAR0": [0xFFFFFFFF, 36],
              "VFBAR1": [0xFFFFFFFF, 40],
              "VFBAR2": [0xFFFFFFFF, 44],
              "VFBAR3": [0xFFFFFFFF, 48],
              "VFBAR4": [0xFFFFFFFF, 52],
              "VFBAR5": [0xFFFFFFFF, 56],
              "VFMigStaArrayOffset":{
                  "VFMigStaBIR": [0x07, 60],
                  "VFMigStaOffset": [0xFFFFFFF8, 60],
              },
              }
    length = 64
    name = 'SR-IOV Extended Capability'
    cap_id = PCI_EXT_CAP_ID.PCI_EXT_CAP_ID_SRIOV.value
    def __init__(self, raw_data, offset):
        super(SRIOVCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class NPEMCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              "NPEMCap": {
                  "En": [0x01, 4],
                  "Reset": [0x02, 4],
                  "OK": [0x04, 4],
                  "Locate": [0x08, 4],
                  "Locate": [0x10, 4],
                  "Rebuild": [0x20, 4],
                  "PFA": [0x40, 4],
                  "HotSpare": [0x80, 4],
                  "CriticalArray": [0x01, 5],
                  "FailedArray": [0x02, 5],
                  "InvalidDevice": [0x04, 5],
                  "Dis": [0x08, 5],
                  "EncSp": [0xFF, 7],
              },
              "NPEMCtrl": {
                  "En": [0x01, 8],
                  "Reset": [0x02, 8],
                  "OK": [0x04, 8],
                  "Locate": [0x08, 8],
                  "Locate": [0x10, 8],
                  "Rebuild": [0x20, 8],
                  "PFA": [0x40, 8],
                  "HotSpare": [0x80, 8],
                  "CriticalArray": [0x01, 9],
                  "FailedArray": [0x02, 9],
                  "InvalidDevice": [0x04, 9],
                  "Dis": [0x08, 9],
                  "EncSp": [0xFF, 11],
              },
              "NPEMSta": {
                  "CommandCplt": [0x01, 12],
                  "EncSp": [0xFF, 15],
              },
              }
    length = 16
    name = 'NPEM Extended Capability'
    cap_id = PCI_EXT_CAP_ID.PCI_EXT_CAP_ID_NPEM.value
    def __init__(self, raw_data, offset):
        super(NPEMCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class SecondaryPCIeCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              "LnkCtl3": {"LnkEquIntrruptEn": [0x01, 4],
                          "PerformEqu": [0x02, 4],
                          "EnLowerSKPOSGenVec": [0xFE, 5],
                          },
              "LaneErrStat": [0xFFFFFFFF, 8],
              }
    length = 76
    name = 'Secondary PCI Express'
    cap_id = PCI_EXT_CAP_ID.PCI_EXT_CAP_ID_SECPCI.value
    def __init__(self, raw_data, offset):
        super(SecondaryPCIeCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class PLGen4ExtendCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              "Gen4Cap": [0xFFFFFFFF, 4],
              "Gen4Ctl": [0xFFFFFFFF, 8],
              "Gen4Sta": [0xFFFFFFFF, 12],
              "LocDataPMSta": [0xFFFFFFFF, 16],
              "1stRetimerPMSta": [0xFFFFFFFF, 20],
              "2ndRetimerPMSta": [0xFFFFFFFF, 24],
              "EqCtl": {"L0": [0xFF, 32],
                        "L1": [0xFF, 33],
                        "L2": [0xFF, 34],
                        "L3": [0xFF, 35],
                        "L4": [0xFF, 36],
                        "L5": [0xFF, 37],
                        "L6": [0xFF, 38],
                        "L7": [0xFF, 39],
                        "L8": [0xFF, 40],
                        "L9": [0xFF, 41],
                        "L10": [0xFF, 42],
                        "L11": [0xFF, 43],
                        "L12": [0xFF, 44],
                        "L13": [0xFF, 45],
                        "L14": [0xFF, 46],
                        "L15": [0xFF, 47],
                        "L16": [0xFF, 48],
                        "L17": [0xFF, 49],
                        "L18": [0xFF, 50],
                        "L19": [0xFF, 51],
                        "L20": [0xFF, 52],
                        "L21": [0xFF, 53],
                        "L22": [0xFF, 54],
                        "L23": [0xFF, 55],
                        "L24": [0xFF, 56],
                        "L25": [0xFF, 57],
                        "L26": [0xFF, 58],
                        "L27": [0xFF, 59],
                        "L28": [0xFF, 60],
                        "L29": [0xFF, 61],
                        "L30": [0xFF, 62],
                        "L31": [0xFF, 63],
                        },
    }
    length = 64
    name = 'Physical Layer 16.0 GT/s Extended Capability'
    cap_id = PCI_EXT_CAP_ID.PCI_EXT_CAP_ID_PL_16GT.value
    def __init__(self, raw_data, offset):
        super(PLGen4ExtendCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class PLGen5ExtendCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              "Gen5Cap": [0xFFFFFFFF, 4],
              "Gen5Ctl": [0xFFFFFFFF, 8],
              "Gen5Sta": [0xFFFFFFFF, 12],
              "RxModData1": [0xFFFFFFFF, 16],
              "RxModData2": [0xFFFFFFFF, 20],
              "TxModData1": [0xFFFFFFFF, 24],
              "TxModData2": [0xFFFFFFFF, 28],
              "EqCtl": {"L0": [0xFF, 32],
                        "L1": [0xFF, 33],
                        "L2": [0xFF, 34],
                        "L3": [0xFF, 35],
                        "L4": [0xFF, 36],
                        "L5": [0xFF, 37],
                        "L6": [0xFF, 38],
                        "L7": [0xFF, 39],
                        "L8": [0xFF, 40],
                        "L9": [0xFF, 41],
                        "L10": [0xFF, 42],
                        "L11": [0xFF, 43],
                        "L12": [0xFF, 44],
                        "L13": [0xFF, 45],
                        "L14": [0xFF, 46],
                        "L15": [0xFF, 47],
                        "L16": [0xFF, 48],
                        "L17": [0xFF, 49],
                        "L18": [0xFF, 50],
                        "L19": [0xFF, 51],
                        "L20": [0xFF, 52],
                        "L21": [0xFF, 53],
                        "L22": [0xFF, 54],
                        "L23": [0xFF, 55],
                        "L24": [0xFF, 56],
                        "L25": [0xFF, 57],
                        "L26": [0xFF, 58],
                        "L27": [0xFF, 59],
                        "L28": [0xFF, 60],
                        "L29": [0xFF, 61],
                        "L30": [0xFF, 62],
                        "L31": [0xFF, 63]
              },
    }
    length = 64
    name = 'Physical Layer 32.0 GT/s Extended Capability'
    cap_id = PCI_EXT_CAP_ID.PCI_EXT_CAP_ID_PL_32GT.value
    def __init__(self, raw_data, offset):
        super(PLGen5ExtendCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class PLGen6ExtendCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              "Cap": [0xFFFFFFFF, 4],
              "Ctl": [0xFFFFFFFF, 8],
              "Sta": [0xFFFFFFFF, 12],
              "EqCtl": {"L0": [0xFF, 16],
                        "L1": [0xFF, 17],
                        "L2": [0xFF, 18],
                        "L3": [0xFF, 19],
                        "L4": [0xFF, 20],
                        "L5": [0xFF, 21],
                        "L6": [0xFF, 22],
                        "L7": [0xFF, 23],
                        "L8": [0xFF, 24],
                        "L9": [0xFF, 25],
                        "L10": [0xFF, 26],
                        "L11": [0xFF, 27],
                        "L12": [0xFF, 28],
                        "L13": [0xFF, 29],
                        "L14": [0xFF, 30],
                        "L15": [0xFF, 31],
              },
    }
    length = 32
    name = 'Physical Layer 64.0 GT/s Extended Capability'
    cap_id = PCI_EXT_CAP_ID.PCI_EXT_CAP_ID_PL_64GT.value
    def __init__(self, raw_data, offset):
        super(PLGen6ExtendCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")



class LaneMargineRxExtendCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              "PortCap": [0xFFFF, 4],
              "PortSta": [0xFFFF, 6],
              "LaneCtl": {"lane0": [0xFFFF, 8],
                          "lane1": [0xFFFF, 12],
                          "lane2": [0xFFFF, 16],
                          "lane3": [0xFFFF, 20],
                          "lane4": [0xFFFF, 24],
                          "lane5": [0xFFFF, 28],
                          "lane6": [0xFFFF, 32],
                          "lane7": [0xFFFF, 36],
                          "lane8": [0xFFFF, 40],
                          "lane9": [0xFFFF, 44],
                          "lane10": [0xFFFF, 48],
                          "lane11": [0xFFFF, 52],
                          "lane12": [0xFFFF, 56],
                          "lane13": [0xFFFF, 60],
                          "lane14": [0xFFFF, 64],
                          "lane15": [0xFFFF, 68],
                          "lane16": [0xFFFF, 72],
                          "lane17": [0xFFFF, 76],
                          "lane18": [0xFFFF, 80],
                          "lane19": [0xFFFF, 84],
                          "lane20": [0xFFFF, 88],
                          "lane21": [0xFFFF, 92],
                          "lane22": [0xFFFF, 96],
                          "lane23": [0xFFFF, 100],
                          "lane24": [0xFFFF, 104],
                          "lane25": [0xFFFF, 108],
                          "lane26": [0xFFFF, 112],
                          "lane27": [0xFFFF, 116],
                          "lane28": [0xFFFF, 120],
                          "lane29": [0xFFFF, 124],
                          "lane30": [0xFFFF, 128],
                          "lane31": [0xFFFF, 132],
                          },
              "LaneSta": {"lane0": [0xFFFF, 10],
                          "lane1": [0xFFFF, 14],
                          "lane2": [0xFFFF, 18],
                          "lane3": [0xFFFF, 22],
                          "lane4": [0xFFFF, 26],
                          "lane5": [0xFFFF, 30],
                          "lane6": [0xFFFF, 34],
                          "lane7": [0xFFFF, 38],
                          "lane8": [0xFFFF, 42],
                          "lane9": [0xFFFF, 46],
                          "lane10": [0xFFFF, 50],
                          "lane11": [0xFFFF, 54],
                          "lane12": [0xFFFF, 58],
                          "lane13": [0xFFFF, 62],
                          "lane14": [0xFFFF, 66],
                          "lane15": [0xFFFF, 70],
                          "lane16": [0xFFFF, 74],
                          "lane17": [0xFFFF, 78],
                          "lane18": [0xFFFF, 82],
                          "lane19": [0xFFFF, 86],
                          "lane20": [0xFFFF, 90],
                          "lane21": [0xFFFF, 94],
                          "lane22": [0xFFFF, 98],
                          "lane23": [0xFFFF, 102],
                          "lane24": [0xFFFF, 106],
                          "lane25": [0xFFFF, 110],
                          "lane26": [0xFFFF, 114],
                          "lane27": [0xFFFF, 118],
                          "lane28": [0xFFFF, 122],
                          "lane29": [0xFFFF, 126],
                          "lane30": [0xFFFF, 130],
                          "lane31": [0xFFFF, 134],
                          },
    }
    length = 136
    name = 'Lane Margining at the Receiver Extended Capability'
    cap_id = 0x27
    def __init__(self, raw_data, offset):
        super(LaneMargineRxExtendCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class LTRExtendCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              "MaxSnoopLat": {"LatValue": [0x3FF, 4],
                              "LatScale": [0x1C, 5],},
              "MaxNonSnoopLat": {"LatValue": [0x3FF, 6],
                                 "LatScale": [0x1C, 7],},
    }
    length = 8
    name = 'Latency Tolerance Reporting (LTR) Extended Capability'
    cap_id = PCI_EXT_CAP_ID.PCI_EXT_CAP_ID_LTR.value
    def __init__(self, raw_data, offset):
        super(LTRExtendCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class L1PMSubstatesExtendCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              "L1Cap": {"PCI-PM_L1.2": [0x01, 4],
                        "PCI-PM_L1.1": [0x02, 4],
                        "ASPM_L1.2": [0x04, 4],
                        "ASPM_L1.1": [0x08, 4],
                        "L1PMSubstates": [0x10, 4],
                        "LinkAct": [0x20, 4],
                        "PortCMRT": [0xFF, 5],
                        "PortTPOScale": [0x03, 6],
                        "PortTPOValue": [0xF8, 6],
                        },
              "L1Ctl1": {"PCI-PM_L1.2": [0x01, 8],
                         "PCI-PM_L1.1": [0x02, 8],
                         "ASPM_L1.2": [0x04, 8],
                         "ASPM_L1.1": [0x08, 8],
                         "LinkActInt": [0x10, 8],
                         "LinkAct": [0x20, 8],
                         "CMRT": [0xFF, 9],
                         "LTR_L1.2_TH_Value": [0x3FF, 10],
                         "LTR_L1.2_TH_Scale": [0xE0, 11],
                         },
              "L1Ctl2": {"TPOScale": [0x03, 12],
                         "TPOValue": [0xF8, 12],
                         },
              "L1Sta": {"LinkAct": [0x01, 16],
                        },
    }
    length = 20
    name = 'L1 PM Substates Extended Capability'
    cap_id = PCI_EXT_CAP_ID.PCI_EXT_CAP_ID_L1SS.value
    def __init__(self, raw_data, offset):
        super(L1PMSubstatesExtendCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class ARIExtendCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              "ARICap": {"MFVCFunc": [0x01, 4],
                         "ACSFunc": [0x02, 4],
                         "NextFunc": [0xFF, 5],
                         },
              "ARICtl": {"MFVCFuncEn": [0x01, 6],
                         "ACSFuncEn": [0x02, 6],
                         "FuncGroup": [0x70, 6],
                         },
    }
    length = 8
    name = 'ARI Extended Capability'
    cap_id = PCI_EXT_CAP_ID.PCI_EXT_CAP_ID_ARI.value
    def __init__(self, raw_data, offset):
        super(ARIExtendCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class DevSNExtendCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              "SNLower": [0xFFFFFFFF, 4],
              "SNUpper": [0xFFFFFFFF, 8],
    }
    length = 12
    name = 'Device Serial Number Extended Capability'
    cap_id = PCI_EXT_CAP_ID.PCI_EXT_CAP_ID_DSN.value
    def __init__(self, raw_data, offset):
        super(DevSNExtendCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class VenorSpecExtendCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              "VSHeader": {"VSECID": [0xFFFF, 4],
                           "VSECLen": [0xFFF0, 6],
              },
              "VSReg": ('b', 8, 12),
    }
    length = 20
    name = 'Vendor-Specific Extended Capability'
    cap_id = PCI_EXT_CAP_ID.PCI_EXT_CAP_ID_VNDR.value
    def __init__(self, raw_data, offset):
        super(VenorSpecExtendCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class PowerBudgetingExtendCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              "DataSelect":[0xFF, 4],
              "Data": {"BasePower": [0xFF, 8],
                       "DataScale": [0x03, 9],
                       "PMSubSta": [0x1C, 9],
                       "PMSta": [0x60, 9],
                       "Type": [0x380, 9],
                       "PowerRail": [0x1C, 10],
              },
              "Cap": {"SystemAlloc": [0x01, 12],
                      },
    }
    length = 16
    name = 'Power Budgeting Extended Capability'
    cap_id = PCI_EXT_CAP_ID.PCI_EXT_CAP_ID_PWR.value
    def __init__(self, raw_data, offset):
        super(PowerBudgetingExtendCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class DOEExtendCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              "DOECap":{"IntSup": [0x01, 4],
                        "IntMsgNum": [0xFFE, 4],
                        "AttMechSup": [0x10, 5],
                        "AsyncMsgSup": [0x20, 5],
                        },
              "DOECtl":{"Abort": [0x01, 8],
                        "IntEn": [0x02, 8],
                        "AttNotNeed": [0x04, 8],
                        "AsyncMsgEn": [0x08, 8],
                        "Go": [0x80, 11],
                        },
              "DOESta":{"Busy": [0x01, 12],
                        "IntSta": [0x02, 12],
                        "Error": [0x04, 12],
                        "AsyncMsgSta": [0x08, 12],
                        "At_Att": [0x10, 12],
                        "DataObjReady": [0x80, 15],
                        },
              "DOEWriteMailbox":['b', 16, 4],
              "DOEReadMailbox":['b', 20, 4],
    }
    length = 24
    name = 'Data Object Exchange Extended Capability'
    cap_id = PCI_EXT_CAP_ID.PCI_EXT_CAP_ID_DOE.value
    def __init__(self, raw_data, offset):
        super(DOEExtendCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class TPHReqExtendCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              "ReqCap":{"NoST": [0x01, 4],
                        "IntVec": [0x02, 4],
                        "DevSpec": [0x04, 4],
                        "ExtTPHReq": [0x01, 5],
                        "STTableLoc": [0x06, 5],
                        "STTableSize": [0x7FF, 6],

                        },
              "ReqCtl":{"STMod": [0x07, 8],
                        "TPHReqEn": [0x03, 9],
                        },
    }
    length = 12
    name = 'TPH Requester Extended Capability'
    cap_id = PCI_EXT_CAP_ID.PCI_EXT_CAP_ID_TPH.value
    def __init__(self, raw_data, offset):
        super(TPHReqExtendCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class SecondaryPCIeExtendCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              "LnkCtl3":{"PerfEq": [0x01, 4],
                        "LnkEqReqInt": [0x02, 4],
                        "EnLowerSKPOSGenVec": [0xFE, 5],
                        },
              "LaneErrSta":[0xFFFFFFFF, 8],
              "LaneEqCtl": {"Lane0": [0xFFFF, 12],
                            "Lane1": [0xFFFF, 14],
                            "Lane2": [0xFFFF, 16],
                            "Lane3": [0xFFFF, 18],
                            "Lane4": [0xFFFF, 20],
                            "Lane5": [0xFFFF, 22],
                            "Lane6": [0xFFFF, 24],
                            "Lane7": [0xFFFF, 26],
                            "Lane8": [0xFFFF, 28],
                            "Lane9": [0xFFFF, 30],
                            "Lane10": [0xFFFF, 32],
                            "Lane11": [0xFFFF, 34],
                            "Lane12": [0xFFFF, 36],
                            "Lane13": [0xFFFF, 38],
                            "Lane14": [0xFFFF, 40],
                            "Lane15": [0xFFFF, 42],
                            "Lane16": [0xFFFF, 44],
                            "Lane17": [0xFFFF, 46],
                            "Lane18": [0xFFFF, 48],
                            "Lane19": [0xFFFF, 50],
                            "Lane20": [0xFFFF, 52],
                            "Lane21": [0xFFFF, 54],
                            "Lane22": [0xFFFF, 56],
                            "Lane23": [0xFFFF, 58],
                            "Lane24": [0xFFFF, 60],
                            "Lane25": [0xFFFF, 62],
                            "Lane26": [0xFFFF, 64],
                            "Lane27": [0xFFFF, 66],
                            "Lane28": [0xFFFF, 68],
                            "Lane29": [0xFFFF, 70],
                            "Lane30": [0xFFFF, 72],
                            "Lane31": [0xFFFF, 74],
                            },
    }
    length = 76
    name = 'Secondary PCI Express Extended Capability'
    cap_id = PCI_EXT_CAP_ID.PCI_EXT_CAP_ID_SECPCI.value
    def __init__(self, raw_data, offset):
        super(SecondaryPCIeExtendCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class DataLinkFeatureExtendCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              "Cap":{"LocScaleFCSup": [0x01, 4],
                     "LocImmeReadiness": [0x02, 4],
                     "LocExtVCCnt": [0x1C, 4],
                     "LocL0pExitLat": [0xE0, 4],
                     "ExchangeEn": [0x80, 7],
                     },
              "Sta":{"RmtScaleFCSup": [0x01, 8],
                     "RmtImmeReadiness": [0x02, 8],
                     "RmtExtVCCnt": [0x1C, 8],
                     "RmtL0pExitLat": [0xE0, 8],
                     "RmtSupValid": [0x80, 11],
                     },
    }
    length = 12
    name = 'Data Link Feature Extended Capability'
    cap_id = PCI_EXT_CAP_ID.PCI_EXT_CAP_ID_DLF.value
    def __init__(self, raw_data, offset):
        super(DataLinkFeatureExtendCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class FlitLoggingExtendCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              "Log1": [0xFFFFFFFF, 4],
              "Log2": [0xFFFFFFFF, 8],
              "CntCtl": [0xFFFF, 12],
              "CntSta": [0xFFFF, 14],
              "FBERMesCtl": [0xFFFFFFFF, 16],
              "FBERMesSta": {"1_reg": [0xFFFFFFFF, 20],
                             "2_reg": [0xFFFFFFFF, 24],
                             "3_reg": [0xFFFFFFFF, 28],
                             "4_reg": [0xFFFFFFFF, 32],
                             "5_reg": [0xFFFFFFFF, 36],
                             "6_reg": [0xFFFFFFFF, 40],
                             "7_reg": [0xFFFFFFFF, 44],
                             "8_reg": [0xFFFFFFFF, 48],
                             "9_reg": [0xFFFFFFFF, 52],
                             "10_reg": [0xFFFFFFFF, 56],
                             },
    }
    length = 60
    name = 'Flit Logging Extended Capability'
    cap_id = 0x32
    def __init__(self, raw_data, offset):
        super(FlitLoggingExtendCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class Dev3ExtendCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              "Cap3": [0xFFFFFFFF, 4],
              "Ctl3": [0xFFFFFFFF, 8],
              "Sta3": [0xFFFFFFFF, 12],
    }
    length = 16
    name = 'Device 3 Extended Capability'
    cap_id = 0x2F
    def __init__(self, raw_data, offset):
        super(Dev3ExtendCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class ACSExtendCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              "Cap": [0xFFFF, 4],
              "Ctl": [0xFFFF, 6],
              "EgressCtlVec": [0xFFFFFFFF, 8],
              "AddEgressCtlVec": [0xFFFFFFFF, 12],
    }
    length = 16
    name = 'ACS Extended Capability'
    cap_id = PCI_EXT_CAP_ID.PCI_EXT_CAP_ID_ACS.value
    def __init__(self, raw_data, offset):
        super(ACSExtendCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class ResizableBARExtendCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              "BAR_0": {"Cap": [0xFFFFFFFF, 4],
                        "Ctl": [0xFFFFFFFF, 8],
                         },
              "BAR_1": {"Cap": [0xFFFFFFFF, 12],
                        "Ctl": [0xFFFFFFFF, 16],
                         },
              "BAR_2": {"Cap": [0xFFFFFFFF, 20],
                        "Ctl": [0xFFFFFFFF, 24],
                         },
              "BAR_3": {"Cap": [0xFFFFFFFF, 28],
                        "Ctl": [0xFFFFFFFF, 32],
                         },
              "BAR_4": {"Cap": [0xFFFFFFFF, 36],
                        "Ctl": [0xFFFFFFFF, 40],
                         },
              "BAR_5": {"Cap": [0xFFFFFFFF, 44],
                        "Ctl": [0xFFFFFFFF, 48],
                         },
    }
    length = 52
    name = 'Resizable BAR Extended Capability'
    cap_id = PCI_EXT_CAP_ID.PCI_EXT_CAP_ID_REBAR.value
    def __init__(self, raw_data, offset):
        super(ResizableBARExtendCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class VFResizableBARExtendCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              "BAR_0": {"Cap": [0xFFFFFFFF, 4],
                        "Ctl": [0xFFFFFFFF, 8],
                         },
              "BAR_1": {"Cap": [0xFFFFFFFF, 12],
                        "Ctl": [0xFFFFFFFF, 16],
                         },
              "BAR_2": {"Cap": [0xFFFFFFFF, 20],
                        "Ctl": [0xFFFFFFFF, 24],
                         },
              "BAR_3": {"Cap": [0xFFFFFFFF, 28],
                        "Ctl": [0xFFFFFFFF, 32],
                         },
              "BAR_4": {"Cap": [0xFFFFFFFF, 36],
                        "Ctl": [0xFFFFFFFF, 40],
                         },
              "BAR_5": {"Cap": [0xFFFFFFFF, 44],
                        "Ctl": [0xFFFFFFFF, 48],
                         },
    }
    length = 52
    name = 'VF Resizable BAR Extended Capability'
    cap_id = 0x24
    def __init__(self, raw_data, offset):
        super(VFResizableBARExtendCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class PASIDExtendCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              "Cap": [0xFFFF, 4],
              "Ctl": [0xFFFF, 6],
    }
    length = 8
    name = 'PASID Extended Capability'
    cap_id = PCI_EXT_CAP_ID.PCI_EXT_CAP_ID_PASID.value
    def __init__(self, raw_data, offset):
        super(PASIDExtendCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class FRSQueExtendCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              "Cap": [0xFFFFFFFF, 4],
              "Sta": [0xFFFF, 8],
              "Ctl": [0xFFFF, 10],
              "MsgQueue": [0xFFFFFFFF, 12],
    }
    length = 16
    name = 'FRS Queueing Extended Capability'
    cap_id = 0x21
    def __init__(self, raw_data, offset):
        super(FRSQueExtendCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class FlitPerfMesExtendCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              "Cap": [0xFFFFFFFF, 4],
              "Ctl": [0xFFFFFFFF, 8],
              "Sta": [0xFFFFFFFF, 12],
              "LTSSMSta": {"1_reg": [0xFFFFFFFF, 16],
                           "2_reg": [0xFFFFFFFF, 20],
                           "3_reg": [0xFFFFFFFF, 24],
                           "4_reg": [0xFFFFFFFF, 28],
                           "5_reg": [0xFFFFFFFF, 32],
                           },
    }
    length = 36
    name = 'Flit Performance Measurement Extended Capability'
    cap_id = 0x33
    def __init__(self, raw_data, offset):
        super(FlitPerfMesExtendCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class FlitErrInjExtendCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              "Cap": [0xFFFFFFFF, 4],
              "Ctl1": [0xFFFFFFFF, 8],
              "Ctl2": [0xFFFFFFFF, 12],
              "Sta": [0xFFFFFFFF, 16],
              "OrdInjCtl1": [0xFFFFFFFF, 20],
              "OrdInjCtl2": [0xFFFFFFFF, 24],
              "OrdTxInjSta": [0xFFFFFFFF, 28],
              "OrdRxInjSta": [0xFFFFFFFF, 32],
    }
    length = 36
    name = 'Flit Error Injection Extended Capability'
    cap_id = 0x34
    def __init__(self, raw_data, offset):
        super(FlitErrInjExtendCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class NOPFlitExtendCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              "Cap": [0xFFFFFFFF, 4],
              "Ctl1": [0xFFFFFFFF, 8],
              "Ctl2": [0xFFFFFFFF, 12],
              "Sta": [0xFFFFFFFF, 16],
    }
    length = 20
    name = 'NOP Flit Extended Capability'
    cap_id = 0x37
    def __init__(self, raw_data, offset):
        super(NOPFlitExtendCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class VCExtendCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              "PortCap1": [0xFFFFFFFF, 4],
              "PortCap2": [0xFFFFFFFF, 8],
              "PortCtl": [0xFFFF, 12],
              "PortSta": [0xFFFF, 14],
              "VCRes_0": {"Cap": [0xFFFFFFFF, 16],
                          "Ctl": [0xFFFFFFFF, 20],
                          "Sta": [0xFFFFFFFF, 24],},
    }
    length = 28
    name = 'Virtual Channel Extended Capability'
    cap_id = PCI_EXT_CAP_ID.PCI_EXT_CAP_ID_VC.value
    def __init__(self, raw_data, offset):
        super(VCExtendCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")

class VC9ExtendCap(VCExtendCap):
    cap_id = PCI_EXT_CAP_ID.PCI_EXT_CAP_ID_VC9.value


class MFVCExtendCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              "PortVCCap1": [0xFFFFFFFF, 4],
              "PortVCCap2": [0xFFFFFFFF, 8],
              "PortVCCtl": [0xFFFF, 12],
              "PortVCSta": [0xFFFF, 14],
              "VCRes_0": {"Cap": [0xFFFFFFFF, 16],
                          "Ctl": [0xFFFFFFFF, 20],
                          "Sta": [0xFFFFFFFF, 24],},
    }
    length = 28
    name = 'Multi-Function Virtual Channel Extended Capability'
    cap_id = PCI_EXT_CAP_ID.PCI_EXT_CAP_ID_MFVC.value
    def __init__(self, raw_data, offset):
        super(MFVCExtendCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class DesVenorSpecExtendCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              "Header1": {"ID": [0xFFFF, 4],
                          "Rev": [0x0F, 6],
                          "Len": [0xFFF0, 6],
              },
              "Header2": [0xFFFF, 8],
              "VSReg": ('b', 10, 10),
    }
    length = 20
    name = 'Designated Vendor-Specific Extended Capability'
    cap_id = PCI_EXT_CAP_ID.PCI_EXT_CAP_ID_DVSEC.value
    def __init__(self, raw_data, offset):
        super(DesVenorSpecExtendCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class RCRBExtendCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              "VID": [0xFFFF, 4],
              "DID": [0xFFFF, 6],
              "Cap": [0xFFFFFFFF, 8],
              "Ctl": [0xFFFFFFFF, 12],
    }
    length = 20
    name = 'RCRB Header Extended Capability'
    cap_id = PCI_EXT_CAP_ID.PCI_EXT_CAP_ID_RCRB.value
    def __init__(self, raw_data, offset):
        super(RCRBExtendCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class RCLnkDecExtendCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              "ElSelfDes": [0xFFFFFFFF, 4],
              "LnkEntry_1": ('b', 12, 16),
    }
    length = 28
    name = 'Root Complex Link Declaration Extended Capability'
    cap_id = PCI_EXT_CAP_ID.PCI_EXT_CAP_ID_RCLD.value
    def __init__(self, raw_data, offset):
        super(RCLnkDecExtendCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class RCIntlLnkCtlExtendCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              "Cap": [0xFFFFFFFF, 4],
              "Ctl": [0xFFFF, 8],
              "Sta": [0xFFFF, 10],
    }
    length = 12
    name = 'Root Complex Internal Link Control Extended Capability'
    cap_id = PCI_EXT_CAP_ID.PCI_EXT_CAP_ID_RCILC.value
    def __init__(self, raw_data, offset):
        super(RCIntlLnkCtlExtendCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class RCECEAExtendCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              "BitMap": [0xFFFFFFFF, 4],
              "BusNum": [0xFFFFFFFF, 8],
    }
    length = 12
    name = 'Root Complex Event Collector Endpoint Association Extended Capability'
    cap_id = PCI_EXT_CAP_ID.PCI_EXT_CAP_ID_RCEC.value
    def __init__(self, raw_data, offset):
        super(RCECEAExtendCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class MulticastExtendCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              "Cap": [0xFFFF, 4],
              "Ctl": [0xFFFF, 6],
              "Base_Addr": ('b', 8, 8),
              "Receive": ('b', 16, 8),
              "Block_All": ('b', 24, 8),
              "Block_Unt": ('b', 32, 8),
              "Overlay_BAR": ('b', 40, 8),
    }
    length = 48
    name = 'Multicast Extended Capability'
    cap_id = PCI_EXT_CAP_ID.PCI_EXT_CAP_ID_MCAST.value
    def __init__(self, raw_data, offset):
        super(MulticastExtendCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class DPAExtendCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              "Cap": [0xFFFFFFFF, 4],
              "LatInd": [0xFFFFFFFF, 8],
              "Sta": [0xFFFF, 12],
              "Ctl": [0xFFFF, 14],
              "PwrAllocArray": ('b', 16, 32),
    }
    length = 48
    name = 'Dynamic Power Allocation Extended Capability'
    cap_id = PCI_EXT_CAP_ID.PCI_EXT_CAP_ID_DPA.value
    def __init__(self, raw_data, offset):
        super(DPAExtendCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")

## 
# skip DPC, spec 6.3 page 1361
##
class PTMExtendCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              "Cap": [0xFFFFFFFF, 4],
              "Ctl": [0xFFFFFFFF, 8],
    }
    length = 12
    name = 'Precision Time Measurement Extended Capability'
    cap_id = PCI_EXT_CAP_ID.PCI_EXT_CAP_ID_PTM.value
    def __init__(self, raw_data, offset):
        super(PTMExtendCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class RTRExtendCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              "Reg_1": [0xFFFFFFFF, 4],
              "Reg_2": [0xFFFFFFFF, 8],
    }
    length = 12
    name = 'Readiness Time Reporting Extended Capability'
    cap_id = 0x22
    def __init__(self, raw_data, offset):
        super(RTRExtendCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class HierarchyIDExtendCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              "Sta": [0xFFFFFFFF, 4],
              "Data": [0xFFFFFFFF, 8],
              "GUID":{"Reg_1": [0xFFFFFFFF, 12],
                      "Reg_2": [0xFFFFFFFF, 16],
                      "Reg_3": [0xFFFFFFFF, 20],
                      "Reg_4": [0xFFFFFFFF, 24],
                      "Reg_5": [0xFFFFFFFF, 28],
              },
    }
    length = 32
    name = 'Hierarchy ID Extended Capability'
    cap_id = 0x28
    def __init__(self, raw_data, offset):
        super(HierarchyIDExtendCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class AltProtExtendCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              "Cap": [0xFFFFFFFF, 4],
              "Ctl": [0xFFFFFFFF, 8],
              "Data_1": [0xFFFFFFFF, 12],
              "Data_2": [0xFFFFFFFF, 16],
              },
    length = 20
    name = 'Alternate Protocol Extended Capability'
    cap_id = 0x2B
    def __init__(self, raw_data, offset):
        super(AltProtExtendCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class SFIExtendCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              "Cap": [0xFFFF, 4],
              "Ctl": [0xFFFF, 6],
              "Sta": [0xFFFF, 8],
              "CAM_Addr": [0xFFFFFFFF, 12],
              "CAM_Data": [0xFFFFFFFF, 16],
              },
    length = 20
    name = 'SFI Extended Capability'
    cap_id = 0x2C
    def __init__(self, raw_data, offset):
        super(SFIExtendCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")

class ShadowFunctionsExtendCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              "Cap": [0xFFFFFFFF, 4],
              "Ctl": [0xFFFFFFFF, 8],
              "Instance": {"Reg_0": [0xFFFFFFFF, 12],
                           "Reg_1": [0xFFFFFFFF, 16],
                           "Reg_2": [0xFFFFFFFF, 20],
                           "Reg_3": [0xFFFFFFFF, 24],
                           },
              },
    length = 28
    name = 'Shadow Functions Extended Capability'
    cap_id = 0x2D
    def __init__(self, raw_data, offset):
        super(ShadowFunctionsExtendCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class SVCExtendCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              "PortCap_1": {"VC_count": [0x07, 4],},
              "PortCap_2": [0xFFFFFFFF, 8],
              "PortCtl": [0xFFFFFFFF, 12],
              "PortSta": [0xFFFFFFFF, 16],
              "Resource_0": {"Cap": [0xFFFFFFFF, 20],
                             "Ctl": [0xFFFFFFFF, 24],
                             "Sta": [0xFFFFFFFF, 28],
                             },
              "Resource_1": {"Cap": [0xFFFFFFFF, 32],
                             "Ctl": [0xFFFFFFFF, 36],
                             "Sta": [0xFFFFFFFF, 40],
                             },
              "Resource_2": {"Cap": [0xFFFFFFFF, 44],
                             "Ctl": [0xFFFFFFFF, 48],
                             "Sta": [0xFFFFFFFF, 52],
                             },
              "Resource_3": {"Cap": [0xFFFFFFFF, 56],
                             "Ctl": [0xFFFFFFFF, 60],
                             "Sta": [0xFFFFFFFF, 64],
                             },
              "Resource_4": {"Cap": [0xFFFFFFFF, 68],
                             "Ctl": [0xFFFFFFFF, 72],
                             "Sta": [0xFFFFFFFF, 76],
                             },
              "Resource_5": {"Cap": [0xFFFFFFFF, 80],
                             "Ctl": [0xFFFFFFFF, 84],
                             "Sta": [0xFFFFFFFF, 88],
                             },
              "Resource_6": {"Cap": [0xFFFFFFFF, 92],
                             "Ctl": [0xFFFFFFFF, 96],
                             "Sta": [0xFFFFFFFF, 100],
                             },
              "Resource_7": {"Cap": [0xFFFFFFFF, 104],
                             "Ctl": [0xFFFFFFFF, 108],
                             "Sta": [0xFFFFFFFF, 112],
                             },
              },
    length = 116  # default max value
    name = 'Streamlined Virtual Channel Extended Capability'
    cap_id = 0x35
    def __init__(self, raw_data, offset):
        super(SVCExtendCap, self).__init__(raw_data, offset=offset)
        self.raw_data = self.raw_data[0:(self.decode_data["PortCap_1"]["VC_count"] * 12 + 32)]
        self.BitMap = SVCExtendCap.BitMap.copy()
        for i in range(self.decode_data["PortCap_1"]["VC_count"]+1, 8):
            self.BitMap.pop("Resource_%d" % i)
        self.decode_data.clear()
        decode_bits_iterative(self.raw_data, self.BitMap, self.decode_data, byteorder='little')

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class MRBLExtendCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              "Cap": {"length": [0xFFF, 4],},
              },
    length = 8
    name = 'MMIO Register Block Locator Extended Capability'
    cap_id = 0x36
    def __init__(self, raw_data, offset):
        super(MRBLExtendCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class ATSExtendCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              "Cap": [0xFFFF, 4],
              "Ctl": [0xFFFF, 6],
              },
    length = 8
    name = 'ATS Extended Capability'
    cap_id = PCI_EXT_CAP_ID.PCI_EXT_CAP_ID_ATS.value
    def __init__(self, raw_data, offset):
        super(ATSExtendCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class PageReqExtendCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              "Ctl": [0xFFFF, 4],
              "Sta": [0xFFFF, 6],
              "Outstd_Cap": [0xFFFFFFFF, 8],
              "Outstd_Alloc": [0xFFFFFFFF, 12],
              },
    length = 16
    name = 'Page Request Extended Capability'
    cap_id = PCI_EXT_CAP_ID.PCI_EXT_CAP_ID_PRI.value
    def __init__(self, raw_data, offset):
        super(PageReqExtendCap, self).__init__(raw_data, offset=offset)

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")


class PMUXExtendCap(CapDataBase):
    BitMap = {"CapabilityID": [0xFFFF, 0],
              "CapVer": [0x0F, 2],
              "NextCapabilityPointer": [0xFFF0, 2],
              "Cap": {"ArraySzie": [0x3F, 4],
                      "LnkSpeed": [0xFF, 5],
                      },
              "Ctl": [0xFFFFFFFF, 8],
              "Sta": [0xFFFFFFFF, 12],
              "Prot_Array": {"Prot_Array": {"A_%d" % i : [0xFFFFFFFF, 16+i*4] for i in range(1, 64)}},
              },
    length = 268  # default max value
    name = 'PMUX Extended Capability'
    cap_id = PCI_EXT_CAP_ID.PCI_EXT_CAP_ID_PMUX.value
    def __init__(self, raw_data, offset):
        super(PMUXExtendCap, self).__init__(raw_data, offset=offset)
        self.raw_data = self.raw_data[0:(self.decode_data["Cap"]["ArraySzie"] * 4 + 16)]
        self.BitMap = PMUXExtendCap.BitMap.copy()
        for i in range(self.decode_data["Cap"]["ArraySzie"]+1, 64):
            self.BitMap["Prot_Array"].pop("A_%d" % i)
        self.decode_data.clear()
        decode_bits_iterative(self.raw_data, self.BitMap, self.decode_data, byteorder='little')

    @property
    def CapabilityID(self):
        return self.decode_data.get("CapabilityID")

    @property
    def CapVer(self):
        return self.decode_data.get("CapVer")

    @property
    def NextCapabilityPointer(self):
        return self.decode_data.get("NextCapabilityPointer")



class PCIeExtendCap(object): # PCIe Extended Capabilities
    PCIeExtendCapTable = {SRIOVCap.cap_id: SRIOVCap,
                          AERCap.cap_id: AERCap,
                          NPEMCap.cap_id: NPEMCap,
                          SecondaryPCIeCap.cap_id: SecondaryPCIeCap,
                          PLGen4ExtendCap.cap_id: PLGen4ExtendCap,
                          PLGen5ExtendCap.cap_id: PLGen5ExtendCap,
                          LaneMargineRxExtendCap.cap_id: LaneMargineRxExtendCap,
                          LTRExtendCap.cap_id: LTRExtendCap,
                          L1PMSubstatesExtendCap.cap_id: L1PMSubstatesExtendCap,
                          ARIExtendCap.cap_id: ARIExtendCap,
                          DevSNExtendCap.cap_id: DevSNExtendCap,
                          VenorSpecExtendCap.cap_id: VenorSpecExtendCap,
                          PowerBudgetingExtendCap.cap_id: PowerBudgetingExtendCap,
                          DOEExtendCap.cap_id: DOEExtendCap,
                          TPHReqExtendCap.cap_id: TPHReqExtendCap,
                          SecondaryPCIeExtendCap.cap_id: SecondaryPCIeExtendCap,
                          DataLinkFeatureExtendCap.cap_id: DataLinkFeatureExtendCap,
                          PLGen6ExtendCap.cap_id: PLGen6ExtendCap,
                          FlitLoggingExtendCap.cap_id: FlitLoggingExtendCap,
                          Dev3ExtendCap.cap_id: Dev3ExtendCap,
                          ACSExtendCap.cap_id: ACSExtendCap,
                          ResizableBARExtendCap.cap_id: ResizableBARExtendCap,
                          FRSQueExtendCap.cap_id: FRSQueExtendCap,
                          FlitPerfMesExtendCap.cap_id: FlitPerfMesExtendCap,
                          FlitErrInjExtendCap.cap_id: FlitErrInjExtendCap,
                          NOPFlitExtendCap.cap_id: NOPFlitExtendCap,
                          VCExtendCap.cap_id: VCExtendCap,
                          VC9ExtendCap.cap_id: VC9ExtendCap,
                          MFVCExtendCap.cap_id: MFVCExtendCap,
                          VFResizableBARExtendCap.cap_id: VFResizableBARExtendCap,
                          PASIDExtendCap.cap_id: PASIDExtendCap,
                          DesVenorSpecExtendCap.cap_id: DesVenorSpecExtendCap,
                          RCRBExtendCap.cap_id: RCRBExtendCap,
                          RCLnkDecExtendCap.cap_id: RCLnkDecExtendCap,
                          RCIntlLnkCtlExtendCap.cap_id: RCIntlLnkCtlExtendCap,
                          RCECEAExtendCap.cap_id: RCECEAExtendCap,
                          MulticastExtendCap.cap_id: MulticastExtendCap,
                          DPAExtendCap.cap_id: DPAExtendCap,
                          PTMExtendCap.cap_id: PTMExtendCap,
                          RTRExtendCap.cap_id: RTRExtendCap,
                          NullExtendCap.cap_id: NullExtendCap,
                          HierarchyIDExtendCap.cap_id: HierarchyIDExtendCap,
                          AltProtExtendCap.cap_id: AltProtExtendCap,
                          SFIExtendCap.cap_id: SFIExtendCap,
                          ShadowFunctionsExtendCap.cap_id: ShadowFunctionsExtendCap,
                          SVCExtendCap.cap_id: SVCExtendCap,
                          MRBLExtendCap.cap_id: MRBLExtendCap,
                          ATSExtendCap.cap_id: ATSExtendCap,
                          PageReqExtendCap.cap_id: PageReqExtendCap,
                          PMUXExtendCap.cap_id: PMUXExtendCap,
                          }
    locate_offset = 256
    def __init__(self, raw_data):
        self.__raw_data = raw_data
        self.__pcie_extend_cap_decode = {}
        self.read_config()
        
    @property
    def raw_data(self):
        return self.__raw_data
    
    @property
    def decode_data(self):
        return self.__pcie_extend_cap_decode

    @staticmethod
    def _get_self_locate(offset):
        return offset - PCIeExtendCap.locate_offset

    def read_config(self):
        """
        Read the pcie extend cap data
        """
        offset = 0x100
        for i in range(960):
            # check offset
            if 0xFF < offset < 0xFFF:
                _self_locate = self._get_self_locate(offset)
                pci_extend_cap_id = PCIeExtendCapID(self.__raw_data[_self_locate:_self_locate+PCIeExtendCapID.length], offset)
                if pci_extend_cap_id.CapabilityID in PCIeExtendCap.PCIeExtendCapTable:
                    func = PCIeExtendCap.PCIeExtendCapTable.get(pci_extend_cap_id.CapabilityID)
                    data_len = min(func.length, pci_extend_cap_id.NextCapabilityPointer-offset) if (pci_extend_cap_id.NextCapabilityPointer-offset) > 0 else func.length
                    self.__pcie_extend_cap_decode[pci_extend_cap_id.CapabilityID] = func(self.__raw_data[_self_locate:_self_locate+data_len], offset)
                else:
                    self.__pcie_extend_cap_decode[pci_extend_cap_id.CapabilityID] = pci_extend_cap_id # Unknown Capability
                ## no other items
                if pci_extend_cap_id.NextCapabilityPointer == 0: 
                    break
                ## Get next cap
                offset = pci_extend_cap_id.NextCapabilityPointer
            else:
                raise ValueError("Incorrect PCIe Extended Capabilities Data offset(%#x)." % offset)
        else:
            raise ValueError("Incorrect PCIe Extended Capabilities Data.")

## 
# line to spec 6.3 page 1382
##
################ PCIe Extend Capabilities End #########################

class PCIConfigSpace(object):
    PCIBitMap = {"PCIConfigHeader": ("b", 0, 64),
                 "PCICap": ("b", 64, 192),
                 }
    PCIeBitMap = {"PCIeExtendCap": ("b", 256, 3840)}
    PCIeBitMap.update(PCIBitMap)
    def __init__(self, raw_data):
        self.__raw_data = raw_data
        self.__pci_config = {}
        if len(self.__raw_data) > 256:
            decode_bits(raw_data, PCIConfigSpace.PCIeBitMap, self.__pci_config)
        else:
            decode_bits(raw_data, PCIConfigSpace.PCIBitMap, self.__pci_config)

    @property
    def raw_data(self):
        return self.__raw_data

    @property
    def decode_data(self):
        return self.__pci_config  

    @property
    def PCIConfigHeader(self):
        return PCIConfigHeader(self.__pci_config.get("PCIConfigHeader"))

    @property
    def PCICap(self):
        return PCICap(self.__pci_config.get("PCICap"), self.PCIConfigHeader)

    @property
    def PCIeExtendCap(self):
        return PCIeExtendCap(self.__pci_config.get("PCIeExtendCap"))


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
