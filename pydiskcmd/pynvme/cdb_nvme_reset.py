# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmd.system.os_tool import os_type
from pydiskcmd.exceptions import CommandNotSupport

if os_type == "Linux":
    from pydiskcmd.pynvme.nvme_command import LinCommand,build_int_by_bitmap
    ## linux command
    IOCTL_REQ = LinCommand.linux_req.get("NVME_IOCTL_RESET")
    class Reset(LinCommand):
        def __init__(self):
            super(Reset, self).__init__(IOCTL_REQ)

elif os_type == "Windows":
    from pydiskcmd.pynvme.nvme_command import WinCommand
    class Reset(WinCommand):
        def __init__(self, *args, **kwargs):
            raise CommandNotSupport("Reset Not Support")
else:
    raise NotImplementedError("%s not support" % os_type)
