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
class OCPFeatureIdentifier(Enum):
    Error_Injection = 0xC0
    #DEVICE_ERROR_RECOVERY = 0xC1
    EOL_PLP_Failure_Mode = 0xC2
    Clear_PCIe_CE_Counter = 0xC3
    Enable_IEEE1667_Silo = 0xC4
    Latency_Monitor = 0xC5
    PLP_Health_Check_Interval = 0xC6
    DSSD_PS = 0xC7
    Telemetry_Profile = 0xC8
    DSSD_Async_Event_Cfg = 0xC9

##### For windows vendor spec log page
# Callers could use a STORAGE_PROPERTY_ID of StorageAdapterProtocolSpecificProperty, and whose 
# STORAGE_PROTOCOL_SPECIFIC_DATA or STORAGE_PROTOCOL_SPECIFIC_DATA_EXT structure is set to 
# ProtocolDataRequestValue=VENDOR_SPECIFIC_LOG_PAGE_IDENTIFIER to request 512 byte chunks of vendor specific data.
##### For windows vendor spec log page
class GetErrorInjection(NVMeCommand):
    _support_ocp_ver = ("2.0", "2.5")
    if os_type == "Linux":
        _req_id = linux_nvme_command.IOCTLRequest.NVME_IOCTL_ADMIN_CMD.value
    elif os_type == "Windows":
        _req_id = win_nvme_command.IOCTLRequest.IOCTL_STORAGE_QUERY_PROPERTY.value
    def __init__(self, sel, uuid_index=0, timeout=admin_timeout_ms):
        data_length = 4096
        cdw10 = build_int_by_bitmap({"fid": (0xFF, 0, OCPFeatureIdentifier.Error_Injection.value),      # log id
                                    "SEL": (0x07, 1, sel),
                                    })
        cdw14 = build_int_by_bitmap({"UUID Index": (0x7F, 0, uuid_index),      # log id
                                    })
    ### build command 
        super(GetErrorInjection, self).__init__()
        if os_type == "Linux":
            ## init data buffer
            data_buffer = self.init_data_buffer(data_length=data_length)
            self.build_command(opcode=CmdOPCode,
                               nsid=0,
                               addr=data_buffer.addr,
                               data_len=data_buffer.data_length,
                               cdw10=cdw10,
                               cdw14=cdw14,
                               timeout_ms=timeout)
        elif os_type == "Windows":
            self.build_command(PropertyId=win_nvme_command.StoragePropertyID.StorageDeviceProtocolSpecificProperty.value,
                               QueryType=win_nvme_command.StorageQueryType.PropertyStandardQuery.value,
                               ProtocolType=win_nvme_command.StroageProtocolType.ProtocolTypeNvme.value,
                               DataType=win_nvme_command.StorageProtocolNVMeDataType.NVMeDataTypeFeature.value,
                               ProtocolDataLength=data_length,
                               ProtocolDataRequestValue=cdw10,
                               ProtocolDataRequestSubValue3=cdw14,
                              )

