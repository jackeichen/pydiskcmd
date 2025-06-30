# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
#import traceback
from pydiskcmdcli.system.win_os_tool import scan_all_physical_drive
from pydiskcmdlib.utils import init_device
from pydiskcmdlib.csmi.csmi_controller import CSMIController  # noqa
from pydiskcmdlib import log

def scan_csmi_controller():
    """
    Scan for CSMI controllers and yield CSMIController objects.

    This function scans all physical drives of type 'Scsi' and attempts to
    initialize them as CSMI controllers. If successful, it sends a get_driver_info
    command to confirm the controller type. If the controller is a CSMI controller,
    it is yielded. If an exception occurs during the process, the device is closed
    and the exception is ignored.

    Yields:
        CSMIController: A CSMI controller object representing a CSMI controller.

    """
    for device_path in scan_all_physical_drive(device_type='Scsi'):
        try:
            log.debug("Checking CSMI controller for %s", device_path)
            device = init_device(device_path, open_t='csmi')
            raid_controller = CSMIController(device)
            # try to send get_driver_info command,
            # if success, then should be CSMI Controller
            cmd = raid_controller.get_driver_info()
            cmd.check_return_status(fail_hint=False, raise_if_fail=True)
            yield raid_controller
        except Exception as e:
            # traceback.print_exc()
            log.debug("Skip device %s, for occurring error: %s" % (device_path, str(e)))
            device.close()
    return
