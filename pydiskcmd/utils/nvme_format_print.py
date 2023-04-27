# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import json
from pydiskcmd.pynvme.nvme_spec import (
    decode_LBA_Status_Descriptor_List,
    nvme_smart_decode,
    nvme_id_ctrl_decode,
    )
from pydiskcmd.utils.format_print import format_dump_bytes
from pydiskcmd.utils.converter import scsi_ba_to_int,ba_to_ascii_string


def json_print(json_object):
    print (json.dumps(json_object, sort_keys=False, indent=2))

def format_print_LBA_Status_Descriptor(raw_data, print_type='normal'):
    if print_type == 'normal':
        decoded_data = decode_LBA_Status_Descriptor_List(raw_data)
        if "header" in decoded_data:
            print ("Number of LBA Status Descriptors: %d" % scsi_ba_to_int(decoded_data["header"]["NLSD"], 'little'))
            print ("Completion Condition            : %#x" % scsi_ba_to_int(decoded_data["header"]["CMPC"], 'little'))
        if "entry_list" in decoded_data:
            print ("")
            for k,v in enumerate(decoded_data["entry_list"]):
                print ("")
                print ("Entry %d" % k)
                print ("-"*30)
                print ("Descriptor Starting LBA  : %d" % scsi_ba_to_int(v["DSLBA"], 'little'))
                print ("Number of Logical Blocks : %d" % scsi_ba_to_int(v["NLB"], 'little'))
                print ("Status                   : %#x" % scsi_ba_to_int(v["NLB"], 'little'))
    elif print_type == 'hex':
        format_dump_bytes(raw_data)
    elif print_type == 'json':
        decoded_data = decode_LBA_Status_Descriptor_List(raw_data)
        if "header" in decoded_data:
            decoded_data["header"]["NLSD"] = scsi_ba_to_int(decoded_data["header"]["NLSD"], 'little')
            decoded_data["header"]["CMPC"] = scsi_ba_to_int(decoded_data["header"]["CMPC"], 'little')
        if "entry_list" in decoded_data:
            for k in range(len(decoded_data["entry_list"])):
                for i in list(decoded_data["entry_list"][k].keys()):
                    decoded_data["entry_list"][k][i] = scsi_ba_to_int(decoded_data["entry_list"][k][i], 'little')
        json_print(decoded_data)
    elif print_type == 'raw':
        print (raw_data)
    else:
        raise NotImplementedError("Not Support type: %s" % print_type)

def format_print_smart_log(raw_data, print_type='normal'):
    if print_type == 'normal' or print_type == 'json':
        decoded_data = nvme_smart_decode(raw_data)
        for k in list(decoded_data.keys()):
            decoded_data[k] = scsi_ba_to_int(decoded_data[k], 'little')
        if print_type == 'normal':
            for k,v in decoded_data.items():
                if k == "Composite Temperature":
                    print ("%-40s: %.2f" % ("%s(C)" % k, v-273.15))
                elif k in ("Critical Warning",):
                    print ("%-40s: %#x" % (k, v))
                else:
                    print ("%-40s: %s" % (k, v))
        else:
            json_print(decoded_data)
    elif print_type == 'hex':
        format_dump_bytes(raw_data, end=511)
    elif print_type == 'raw':
        print (raw_data)
    else:
        raise NotImplementedError("Not Support type: %s" % print_type)

def format_print_id_ctrl(raw_data, print_type='normal'):
    if print_type == 'normal':
        decoded_data = nvme_id_ctrl_decode(raw_data)
        for k,v in decoded_data.items():
            if k in ("VID", "SSVID", "VER", "RTD3R", "RTD3E", "OAES", "OACS", "FRMW", "LPA", "SANICAP", "SQES", "CQES", "FNA", "SGLS"):
                print ("%-10s: %#x" % (k,scsi_ba_to_int(v, 'little')))
            elif k in ("SN", "MN", "FR", "SUBNQN"):
                print ("%-10s: %s" % (k,ba_to_ascii_string(v, "")))
            elif k in ("IEEE",):
                print ("%-10s: %x" % (k,scsi_ba_to_int(v, 'little')))
            elif k == "PSD":
                print ("%-10s:" % k)
                for ps,psd in decoded_data[k].items():
                    print ("  %d->" % ps)
                    for m,n in psd.items():
                        if isinstance(n, bytes):
                            print ("     %-5s:%s" % (m, scsi_ba_to_int(n, 'little')))
                        else:
                            print ("     %-5s:%s" % (m, n))
            else:
                print ("%-10s: %s" % (k,scsi_ba_to_int(v, 'little')))
    elif print_type == 'hex':
        format_dump_bytes(raw_data, byteorder='obverse')
    elif print_type == 'raw':
        print (raw_data)
    elif print_type == 'json':
        decoded_data = nvme_id_ctrl_decode(raw_data)
        for k in list(decoded_data.keys()):
            if k in ("SN", "MN", "FR", "SUBNQN"):
                decoded_data[k] = ba_to_ascii_string(decoded_data[k], "")
            elif k == "PSD":
                for ps in list(decoded_data[k].keys()):
                    for m in list(decoded_data[k][ps].keys()):
                        if isinstance(decoded_data[k][ps][m], bytes):
                            decoded_data[k][ps][m] = scsi_ba_to_int(decoded_data[k][ps][m], "little")
            else:
                decoded_data[k] = scsi_ba_to_int(decoded_data[k], 'little')
        json_print(decoded_data)
    else:
        raise NotImplementedError("Not Support type: %s" % print_type)
