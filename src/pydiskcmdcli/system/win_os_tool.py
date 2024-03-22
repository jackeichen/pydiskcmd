# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmdlib import os_type
import ctypes
    ##

def is_winAdmin():
    '''
    Checks for a windows admin user
    '''
    try:
        if ctypes.windll.shell32.IsUserAnAdmin() == 0:
            return False
    except:
        pass
    return True

def scan_all_physical_drive(device_type='PhysicalDrive'):
    '''
    function from smartie project:
    https://github.com/TkTech/smartie
    
    smartie.device.get_all_devices()

    device_type: PhysicalDrive | Scsi
    '''
    if os_type != "Windows":
        raise RuntimeError("Function Only Windows Support")
    ## init kernel32 object
    k32 = ctypes.WinDLL('kernel32', use_last_error=True)
    ##
    devices = ctypes.create_unicode_buffer(65536)
    # QueryDosDevice will return a list of NULL-terminated strings as a
    # binary blob. Each string is the name of a device (usually hundreds
    # on the typical desktop) that we may or may not care about.
    # The function returns the number of bytes it actually wrote to
    # `devices`.
    bytes_written = k32.QueryDosDeviceW(
        None,
        devices,
        ctypes.sizeof(devices)
    )
    if bytes_written == 0:
        raise RuntimeError('')
    
    if device_type == 'PhysicalDrive':
        def check_name(device_name):
            return device_name.startswith('PhysicalDrive')
    elif device_type == 'Scsi':
        def check_name(device_name):
            return (device_name.startswith('Scsi') and device_name.endswith(":"))
    else:
        def check_name(device_name):
            return False

    device_name = ''
    count = 0
    for i in devices:
        if i != '\x00':
            device_name += i
            if count > 0:
                count = 0
        else:
            # first check if we need
            if check_name(device_name):
                yield (f'\\\\.\\%s' % device_name)
            device_name = ''
            count += 1
            if count > 100:
                break
    return
