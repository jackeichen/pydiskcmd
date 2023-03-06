# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later

import os
import sys
import inspect
from pydiskcmd.system.env_var import os_type
from pydiskcmd.system.os_tool import check_dir_path

etc_file_absolute_path = "/etc/sysconfig/pydiskhealthd"
systemd_absolute_path = "/usr/lib/systemd/system/pydiskhealthd.service"
## win path
win_base_path = "C:\\Program Files\\pydiskcmd"
win_etc_file_absolute_path = os.path.join(win_base_path, "pydiskhealthd")
##

def enable_systemd_pydiskhealthd():
    systemd_file_in = os.path.join(CurrentBasePath, "pydiskhealthd.service")
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
    CurrentBasePath = os.path.dirname(inspect.getfile(enable_systemd_pydiskhealthd))
    etc_file_in = os.path.join(CurrentBasePath, "pydiskhealthd.cfg")
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
    ##
    check_dir_path(win_base_path, create_if_not_exist=True)
    CurrentBasePath = os.path.dirname(inspect.getfile(enable_schtasks))
    etc_file_in = os.path.join(CurrentBasePath, "pydiskhealthd.cfg")
    if os.path.isfile(etc_file_in):
        with open(etc_file_in, "r") as f:
            content = f.read()
        print ("The bellow text will be write: ")
        print ("*"*60)
        print (content)
        print ("*"*60)
        with open(win_etc_file_absolute_path, "w") as f:
            f.write(content)
        print ("Write pydiskhealthd service config file(%s) Done!" % win_etc_file_absolute_path)
    ##
    pydiskhealthd_path = os.path.join(os.path.dirname(sys.executable), "Scripts", "pydiskhealthd.exe")
    ##
    if os.path.isfile(pydiskhealthd_path):
        cmd = '''schtasks /create /TN "pydiskhealthd" /RU SYSTEM /SC ONSTART /DELAY 0000:10 /TR "'%s' --config_file='%s'"''' % (pydiskhealthd_path, win_etc_file_absolute_path)
        os.system(cmd)
        print ("")
        print ("Windows schtasks name: pydiskhealthd")
    else:
        pritn ("Failed: cannot find executable pydiskhealthd command!")
    return

def diable_schtasks():
    cmd = 'schtasks /delete /F /TN "pydiskhealthd"'
    return os.system(cmd)

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