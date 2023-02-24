# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmd.system.env_var import os_type
if os_type == "Windows":
    import ctypes
    ##
    def scan_all_physical_drive():
        '''
        function from smartie project:
        https://github.com/TkTech/smartie
        
        smartie.device.get_all_devices()
        '''
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
        
        device_name = ''
        count = 0
        for i in devices:
            if i != '\x00':
                device_name += i
                if count > 0:
                    count = 0
            else:
                # first check if we need
                if device_name.startswith('PhysicalDrive'):
                    yield (f'\\\\.\\%s' % device_name)
                device_name = ''
                count += 1
                if count > 100:
                    break
        return