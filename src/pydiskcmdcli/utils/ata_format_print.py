# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
try:
    from collections import Iterable
except ImportError:
    from collections.abc import Iterable
import binascii
from pydiskcmdlib.utils.converter import bytearray2string,translocate_bytearray,scsi_ba_to_int
from pydiskcmdcli.sata_spec import (
    read_log_decode_set,
    smart_read_log_decode_set,
    decode_smart_thresh,
    SMART_KEY,
    SMART_ATTR,
    SmartExecuteOfflineImmediateSubcommandsDescription,
    SelftestExecutionStatusDescription,
    ReadLogLogDirectoryDescription,
)
from pydiskcmdcli.utils.format_print import format_dump_bytes,json_print


def bytearray2hex_l(data,start,offset):
    a = data[start:start+offset][::-1]
    t = binascii.hexlify(a)
    return int(t,16)

def _print_return_status(ata_status_return):
    if ata_status_return:
        print ("Return Status:")
        for k,v in ata_status_return.items():
            print ("%-30s: %s" % (k,v))
        print ('')

def _get_log_directory_description(log_address):
    if log_address in ReadLogLogDirectoryDescription:
        return ReadLogLogDirectoryDescription[log_address]
    else:
        for i in ReadLogLogDirectoryDescription.keys():
            if isinstance(i, Iterable) and log_address in i:
                return ReadLogLogDirectoryDescription[i]

def print_ata_cmd_status(cmd):
    cmd._decode_sense().print_data()

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
    return_status = cmd.get_ata_status_return()
    if show_status and print_type != 'json':
        print_ata_cmd_status(cmd)
    print ('')
    if print_type == 'normal' or print_type == 'json':
        target = {"return_status": return_status,
                  "content": {}}
        for k,v in cmd.result.items():
            if k in ("FirmwareRevision", "SerialNumber", "ModelNumber"):
                value = bytearray2string(translocate_bytearray(v))
            elif k in ("WorldWideName"):
                value = int(binascii.hexlify(translocate_bytearray(v)),16)
            elif k in ("TotalUserLBA"):
                value = int(binascii.hexlify(translocate_bytearray(v, 2)),16)
            else:
                value = int(binascii.hexlify(translocate_bytearray(v)),16)
            target["content"][k] = value
        if print_type == 'normal':
            for k,v in target["content"].items():
                if isinstance(v, str):
                    print ("%-24s: %s" % (k, v))
                elif k in ("NormalEraseTime", "EnhancedEraseTime"):
                    print ("%-24s: %d(minutes)" % (k, v*2))
                elif k in ("DRQLBAMax", "CurrentAPMLevel", "TotalUserLBA"):
                    print ("%-24s: %d" % (k, v))
                else:
                    print ("%-24s: %#x" % (k, v))
        else:
            json_print(target)
    elif print_type == 'hex':
        format_dump_bytes(cmd.datain, byteorder='obverse')
    elif print_type == 'raw':
        print (cmd.datain)
    else:
        raise NotImplementedError("Not Support type: %s" % print_type)

def format_print_smart(cmd_read_data, cmd_thread, print_type='normal', show_status=False, smart_attr=None) -> None:
    """
    This function is used to print format smart information.

    Parameters:
    cmd_read_data: Contains smart reading data.
    cmd_thread: Contains smart thread information.
    print_type: Specifies the printing type, including 'normal', 'json', 'hex', and 'raw'.
    show_status: A Boolean value indicating whether to display status information.

    Returns:
    None.
    """
    if show_status and print_type != 'json':
        print ('Smart Read Data Status:')
        print ('')
        _print_return_status(cmd_read_data.ata_status_return_descriptor)
        print ('Smart Threshold Status:')
        print ('')
        _print_return_status(cmd_thread.ata_status_return_descriptor)
    print ('')
    if print_type == 'normal' or print_type == 'json':
        if not smart_attr:
            smart_attr = SMART_ATTR
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
                target["content"]["vendor_spec"][ID] = {"AttrName": smart_attr[ID] if ID in smart_attr else 'Unknown_Attribute',
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
                      (ID,                      # ID
                       value["AttrName"],       # ATTRIBUTE_NAME
                       value["Flag"],           # FLAG
                       value["Value"],          # VALUE
                       value["Worst"],          # WORST
                       value["Thresh"],         # THRESHOLD
                       value["RawValue"])       # RAW_VALUE0
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

def format_print_set_feature_guide():
    def filter_lba(string):
        return ("%s " % string).ljust(20, "·")
    _format_print = "%-10s%-18s%-20s %s"
    print (_format_print % ("Feature", "Count", "LBA", "Description"))
    print (_format_print % ("0x01", "·"*18, "·"*20, "Reserved for CFA"))
    print (_format_print % ("0x02", "·"*18, "·"*20, "Enable volatile write cache"))
    print (_format_print % ("0x03", "·"*18, "·"*20, "Set transfer mode"))
    print (_format_print % (" |-----", "0", filter_lba("NA"), "PIO default mode"))
    print (_format_print % (" |-----", "1", filter_lba("NA"), "PIO default mode, disable IORDY"))
    print (_format_print % (" |-----", "00001b|xxxb(Mode)", filter_lba("NA"), "PIO flow control transfer mode"))
    print (_format_print % (" |-----", "00010b|xxxb(NA)", filter_lba("NA"), "Retired"))
    print (_format_print % (" |-----", "00100b|xxxb(Mode)", filter_lba("NA"), "Multiword DMA mode"))
    print (_format_print % (" ------", "01000b|xxxb(Mode)", filter_lba("NA"), "Ultra DMA mode"))
    print (_format_print % ("0x05", "·"*18, "·"*20, "Enable the APM feature set"))
    print (_format_print % (" |-----", "0x01", filter_lba("NA"), "Minimum power consumption with Standby mode"))
    print (_format_print % (" |-----", "0x02~0x7F", filter_lba("NA"), "Intermediate power management levels with Standby mode"))
    print (_format_print % (" |-----", "0x80", filter_lba("NA"), "Minimum power consumption without Standby mode"))
    print (_format_print % (" |-----", "0x81~0xFD", filter_lba("NA"), "Intermediate power management levels without Standby mode"))
    print (_format_print % (" ------", "0xFE", filter_lba("NA"), "Maximum performance"))
    print (_format_print % ("0x06", "·"*18, "·"*20, "Enable the PUIS feature set"))
    print (_format_print % ("0x07", "·"*18, "·"*20, "PUIS feature set device spin-up"))
    print (_format_print % ("0x09", "·"*18, "·"*20, "If the device implements the CFA feature set, then this subcommand is reserved for CFA; otherwise, this subcommand is obsolete"))
    print (_format_print % ("0x0A", "·"*18, "·"*20, "Reserved for CFA"))
    print (_format_print % ("0x0B", "·"*18, "·"*20, "Enable Write-Read-Verify feature se"))
    print (_format_print % (" |-----", "NA", filter_lba("0x00"), "Write-Read-Verify Mode 0(Always enabled)"))
    print (_format_print % (" |-----", "NA", filter_lba("0x01"), "Write-Read-Verify Mode 1(See ATA command set)"))
    print (_format_print % (" |-----", "NA", filter_lba("0x02"), "Write-Read-Verify Mode 2(The number of logical sectors on which a device performs a Write-Read-Verify is vendor specific)"))
    print (_format_print % (" ------", "NA", filter_lba("0x03"), "Write-Read-Verify Mode 3(See ATA command set)"))
    print (_format_print % ("0x10", "·"*18, "·"*20, "Enable use of SATA feature"))
    print (_format_print % (" |-----", "0x01", filter_lba("NA"), "Non-zero Buffer Offsets"))
    print (_format_print % (" |-----", "0x02", filter_lba("NA"), "DMA Setup FIS Auto-Activate optimization"))
    print (_format_print % (" |-----", "0x03", filter_lba("NA"), "Device-initiated interface power state transitions"))
    print (_format_print % (" |-----", "0x04", filter_lba("NA"), "Guaranteed In-Order Data Delivery"))
    print (_format_print % (" |-----", "0x05", filter_lba("NA"), "Asynchronous Notification"))
    print (_format_print % (" |-----", "0x06", filter_lba("NA"), "Software Settings Preservation"))
    print (_format_print % (" |-----", "0x07", filter_lba("NA"), "Device Automatic Partial to Slumber transitions"))
    print (_format_print % (" ------", "0x08", filter_lba("NA"), "Enable Hardware Feature Control"))
    print (_format_print % ("0x41", "·"*18, "·"*20, "Enable the Free-fall Control feature set"))
    print (_format_print % ("0x43", "·"*18, "·"*20, "Set Maximum Host Interface Sector Times"))
    print (_format_print % (" |-----", "bit(7:0)", filter_lba("Combinable"), "COUNT: Typical PIO Mode Host Interface Sector Time (7:0)"))
    print (_format_print % (" ------", "Combinable", filter_lba("bit(23:8)|bit(7:0)"), "LBA: Typical PIO Mode Host Interface Sector Time (15:8),Typical DMA Mode Host Interface Sector Time"))
    print (_format_print % ("0x4A", "·"*18, "·"*20, "Extended Power Conditions subcommand"))
    print (_format_print % (" |-----", "0x00", filter_lba("Combinable"), "Standby_z(A substate of the PM2:Standby state)"))
    print (_format_print % (" |-----", "0x01", filter_lba("Combinable"), "Standby_y(A substate of the PM2:Standby state)"))
    print (_format_print % (" |-----", "0x81", filter_lba("Combinable"), "Idle_a(A substate of the PM1:Idle state)"))
    print (_format_print % (" |-----", "0x82", filter_lba("Combinable"), "Idle_b(A substate of the PM1:Idle state)"))
    print (_format_print % (" |-----", "0x83", filter_lba("Combinable"), "Idle_c(A substate of the PM1:Idle state)"))
    print (_format_print % (" |-----", "0xFF", filter_lba("Combinable"), "All(All supported power conditions)"))
    print (_format_print % (" |-----", "Combinable", filter_lba("0x00"), "Restore Power Condition Settings"))
    print (_format_print % (" |-----", "Combinable", filter_lba("0x01"), "Go To Power Condition"))
    print (_format_print % (" |-----", "Combinable", filter_lba("0x02"), "Set Power Condition Timer"))
    print (_format_print % (" |-----", "Combinable", filter_lba("0x03"), "Set Power Condition State"))
    print (_format_print % (" |-----", "Combinable", filter_lba("0x04"), "Enable the EPC feature set"))
    print (_format_print % (" |-----", "Combinable", filter_lba("0x05"), "Disable the EPC feature set"))
    print (_format_print % (" ------", "Combinable", filter_lba("0x06"), "Set EPC Power Source"))
    print (_format_print % ("0x55", "·"*18, "·"*20, "Disable read look-ahead feature"))
    print (_format_print % ("0x62", "", "", "Long Physical Sector Alignment Error Reporting Control"))
    print (_format_print % (" |-----", "0x00", filter_lba("NA"), "Disable Alignment Error reporting"))
    print (_format_print % (" |-----", "0x01", filter_lba("NA"), "Set the ALIGNMENT ERROR bit to one in response to a write command(See ATA command set)"))
    print (_format_print % (" ------", "0x02", filter_lba("NA"), "set the ALIGNMENT ERROR bit to one, leaving the condition of the data unknown, in response to a write command(See ATA command set)"))
    print (_format_print % ("0x63", "·"*18, "·"*20, "Enable/Disable the DSN feature set"))
    print (_format_print % (" |-----", "0x01", filter_lba("NA"), "Enable DSN feature set"))
    print (_format_print % (" ------", "0x02", filter_lba("NA"), "Disable DSN feature set"))
    print (_format_print % ("0x66", "·"*18, "·"*20, "Disable reverting to power-on defaults"))
    print (_format_print % ("0x82", "·"*18, "·"*20, "Disable volatile write cache"))
    print (_format_print % ("0x85", "·"*18, "·"*20, "Disable the APM feature set"))
    print (_format_print % ("0x86", "·"*18, "·"*20, "Disable the PUIS feature set"))
    print (_format_print % ("0x89", "·"*18, "·"*20, "If the device implements the CFA feature set, then this subcommand is reserved for CFA; otherwise, this subcommand is obsolete"))
    print (_format_print % ("0x8A", "·"*18, "·"*20, "Reserved for CFA"))
    print (_format_print % ("0x8B", "·"*18, "·"*20, "Disable Write-Read-Verify feature set"))
    print (_format_print % ("0x90", "·"*18, "·"*20, "Disable use of SATA feature"))
    print (_format_print % ("0xAA", "·"*18, "·"*20, "Enable read look-ahead feature"))
    print (_format_print % ("0xC1", "·"*18, "·"*20, "Disable the Free-fall Control feature set"))
    print (_format_print % ("0xC3", "·"*18, "·"*20, "Enable/Disable the Sense Data Reporting feature set"))
    print (_format_print % (" |-----", "0x00", filter_lba("NA"), "Enable the Sense Data Reporting feature set"))
    print (_format_print % (" ------", "0x01", filter_lba("NA"), "Disabled the Sense Data Reporting feature set"))
    print (_format_print % ("0xCC", "·"*18, "·"*20, "Enable reverting to power-on defaults"))
    return
