# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmdcli.system.win_os_tool import scan_all_physical_drive
from pydiskcmdlib.utils import init_device
from pydiskcmdlib.csmi.csmi_controller import CSMIController  # noqa

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
    for device in scan_all_physical_drive(device_type='Scsi'):
        try:
            device = init_device(device, open_t='csmi')
            raid_controller = CSMIController(device)
            # try to send get_driver_info command,
            # if success, then should be CSMI Controller
            raid_controller.get_driver_info()
            yield raid_controller
        except Exception as e:
            # import traceback
            # traceback.print_exc()
            # print ("Device %s occur error: %s" % (device, str(e)))
            device.close()
    return
