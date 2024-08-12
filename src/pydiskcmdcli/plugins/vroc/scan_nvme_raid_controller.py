# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmdcli.system.win_os_tool import scan_all_physical_drive
from pydiskcmdlib.utils import init_device
try:
    from pydiskcmdlib.vroc.nvme_raid import RaidController  # noqa
    VROC_ENABLE = True
except ModuleNotFoundError:
    VROC_ENABLE = False

def scan_nvme_raid_controller():
    for device in scan_all_physical_drive(device_type='Scsi'):
        try:
            device = init_device(device, open_t='vroc')
            raid_controller = RaidController(device)
            yield raid_controller
        except Exception as e:
            # import traceback
            # traceback.print_exc()
            # print ("Device %s occur error: %s" % (device, str(e)))
            device.close()
    return
