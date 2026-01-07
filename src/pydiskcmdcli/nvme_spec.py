# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later

from pydiskcmdlib.utils.converter import decode_bits,scsi_ba_to_int

nvme_smart_bit_mask = {"Critical Warning": ('b', 0, 1),
                       "Composite Temperature": ('b', 1, 2),
                       "Available Spare": ('b', 3, 1),
                       "Available Spare Threshold": ('b', 4, 1),
                       "Percentage Used": ('b', 5, 1),
                       "Endurance Group Critical Warning Summary": ('b', 6, 1),
                       "Data Units Read": ('b', 32, 16),
                       "Data Units Written": ('b', 48, 16),
                       "Host Read Commands": ('b', 64, 16),
                       "Host Write Commands": ('b', 80, 16),
                       "Controller Busy Time": ('b', 96, 16),
                       "Power Cycles": ('b', 112, 16),
                       "Power On Hours": ('b', 128, 16),
                       "Unsafe Shutdowns": ('b', 144, 16),
                       "Media and Data Integrity Errors": ('b', 160, 16),
                       "Number of Error Information Log Entries": ('b', 176, 16),
                       "Warning Composite Temperature Time": ('b', 192, 4),
                       "Critical Composite Temperature Time": ('b', 196, 4),
                       "Temperature Sensor 1": ('b', 200, 2),
                       "Temperature Sensor 2": ('b', 202, 2),
                       "Temperature Sensor 3": ('b', 204, 2),
                       "Temperature Sensor 4": ('b', 206, 2),
                       "Temperature Sensor 5": ('b', 208, 2),
                       "Temperature Sensor 6": ('b', 210, 2),
                       "Temperature Sensor 7": ('b', 212, 2),
                       "Temperature Sensor 8": ('b', 214, 2),
                       "Thermal Management T1 Transition Count": ('b', 216, 4),
                       "Thermal Management T2 Transition Count": ('b', 220, 4),
                       "Total Time For Thermal Management T1": ('b', 224, 4),
                       "Total Time For Thermal Management T2": ('b', 228, 4),
                       }


nvme_id_ctrl_bit_mask = {"VID": ('b', 0, 2),
                         "SSVID": ('b', 2, 2),
                         "SN": ('b', 4, 20),
                         "MN": ('b', 24, 40),
                         "FR": ('b', 64, 8),
                         "RAB": ('b', 72, 1),
                         "IEEE": ('b', 73, 3),
                         "CMIC": ('b', 76, 1),
                         "MDTS": ('b', 77, 1),
                         "CNTLID": ('b', 78, 2),
                         "VER": ('b', 80, 4),
                         "RTD3R": ('b', 84, 4),
                         "RTD3E": ('b', 88, 4),
                         "OAES": ('b', 92, 4),
                         "CTRATT": ('b', 96, 4),
                         "RRLS": ('b', 100, 2),
                         "CNTRLTYPE": ('b', 111, 1),
                         "FGUID": ('b', 112, 16),
                         "CRDT1": ('b', 128, 2),
                         "CRDT2": ('b', 130, 2),
                         "CRDT3": ('b', 132, 2),
                         "NVMSR": ('b', 253, 1),          ## NVM Subsystem Report, nvme spec 2.0
                         "VMCI": ('b', 254, 1),           ## VPD Write Cycle Information, nvme spec 2.0
                         "MEC": ('b', 255, 1),            ## Management Endpoint Capabilities, nvme spec 2.0
                         "OACS": ('b', 256, 2),           ## Optional Admin Command Support
                         "ACL": ('b', 258, 1),            ## Abort Command Limit
                         "AERL": ('b', 259, 1),           ## Asynchronous Event Request Limit
                         "FRMW": ('b', 260, 1),           ## Firmware Updates
                         "LPA": ('b', 261, 1),            ## Log Page Attributes
                         "ELPE": ('b', 262, 1),           ## Error Log Page Entries
                         "NPSS": ('b', 263, 1),           ## Number of Power States Support
                         "AVSCC": ('b', 264, 1),          ## Admin Vendor Specific Command Configuration
                         "APSTA": ('b', 265, 1),          ## Autonomous Power State Transition Attributes
                         "WCTEMP": ('b', 266, 2),         ## Warning Composite Temperature Threshold
                         "CCTEMP": ('b', 268, 2),         ## Critical Composite Temperature Threshold
                         "MTFA": ('b', 270, 2),           ## Maximum Time for Firmware Activation
                         "HMPRE": ('b', 272, 4),          ## Host Memory Buffer Preferred Size
                         "HMMIN": ('b', 276, 4),          ## Host Memory Buffer Minimum Size
                         "TNVMCAP": ('b', 280, 16),       ## Total NVM Capacity
                         "UNVMCAP": ('b', 296, 16),       ## Unallocated NVM Capacity
                         "RPMBS": ('b', 312, 4),          ## Replay Protected Memory Block Support
                         "EDSTT": ('b', 316, 2),          ## Extended Device Self-test Time
                         "DSTO": ('b', 318, 1),           ## Device Self-test Options
                         "FWUG": ('b', 319, 1),           ## Firmware Update Granularity
                         "KAS": ('b', 320, 2),            ## Keep Alive Support
                         "HCTMA": ('b', 322, 2),          ## Host Controlled Thermal Management Attributes
                         "MNTMT": ('b', 324, 2),          ## Minimum Thermal Management Temperature
                         "MXTMT": ('b', 326, 2),          ## Maximum Thermal Management Temperature
                         "SANICAP": ('b', 328, 4),        ## Sanitize Capabilities
                         "HMMINDS": ('b', 332, 4),        ## Host Memory Buffer Minimum Descriptor Entry Size
                         "HMMAXD": ('b', 336, 2),         ## Host Memory Maximum Descriptors Entries
                         "NSETIDMAX": ('b', 338, 2),      ## NVM Set Identifier Maximum
                         "ENDGIDMAX": ('b', 340, 2),      ## Endurance Group Identifier Maximum
                         "ANATT": ('b', 342, 1),          ## ANA Transition Time
                         "ANACAP": ('b', 343, 1),         ## Asymmetric Namespace Access Capabilities
                         "ANAGRPMAX": ('b', 344, 4),      ## ANA Group Identifier Maximum
                         "NANAGRPID": ('b', 348, 4),      ## Number of ANA Group Identifiers
                         "PELS": ('b', 352, 4),           ## Persistent Event Log Size
                         "SQES": ('b', 512, 1),           ## Submission Queue Entry Size
                         "CQES": ('b', 513, 1),           ## Completion Queue Entry Size
                         "MAXCMD": ('b', 514, 2),         ## Maximum Outstanding Commands
                         "NN": ('b', 516, 4),             ## Number of Namespaces
                         "ONCS": ('b', 520, 2),           ## Optional NVM Command Support
                         "FUSES": ('b', 522, 2),          ## Fused Operation Support
                         "FNA": ('b', 524, 1),            ## Format NVM Attributes
                         "VWC": ('b', 525, 1),            ## Volatile Write Cache
                         "AWUN": ('b', 526, 2),           ## Atomic Write Unit Normal
                         "AWUPF": ('b', 528, 2),          ## Atomic Write Unit Power Fail
                         "NVSCC": ('b', 530, 1),          ## NVM Vendor Specific Command Configuration
                         "NWPC": ('b', 531, 1),           ## Namespace Write Protection Capabilities
                         "ACWU": ('b', 532, 2),           ## Atomic Compare & Write Unit
                         "SGLS": ('b', 536, 4),           ## SGL Support
                         "MNAN": ('b', 540, 4),           ## Maximum Number of Allowed Namespaces
                         "SUBNQN": ('b', 768, 256),       ## NVM Subsystem NVMe Qualified Name
                       }

nvme_id_ctrl_ps_bit_mask = {"MP": ('b', 0, 2),            ## Maximum Power
                            "MXPS": [0x01, 3],            ## Max Power Scale
                            "NOPS": [0x02, 3],            ## Non-Operational State
                            "ENLAT": ('b', 4, 4),         ## Entry Latency
                            "EXLAT": ('b', 8, 4),         ## Exit Latency
                            "RRT": [0x1F, 12],            ## Relative Read Throughput
                            "RRL": [0x1F, 13],            ## Relative Read Latency
                            "RWT": [0x1F, 14],            ## Relative Write Throughput
                            "RWL": [0x1F, 15],            ## Relative Write Latency
                            "IDLP": ('b', 16, 2),         ## Idle Power
                            "IPS": [0xC0, 18],            ## Idle Power Scale
                            "ACTP": ('b', 20, 2),         ## Active Power
                            "APW": [0x07, 22],            ## Active Power Workload
                            "APS": [0xC0, 22],            ## Active Power Scale
                           }


nvme_id_ns_bit_mask = {"NSZE": ('b', 0, 8),               ## Namespace Size
                       "NCAP": ('b', 8, 8),               ## Namespace Capacity
                       "NUSE": ('b', 16, 8),              ## Namespace Utilization
                       "NSFEAT": ('b', 24, 1),            ## Namespace Features
                       "NLBAF": ('b', 25, 1),             ## Number of LBA Formats
                       "FLBAS": ('b', 26, 1),             ## Formatted LBA Size
                       "MC": ('b', 27, 1),                ## Metadata Capabilities
                       "DPC": ('b', 28, 1),               ## End-to-end Data Protection Capabilities
                       "DPS": ('b', 29, 1),               ## End-to-end Data Protection Type Settings
                       "NMIC": ('b', 30, 1),              ## Namespace Multi-path I/O and Namespace Sharing Capabilities
                       "RESCAP": ('b', 31, 1),            ## Reservation Capabilities
                       "FPI": ('b', 32, 1),               ## Format Progress Indicator
                       "DLFEAT": ('b', 33, 1),            ## Deallocate Logical Block Features
                       "NAWUN": ('b', 34, 2),             ## Namespace Atomic Write Unit Normal
                       "NAWUPF": ('b', 36, 2),            ## Namespace Atomic Write Unit Power Fail
                       "NACWU": ('b', 38, 2),             ## Namespace Atomic Compare & Write Unit
                       "NABSN": ('b', 40, 2),             ## Namespace Atomic Boundary Size Normal
                       "NABO": ('b', 42, 2),              ## Namespace Atomic Boundary Offset
                       "NABSPF": ('b', 44, 2),            ## Namespace Atomic Boundary Size Power Fail
                       "NOIOB": ('b', 46, 2),             ## Namespace Optimal I/O Boundary 
                       "NVMCAP": ('b', 48, 16),           ## NVM Capacity
                       "NPWG": ('b', 64, 2),              ## Namespace Preferred Write Granularity 
                       "NPWA": ('b', 66, 2),              ## Namespace Preferred Write Alignment
                       "NPDG": ('b', 68, 2),              ## Namespace Preferred Deallocate Granularity
                       "NPDA": ('b', 70, 2),              ## Namespace Preferred Deallocate Alignment
                       "NOWS": ('b', 72, 2),              ## Namespace Optimal Write Size
                       "ANAGRPID": ('b', 92, 4),          ## ANA Group Identifier
                       "NSATTR": ('b', 99, 1),            ## Namespace Size
                       "NVMSETID": ('b', 100, 2),         ## NVM Set Identifier
                       "ENDGID": ('b', 102, 2),           ## Endurance Group Identifier
                       "NGUID": ('b', 104, 16),           ## Namespace Globally Unique Identifier
                       "EUI64": ('b', 120, 8),            ## Number of LBA Formats
                      }


nvme_id_ns_lbaf_bit_mask = {"MS": ('b', 0, 2),            ## Metadata Size
                            "LBADS": ('b', 2, 1),         ## LBA Data Size
                            "RP": [0x03, 3],              ## Relative Performance
                           }

nvme_fw_slot_info_bit_mask  = {"AFI": ('b', 0, 1),      ## Active Firmware Info
                               "FRS1": ('b', 8, 8),     ## Firmware Revision for Slot 1
                               "FRS2": ('b', 16, 8),    ## Firmware Revision for Slot 2
                               "FRS3": ('b', 24, 8),    ## Firmware Revision for Slot 3
                               "FRS4": ('b', 32, 8),    ## Firmware Revision for Slot 4
                               "FRS5": ('b', 40, 8),    ## Firmware Revision for Slot 5
                               "FRS6": ('b', 48, 8),    ## Firmware Revision for Slot 6
                               "FRS7": ('b', 56, 8),    ## Firmware Revision for Slot 7
                              }

nvme_sanitize_log_bit_mask  = {"SPROG": ('b', 0, 2),             ## Sanitize Progress (SPROG)
                               "SSTAT": ('b', 2, 2),             ## Sanitize Status (SSTAT)
                               "SCDW10": ('b', 4, 4),            ## Sanitize Command Dword 10 Information (SCDW10)
                               "Overwrite_Time": ('b', 8, 4),    ## Estimated Time For Overwrite
                               "BlockErase_Time": ('b', 12, 4),  ## Estimated Time For Block Erase
                               "CryptoErase_Time": ('b', 16, 4), ## Estimated Time For Crypto Erase
                               "Overwrite_No-Deallocate_Estimated": ('b', 20, 4),    ## Estimated Time For Overwrite With No-Deallocate Media Modification
                               "BlockErase_No-Deallocate_Estimated": ('b', 24, 4),   ## Estimated Time For Block Erase With No-Deallocate Media Modification
                               "CryptoErase_No-Deallocate_Estimated": ('b', 28, 4),  ## Estimated Time For Crypto Erase With No-Deallocate Media Modification
                              }

nvme_sanitize_log_SSTAT_bit_mask = {}

nvme_power_management_cq_bit_mask = {"PS": [0x1F, 0],   ## Power State
                                     "WH": [0xE0, 0],   ## Workload Hint
                                    }


nvme_error_log_entry_bit_mask = {}

PersistentEventLogHeader_bit_mask = {"LogID": ('b', 0, 1),      ## Log Identifier: This field shall be set to 0Dh.
                                     "TNEV": ('b', 4, 4),       ## Total Number of Events (TNEV): Contains the number of event entries in the log.
                                     "TLL": ('b', 8, 8),        ## Total Log Length (TLL): Contains the total number of bytes of persistent event log page data available, including the header.
                                     "LogRev": ('b', 16, 1),    ## Log Revision:
                                     "LogHL": ('b', 18, 2),     ## Log Header Length: 
                                     "Timestamp": ('b', 20, 8), ## Timestamp
                                     "POH": ('b', 28, 16),      ## Power on Hours (POH)
                                     "PCC": ('b', 44, 8),       ## Power Cycle Count
                                     "VID": ('b', 52, 2),       ## PCI Vendor ID (VID)
                                     "SSVID": ('b', 54, 2),     ## PCI Subsystem Vendor ID (SSVID)
                                     "SN": ('b', 56, 20),       ## Serial Number (SN):
                                     "MN": ('b', 76, 40),       ## Model Number (MN)
                                     "SUBNQN": ('b', 116, 256), ## NVM Subsystem NVMe Qualified Name (SUBNQN): 
                                     "SEB": ('b', 480, 32),     ## Supported Events Bitmap: 
                                    }

SupportedEventsBitmap = {"smart_snapshot": [0x02, 0],           ## SMART / Health Log Snapshot Event Supported
                         "fw_commit": [0x04, 0],                ## Firmware Commit Event Supported
                         "timestamp_change": [0x08, 0],         ## Timestamp Change Event Supported
                         "poweron_reset": [0x10, 0],            ## Power-on or Reset Event Supported
                         "nvmsub_hardware_err": [0x20, 0],      ## Power-on or Reset Event Supported
                         "change_ns": [0x40, 0],                ## Change Namespace Event Support
                         "format_start": [0x80, 0],             ## Format NVM Start Event Support
                         "format_end": [0x01, 1],               ## Format NVM Completion Even Support
                         "sanitize_start": [0x02, 1],           ## Sanitize Start Event Support
                         "sanitize_end": [0x04, 1],             ## Sanitize Completion Event Support
                         "set_feature": [0x08, 1],              ## Set Feature Event Support
                         "telemetry_log_create": [0x10, 1],     ## Telemetry Log Create Event Support
                         "thermal_excursion": [0x20, 1],        ## Telemetry Log Create Event Support
                         "vendor_spec": [0x40, 27],             ## Telemetry Log Create Event Support
                        }

Persistent_Event_Log_Event_Header_bit_mask = {"event_type": ('b', 0, 1),                ## Event Type
                                              "event_type_revision": ('b', 1, 1),       ## Event Type Revision
                                              "EHL": ('b', 2, 1),                       ## Event Type Revision
                                              "ctrl_id": ('b', 4, 2),                   ## Controller Identifier
                                              "event_timestamp": ('b', 6, 8),           ## Event Timestamp
                                              "VSIL": ('b', 20, 2),                     ## Vendor Specific Information Length (VSIL)
                                              "EL": ('b', 22, 2),                       ## Event Length (EL)
                                             }


self_test_log_bit_mask = {"operation_status": [0x0F, 0],                  ## Current Device Self-Test Operation
                          "test_process": [0x7F, 1],                      ## Current Device Self-Test Completion
                          }

self_test_return_data_struc_bit_mask = {"test_result": [0x0F, 0],          ##  the result of the device self-test operation that this Self-test Result Data Structure describes
                                        "operation_type": [0xF0, 0],       ##  the Self-test Code value that was specified in the Device Self-test command
                                        "Segment_num": ('b', 1, 1),        ##  Segment Number
                                        "valid_diag_info": ('b', 2, 1),    ##  Valid Diagnostic Information
                                        "POH": ('b', 4, 8),                ##  Power On Hours (POH)
                                        "NSID": ('b', 12, 4),              ##  Namespace Identifier (NSID)
                                        "failing_lba": ('b', 16, 8),       ##  Failing LBA
                                        "status_code_type": ('b', 24, 1),  ##  Status Code Type
                                        "status_code": ('b', 25, 1),       ##  Status Code
                                        }

commands_supported_and_effects_bit_mask = {"CSUPP": [0x01, 0],
                                           "LBCC": [0x02, 0],
                                           "NCC": [0x04, 0],
                                           "NIC": [0x08, 0],
                                           "CCC": [0x10, 0],
                                           "CSE": [0x07, 2],
                                           "UUIDSS": [0x08, 2],
                                           }

LBAStatusDescriptorListHeader_bit_mask = {"NLSD": ('b', 0, 4),       # Number of LBA Status Descriptors
                                          "CMPC": ('b', 4, 1),       # Completion Condition
                                          }

LBAStatusDescriptorEntry_bit_mask = {"DSLBA": ('b', 0, 8),       # Descriptor Starting LBA
                                     "NLB": ('b', 8, 4),         # Number of Logical Blocks
                                     "Status": ('b', 13, 1),     # This field contains additional status about this LBA range.
                                     }

ctrl_register_bit_mask = {"cap": ('b', 0, 8),
                          "version": ('b', 0x08, 4),
                          "intms": ('b', 0x0C, 4),
                          "intmc": ('b', 0x10, 4),
                          "cc": ('b', 0x14, 4),
                          "csts": ('b', 0x1C, 4),
                          "nssr": ('b', 0x20, 4),
                          "aqa": ('b', 0x24, 4),
                          "asq": ('b', 0x28, 8),
                          "acq": ('b', 0x30, 8),
                          "cmbloc": ('b', 0x38, 4),
                          "cmbsz": ('b', 0x3C, 4),
                          "bpinfo": ('b', 0x40, 4),
                          "bprsel": ('b', 0x44, 4),
                          "bpmbl": ('b', 0x48, 8),
                          "cmbmsc": ('b', 0x50, 8),
                          "cmbsts": ('b', 0x58, 4),
                          "pmrcap": ('b', 0xE00, 4),
                          "pmrctl": ('b', 0xE04, 4),
                          "pmrsts": ('b', 0xE08, 4),
                          "pmrebs": ('b', 0xE0C, 4),
                          "pmrswtp": ('b', 0xE10, 4),
                          "pmrmscl": ('b', 0xE14, 4),
                          "pmrmscu": ('b', 0xE18, 4),
                          }

mi_commands_supported_and_effects_bit_mask = {"CSUPP": [0x01, 0],
                                              "UDCC": [0x02, 0],
                                              "NCC": [0x04, 0],
                                              "NIC": [0x08, 0],
                                              "CCC": [0x10, 0],
                                              "CSP": [0xFFF0, 2],
                                              }

nvme_mi_command_names = {0x00: "Read NVMe-MI Data Structure",
                         0x01: "NVM Subsystem Health Status Poll",
                         0x02: "Controller Health Status Poll",
                         0x03: "Configuration Set",
                         0x04: "Configuration Get",
                         0x05: "VPD Read",
                         0x06: "VPD Write",
                         0x07: "Reset",
                         0x08: "SES Receive",
                         0x09: "SES Send",
                         0x0A: "Management Endpoint Buffer Read",
                         0x0B: "Management Endpoint Buffer Write",
                         0x0C: "Shutdown",
                         tuple(range(0x0D, 0xC0)): "Reserved",
                         tuple(range(0xC0, 0x100)): "Vendor specific",
                         }

def get_nvme_mi_command_name(opcode: int) -> str:
    if opcode < 0x0D:
        name = nvme_mi_command_names.get(opcode)
    elif opcode < 0xC0:
        name = "Reserved"
    elif opcode < 0x100:
        name = "Vendor specific"
    else:
        name = "Unknown"
    return name

class ErrorInfomationLogEntryUnit(object):
    def __init__(self, data):
        self.error_count = int.from_bytes(data[0:8], byteorder='little', signed=False)
        self.sqid = int.from_bytes(data[8:10], byteorder='little', signed=False)
        self.cid = int.from_bytes(data[10:12], byteorder='little', signed=False)
        self.phase_tag = data[12] & 0x01
        self.status_field = ((data[12] >> 1) & 0x7F) + (data[13] << 15)
        self.para_error_location = int.from_bytes(data[14:16], byteorder='little', signed=False)
        self.lba = int.from_bytes(data[16:24], byteorder='little', signed=False)
        self.ns = int.from_bytes(data[24:28], byteorder='little', signed=False)
        self.vendor_spec_info_ava = data[28]
        self.transport_type = data[29]
        self.command_spec_info = data[32:40]
        self.transport_type_spec_info = data[40:42]

    def _to_int(self, b):
        if not isinstance(b, int):
            b = int.from_bytes(b, byteorder='little', signed=False)
        return b

    def dump(self):
        return {"error_count": self._to_int(self.error_count),
                "sqid": self._to_int(self.sqid),
                "cmdid": self._to_int(self.cid),
                "status_field": self._to_int(self.status_field),
                "parm_err_loc": self._to_int(self.para_error_location),
                "lba": self._to_int(self.lba),
                "nsid": self._to_int(self.ns),
                "vs": self._to_int(self.vendor_spec_info_ava),
                "trtype": self._to_int(self.transport_type),
                "cs": self._to_int(self.command_spec_info),
                "trtype_spec_info": self._to_int(self.transport_type_spec_info),
               }


def nvme_smart_decode(data):
    result = {}
    decode_bits(data, nvme_smart_bit_mask, result)
    return result

def nvme_id_ctrl_decode(data):
    result = {}
    decode_bits(data, nvme_id_ctrl_bit_mask, result)
    ## power state
    result["PSD"] = {}
    for i in range(32):
        _offset = 2048 + 32*i
        _data = data[_offset:(_offset+32)]
        power_state = {}
        decode_bits(_data, nvme_id_ctrl_ps_bit_mask, power_state)
        if power_state.get("MP") != b'\x00\x00':
            result["PSD"][i] = power_state
    return result

def nvme_id_ns_decode(data):
    result = {}
    decode_bits(data, nvme_id_ns_bit_mask, result)
    ## lba format
    result["LBAF"] = {}
    for i in range(16):
        _offset = 128 + 4*i
        _data = data[_offset:(_offset+4)]
        lba_format = {}
        decode_bits(_data, nvme_id_ns_lbaf_bit_mask, lba_format)
        if lba_format.get("LBADS") != b'\x00':
            result["LBAF"][i] = lba_format
    return result

def nvme_fw_slot_info_decode(data, check_invalid_frs=True):
    result = {}
    decode_bits(data, nvme_fw_slot_info_bit_mask, result)
    ##
    if check_invalid_frs:  
        for name in list(result.keys()):
            if "FRS" in name:
                if result[name] == b'\x00\x00\x00\x00\x00\x00\x00\x00':
                    result.pop(name)
    return result

def nvme_power_management_cq_decode(data):
    result = {}
    data = data.to_bytes(4, byteorder='little')
    decode_bits(data, nvme_power_management_cq_bit_mask, result)
    return result

def nvme_error_log_decode(data):
    error_log_entry_list = []
    offset = 0
    # data should be 64 bytes aligned
    index = len(data) % 64
    if index > 0:
        data = data[0:-index]
    #
    while True:
        if offset >= len(data):
            break
        #error_log_entry_list.insert(0, ErrorInfomationLogEntryUnit(data[offset:(offset+64)]))
        error_log_entry_list.append(ErrorInfomationLogEntryUnit(data[offset:(offset+64)]))
        offset += 64
    return error_log_entry_list

def persistent_event_log_header_decode(data):
    result = {}
    decode_bits(data, PersistentEventLogHeader_bit_mask, result)
    if "SEB" in result:
        result_temp = {}
        decode_bits(result["SEB"], SupportedEventsBitmap, result_temp)
        result["SEB"] = result_temp
    return result

def persistent_event_log_events_decode(raw_data, total_event_number):
    offset = 0
    event_log_events = {}
    if raw_data:
        for i in range(total_event_number):
            event_log_event_format = {}
            event_log_event_header = {}
            # fix a bug: break loop when there is no avaliable data
            # By Eric, 2024-04-15
            if not raw_data[offset:offset+24]:
                break
            decode_bits(raw_data[offset:offset+24], Persistent_Event_Log_Event_Header_bit_mask, event_log_event_header)
            event_log_event_format["event_log_event_header"] = event_log_event_header
            ##
            ehl_int = scsi_ba_to_int(event_log_event_header.get("EHL"), 'little')
            vsil_int = scsi_ba_to_int(event_log_event_header.get("VSIL"), 'little')
            el_int = scsi_ba_to_int(event_log_event_header.get("EL"), 'little')
            #
            vendor_spec_info = raw_data[offset+ehl_int+3:offset+ehl_int+2+vsil_int+1]
            event_log_event_data = raw_data[offset+ehl_int+3+vsil_int:offset+ehl_int+el_int+2+1]
            event_log_event_format["vendor_spec_info"] = vendor_spec_info
            event_log_event_format["event_log_event_data"] = event_log_event_data
            event_log_events[i] = event_log_event_format
            offset += (ehl_int+el_int+2+1)
    return event_log_events

def self_test_log_decode(raw_data):
    result = {}
    decode_bits(raw_data, self_test_log_bit_mask, result)
    result["LogEntry"] = {}
    ## by nvme spec 1.4a
    for i in range(20):
        temp = {}
        decode_bits(raw_data[4+i*28:32+i*28], self_test_return_data_struc_bit_mask, temp)
        if temp["test_result"] != 0x0F:
            result["LogEntry"][i] = temp
    return result

def decode_ctrl_list_format(raw_data):
    target = []
    max_cycle = scsi_ba_to_int(raw_data[0:2], 'little')
    for i in range(max_cycle):
        v = scsi_ba_to_int(raw_data[i*2+2:i*2+4], 'little')
        target.append(v)
    return target

def decode_ns_list_format(raw_data):
    target = []
    max_cycle = int(len(raw_data) / 4)
    for i in range(max_cycle):
        v = scsi_ba_to_int(raw_data[i*4:i*4+4], 'little')
        if v == 0:
            break
        target.append(v)
    return target

def decode_commands_supported_and_effects(data):
    result = [[], []]
    # admin command
    for i in range(256):
        temp = {"opcode": i}
        decode_bits(data[i*4:(i+1)*4], commands_supported_and_effects_bit_mask, temp)
        if temp["CSUPP"]:
            result[0].append(temp)
    # IO command
    for i in range(256, 512):
        temp = {"opcode": i-256}
        decode_bits(data[i*4:(i+1)*4], commands_supported_and_effects_bit_mask, temp)
        if temp["CSUPP"]:
            result[1].append(temp)
    return result

def decode_LBA_Status_Descriptor_List(data):
    result = {"header": {}, "entry_list": []}
    ##
    decode_bits(data[0:8], LBAStatusDescriptorListHeader_bit_mask, result["header"])
    #
    index = 8
    while True:
        temp_data = data[index:(index+16)]
        if temp_data:
            temp_res = {}
            decode_bits(temp_data, LBAStatusDescriptorEntry_bit_mask, temp_res)
            result["entry_list"].append(temp_res)
            index += 16
        else:
            break
    return result

def decode_sanitize_log(data):
    result = {}
    decode_bits(data, nvme_sanitize_log_bit_mask, result)
    for k,v in result.items():
        result[k] = scsi_ba_to_int(v, 'little')
    return result

def decode_ctrl_register(data):
    result = {}
    decode_bits(data, ctrl_register_bit_mask, result)
    for k,v in result.items():
        result[k] = scsi_ba_to_int(v, 'little')
    return result

def decode_mi_commands_supported_and_effects(data):
    result = {}
    for i in range(256):
        temp = {}
        decode_bits(data[i*4:(i+1)*4], mi_commands_supported_and_effects_bit_mask, temp)
        if temp['CSUPP']:
            result[i] = temp
    return result
