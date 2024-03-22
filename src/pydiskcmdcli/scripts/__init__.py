# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import sys
import time
from pydiskcmdcli.system.os_tool import checkAdmin

__all__ = []

ExitCode = {0: "Success",
            1: "Common Error",
            10: "privilege limited",
            11: "Operation Cancelled",
            12: "KeyboardInterrupt Detect",
            255: "Unkown Error",
            }

def parser_update(parser, add_output=[], add_force=False, add_debug=False):
    if add_output:
        parser.add_option("-o", "--output-format", type="choice", dest="output_format", action="store", choices=add_output, default=add_output[0],
            help="Output format: %s, default %s" % ('|'.join(add_output), add_output[0]))
    if add_force:
        parser.add_option("", "--force", dest="force", action="store_true", default=False,
            help="Continue operate without dangerous hint")
    if add_debug:
        parser.add_option("", "--debug", dest="debug", action="store_true", default=False,
            help="Set debug mode")
    return parser

def script_check(options, danger_check=False, admin_check=False, delay_act=False):
    if admin_check:
        if not checkAdmin():
            print ("ERROR - Script required root or admin permissions to run!")
            print ("")
            sys.exit(10)
    if danger_check and not options.force:
        if delay_act:
            try:
                for i in range(3):
                    print ("This is a dangerous operation, it will continue after 15s. You can break with CTRL+C")
                    print ("Time remained: %ds" % (15-i*5))
                    time.sleep(5)
                    print ("")
            except KeyboardInterrupt:
                print ("")
                print ("Operation exit")
                sys.exit(12)
            except Exception as e:
                sys.exit(255)
        else:
            while True:
                answer = input("This is a dangerous operation, may destroy the data on disk, continue(yes/no): ")
                answer = answer.strip().lower()
                if answer in ('y', 'yes'):
                    break
                elif answer in ('n', 'no'):
                    sys.exit(11)
                else:
                    print ("Wrong input")
                    print ("")
    return 0
