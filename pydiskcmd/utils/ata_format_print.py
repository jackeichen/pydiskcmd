# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
try:
    from collections import Iterable
except ImportError:
    from collections.abc import Iterable
import binascii
from pydiskcmd.pysata.sata_spec import (
    read_log_decode_set,
    smart_read_log_decode_set,
    decode_smart_thresh,
    SMART_KEY,
    SMART_ATTR,
    SmartExecuteOfflineImmediateSubcommandsDescription,
    SelftestExecutionStatusDescription,
    ReadLogLogDirectoryDescription,
) 
from pydiskcmd.utils.converter import bytearray2string,translocate_bytearray,scsi_ba_to_int
from pydiskcmd.utils.format_print import format_dump_bytes,json_print


def bytearray2hex_l(data,start,offset):
    a = data[start:start+offset][::-1]
    t = binascii.hexlify(a)
    return int(t,16)

def _print_return_status(ata_status_return_descriptor):
    print ("Return Status:")
    for k,v in ata_status_return_descriptor.items():
        print ("%-30s: %s" % (k,v))
    print ('')

def _get_log_directory_description(log_address):
    if log_address in ReadLogLogDirectoryDescription:
        return ReadLogLogDirectoryDescription[log_address]
    else:
        for i in ReadLogLogDirectoryDescription.keys():
            if isinstance(i, Iterable) and log_address in i:
                return ReadLogLogDirectoryDescription[i]

def print_read_log_LogDirectory(raw_data):
    if 0 in read_log_decode_set:
        func = read_log_decode_set.get(0)
        result = func(raw_data)
        rev_ver = result.pop("LoggingVersion")
        print ("General Purpose Logging Version: %#x" % rev_ver)
        print ("")
        print_format = "%-12s     %-10s     %s"
        print (print_format % ("Log Address", "Log length", "Description"))
        for k,v in result.items():
            print (print_format % (k, v, _get_log_directory_description(k)))

def print_smart_read_log_LogDirectory(raw_data):
    if 0 in smart_read_log_decode_set:
        func = smart_read_log_decode_set.get(0)
        result = func(raw_data)
        rev_ver = result.pop("LoggingVersion")
        print ("SMART Logging Version: %#x" % rev_ver)
        print ("")
        print_format = "%-12s     %-10s     %s"
        print (print_format % ("Log Address", "Log length", "Description"))
        for k,v in result.items():
            print (print_format % (k, v, _get_log_directory_description(k)))

def print_read_log_extend_selftest(raw_data, page_offset):
    # Num  Test_Description    Status                  Remaining  LifeTime(hours)  LBA_of_first_error
    if 0x07 in read_log_decode_set:
        func = read_log_decode_set.get(7)
        result = func(raw_data)
        print_format = "%-5s%-20s%-24s%-11s%-17s%s"

        if result[0].get("revision number"):
            print ("SMART Self-test log structure revision number: %d" % (result[0].get("revision number")[0] & 0xFF))
            print ("Current descriptor index: %d" % scsi_ba_to_int(result[0].get("descriptor index"), byteorder="little"))
            print ("")
        print (print_format % ("Num", "Test_Description", "Status", "Remaining", "LifeTime(hours)", "LBA_of_first_error"))

        _id = page_offset * 19
        for i in result:
            for m in i["entry"]:
                _id += 1
                num = "# %d" % _id
                test_description = SmartExecuteOfflineImmediateSubcommandsDescription.get(m["subcommand_lba"][0])
                remaining = "%s%%" % ((m["status"][0] & 0x0F)*10)
                status = SelftestExecutionStatusDescription.get(m["status"][0] & 0xF0)
                life_time = scsi_ba_to_int(m["life_timestamp"], byteorder='little')
                if m["status"][0] & 0xF0 in (6,7,):
                    lba_failed = scsi_ba_to_int(m["failing_lba"], byteorder='little')
                else:
                    lba_failed = '-'
                print (print_format % (num, test_description, status, remaining, life_time, lba_failed))


read_log_format_print_set = {0: print_read_log_LogDirectory, 7: print_read_log_extend_selftest}
smart_read_log_format_print_set = {0: print_smart_read_log_LogDirectory,}

#############################
def format_print_identify(cmd, dev='', print_type='normal', show_status=False):
    return_descriptor = cmd.ata_status_return_descriptor
    if show_status:
        if print_type != 'json':
            _print_return_status(return_descriptor)
    elif print_type != 'json':
        print ('')
        print ('status err_bit:', return_descriptor.get("status") & 0x01)
    print ('')
    if print_type == 'normal' or print_type == 'json':
        target = {"return_status": return_descriptor,
                  "content": {}}
        for k,v in cmd.result.items():
            if k in ("FirmwareRevision", "SerialNumber", "ModelNumber"):
                value = bytearray2string(translocate_bytearray(v))
            elif k in ("Capacity", "NormalEraseTime"):
                value = int(binascii.hexlify(translocate_bytearray(v, 2)),16)
                if k == "Capacity":
                    value = value *512/1024/1024/1024  # byte --> GB
                    value = "%.2f GB" % value
            else:
                value = int(binascii.hexlify(translocate_bytearray(v, 2)),16)
            target["content"][k] = value
        if print_type == 'normal':
            for k,v in target["content"].items():
                print ("%s: %s" % (k, v))
        else:
            json_print(target)
    elif print_type == 'hex':
        format_dump_bytes(cmd.datain, byteorder='obverse')
    elif print_type == 'raw':
        print (cmd.datain)
    else:
        raise NotImplementedError("Not Support type: %s" % print_type)

def format_print_smart(cmd_read_data, cmd_thread, dev='', print_type='normal', show_status=False):
    if show_status:
        if print_type != 'json':
            print ('Smart Read Data Status:')
            print ('')
            _print_return_status(cmd_read_data.ata_status_return_descriptor)
            print ('Smart Threshold Status:')
            print ('')
            _print_return_status(cmd_thread.ata_status_return_descriptor)
    elif print_type != 'json':
        print ('')
        print ('status err_bit of Smart Read Data:', cmd_read_data.ata_status_return_descriptor.get("status") & 0x01)
        print ('status err_bit of Smart Threshold:', cmd_thread.ata_status_return_descriptor.get("status") & 0x01)
    print ('')
    if print_type == 'normal' or print_type == 'json':
        target = {"return_status": {"smart_read_data": cmd_read_data.ata_status_return_descriptor, "smart_thread": cmd_thread.ata_status_return_descriptor}, 
                  "content": {"vendor_spec": {}, "general_info": {}},
                  }
        for name,value in cmd_read_data.result.items(): 
            if name != 'smartInfo':
                target["content"]["general_info"][name] = scsi_ba_to_int(value, 'little')
        ##
        smart_thread = decode_smart_thresh(cmd_thread.datain[2:362])
        data = cmd_read_data.result['smartInfo']
        for i in range(0, 359, 12):
            ID = data[i]
            if ID:
                attr_name = SMART_ATTR[ID] if ID in SMART_ATTR else 'Unknown_Attribute'
                flag = data[i+1:i+3]
                value = data[i+3]
                worst = data[i+4]
                raw_value = data[i+5:i+11]
                target["content"]["vendor_spec"][ID] = {"AttrName": SMART_ATTR[ID] if ID in SMART_ATTR else 'Unknown_Attribute',
                                             "Flag": scsi_ba_to_int(data[i+1:i+3], 'little'),
                                             "Value": data[i+3],
                                             "Worst": data[i+4],
                                             "Thresh": smart_thread[ID],
                                             "RawValue": scsi_ba_to_int(data[i+5:i+11], 'little')}
        if print_type == 'normal':
            print ('General SMART Values:')
            print ('=' * 100)
            for name,value in target["content"]["general_info"].items():
                print ('%34s: %-10d [%#x]' % (name,value,value))
            
            print ('')
            print ('Vendor Specific SMART Attributes with Thresholds:')
            print ('=' * 100)
            print_fomrat = '%3s %-25s %-6s %-6s %-6s %-10s %s'
            print (print_fomrat %
                  ('ID#','ATTRIBUTE_NAME','FLAG','VALUE','WORST','THRESHOLD','RAW_VALUE'))
            print ('-'*100)
            print_fomrat = '%3s %-25s %#-6x %-6s %-6s %-10s %s'
            for ID,value in target["content"]["vendor_spec"].items():
                print (print_fomrat %
                      (ID,                                          # ID
                       value["AttrName"],                              # ATTRIBUTE_NAME
                       value["Flag"], # FLAG
                       value["Value"],                               # VALUE
                       value["Worst"],                               # WORST
                       value["Thresh"],                   # THRESHOLD
                       value["RawValue"])           # RAW_VALUE0
                       )
        else:
            json_print(target)
    elif print_type == 'hex':
        print ("SMART Read DATA bellow:")
        print ("")
        format_dump_bytes(cmd_read_data.datain, byteorder='obverse')
        print ("")
        print ("")
        print ("SMART THRESH value:")
        print ("")
        format_dump_bytes(cmd_thread.datain, byteorder='obverse')
    elif print_type == 'raw':
        print ("SMART Read DATA bellow:")
        print ("")
        print (cmd_read_data.datain)
        print ("")
        print ("")
        print ("SMART THRESH value:")
        print ("")
        print (cmd_thread.datain)
    else:
        raise NotImplementedError("Not Support type: %s" % print_type)
