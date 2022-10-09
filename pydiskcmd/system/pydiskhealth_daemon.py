# SPDX-FileCopyrightText: 2014 The python-scsi Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later

import os
import inspect


etc_file_absolute_path = "/etc/sysconfig/pydiskhealthd"
systemd_absolute_path = "/usr/lib/systemd/system/pydiskhealthd.service"

def enable_systemd_pydiskhealthd():
    BasePath = os.path.dirname(inspect.getfile(enable_systemd_pydiskhealthd))
    ##
    systemd_file_in = os.path.join(BasePath, "pydiskhealthd.service")
    if os.path.isfile(systemd_file_in):
        with open(systemd_file_in, "r") as f:
            content = f.read()
        print ("The bellow text will be write: ")
        print ("*"*60)
        print (content)
        print ("*"*60)
        with open(systemd_absolute_path, "w") as f:
            f.write(content)
        print ("Write systemd service file(%s) Done!" % systemd_absolute_path)
    else:
        print ("No systemd service file in program")
    ##
    print ("")
    etc_file_in = os.path.join(BasePath, "pydiskhealthd.cfg")
    if os.path.isfile(etc_file_in):
        with open(etc_file_in, "r") as f:
            content = f.read()
        print ("The bellow text will be write: ")
        print ("*"*60)
        print (content)
        print ("*"*60)
        with open(etc_file_absolute_path, "w") as f:
            f.write(content)
        print ("Write systemd service config file(%s) Done!" % etc_file_absolute_path)
    else:
        print ("No systemd service config file in program")
    print ("")
    ##
    os.system("systemctl daemon-reload")
    os.system("systemctl enable pydiskhealthd.service")
    os.system("systemctl start pydiskhealthd.service")
    os.system("systemctl status pydiskhealthd.service")
    return
