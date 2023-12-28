# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later

import os
import time
import subprocess
from pydiskcmd.system.env_var import os_type
from pydiskcmd.system.lin_os_tool import get_block_devs,get_nvme_dev_info
from pydiskcmd.system.lin_os_tool import SystemdNotify,get_nvme_block_dev_by_ctrl_id,scan_nvme_system,NVMeController
###

def timeit(func):
    def wrap(*args, **kwargs):
        start_time = time.time()
        print (f'{func.__name__} starting')
        result = func(*args, **kwargs)
        elapsed = time.time() - start_time
        print (f'{func.__name__} complete. Runtime {elapsed:.10f} secs')
        return result
    return wrap

def check_device_exist(dev_path):
    if os_type == "Linux":
        return os.path.exists(dev_path)
    elif os_type == "Windows":
        return True
    return True

def check_dir_path(dir_path, create_if_not_exist=False):
    if not os.path.isdir(dir_path):
        if create_if_not_exist:
            os.makedirs(dir_path)
        else:
            return False
    return True

def read_kv_file(file_path, target_key_strip=(), target_value_strip=()):
    if os.path.isfile(file_path):
        target = {}
        with open(file_path, 'r') as f:
            while True:
                temp = f.readline()
                if not temp:
                    break
                temp = temp.strip()
                index = temp.find("#")
                if index > 0:
                    temp = temp[0:index]
                elif index == 0:
                    continue
                target_index = temp.find("=")
                if target_index > 0:
                    key = temp[0:target_index]
                    for i in target_key_strip:
                        key = key.strip(i)
                    value = temp[target_index+1:]
                    for i in target_value_strip:
                        value = value.strip(i)
                    target[key] = value
        return target

def check_backaround_running():
    if os_type == "Linux":
        ##
        proc = subprocess.Popen(["pgrep", "-l", "-f", "pydiskhealthd"], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        proc.wait()
        stdout = proc.stdout.read()
        stderr = proc.stderr.read()
        if proc.returncode == 0:
            content_all = stdout.split("\n")
            running_number = 0
            for c in content_all:
                if c:
                    temp = c.split(' ')
                    progress_id = temp[0]
                    progress_name = ' '.join(temp[1:])
                    if progress_name == "pydiskhealthd":
                        running_number += 1
            ## because you are running the pydiskheal, so count should be >= 2 if another is running
            if running_number > 1:
                print ("pydiskhealthd is running(PID %s)" % progress_id)
                return 1
        else:
            print ("Run pgrep command error, return code: %s" % proc.returncode)
            print (stderr)
            return 2
    elif os_type == "Windows":
        ##
        proc = subprocess.Popen(['tasklist', '/FI', 'imagename eq pydiskhealthd.exe'], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        proc.wait()
        stdout = proc.stdout.read()
        stderr = proc.stderr.read()
        if proc.returncode == 0:
            running_number = 0
            index = -18
            while True:
                stdout = stdout[index+18:]
                index = stdout.find("pydiskhealthd.exe")
                if index < 0:
                    break
                running_number += 1

            if running_number > 1:
                print ("pydiskhealthd is running")
                return 1
        else:
            print ("Run tasklist command error, return code: %s" % proc.returncode)
            print (stderr)
            return 2
    else:
        return 3
    return 0
