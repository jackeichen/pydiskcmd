# SPDX-FileCopyrightText: 2014 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import os

def check_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

SMARTTracePath = "/var/log/pydiskcmd/smart_trace/"
check_dir(SMARTTracePath)
