# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmdlib import os_type
from pydiskcmdlib.command_utils import CommandWrapper

if os_type == "Windows":
    from pydiskcmdlib.device.win_device import WinIOCTLDevice,BytesReturnedStruc
    from pydiskcmdlib.exceptions import *

    class CSMIDevice(WinIOCTLDevice):
        def __init__(self, 
                     device,
                     readwrite=True,
                     detect_replugged=True):
            super(CSMIDevice, self).__init__(device, readwrite, detect_replugged)

        def execute(self, cmd: CommandWrapper):
            """
            execute a IOCTL command

            :param cmd: a Command Structure
            """
            if not cmd.cdb:
                raise CommandDataStrucError("Invalid Command Data Structure %s" % cmd.cdb)
            ## execute
            cmd._bytes_returned = BytesReturnedStruc(0)
            result = WinIOCTLDevice.execute(self, 
                                            cmd.req_id,   #
                                            cmd.cdb,
                                            cmd.cdb,
                                            BytesReturned=BytesReturnedStruc(0))
            cmd._ioctl_result = result
            return cmd