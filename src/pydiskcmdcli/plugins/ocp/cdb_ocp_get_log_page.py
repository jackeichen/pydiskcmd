# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmdcli import os_type
from .constants import CommandTimeout
from pydiskcmdlib.pynvme.nvme_command import NVMeCommand,AdminCommandOpcode,build_int_by_bitmap
from pydiskcmdlib.pynvme import linux_nvme_command,win_nvme_command
from enum import Enum
#####
CmdOPCode = AdminCommandOpcode.GetLogPage.value
admin_timeout_ms = CommandTimeout.admin.value
#####
class OCPLogIdentifier(Enum):
    DEVICE_SMART_INFORMATION = 0xC0
    DEVICE_ERROR_RECOVERY = 0xC1
    FIRMWARE_ACTIVATION_HISTORY = 0xC2
    LATENCY_MONITOR = 0xC3
    DEVICE_CAPABILITIES = 0xC4
    UNSUPPORTED_REQUIREMENTS = 0xC5
    HARDWARE_COMPONENT = 0xC6
    TCG_CONFIGURATION = 0xC7
    TELEMETRY_STRING_LOG = 0xC9

##### For windows vendor spec log page
# Callers could use a STORAGE_PROPERTY_ID of StorageAdapterProtocolSpecificProperty, and whose 
# STORAGE_PROTOCOL_SPECIFIC_DATA or STORAGE_PROTOCOL_SPECIFIC_DATA_EXT structure is set to 
# ProtocolDataRequestValue=VENDOR_SPECIFIC_LOG_PAGE_IDENTIFIER to request 512 byte chunks of vendor specific data.
##### For windows vendor spec log page

class SmartExtendedLog(NVMeCommand):
    if os_type == "Linux":
        _req_id = linux_nvme_command.IOCTLRequest.NVME_IOCTL_ADMIN_CMD.value
    elif os_type == "Windows":
        _req_id = win_nvme_command.IOCTLRequest.IOCTL_STORAGE_QUERY_PROPERTY.value
    def __init__(self, uuid_index=0, data_buffer=None):
        data_length = 512
        ### build command
        numdl = int(data_length / 4) - 1
        cdw10 = build_int_by_bitmap({"lid": (0xFF, 0, OCPLogIdentifier.DEVICE_SMART_INFORMATION.value),      # log id
                                     "numdl": (0x0FFF, 2, numdl),})
        cdw14 = build_int_by_bitmap({"UUID Index": (0x7F, 0, uuid_index),      # log id
                                    })
        ##     
        super(SmartExtendedLog, self).__init__()
        if os_type == "Linux":
            ## init data buffer
            data_buffer = self.init_data_buffer(data_length=data_length, data_buffer=data_buffer)
            self.build_command(opcode=CmdOPCode,
                               nsid=0,
                               addr=data_buffer.addr,
                               data_len=data_buffer.data_length,
                               cdw10=cdw10,
                               cdw14=cdw14,
                               timeout_ms=admin_timeout_ms)
        elif os_type == "Windows":
            self.build_command(PropertyId=win_nvme_command.StoragePropertyID.StorageAdapterProtocolSpecificProperty.value,
                               QueryType=win_nvme_command.StorageQueryType.PropertyStandardQuery.value,
                               ProtocolType=win_nvme_command.StroageProtocolType.ProtocolTypeNvme.value,
                               DataType=win_nvme_command.StorageProtocolNVMeDataType.NVMeDataTypeLogPage.value,
                               ProtocolDataOffset=win_nvme_command.sizeof(win_nvme_command.StorageProtocolSpecificData),
                               ProtocolDataLength=data_length,
                               ProtocolDataRequestValue=OCPLogIdentifier.DEVICE_SMART_INFORMATION.value)


class ErrorRecoveryLog(NVMeCommand):
    if os_type == "Linux":
        _req_id = linux_nvme_command.IOCTLRequest.NVME_IOCTL_ADMIN_CMD.value
    elif os_type == "Windows":
        _req_id = win_nvme_command.IOCTLRequest.IOCTL_STORAGE_QUERY_PROPERTY.value
    def __init__(self, uuid_index=0, data_buffer=None):
        data_length = 512
        ### build command
        numdl = int(data_length / 4) - 1
        cdw10 = build_int_by_bitmap({"lid": (0xFF, 0, OCPLogIdentifier.DEVICE_ERROR_RECOVERY.value),      # log id
                                     "numdl": (0x0FFF, 2, numdl),})
        cdw14 = build_int_by_bitmap({"UUID Index": (0x7F, 0, uuid_index),      # log id
                                    })
        ##     
        super(ErrorRecoveryLog, self).__init__()
        if os_type == "Linux":
            ## init data buffer
            data_buffer = self.init_data_buffer(data_length=data_length, data_buffer=data_buffer)
            self.build_command(opcode=CmdOPCode,
                               nsid=0,
                               addr=data_buffer.addr,
                               data_len=data_buffer.data_length,
                               cdw10=cdw10,
                               cdw14=cdw14,
                               timeout_ms=admin_timeout_ms)
        elif os_type == "Windows":
            self.build_command(PropertyId=win_nvme_command.StoragePropertyID.StorageAdapterProtocolSpecificProperty.value,
                               QueryType=win_nvme_command.StorageQueryType.PropertyStandardQuery.value,
                               ProtocolType=win_nvme_command.StroageProtocolType.ProtocolTypeNvme.value,
                               DataType=win_nvme_command.StorageProtocolNVMeDataType.NVMeDataTypeLogPage.value,
                               ProtocolDataOffset=win_nvme_command.sizeof(win_nvme_command.StorageProtocolSpecificData),
                               ProtocolDataLength=data_length,
                               ProtocolDataRequestValue=OCPLogIdentifier.DEVICE_ERROR_RECOVERY.value)


class LatencyMonitor(NVMeCommand):
    if os_type == "Linux":
        _req_id = linux_nvme_command.IOCTLRequest.NVME_IOCTL_ADMIN_CMD.value
    elif os_type == "Windows":
        _req_id = win_nvme_command.IOCTLRequest.IOCTL_STORAGE_QUERY_PROPERTY.value
    def __init__(self, uuid_index=0, data_buffer=None):
        data_length = 512
        lid = OCPLogIdentifier.LATENCY_MONITOR.value
        ### build command
        numdl = int(data_length / 4) - 1
        cdw10 = build_int_by_bitmap({"lid": (0xFF, 0, lid),      # log id
                                     "numdl": (0x0FFF, 2, numdl),})
        cdw14 = build_int_by_bitmap({"UUID Index": (0x7F, 0, uuid_index),      # log id
                                    })
        ##
        super(LatencyMonitor, self).__init__()
        if os_type == "Linux":
            ## init data buffer
            data_buffer = self.init_data_buffer(data_length=data_length, data_buffer=data_buffer)
            self.build_command(opcode=CmdOPCode,
                               nsid=0,
                               addr=data_buffer.addr,
                               data_len=data_buffer.data_length,
                               cdw10=cdw10,
                               cdw14=cdw14,
                               timeout_ms=admin_timeout_ms)
        elif os_type == "Windows":
            self.build_command(PropertyId=win_nvme_command.StoragePropertyID.StorageAdapterProtocolSpecificProperty.value,
                               QueryType=win_nvme_command.StorageQueryType.PropertyStandardQuery.value,
                               ProtocolType=win_nvme_command.StroageProtocolType.ProtocolTypeNvme.value,
                               DataType=win_nvme_command.StorageProtocolNVMeDataType.NVMeDataTypeLogPage.value,
                               ProtocolDataOffset=win_nvme_command.sizeof(win_nvme_command.StorageProtocolSpecificData),
                               ProtocolDataLength=data_length,
                               ProtocolDataRequestValue=lid)


class DeviceCapabilities(NVMeCommand):
    if os_type == "Linux":
        _req_id = linux_nvme_command.IOCTLRequest.NVME_IOCTL_ADMIN_CMD.value
    elif os_type == "Windows":
        _req_id = win_nvme_command.IOCTLRequest.IOCTL_STORAGE_QUERY_PROPERTY.value
    def __init__(self, uuid_index=0, data_buffer=None):
        data_length = 4096
        lid = OCPLogIdentifier.DEVICE_CAPABILITIES.value
        ### build command
        numdl = int(data_length / 4) - 1
        cdw10 = build_int_by_bitmap({"lid": (0xFF, 0, lid),      # log id
                                     "numdl": (0x0FFF, 2, numdl),})
        cdw14 = build_int_by_bitmap({"UUID Index": (0x7F, 0, uuid_index),      # log id
                                    })
        ##
        super(DeviceCapabilities, self).__init__()
        if os_type == "Linux":
            ## init data buffer
            data_buffer = self.init_data_buffer(data_length=data_length, data_buffer=data_buffer)
            self.build_command(opcode=CmdOPCode,
                               nsid=0,
                               addr=data_buffer.addr,
                               data_len=data_buffer.data_length,
                               cdw10=cdw10,
                               cdw14=cdw14,
                               timeout_ms=admin_timeout_ms)
        elif os_type == "Windows":
            self.build_command(PropertyId=win_nvme_command.StoragePropertyID.StorageAdapterProtocolSpecificProperty.value,
                               QueryType=win_nvme_command.StorageQueryType.PropertyStandardQuery.value,
                               ProtocolType=win_nvme_command.StroageProtocolType.ProtocolTypeNvme.value,
                               DataType=win_nvme_command.StorageProtocolNVMeDataType.NVMeDataTypeLogPage.value,
                               ProtocolDataOffset=win_nvme_command.sizeof(win_nvme_command.StorageProtocolSpecificData),
                               ProtocolDataLength=data_length,
                               ProtocolDataRequestValue=lid)


class UnsupportedRequirements(NVMeCommand):
    if os_type == "Linux":
        _req_id = linux_nvme_command.IOCTLRequest.NVME_IOCTL_ADMIN_CMD.value
    elif os_type == "Windows":
        _req_id = win_nvme_command.IOCTLRequest.IOCTL_STORAGE_QUERY_PROPERTY.value
    def __init__(self, uuid_index=0, data_buffer=None):
        data_length = 4096
        lid = OCPLogIdentifier.UNSUPPORTED_REQUIREMENTS.value
        ### build command
        numdl = int(data_length / 4) - 1
        cdw10 = build_int_by_bitmap({"lid": (0xFF, 0, lid),      # log id
                                     "numdl": (0x0FFF, 2, numdl),})
        cdw14 = build_int_by_bitmap({"UUID Index": (0x7F, 0, uuid_index),      # log id
                                    })
        ##
        super(UnsupportedRequirements, self).__init__()
        if os_type == "Linux":
            ## init data buffer
            data_buffer = self.init_data_buffer(data_length=data_length, data_buffer=data_buffer)
            self.build_command(opcode=CmdOPCode,
                               nsid=0,
                               addr=data_buffer.addr,
                               data_len=data_buffer.data_length,
                               cdw10=cdw10,
                               cdw14=cdw14,
                               timeout_ms=admin_timeout_ms)
        elif os_type == "Windows":
            self.build_command(PropertyId=win_nvme_command.StoragePropertyID.StorageAdapterProtocolSpecificProperty.value,
                               QueryType=win_nvme_command.StorageQueryType.PropertyStandardQuery.value,
                               ProtocolType=win_nvme_command.StroageProtocolType.ProtocolTypeNvme.value,
                               DataType=win_nvme_command.StorageProtocolNVMeDataType.NVMeDataTypeLogPage.value,
                               ProtocolDataOffset=win_nvme_command.sizeof(win_nvme_command.StorageProtocolSpecificData),
                               ProtocolDataLength=data_length,
                               ProtocolDataRequestValue=lid)


class HardwareComponent(NVMeCommand):
    if os_type == "Linux":
        _req_id = linux_nvme_command.IOCTLRequest.NVME_IOCTL_ADMIN_CMD.value
    elif os_type == "Windows":
        _req_id = win_nvme_command.IOCTLRequest.IOCTL_STORAGE_QUERY_PROPERTY.value
    def __init__(self, data_length, uuid_index=0, data_buffer=None):
        lid = OCPLogIdentifier.HARDWARE_COMPONENT.value
        ### build command
        numdl = int(data_length / 4) - 1
        cdw10 = build_int_by_bitmap({"lid": (0xFF, 0, lid),      # log id
                                     "numdl": (0x0FFF, 2, numdl),})
        cdw14 = build_int_by_bitmap({"UUID Index": (0x7F, 0, uuid_index),      # log id
                                    })
        ##
        super(HardwareComponent, self).__init__()
        if os_type == "Linux":
            ## init data buffer
            data_buffer = self.init_data_buffer(data_length=data_length, data_buffer=data_buffer)
            self.build_command(opcode=CmdOPCode,
                               nsid=0,
                               addr=data_buffer.addr,
                               data_len=data_buffer.data_length,
                               cdw10=cdw10,
                               cdw14=cdw14,
                               timeout_ms=admin_timeout_ms)
        elif os_type == "Windows":
            self.build_command(PropertyId=win_nvme_command.StoragePropertyID.StorageAdapterProtocolSpecificProperty.value,
                               QueryType=win_nvme_command.StorageQueryType.PropertyStandardQuery.value,
                               ProtocolType=win_nvme_command.StroageProtocolType.ProtocolTypeNvme.value,
                               DataType=win_nvme_command.StorageProtocolNVMeDataType.NVMeDataTypeLogPage.value,
                               ProtocolDataOffset=win_nvme_command.sizeof(win_nvme_command.StorageProtocolSpecificData),
                               ProtocolDataLength=data_length,
                               ProtocolDataRequestValue=lid)


class TCGConfiguration(NVMeCommand):
    if os_type == "Linux":
        _req_id = linux_nvme_command.IOCTLRequest.NVME_IOCTL_ADMIN_CMD.value
    elif os_type == "Windows":
        _req_id = win_nvme_command.IOCTLRequest.IOCTL_STORAGE_QUERY_PROPERTY.value
    def __init__(self, uuid_index=0, data_buffer=None):
        data_length = 512
        lid = OCPLogIdentifier.TCG_CONFIGURATION.value
        ### build command
        numdl = int(data_length / 4) - 1
        cdw10 = build_int_by_bitmap({"lid": (0xFF, 0, lid),      # log id
                                     "numdl": (0x0FFF, 2, numdl),})
        cdw14 = build_int_by_bitmap({"UUID Index": (0x7F, 0, uuid_index),      # log id
                                    })
        ##
        super(TCGConfiguration, self).__init__()
        if os_type == "Linux":
            ## init data buffer
            data_buffer = self.init_data_buffer(data_length=data_length, data_buffer=data_buffer)
            self.build_command(opcode=CmdOPCode,
                               nsid=0,
                               addr=data_buffer.addr,
                               data_len=data_buffer.data_length,
                               cdw10=cdw10,
                               cdw14=cdw14,
                               timeout_ms=admin_timeout_ms)
        elif os_type == "Windows":
            self.build_command(PropertyId=win_nvme_command.StoragePropertyID.StorageAdapterProtocolSpecificProperty.value,
                               QueryType=win_nvme_command.StorageQueryType.PropertyStandardQuery.value,
                               ProtocolType=win_nvme_command.StroageProtocolType.ProtocolTypeNvme.value,
                               DataType=win_nvme_command.StorageProtocolNVMeDataType.NVMeDataTypeLogPage.value,
                               ProtocolDataOffset=win_nvme_command.sizeof(win_nvme_command.StorageProtocolSpecificData),
                               ProtocolDataLength=data_length,
                               ProtocolDataRequestValue=lid)


class TelemetryStringLog(NVMeCommand):
    if os_type == "Linux":
        _req_id = linux_nvme_command.IOCTLRequest.NVME_IOCTL_ADMIN_CMD.value
    elif os_type == "Windows":
        _req_id = win_nvme_command.IOCTLRequest.IOCTL_STORAGE_QUERY_PROPERTY.value
    def __init__(self, data_length, uuid_index=0, data_buffer=None):
        lid = OCPLogIdentifier.TELEMETRY_STRING_LOG.value
        ### build command
        numdl = int(data_length / 4) - 1
        cdw10 = build_int_by_bitmap({"lid": (0xFF, 0, lid),      # log id
                                     "numdl": (0x0FFF, 2, numdl),})
        cdw14 = build_int_by_bitmap({"UUID Index": (0x7F, 0, uuid_index),      # log id
                                    })
        ##
        super(TelemetryStringLog, self).__init__()
        if os_type == "Linux":
            ## init data buffer
            data_buffer = self.init_data_buffer(data_length=data_length, data_buffer=data_buffer)
            self.build_command(opcode=CmdOPCode,
                               nsid=0,
                               addr=data_buffer.addr,
                               data_len=data_buffer.data_length,
                               cdw10=cdw10,
                               cdw14=cdw14,
                               timeout_ms=admin_timeout_ms)
        elif os_type == "Windows":
            self.build_command(PropertyId=win_nvme_command.StoragePropertyID.StorageAdapterProtocolSpecificProperty.value,
                               QueryType=win_nvme_command.StorageQueryType.PropertyStandardQuery.value,
                               ProtocolType=win_nvme_command.StroageProtocolType.ProtocolTypeNvme.value,
                               DataType=win_nvme_command.StorageProtocolNVMeDataType.NVMeDataTypeLogPage.value,
                               ProtocolDataOffset=win_nvme_command.sizeof(win_nvme_command.StorageProtocolSpecificData),
                               ProtocolDataLength=data_length,
                               ProtocolDataRequestValue=lid)
