# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later

import os
import inspect
from pydiskcmd.system.env_var import os_type

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

def disable_systemd_pydiskhealthd():
    os.system("systemctl stop pydiskhealthd.service")
    os.system("systemctl disable pydiskhealthd.service")
    os.system("systemctl status pydiskhealthd.service")
    return

def enable_schtasks():
    raise NotImplementedError("Windows Function Not Ready")

def diable_schtasks():
    raise NotImplementedError("Windows Function Not Ready")

def enable_starup_programe():
    if os_type == "Linux":
        enable_systemd_pydiskhealthd()
    elif os_type == "Windows":
        enable_schtasks()
    else:
        raise NotImplementedError("OS %s Not support" % os_type)

def disable_starup_programe():
    if os_type == "Linux":
        disable_systemd_pydiskhealthd()
    elif os_type == "Windows":
        diable_schtasks()
    else:
        raise NotImplementedError("OS %s Not support" % os_type)