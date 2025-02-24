# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from .cdb_rst_nvme_passthr import RSTNVMePass
from pydiskcmdlib.pynvme.cdb_get_log_page import CmdOPCode,LogIdentifier
from pydiskcmdlib.pynvme.nvme_command import build_int_by_bitmap

class GetLogPage(RSTNVMePass):
    """
    Initialize the GetLogPage class.

    :param path_id: The path ID for the device.
    :param nsid: The namespace ID.
    :param lid: The log page identifier.
    :param lsp: The log specific parameter.
    :param rae: The retain asynchronous event flag.
    :param numdl: The number of dwords lower.
    :param numdu: The number of dwords upper.
    :param lsi: The log specific identifier.
    :param lpol: The log page offset lower.
    :param lpou: The log page offset upper.
    :param uuid: The UUID index.
    :param ot: The offset type.
    :param csi: The command set identifier.
    :param data_length: The length of the data.
    """
    def __init__(self,
                 path_id,
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
                ):
        if data_length is None:
            data_length = (numdl + (numdu << 16) + 1) * 4
        # build cdw
        cdw10 = build_int_by_bitmap({"lid": (0xFF, 0, lid),
                                     "lsp": (0x7F, 1, lsp),
                                     "rae": (0x80, 1, rae),
                                     "numdl": (0xFFFF, 2, numdl),
                                     }) 
        cdw11 = build_int_by_bitmap({"numdu": (0xFFFF, 0, numdu),
                                     "lsi": (0xFFFF, 2, lsi),
                                     })
        cdw12 = build_int_by_bitmap({"lpol": (0xFFFFFFFF, 0, lpol)})
        cdw13 = build_int_by_bitmap({"lpou": (0xFFFFFFFF, 0, lpou)})
        cdw14 = build_int_by_bitmap({"uuid": (0x7F, 0, uuid),
                                     "ot": (0x80, 2, ot),
                                     "csi": (0xFF, 3, csi),
                                     })

        RSTNVMePass.__init__(self,
                             path_id,
                             0,        # 0 for admincommand, 1 for iocommand
                             CmdOPCode,
                             nsid,
                             cdw10,
                             cdw11,
                             cdw12,
                             cdw13,
                             cdw14,
                             0,       # CDW15
                             data_length,
                             0,       # metadata_buffer_len
                             )


class ErrorLog(GetLogPage):
    def __init__(self,
                 path_id,
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
                            path_id,
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
                 path_id, 
                 nsid=0,
                 rae=0,       # CDW10: Retain Asynchronous Event (RAE)
                 numdl=127,   # CDW10: Number of Dwords Lower
                 lpol=0,      # CDW12: Log Page Offset Lower
                 ):
        GetLogPage.__init__(self,
                            path_id,
                            nsid,    # nsid
                            LogIdentifier.SMARTHealthInformation.value,  # CDW10: Log Page Identifier
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
                 path_id,
                 numdl=127,   # CDW10: Number of Dwords Lower
                 lpol=0,      # CDW12: Log Page Offset Lower
                 ):
        ## init command
        GetLogPage.__init__(self,
                            path_id,
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
                 path_id,
                 rae=0,       # CDW10: Retain Asynchronous Event (RAE)
                 numdl=1023,  # CDW10: Number of Dwords Lower
                 lpol=0,      # CDW12: Log Page Offset Lower
                 ):
        ## init command
        GetLogPage.__init__(self,
                            path_id,
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
                 path_id,
                 numdl=1023,   # CDW10: Number of Dwords Lower
                 lpol=0,      # CDW12: Log Page Offset Lower
                 ):
        ## init command
        GetLogPage.__init__(self,
                            path_id,
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
                 path_id,
                 numdl=140,   # CDW10: Number of Dwords Lower
                 lpol=0,      # CDW12: Log Page Offset Lower
                 uuid=0,      # CDW14: UUID Index
                 ):
        ## init command
        GetLogPage.__init__(self,
                            path_id,
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
                 path_id,
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
                            path_id,
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
                 path_id,
                 numdl,       # CDW10: Number of Dwords Lower
                 numdu=0,     # CDW10: Number of Dwords Upper
                 lpol=0,      # CDW12: Log Page Offset Lower
                 lpou=0,      # CDW12: Log Page Offset Upper
                 uuid=0,      # CDW14: UUID Index
                 data_buffer=None
                 ):
        ## init command
        GetLogPage.__init__(self,
                            path_id,
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
                 path_id,
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
                            path_id,
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


class SanitizeStatus(GetLogPage):
    def __init__(self,
                 path_id,
                 numdl=127,   # CDW10: Number of Dwords Lower
                 lpol=0,      # CDW12: Log Page Offset Lower
                 ):
        ## init command
        GetLogPage.__init__(self,
                            path_id,
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
