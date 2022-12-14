# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmd.pydiskhealthd.DB import all_disk_info,disk_trace_pool

def get_stored_disk_info(target_dev_id=None):
    disks_info = {}
    disk_in_disk_info = all_disk_info.get_all_disks_id()
    for dev_id in disk_in_disk_info:
        if target_dev_id and dev_id != target_dev_id:
            continue
        #
        disks_info[dev_id] = all_disk_info.get_disk_info(dev_id)
    return disks_info
