# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmdlib.utils.converter import decode_bits,scsi_ba_to_int


ocp_smart_extended_bit_mask = {"Physical Media Units Written": ('b', 0, 16),
                               "Physical Media Units Read": ('b', 16, 16),
                               "Bad User NAND Blocks": ('b', 32, 8),
                               "Bad System NAND Blocks": ('b', 40, 8),
                               "XOR Recovery Count": ('b', 48, 8),
                               "Uncorrectable  Read Error Count": ('b', 56, 8),
                               "Soft ECC Error Count": ('b', 64, 8),
                               "E2E Correction Counts": ('b', 72, 8),
                               "System Data Used": ('b', 80, 1),
                               "Refresh Count": ('b', 81, 7),
                               "User Data Erase Counts": ('b', 88, 8),
                               "Thermal Throttling Status and Count": ('b', 96, 2),
                               "DSSD Spec Version": ('b', 98, 6),
                               "PCIe Correctable Error Count": ('b', 104, 8),
                               "Incomplete Shutdowns": ('b', 112, 4),
                               "Free Blocks": ('b', 120, 1),
                               "Capacitor Health": ('b', 128, 2),
                               "NVMe Errata Version": ('b', 130, 1),
                               "Unaligned IO": ('b', 136, 8),
                               "Security Version Number": ('b', 144, 8),
                               "Total NUSE": ('b', 152, 8),
                               "PLP Start Count": ('b', 160, 16),
                               "Endurance Estimate": ('b', 176, 16),
                               "PCIe Link Retraining Count": ('b', 192, 8),
                               "Power State Change Count": ('b', 200, 8),
                               "Log Page Version": ('b', 494, 2),
                               "Log Page GUID": ('b', 496, 16),
                               }

ocp_error_recovery_bit_mask = {"Panic Reset Wait Time": ('b', 0, 2),
                               "Panic Reset Action": ('b', 2, 1),
                               "Device Recovery Action_1": ('b', 3, 1),
                               "Panic ID": ('b', 4, 8),
                               "Device Capabilities": ('b', 12, 4),
                               "VS Recovery OPcode": ('b', 16, 1),
                               "VS Command CDW12": ('b', 20, 4),
                               "VS Command CDW13": ('b', 24, 4),
                               "VS Command Timeout": ('b', 28, 1),
                               "Device Recovery Action_2": ('b', 29, 1),
                               "Device Recovery Action_2 Timeout": ('b', 30, 1),
                               "Log Page Version": ('b', 494, 2),
                               "Log Page GUID": ('b', 496, 16),
                               }

###################
ocp_latency_monitor_bit_mask = {"Latency Monitor Feature Status": ('b', 0, 1),
                                "Active Bucket Timer": ('b', 2, 2),
                                "Active Bucket Timer Threshold": ('b', 4, 2),
                                "Active Threshold A": ('b', 6, 1),
                                "Active Threshold B": ('b', 7, 1),
                                "Active Threshold C": ('b', 8, 1),
                                "Active Threshold D": ('b', 9, 1),
                                "Active Latency Configuration": ('b', 10, 2),
                                "Active Latency Minimum Window": ('b', 12, 1),
                                "Active Bucket Counter 0": ('b', 32, 16),
                                "Active Bucket Counter 1": ('b', 48, 16),
                                "Active Bucket Counter 2": ('b', 64, 16),
                                "Active Bucket Counter 3": ('b', 80, 16),
                                "Active Latency Stamp": ('b', 96, 96),
                                "Active Measured Latency": ('b', 192, 24),




                                "Device Recovery Action_2 Timeout": ('b', 30, 1),
                                "Log Page Version": ('b', 494, 2),
                                "Log Page GUID": ('b', 496, 16),
                                }




def ocp_smart_extended_decode(data):
    result = {}
    decode_bits(data, ocp_smart_extended_bit_mask, result)
    return result

def ocp_error_recovery_decode(data):
    result = {}
    decode_bits(data, ocp_error_recovery_bit_mask, result)
    return result

def ocp_latency_monitor_decode(data):
    pass
