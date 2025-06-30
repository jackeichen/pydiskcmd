# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmdlib import os_type
from pydiskcmdlib.command_utils import CommandWrapper

if os_type == "Windows":
    from pydiskcmdlib.device.win_device import WinIOCTLDevice
    from pydiskcmdlib.exceptions import *
    from pydiskcmdlib import log

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
            log.debug("CSMIDevice execute Request %#x, cmd: %s" % (cmd.req_id, ' '.join(['%#x' % i for i in cmd.cdb_struc])))
            ## execute
            cmd.ioctl_result = WinIOCTLDevice.execute(self, 
                                                      cmd.req_id,   #
                                                      cmd.cdb,
                                                      cmd.cdb,
                                                      BytesReturned=cmd.bytes_returned,
                                                      Overlapped=cmd.over_lapped,
                                                      raise_if_fail=False)
            log.debug("CSMIDevice execute done. Ioctl Result %d, BytesReturned=%#x" % (cmd.ioctl_result, cmd.bytes_returned.return_bytes))
            return cmd
