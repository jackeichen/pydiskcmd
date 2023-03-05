# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import os
from pydiskcmd.system.env_var import os_type 

def check_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

if os_type == "Linux":
    DiskTracePath = "/var/log/pydiskcmd/disk_trace/"
    check_dir(DiskTracePath)
elif os_type == "Windows":
    DiskTracePath = "C:\\Windows\\Temp\\pydiskcmd\\disk_trace\\"
    check_dir(DiskTracePath)
