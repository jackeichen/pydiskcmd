# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmdlib import os_type

if os_type == "Windows":
    from pydiskcmdlib.device.win_device import WinIOCTLDevice,BytesReturnedStruc
    from pydiskcmdlib.exceptions import *
    from pydiskcmdlib.command_utils import CommandWrapper
    from pydiskcmdlib import log

    class RSTDevice(WinIOCTLDevice):
        def __init__(self, 
                     device,
                     readwrite=True,
                     detect_replugged=True):
            super(RSTDevice, self).__init__(device, readwrite, detect_replugged, share_mode=0, flags_and_attributes=0)

        def execute(self, cmd: CommandWrapper):
            """
            execute a IOCTL command

            :param cmd: a Command Structure
            """
            if not cmd.cdb:
                raise CommandDataStrucError("Invalid Command Data Structure %s" % cmd.cdb)
            log.debug("RSTDevice execute Request %#x, cmd: %s" % (cmd.req_id, ' '.join(['%#x' % i for i in cmd.cdb_struc])))
            ## execute
            cmd.ioctl_result = WinIOCTLDevice.execute(self, 
                                                      cmd.req_id,   #
                                                      cmd.cdb,
                                                      cmd.cdb,
                                                      BytesReturned=cmd.bytes_returned,
                                                      Overlapped=cmd.over_lapped,
                                                      raise_if_fail=False)
            log.debug("RSTDevice execute done. Ioctl Result %d, BytesReturned=%#x" % (cmd.ioctl_result, cmd.bytes_returned.return_bytes))
            return cmd
