# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
try:
    from collections import Iterable
except ImportError:
    from collections.abc import Iterable
from pydiskcmd.pysata.sata_spec import (
    read_log_decode_set,
    smart_read_log_decode_set,
    SmartExecuteOfflineImmediateSubcommandsDescription,
    SelftestExecutionStatusDescription,
    ReadLogLogDirectoryDescription,
) 
from pydiskcmd.utils.converter import scsi_ba_to_int


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
