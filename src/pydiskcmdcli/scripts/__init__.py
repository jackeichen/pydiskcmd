# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import sys
import time
from pydiskcmdcli.system.os_tool import checkAdmin
from pydiskcmdcli.exceptions import UserDefinedError
from pydiskcmdlib import log as lib_log
from pydiskcmdcli import log as cli_log
from pydiskcmdlib.log import set_debug_mode

__all__ = []

def parser_update(parser, add_output=[], add_force=False, add_debug=True):
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

def script_check(options, danger_check=False, admin_check=False, delay_act=False, debug_check=True):
    if admin_check:
        if not checkAdmin():
            e = UserDefinedError("Script required root or admin permissions to run!", 10)
            print (str(e))
            print ("")
            sys.exit(e.exit_code)
    if danger_check and hasattr(options, 'force') and (not options.force):
        if delay_act:
            try:
                for i in range(3):
                    print ("This is a dangerous operation, it will continue after 15s. You can break with CTRL+C")
                    print ("Time remained: %ds" % (15-i*5))
                    time.sleep(5)
                    print ("")
            except KeyboardInterrupt:
                e = UserDefinedError("Operation exit", 12)
                print (str(e))
                print ("")
                sys.exit(e.exit_code)
            except Exception as _e:
                e = UserDefinedError(str(_e), 15)
                print (str(e))
                print ("")
                sys.exit(e.exit_code)
        else:
            while True:
                answer = input("This is a dangerous operation, may destroy the data on disk, continue(yes/no): ")
                answer = answer.strip().lower()
                if answer in ('y', 'yes'):
                    break
                elif answer in ('n', 'no'):
                    e = UserDefinedError("Canceled by user", 11)
                    print (str(e))
                    print ("")
                    sys.exit(e.exit_code)
                else:
                    print ("Wrong input")
                    print ("")
    if debug_check and options.debug:
        set_debug_mode(lib_log)
        set_debug_mode(cli_log)
    return 0

def func_debug_info(func):
    def decorator(*args, **kwargs):
        start_t = time.time()
        ret = func(*args, **kwargs)
        cli_log.debug("Function %s used %s seconds" % (func.__qualname__, (time.time() - start_t)))
        return ret
    return decorator




