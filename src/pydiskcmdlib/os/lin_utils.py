# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import os
import re

def get_host_ids():
    host_ids = []
    if os.path.exists("/sys/class/scsi_host/"):
        for host in os.listdir("/sys/class/scsi_host/"):
            g = re.fullmatch(r"host(\d+)", host)
            if g:
                try:
                    host_id = int(g.group(1))
                except:
                    continue
                else:
                    host_ids.append(host_id)
    return host_ids
