# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmd.system.os_tool import os_type
from pydiskcmd.exceptions import CommandNotSupport

if os_type == "Linux":
    from pydiskcmd.pynvme.nvme_command import LinCommand
    ## linux command
    IOCTL_REQ = LinCommand.linux_req.get("NVME_IOCTL_SUBSYS_RESET")
    class SubsysReset(LinCommand):
        def __init__(self):
            super(SubsysReset, self).__init__(IOCTL_REQ)

elif os_type == "Windows":
    from pydiskcmd.pynvme.nvme_command import WinCommand
    class SubsysReset(WinCommand):
        def __init__(self, *args, **kwargs):
            raise CommandNotSupport("SubsysReset Not Support")
else:
    raise NotImplementedError("%s not support" % os_type)
