# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import json
from pydiskcmd.pynvme.nvme_spec import (
    decode_LBA_Status_Descriptor_List,
    nvme_smart_decode,
    nvme_id_ctrl_decode,
    nvme_id_ns_decode,
    nvme_error_log_decode,
    nvme_fw_slot_info_decode,
    persistent_event_log_header_decode,
    persistent_event_log_events_decode,
    self_test_log_decode,
    decode_commands_supported_and_effects,
    decode_ns_list_format,
    decode_ctrl_list_format,
    nvme_power_management_cq_decode,
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

def format_print_id_ns(raw_data, print_type='normal'):
    if print_type == 'normal':
        decoded_data = nvme_id_ns_decode(raw_data)
        for k,v in decoded_data.items():
            if k in ("NSZE", "NCAP", "NUSE", "MC", "DPC"):
                print ("%-10s: %#x" % (k,scsi_ba_to_int(v, 'little')))
            elif k in ("NGUID", "EUI64"):
                print ("%-10s: %x" % (k,scsi_ba_to_int(v, 'big')))
            elif k == "LBAF":
                print ("%-10s:" % k)
                for i,lbaf in decoded_data[k].items():
                    print ("  %d->" % i)
                    for m,n in lbaf.items():
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
        decoded_data = nvme_id_ns_decode(raw_data)
        for k in list(decoded_data.keys()):
            if k == "LBAF":
                for lbaf in list(decoded_data[k].keys()):
                    for m in list(decoded_data[k][lbaf].keys()):
                        if isinstance(decoded_data[k][lbaf][m], bytes):
                            decoded_data[k][lbaf][m] = scsi_ba_to_int(decoded_data[k][lbaf][m], "little")
            else:
                decoded_data[k] = scsi_ba_to_int(decoded_data[k], 'little')
        json_print(decoded_data)
    else:
        raise NotImplementedError("Not Support type: %s" % print_type)

def format_print_error_log(raw_data, dev='', print_type='normal'):
    if print_type == 'normal':
        decoded_data = nvme_error_log_decode(raw_data)
        if decoded_data:
            print ('Error Log Entries for device:%s entries:%s' % (dev, len(decoded_data)))
            print ('.................')
        for index,unit in enumerate(decoded_data):
            print ('Entry[%s]' % index)
            print ('.................')
            print ('error_count     : %s' % unit.error_count)
            print ('sqid            : %s' % unit.sqid)
            print ('cmdid           : %s' % unit.cid)
            print ('status_field    : %s' % unit.status_field)
            print ('parm_err_loc    : %s' % unit.para_error_location)
            print ('lba             : %s' % unit.lba)
            print ('nsid            : %s' % unit.ns)
            print ('vs              : %s' % unit.vendor_spec_info_ava)
            print ('trtype          : %s' % unit.transport_type)
            print ('cs              : %s' % unit.command_spec_info)
            print ('trtype_spec_info: %s' % unit.transport_type_spec_info)
            print ('.................')
    elif print_type == 'hex':
        format_dump_bytes(raw_data, byteorder='obverse')
    elif print_type == 'raw':
        print (raw_data)
    elif print_type == 'json':
        decoded_data = nvme_error_log_decode(raw_data)
        json_print({"errors": [i.dump() for i in decoded_data]})
    else:
        raise NotImplementedError("Not Support type: %s" % print_type)

def format_print_fw_log(raw_data, dev='', print_type='normal'):
    if print_type == 'normal':
        decoded_data = nvme_fw_slot_info_decode(raw_data)
        for k,v in decoded_data.items():
            if "FRS" in k:
                print ("%-5s: %s" % (k,ba_to_ascii_string(v, "")))
            else:
                print ("%-5s: %#x" % (k,scsi_ba_to_int(v, 'little')))
    elif print_type == 'hex':
        format_dump_bytes(raw_data, byteorder='obverse')
    elif print_type == 'raw':
        print (raw_data)
    elif print_type == 'json':
        decoded_data = nvme_fw_slot_info_decode(raw_data)
        result = {}
        for k,v in decoded_data.items():
            if "FRS" in k:
                result[k] = ba_to_ascii_string(v, "")
            else:
                result[k] = scsi_ba_to_int(v, 'little')
        json_print({dev:result})
    else:
        raise NotImplementedError("Not Support type: %s" % print_type)

def format_print_event_log(raw_data, dev='', print_type='normal', event_filter=[]):
    if print_type == 'normal':
        event_log_header = persistent_event_log_header_decode(raw_data[0:512])
        event_log_events = persistent_event_log_events_decode(raw_data[512:], scsi_ba_to_int(event_log_header.get("TNEV"), 'little'))
        print ("Persistent Event Log Header: ")
        for k,v in event_log_header.items():
            if k in ("LogID", "VID", "SSVID"):
                print ("%-10s: %#x" % (k,scsi_ba_to_int(v, 'little')))
            elif k in ("SN", "MN", "SUBNQN"):
                print ("%-10s: %s" % (k,ba_to_ascii_string(v, "")))
            elif k == "SEB":
                print ("Supported Events Bitmap: ")
                for m,n in v.items():
                    print ("     %-20s:%s" % (m,n))
            else:
                print ("%-10s: %s" % (k,scsi_ba_to_int(v, 'little')))
        ##
        print ("="*60)
        if event_log_events:
            print ("Persistent Event Log Events: ")
            print ('......................')
        for k,v in event_log_events.items():
            if event_filter and (scsi_ba_to_int(v['event_log_event_header']['event_type'], 'little') not in event_filter):
                continue
            print ('Entry[%s]' % k)
            print ('......................')
            for m,n in v.items():
                if m == 'event_log_event_header' and n:
                    for p,q in n.items():
                        print ('%-20s : %s' % (p,scsi_ba_to_int(q, 'little')))
                elif m in ("vendor_spec_info", "event_log_event_data"):
                    print ('%-20s : %s' % (m,n))
                else:
                    print ('%-20s : %s' % (m,scsi_ba_to_int(n, 'little')))
            print ('......................')
    elif print_type == 'hex':
        format_dump_bytes(raw_data, byteorder='obverse')
    elif print_type == 'raw':
        print (raw_data)
    elif print_type == 'json':
        event_log_header = persistent_event_log_header_decode(raw_data[0:512])
        event_log_events = persistent_event_log_events_decode(raw_data[512:], scsi_ba_to_int(event_log_header.get("TNEV"), 'little'))
        ##
        result = {"header": {}, "events": {}}
        for k,v in event_log_header.items():
            if k in ("LogID", "VID", "SSVID"):
                result["header"][k] = scsi_ba_to_int(v, 'little')
            elif k in ("SN", "MN", "SUBNQN"):
                result["header"][k] = ba_to_ascii_string(v, "")
            elif k == "SEB":
                result["header"][k] = v
            else:
                result["header"][k] = scsi_ba_to_int(v, "")
        for k,v in event_log_events.items():
            if event_filter and (scsi_ba_to_int(v['event_log_event_header']['event_type'], 'little') not in event_filter):
                continue
            result["events"][k] = {}
            for m,n in v.items():
                if m == 'event_log_event_header' and n:
                    result["events"][k]["event_header"] = {}
                    for p,q in n.items():
                        result["events"][k]["event_header"][p] = scsi_ba_to_int(q, 'little')
                elif m in ("vendor_spec_info", "event_log_event_data"):
                    result["events"][k][m] = []
                    i = 0
                    while (i < len(n)):
                        result["events"][k][m].append(scsi_ba_to_int(n[i:i+4], 'little'))
                        i += 4
                else:
                    result["events"][k][m] = scsi_ba_to_int(n, 'little')
                    print ('%-20s : %s' % (m,scsi_ba_to_int(n, 'little')))
        json_print(result)
    else:
        raise NotImplementedError("Not Support type: %s" % print_type)

def format_print_self_test_log(raw_data, dev='', print_type='normal'):
    if print_type == 'normal':
        result = self_test_log_decode(raw_data)
        print ("Current Device Self-Test Operation Status :  %s" % result["operation_status"])
        print ("Current Device Self-Test Process          :  %s" % result["test_process"])
        print ('')
        print_format = "  %-40s: %s"
        for k,v in result["LogEntry"].items():
            print("LogEntry%s" % k)
            for _k,_v in v.items():
                if isinstance(_v, bytes):
                    _v = scsi_ba_to_int(_v, 'little')
                print (print_format % (_k, _v))
            print ('-'*45)
    elif print_type == 'hex':
        format_dump_bytes(raw_data, byteorder='obverse')
    elif print_type == 'raw':
        print (raw_data)
    elif print_type == 'json':
        result = self_test_log_decode(raw_data)
        target = {"Status": result["operation_status"],
                  "Process": result["test_process"],
                  "LogEntry": {}}
        for k,v in result["LogEntry"].items():
            target["LogEntry"][k] = {}
            for _k,_v in v.items():
                if isinstance(_v, bytes):
                    _v = scsi_ba_to_int(_v, 'little')
                target["LogEntry"][k][_k] = _v
        json_print(target)
    else:
        raise NotImplementedError("Not Support type: %s" % print_type)

def format_print_supported_and_effects(raw_data, dev='', print_type='normal'):
    if print_type == 'normal':
        result = decode_commands_supported_and_effects(raw_data)
        admin_cmd = result[0]
        io_cmd = result[1]
        if admin_cmd:
            print ("Admin Command support:")
            for i in admin_cmd:
                print ("."*10)
                print ("%-8s: %d" % ("opcode", i.get("opcode")))
                for k,v in i.items():
                    if k != "opcode":
                        print ("%-8s: %d" % (k, v))
        else:
            print ("No support admin command")
            print ("")
        print ("")
        print ("")
        if io_cmd:
            print ("IO Command support:")
            for i in io_cmd:
                print ("."*10)
                print ("%-8s: %d" % ("opcode", i.get("opcode")))
                for k,v in i.items():
                    if k != "opcode":
                        print ("%-8s: %d" % (k, v))
        else:
            print ("No support admin command")
            print ("")
        print ("")
    elif print_type == 'hex':
        format_dump_bytes(raw_data, byteorder='obverse')
    elif print_type == 'raw':
        print (raw_data)
    elif print_type == 'json':
        result = decode_commands_supported_and_effects(raw_data)
        target = {"admin": result[0],
                  "io": result[1],
                  }
        json_print(target)
    else:
        raise NotImplementedError("Not Support type: %s" % print_type)

def format_print_list_ns(raw_data, dev='', print_type='normal'):
    if print_type == 'normal':
        result = decode_ns_list_format(raw_data)
        for k,v in enumerate(result):
            print ("[%4d]:%d" % (k,v))
    elif print_type == 'hex':
        format_dump_bytes(raw_data, byteorder='obverse')
    elif print_type == 'raw':
        print (raw_data)
    elif print_type == 'json':
        result = decode_ns_list_format(raw_data)
        target = {"nsid_list": []}
        for i in result:
            target["nsid_list"].append({"nsid": i})
        json_print(target)
    else:
        raise NotImplementedError("Not Support type: %s" % print_type)

def format_print_list_ctrl(raw_data, dev='', print_type='normal'):
    if print_type == 'normal':
        result = decode_ctrl_list_format(raw_data)
        for k,v in enumerate(result):
            print ("[%4d]:%d" % (k,v))
    elif print_type == 'hex':
        format_dump_bytes(raw_data, byteorder='obverse')
    elif print_type == 'raw':
        print (raw_data)
    elif print_type == 'json':
        result = decode_ctrl_list_format(raw_data)
        target = {"ctrl_list": []}
        for i in result:
            target["ctrl_list"].append({"ctrl_id": i})
        json_print(target)
    else:
        raise NotImplementedError("Not Support type: %s" % print_type)

def format_print_read_data(meta_data, data, dev='', print_type='normal'):
    if print_type == 'hex':
        if meta_data:
            print ("Metadata read:")
            format_dump_bytes(meta_data, byteorder="obverse")
        else:
            print ("No metadata.")
        print ("")
        print ("Data read:")
        format_dump_bytes(data, byteorder="obverse")
    elif print_type == 'raw':
        if meta_data:
            print ("Metadata read:")
            print (meta_data)
        else:
            print ("No metadata.")
        print ("")
        print ("Data read:")
        print (data)
    else:
        raise NotImplementedError("Not Support type: %s" % print_type)
