# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later

##               Attribute ID : (Weight, Limit )
sata_attr_key_table = {5: (2, 70),    # Reallocated Sectors Count
                       10: (2, 50),   # Spin Retry Count
                       184: (1, 50),  # End-to-End Error
                       196: (1, 40),  # Reallocation Event Count
                       197: (1, 40),  # Current Pending Sectors Count
                       198: (2, 70),  # Offline uncorrectable Sectors Count
                       201: (1, 20),  # Soft Read Error Rate
                       }

sata_attr_comm_table = {1: 0.9,
                        2: 0.9,
                        3: 0.9,
                        4: 0.9,
                        7: 0.9,
                        8: 0.9,
                        9: 0.9,
                        12: 0.9,
                        193: 0.9,
                        194: 0.9,
                        199: 0.9,
                        221: 0.9,
                        225: 0.9,
                        228: 0.9,
                        }

def attribute_formula(attribute_value, weight, limit):
    return (100 - min(limit, attribute_value*weight)) / 100

def get_ata_diskhealth(smart_dict, thresh_info):
    '''
    smart_dict: dict type, from sata_spec.decode_smart_info
    thresh_info: dict type, from sata_spec.decode_smart_thresh
    '''
    disk_health = 1
    for k,v in sata_attr_key_table.items():
        if k in smart_dict:
            disk_health *= attribute_formula(smart_dict[k].raw_value_int, v[0], v[1])
    ##
    for k,v in sata_attr_comm_table.items():
        if (k in smart_dict) and (k in thresh_info) and (thresh_info[k] > 0) and (smart_dict[k].value <= thresh_info[k]):
            disk_health *= v
    return disk_health
