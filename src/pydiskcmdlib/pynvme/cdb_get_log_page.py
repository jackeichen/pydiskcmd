# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from enum import Enum
from pydiskcmdlib import os_type
from pydiskcmdlib.pynvme.nvme_command import NVMeCommand,AdminCommandOpcode,CommandTimeout,build_int_by_bitmap
from pydiskcmdlib.pynvme import linux_nvme_command,win_nvme_command
#####
CmdOPCode = AdminCommandOpcode.GetLogPage.value
#####

class LogIdentifier(Enum):
    ErrorInformation                 = 0x01
    SMARTHealthInformation           = 0x02
    FirmwareSlotInformation          = 0x03
    ChangedNamespaceList             = 0x04
    CommandsSupportedAndEffects      = 0x05
    DeviceSelftest                   = 0x06
    TelemetryHostInitiated           = 0x07
    TelemetryControllerInitiated     = 0x08
    EnduranceGroupInformation        = 0X09
    PredictableLatencyPerNVMSet      = 0X0A
    PredictableLatencyEventAggregate = 0X0B
    AsymmetricNamespaceAccess        = 0x0C
    PersistentEventLog               = 0x0D
    LBAStatusInformation             = 0x0E
    EnduranceGroupEventAggregate     = 0x0F
    MICommandsSupportedAndEffects    = 0x13
    Discovery                        = 0x70   # refer to the NVMe over Fabrics specification
    ReservationNotification          = 0x80
    SanitizeStatus                   = 0x81
#####

class GetLogPage(NVMeCommand):
    if os_type == "Linux":
        _req_id = linux_nvme_command.IOCTLRequest.NVME_IOCTL_ADMIN_CMD.value
        _cdb_bits = {"opcode": [0xFF, 0],
                     "flags": [0xFF, 1],
                     "rsvd1": [0xFFFF, 2],
                     "nsid":[0xFFFFFFFF, 4],
                     "cdw2":[0xFFFFFFFF, 8],
                     "cdw3":[0xFFFFFFFF, 12],
                     "metadata":[0xFFFFFFFFFFFFFFFF, 16],
                     "addr":[0xFFFFFFFFFFFFFFFF, 24],
                     "metadata_len":[0xFFFFFFFF, 32],
                     "data_len":[0xFFFFFFFF, 36],
                     #"cdw10":[0xFFFFFFFF, 40],
                     "lid": [0xFF, 40],
                     "lsp": [0x7F, 41],
                     "rae": [0x80, 41],
                     "numdl": [0xFFFF, 42],
                     #"cdw11":[0xFFFFFFFF, 44],
                     "numdu": [0xFFFF, 44],
                     "lsi": [0xFFFF, 46],
                     #"cdw12":[0xFFFFFFFF, 48],
                     "lpol": [0xFFFFFFFF, 48],
                     #"cdw13":[0xFFFFFFFF, 52],
                     "lpou": [0xFFFFFFFF, 52],
                     #"cdw14":[0xFFFFFFFF, 56],
                     "uuid": [0x7F, 56],
                     "ot": [0x80, 58],
                     "csi": [0xFF, 59],
                     "cdw15":[0xFFFFFFFF, 60],
                     "timeout_ms":[0xFFFFFFFF, 64],
                     "result":[0xFFFFFFFF, 68],
                     }
    elif os_type == "Windows":
        _req_id = win_nvme_command.IOCTLRequest.IOCTL_STORAGE_QUERY_PROPERTY.value
        _cdb_bits = {"PropertyId": [0xFFFFFFFF, 0],
                     "QueryType": [0xFFFFFFFF, 4],
                     "ProtocolType": [0xFFFFFFFF, 8],
                     "DataType": [0xFFFFFFFF, 12],
                     # "ProtocolDataRequestValue": [0xFFFFFFFF, 16],
                     "lid":  [0xFFFFFFFF, 16],  # ProtocolDataRequestValue Field
                     # "ProtocolDataRequestSubValue": [0xFFFFFFFF, 20],
                     "lpol": [0xFFFFFFFF, 20], # ProtocolDataRequestSubValue, this will be passed as the lower 32 bit of log page offset if controller supports extended data for the Get Log Page.
                     "ProtocolDataOffset": [0xFFFFFFFF, 24],
                     "ProtocolDataLength": [0xFFFFFFFF, 28],
                     "FixedProtocolReturnData": [0xFFFFFFFF, 32],
                     # "ProtocolDataRequestSubValue2": [0xFFFFFFFF, 36],
                     "lpou": [0xFFFFFFFF, 36], # ProtocolDataRequestSubValue2, this will be passed as the higher 32 bit of log page offset if controller supports extended data for the Get Log Page.
                     # "ProtocolDataRequestSubValue3": [0xFFFFFFFF, 40],
                     "lsi": [0xFFFFFFFF, 40], # ProtocolDataRequestSubValue3, this will be passed as Log Specific Identifier in CDW11.
                     # "ProtocolDataRequestSubValue4": [0xFFFFFFFF, 44],
                     "rae": [0x01, 44], # ProtocolDataRequestSubValue4, this will map to STORAGE_PROTOCOL_DATA_SUBVALUE_GET_LOG_PAGE definition, then user can pass Retain Asynchronous Event, Log Specific Field.
                     "lsp": [0x1E, 44], # ProtocolDataRequestSubValue4, this will map to STORAGE_PROTOCOL_DATA_SUBVALUE_GET_LOG_PAGE definition, then user can pass Retain Asynchronous Event, Log Specific Field.
                     "Reserved": [0xFFFFFFE0, 44], # ProtocolDataRequestSubValue4, this will map to STORAGE_PROTOCOL_DATA_SUBVALUE_GET_LOG_PAGE definition, then user can pass Retain Asynchronous Event, Log Specific Field.
                    }

    def __init__(self,
                 nsid,    # Namespace ID
                 lid,     # CDW10: Log Page Identifier
                 lsp,     # CDW10: Log Specific Parameter
                 rae,     # CDW10: Retain Asynchronous Event
                 numdl,   # CDW10: Number of Dwords Lower
                 numdu,   # CDW11: Number of Dwords
                 lsi,     # CDW11: Log Specific Identifier
                 lpol,    # CDW12: Log Page Offset Lower
                 lpou,    # CDW13: Log Page Offset Upper
                 uuid,    # CDW14: UUID Index
                 ot,      # CDW14: Offset Type
                 csi,     # CDW14: Command Set Identifier 
                 data_length=None,
                 data_buffer=None,
                 timeout=CommandTimeout.admin.value,
                 ):
        '''
        Some ways to set Data buffer, the priority is:
        1. Set the data_buffer/metadata_buffer, DataBuffer of the target data;
        2. If set the data_out/metadata_out, data_length/metadata_length is need;
        3. Set the data_length/metadata_length, then a 0 based buffer is created
        '''
        super(GetLogPage, self).__init__()
        if data_length is None:
            data_length = (numdl + (numdu << 16) + 1) * 4
        if os_type == "Linux":
            ## init data buffer
            data_buffer = self.init_data_buffer(data_length=data_length, data_buffer=data_buffer)
            ##
            self.build_command(opcode=CmdOPCode,
                               nsid=nsid,
                               addr=data_buffer.addr,
                               data_len=data_buffer.data_length,
                               lid=lid,
                               lsp=lsp,
                               rae=rae,
                               numdl=numdl,
                               numdu=numdu,
                               lsi=lsi,
                               lpol=lpol,
                               lpou=lpou,
                               uuid=uuid,
                               ot=ot,
                               csi=csi,
                               data_buffer=data_buffer,
                               timeout_ms=timeout)
        elif os_type == "Windows":
            self.build_command(PropertyId=win_nvme_command.StoragePropertyID.StorageDeviceProtocolSpecificProperty.value,
                               QueryType=win_nvme_command.StorageQueryType.PropertyStandardQuery.value,
                               ProtocolType=win_nvme_command.StroageProtocolType.ProtocolTypeNvme.value,
                               DataType=win_nvme_command.StorageProtocolNVMeDataType.NVMeDataTypeLogPage.value,
                               ProtocolDataOffset=win_nvme_command.sizeof(win_nvme_command.StorageProtocolSpecificData),
                               ProtocolDataLength=data_length,
                               lid=lid,
                               lpol=lpol,
                               lpou=lpou,
                               lsi=lsi,
                               rae=rae,
                               lsp=lsp)


class ErrorLog(GetLogPage):
    def __init__(self,
                 max_entry,   # the max number log entries
                 nsid=0,
                 numdl=None,   # CDW10: Number of Dwords Lower
                 numdu=0,
                 lpol=0,      # CDW12: Log Page Offset Lower
                 lpou=0,      # CDW12: Log Page Offset Lower
                 ):
        if numdl is None:
            ## get the max number log entries
            numd = max_entry * 16 - 1    # 16 = 64 / 4, 0 based value
            ## Identify controller Byte 262, so the numbet_dw <= 256*16= 4096,
            #  so 0xFFFF is enough for numd
            numdl = numd & 0xFFFF
            numdu = (numd >> 16) & 0xFFFF
        ## init command
        GetLogPage.__init__(self,
                            nsid,       # Namespace ID
                            LogIdentifier.ErrorInformation.value,    # CDW10: Log Page Identifier
                            0,       # CDW10: Log Specific Parameter
                            0,       # CDW10: Retain Asynchronous Event
                            numdl,   # CDW10: Number of Dwords Lower
                            numdu,   # CDW11: Number of Dwords
                            0,       # CDW11: Log Specific Identifier
                            lpol,    # CDW12: Log Page Offset Lower
                            lpou,    # CDW13: Log Page Offset Upper
                            0,       # CDW14: UUID Index
                            0,       # CDW14: Offset Type
                            0,       # CDW14: Command Set Identifier 
                            )


class SmartLog(GetLogPage):
    def __init__(self,
                 rae=0,       # CDW10: Retain Asynchronous Event (RAE)
                 numdl=127,   # CDW10: Number of Dwords Lower
                 lpol=0,      # CDW12: Log Page Offset Lower
                 ):
        ## init command
        GetLogPage.__init__(self,
                            0,       # Namespace ID
                            LogIdentifier.SMARTHealthInformation.value,    # CDW10: Log Page Identifier
                            0,       # CDW10: Log Specific Parameter
                            rae,     # CDW10: Retain Asynchronous Event
                            numdl,   # CDW10: Number of Dwords Lower
                            0,       # CDW11: Number of Dwords
                            0,       # CDW11: Log Specific Identifier
                            lpol,    # CDW12: Log Page Offset Lower
                            0,       # CDW13: Log Page Offset Upper
                            0,       # CDW14: UUID Index
                            0,       # CDW14: Offset Type
                            0,       # CDW14: Command Set Identifier 
                            )


class FWSlotInfo(GetLogPage):
    def __init__(self,
                 numdl=127,   # CDW10: Number of Dwords Lower
                 lpol=0,      # CDW12: Log Page Offset Lower
                 ):
        ## init command
        GetLogPage.__init__(self,
                            0,       # Namespace ID
                            LogIdentifier.FirmwareSlotInformation.value,    # CDW10: Log Page Identifier
                            0,       # CDW10: Log Specific Parameter
                            0,       # CDW10: Retain Asynchronous Event
                            numdl,   # CDW10: Number of Dwords Lower
                            0,       # CDW11: Number of Dwords
                            0,       # CDW11: Log Specific Identifier
                            lpol,    # CDW12: Log Page Offset Lower
                            0,       # CDW13: Log Page Offset Upper
                            0,       # CDW14: UUID Index
                            0,       # CDW14: Offset Type
                            0,       # CDW14: Command Set Identifier 
                            )


class ChangedNamespaceList(GetLogPage):
    def __init__(self,
                 rae=0,       # CDW10: Retain Asynchronous Event (RAE)
                 numdl=1023,  # CDW10: Number of Dwords Lower
                 lpol=0,      # CDW12: Log Page Offset Lower
                 ):
        ## init command
        GetLogPage.__init__(self,
                            0,       # Namespace ID
                            LogIdentifier.ChangedNamespaceList.value,    # CDW10: Log Page Identifier
                            0,       # CDW10: Log Specific Parameter
                            rae,     # CDW10: Retain Asynchronous Event
                            numdl,   # CDW10: Number of Dwords Lower
                            0,       # CDW11: Number of Dwords
                            0,       # CDW11: Log Specific Identifier
                            lpol,    # CDW12: Log Page Offset Lower
                            0,       # CDW13: Log Page Offset Upper
                            0,       # CDW14: UUID Index
                            0,       # CDW14: Offset Type
                            0,       # CDW14: Command Set Identifier 
                            )


class CommandsSupportedAndEffectsLog(GetLogPage):
    def __init__(self,
                 numdl=1023,   # CDW10: Number of Dwords Lower
                 lpol=0,      # CDW12: Log Page Offset Lower
                 ):
        ## init command
        GetLogPage.__init__(self,
                            0,       # Namespace ID
                            LogIdentifier.CommandsSupportedAndEffects.value,    # CDW10: Log Page Identifier
                            0,       # CDW10: Log Specific Parameter
                            0,       # CDW10: Retain Asynchronous Event
                            numdl,   # CDW10: Number of Dwords Lower
                            0,       # CDW11: Number of Dwords
                            0,       # CDW11: Log Specific Identifier
                            lpol,    # CDW12: Log Page Offset Lower
                            0,       # CDW13: Log Page Offset Upper
                            0,       # CDW14: UUID Index
                            0,       # CDW14: Offset Type
                            0,       # CDW14: Command Set Identifier 
                            )


class SelfTestLog(GetLogPage):
    def __init__(self,
                 numdl=140,   # CDW10: Number of Dwords Lower
                 lpol=0,      # CDW12: Log Page Offset Lower
                 uuid=0,      # CDW14: UUID Index
                 ):
        ## init command
        GetLogPage.__init__(self,
                            0,       # Namespace ID
                            LogIdentifier.DeviceSelftest.value,    # CDW10: Log Page Identifier
                            0,       # CDW10: Log Specific Parameter
                            0,       # CDW10: Retain Asynchronous Event
                            numdl,   # CDW10: Number of Dwords Lower
                            0,       # CDW11: Number of Dwords
                            0,       # CDW11: Log Specific Identifier
                            lpol,    # CDW12: Log Page Offset Lower
                            0,       # CDW13: Log Page Offset Upper
                            uuid,    # CDW14: UUID Index
                            0,       # CDW14: Offset Type
                            0,       # CDW14: Command Set Identifier 
                            )


class TelemetryHostInitiatedLog(GetLogPage):
    def __init__(self,
                 create_telemetry,
                 numdl,       # CDW10: Number of Dwords Lower
                 numdu=0,     # CDW10: Number of Dwords Upper
                 lpol=0,      # CDW12: Log Page Offset Lower
                 lpou=0,      # CDW12: Log Page Offset Upper
                 uuid=0,      # CDW14: UUID Index
                 data_buffer=None
                 ):
        lsp = build_int_by_bitmap({"create_telemetry": [0x01, 0, create_telemetry]})
        ## init command
        GetLogPage.__init__(self,
                            0,       # Namespace ID
                            LogIdentifier.TelemetryHostInitiated.value,    # CDW10: Log Page Identifier
                            lsp,     # CDW10: Log Specific Field
                            0,       # CDW10: Retain Asynchronous Event
                            numdl,   # CDW10: Number of Dwords Lower
                            numdu,   # CDW11: Number of Dwords
                            0,       # CDW11: Log Specific Identifier
                            lpol,    # CDW12: Log Page Offset Lower
                            lpou,    # CDW13: Log Page Offset Upper
                            uuid,    # CDW14: UUID Index
                            0,       # CDW14: Offset Type
                            0,       # CDW14: Command Set Identifier 
                            data_buffer=data_buffer,
                            )


class TelemetryControllerInitiatedLog(GetLogPage):
    def __init__(self,
                 numdl,       # CDW10: Number of Dwords Lower
                 numdu=0,     # CDW10: Number of Dwords Upper
                 lpol=0,      # CDW12: Log Page Offset Lower
                 lpou=0,      # CDW12: Log Page Offset Upper
                 uuid=0,      # CDW14: UUID Index
                 data_buffer=None
                 ):
        ## init command
        GetLogPage.__init__(self,
                            0,       # Namespace ID
                            LogIdentifier.TelemetryControllerInitiated.value,    # CDW10: Log Page Identifier
                            0,       # CDW10: Log Specific Parameter
                            0,       # CDW10: Retain Asynchronous Event
                            numdl,   # CDW10: Number of Dwords Lower
                            numdu,   # CDW11: Number of Dwords
                            0,       # CDW11: Log Specific Identifier
                            lpol,    # CDW12: Log Page Offset Lower
                            lpou,       # CDW13: Log Page Offset Upper
                            uuid,    # CDW14: UUID Index
                            0,       # CDW14: Offset Type
                            0,       # CDW14: Command Set Identifier 
                            data_buffer=data_buffer,
                            )


class PersistentEventLog(GetLogPage):
    def __init__(self,
                 action,
                 numdl,       # CDW10: Number of Dwords Lower
                 numdu=0,     # CDW10: Number of Dwords Upper
                 lpol=0,      # CDW12: Log Page Offset Lower
                 lpou=0,      # CDW12: Log Page Offset Upper
                 uuid=0,      # CDW14: UUID Index
                 data_buffer=None
                 ):
        lsp = build_int_by_bitmap({"action": [0x03, 0, action]})
        ## init command
        GetLogPage.__init__(self,
                            0,       # Namespace ID
                            LogIdentifier.PersistentEventLog.value,    # CDW10: Log Page Identifier
                            lsp,     # CDW10: Log Specific Field
                            0,       # CDW10: Retain Asynchronous Event
                            numdl,   # CDW10: Number of Dwords Lower
                            numdu,   # CDW11: Number of Dwords
                            0,       # CDW11: Log Specific Identifier
                            lpol,    # CDW12: Log Page Offset Lower
                            lpou,    # CDW13: Log Page Offset Upper
                            uuid,    # CDW14: UUID Index
                            0,       # CDW14: Offset Type
                            0,       # CDW14: Command Set Identifier 
                            data_buffer=data_buffer,
                            )


class MICommandsSupportedAndEffectsLog(GetLogPage):
    def __init__(self,
                 numdl=1023,  # CDW10: Number of Dwords Lower
                 lpol=0,      # CDW12: Log Page Offset Lower
                 ):
        ## init command
        GetLogPage.__init__(self,
                            0,       # Namespace ID
                            LogIdentifier.MICommandsSupportedAndEffects.value,    # CDW10: Log Page Identifier
                            0,       # CDW10: Log Specific Parameter
                            0,       # CDW10: Retain Asynchronous Event
                            numdl,   # CDW10: Number of Dwords Lower
                            0,       # CDW11: Number of Dwords
                            0,       # CDW11: Log Specific Identifier
                            lpol,    # CDW12: Log Page Offset Lower
                            0,       # CDW13: Log Page Offset Upper
                            0,       # CDW14: UUID Index
                            0,       # CDW14: Offset Type
                            0,       # CDW14: Command Set Identifier 
                            )


class SanitizeStatus(GetLogPage):
    def __init__(self,
                 numdl=127,   # CDW10: Number of Dwords Lower
                 lpol=0,      # CDW12: Log Page Offset Lower
                 ):
        ## init command
        GetLogPage.__init__(self,
                            0,       # Namespace ID
                            LogIdentifier.SanitizeStatus.value,    # CDW10: Log Page Identifier
                            0,       # CDW10: Log Specific Parameter
                            0,       # CDW10: Retain Asynchronous Event
                            numdl,   # CDW10: Number of Dwords Lower
                            0,       # CDW11: Number of Dwords
                            0,       # CDW11: Log Specific Identifier
                            lpol,    # CDW12: Log Page Offset Lower
                            0,       # CDW13: Log Page Offset Upper
                            0,    # CDW14: UUID Index
                            0,       # CDW14: Offset Type
                            0,       # CDW14: Command Set Identifier 
                            )
