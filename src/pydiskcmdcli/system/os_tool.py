# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later

import os
import time
from pydiskcmdcli import os_type
###
def checkAdmin():
    '''
    Checks if the script is runnin under admin permissions
    '''
    if os_type == 'Windows':
        from .win_os_tool import is_winAdmin
        return is_winAdmin()
    elif os_type == 'Linux':
        from .lin_os_tool import is_linuxAdmin
        return is_linuxAdmin()
    return True

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
    return False

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
