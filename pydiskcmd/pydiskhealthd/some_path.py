# SPDX-FileCopyrightText: 2014 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import os

def check_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

DiskTracePath = "/var/log/pydiskcmd/disk_trace/"
check_dir(DiskTracePath)
