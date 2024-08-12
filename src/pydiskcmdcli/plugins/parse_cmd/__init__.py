# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import sys
import optparse
from .parse_scsi_cdb import parse_cdb
from .parse_scsi_sense_code import parse_sense_code

parse_cmd_plugin = {"cdb": parse_cdb,
                    "sense_code": parse_sense_code,
                    }

def _parse_cmd_print_help():
    print ("usage: pynvme parse-cmd <sub-command> [<device>] [<args>]")
    print ("")
    print ("Parse Command plugin")
    print ("")
    print ("The following are all implemented sub-commands:")
    print ("")
    print ("  cdb                     Parse the command CDB(in hex format), like A0 01 00 00 00 00")
    print ("  sense-code              Parse the return sense code(in hex format), sense-key/asc/ascq or asc/ascq")
    print ("  help                    Display this help")
    print ("")
    print ("See 'pyscsi parse-cmd help <command>' for more information on a specific command")
    return 0

def _parse_cmd_print_ver():
    print ("parse-cmd Plugin Version: %s" % "1.0")
    print ("")
    return 0

def _cdb():
    usage="usage: %prog parse-cmd cdb CDB0 CDB1 ..."
    parser = optparse.OptionParser(usage)
    if len(sys.argv[3:]) > 1:
        cdb_in_str = [i.strip() for i in sys.argv[3:]]
    else:
        temp = sys.argv[3].strip("0x")
        cdb_in_str = [temp[i:i+2] for i in range(0, len(temp), 2)]
    parsed_cdb = parse_cmd_plugin["cdb"]([int(i, 16) for i in cdb_in_str])
    print ("Command CDB:    %s" % ' '.join(cdb_in_str))
    print ("Command Opcode: 0x%s" % cdb_in_str[0])  # cdb[0] is usually the Opcode
    print ("")
    for spec_name,cdb_desp in parsed_cdb.items():
        print ("-"*30)
        print ("Command in Spec: %s" % spec_name)
        print ("Command Name:    %s" % cdb_desp['cdb_name'])
        print ("")
        for k,v in cdb_desp['cdb'].items():
            print ("%-20s: %s" % (k,v))
    return 0

def _sense_code():
    usage="usage: %prog parse-cmd sense-code sense-key/asc/ascq or asc/ascq"
    parser = optparse.OptionParser(usage)
    if len(sys.argv) < 4:
        parser.error("Please input the sense-code")
    if "/" in sys.argv[3]:
        args = [int(i.strip(), 16) for i in sys.argv[3].split("/")]
    elif ":" in sys.argv[3]:
        args = [int(i.strip(), 16) for i in sys.argv[3].split(":")]
    if len(args) == 3:
        res = parse_cmd_plugin["sense_code"](args[1], args[2], args[0])
        sense_key = "%X" % args[0]
        asc = "%X" % args[1]
        ascq = "%X" % args[2]
        print ("Sense Key=0x%s,      %s" % (sense_key.zfill(2), res[1]))
        print ("ASC=0x%s, ASCQ=0x%s, %s" % (asc.zfill(2), ascq.zfill(2), res[0] if res[0] else "NA"))
    elif len(args) == 2:
        res = parse_cmd_plugin["sense_code"](*args)
        asc = "%X" % args[0]
        ascq = "%X" % args[1]
        print ("ASC=0x%s, ASCQ=0x%s, %s" % (asc.zfill(2), ascq.zfill(2), res if res else "NA"))
    else:
        parser.error("sense-code should sense-key/asc/ascq or asc/ascq")
    return 0


plugin_parse_cmd_commands_dict = {"cdb": _cdb,
                                 "sense-code": _sense_code,
                                 "version": _parse_cmd_print_ver,
                                 "help": _parse_cmd_print_help,}


def parse_cmd():
    if len(sys.argv) > 2:
        plugin_command = sys.argv[2]
        if plugin_command in plugin_parse_cmd_commands_dict:
            plugin_parse_cmd_commands_dict[plugin_command]()
            return
    _parse_cmd_print_help()
    return 0
