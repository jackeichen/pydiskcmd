# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmdcli import os_type
from .constants import CommandTimeout
from pydiskcmdlib.pynvme.nvme_command import NVMeCommand,AdminCommandOpcode,build_int_by_bitmap
from pydiskcmdlib.pynvme import linux_nvme_command,win_nvme_command
#####
CmdOPCode = AdminCommandOpcode.GetLogPage.value
admin_timeout_ms = CommandTimeout.admin.value
#####

class SmartExtendedLog(NVMeCommand):
    if os_type == "Linux":
        _req_id = linux_nvme_command.IOCTLRequest.NVME_IOCTL_ADMIN_CMD.value
    elif os_type == "Windows":
        _req_id = win_nvme_command.IOCTLRequest.IOCTL_STORAGE_QUERY_PROPERTY.value
    def __init__(self, uuid_index=0, data_buffer=None):
        data_length = 512
        ### build command
        numdl = int(data_length / 4) - 1
        cdw10 = build_int_by_bitmap({"lid": (0xFF, 0, 0xC0),      # log id
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
            self.build_command(PropertyId=win_nvme_command.StoragePropertyID.StorageDeviceProtocolSpecificProperty.value,
                               QueryType=win_nvme_command.StorageQueryType.PropertyStandardQuery.value,
                               ProtocolType=win_nvme_command.StroageProtocolType.ProtocolTypeNvme.value,
                               DataType=win_nvme_command.StorageProtocolNVMeDataType.NVMeDataTypeLogPage.value,
                               ProtocolDataOffset=win_nvme_command.sizeof(win_nvme_command.StorageProtocolSpecificData),
                               ProtocolDataLength=data_length,
                               lid=0xC0)


class ErrorRecoveryLog(NVMeCommand):
    if os_type == "Linux":
        _req_id = linux_nvme_command.IOCTLRequest.NVME_IOCTL_ADMIN_CMD.value
    elif os_type == "Windows":
        _req_id = win_nvme_command.IOCTLRequest.IOCTL_STORAGE_QUERY_PROPERTY.value
    def __init__(self, uuid_index=0, data_buffer=None):
        data_length = 512
        ### build command
        numdl = int(data_length / 4) - 1
        cdw10 = build_int_by_bitmap({"lid": (0xFF, 0, 0xC1),      # log id
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
            self.build_command(PropertyId=win_nvme_command.StoragePropertyID.StorageDeviceProtocolSpecificProperty.value,
                               QueryType=win_nvme_command.StorageQueryType.PropertyStandardQuery.value,
                               ProtocolType=win_nvme_command.StroageProtocolType.ProtocolTypeNvme.value,
                               DataType=win_nvme_command.StorageProtocolNVMeDataType.NVMeDataTypeLogPage.value,
                               ProtocolDataOffset=win_nvme_command.sizeof(win_nvme_command.StorageProtocolSpecificData),
                               ProtocolDataLength=data_length,
                               lid=0xC1)


class LatencyMonitor(NVMeCommand):
    if os_type == "Linux":
        _req_id = linux_nvme_command.IOCTLRequest.NVME_IOCTL_ADMIN_CMD.value
    elif os_type == "Windows":
        _req_id = win_nvme_command.IOCTLRequest.IOCTL_STORAGE_QUERY_PROPERTY.value
    def __init__(self, uuid_index=0, data_buffer=None):
        data_length = 512
        lid = 0xC3
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
            self.build_command(PropertyId=win_nvme_command.StoragePropertyID.StorageDeviceProtocolSpecificProperty.value,
                               QueryType=win_nvme_command.StorageQueryType.PropertyStandardQuery.value,
                               ProtocolType=win_nvme_command.StroageProtocolType.ProtocolTypeNvme.value,
                               DataType=win_nvme_command.StorageProtocolNVMeDataType.NVMeDataTypeLogPage.value,
                               ProtocolDataOffset=win_nvme_command.sizeof(win_nvme_command.StorageProtocolSpecificData),
                               ProtocolDataLength=data_length,
                               lid=lid)


class DeviceCapabilities(NVMeCommand):
    if os_type == "Linux":
        _req_id = linux_nvme_command.IOCTLRequest.NVME_IOCTL_ADMIN_CMD.value
    elif os_type == "Windows":
        _req_id = win_nvme_command.IOCTLRequest.IOCTL_STORAGE_QUERY_PROPERTY.value
    def __init__(self, uuid_index=0, data_buffer=None):
        data_length = 4096
        lid = 0xC4
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
            self.build_command(PropertyId=win_nvme_command.StoragePropertyID.StorageDeviceProtocolSpecificProperty.value,
                               QueryType=win_nvme_command.StorageQueryType.PropertyStandardQuery.value,
                               ProtocolType=win_nvme_command.StroageProtocolType.ProtocolTypeNvme.value,
                               DataType=win_nvme_command.StorageProtocolNVMeDataType.NVMeDataTypeLogPage.value,
                               ProtocolDataOffset=win_nvme_command.sizeof(win_nvme_command.StorageProtocolSpecificData),
                               ProtocolDataLength=data_length,
                               lid=lid)


class UnsupportedRequirements(NVMeCommand):
    if os_type == "Linux":
        _req_id = linux_nvme_command.IOCTLRequest.NVME_IOCTL_ADMIN_CMD.value
    elif os_type == "Windows":
        _req_id = win_nvme_command.IOCTLRequest.IOCTL_STORAGE_QUERY_PROPERTY.value
    def __init__(self, uuid_index=0, data_buffer=None):
        data_length = 4096
        lid = 0xC5
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
            self.build_command(PropertyId=win_nvme_command.StoragePropertyID.StorageDeviceProtocolSpecificProperty.value,
                               QueryType=win_nvme_command.StorageQueryType.PropertyStandardQuery.value,
                               ProtocolType=win_nvme_command.StroageProtocolType.ProtocolTypeNvme.value,
                               DataType=win_nvme_command.StorageProtocolNVMeDataType.NVMeDataTypeLogPage.value,
                               ProtocolDataOffset=win_nvme_command.sizeof(win_nvme_command.StorageProtocolSpecificData),
                               ProtocolDataLength=data_length,
                               lid=lid)


class HardwareComponent(NVMeCommand):
    if os_type == "Linux":
        _req_id = linux_nvme_command.IOCTLRequest.NVME_IOCTL_ADMIN_CMD.value
    elif os_type == "Windows":
        _req_id = win_nvme_command.IOCTLRequest.IOCTL_STORAGE_QUERY_PROPERTY.value
    def __init__(self, data_length, uuid_index=0, data_buffer=None):
        lid = 0xC6
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
            self.build_command(PropertyId=win_nvme_command.StoragePropertyID.StorageDeviceProtocolSpecificProperty.value,
                               QueryType=win_nvme_command.StorageQueryType.PropertyStandardQuery.value,
                               ProtocolType=win_nvme_command.StroageProtocolType.ProtocolTypeNvme.value,
                               DataType=win_nvme_command.StorageProtocolNVMeDataType.NVMeDataTypeLogPage.value,
                               ProtocolDataOffset=win_nvme_command.sizeof(win_nvme_command.StorageProtocolSpecificData),
                               ProtocolDataLength=data_length,
                               lid=lid)


class TCGConfiguration(NVMeCommand):
    if os_type == "Linux":
        _req_id = linux_nvme_command.IOCTLRequest.NVME_IOCTL_ADMIN_CMD.value
    elif os_type == "Windows":
        _req_id = win_nvme_command.IOCTLRequest.IOCTL_STORAGE_QUERY_PROPERTY.value
    def __init__(self, uuid_index=0, data_buffer=None):
        data_length = 512
        lid = 0xC7
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
            self.build_command(PropertyId=win_nvme_command.StoragePropertyID.StorageDeviceProtocolSpecificProperty.value,
                               QueryType=win_nvme_command.StorageQueryType.PropertyStandardQuery.value,
                               ProtocolType=win_nvme_command.StroageProtocolType.ProtocolTypeNvme.value,
                               DataType=win_nvme_command.StorageProtocolNVMeDataType.NVMeDataTypeLogPage.value,
                               ProtocolDataOffset=win_nvme_command.sizeof(win_nvme_command.StorageProtocolSpecificData),
                               ProtocolDataLength=data_length,
                               lid=lid)


class TelemetryStringLog(NVMeCommand):
    if os_type == "Linux":
        _req_id = linux_nvme_command.IOCTLRequest.NVME_IOCTL_ADMIN_CMD.value
    elif os_type == "Windows":
        _req_id = win_nvme_command.IOCTLRequest.IOCTL_STORAGE_QUERY_PROPERTY.value
    def __init__(self, data_length, uuid_index=0, data_buffer=None):
        lid = 0xC9
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
            self.build_command(PropertyId=win_nvme_command.StoragePropertyID.StorageDeviceProtocolSpecificProperty.value,
                               QueryType=win_nvme_command.StorageQueryType.PropertyStandardQuery.value,
                               ProtocolType=win_nvme_command.StroageProtocolType.ProtocolTypeNvme.value,
                               DataType=win_nvme_command.StorageProtocolNVMeDataType.NVMeDataTypeLogPage.value,
                               ProtocolDataOffset=win_nvme_command.sizeof(win_nvme_command.StorageProtocolSpecificData),
                               ProtocolDataLength=data_length,
                               lid=lid)
