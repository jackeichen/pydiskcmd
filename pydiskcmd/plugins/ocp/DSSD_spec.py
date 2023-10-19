# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later

from pydiskcmd.utils.converter import decode_bits,scsi_ba_to_int

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

def ocp_smart_extended_decode(data):
    result = {}
    decode_bits(data, ocp_smart_extended_bit_mask, result)
    return result
