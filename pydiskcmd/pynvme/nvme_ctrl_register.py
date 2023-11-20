# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmd.system.os_tool import os_type
from pydiskcmd.exceptions import CommandNotSupport

if os_type == "Linux":
    from pydiskcmd.pypci.linux_pcie_lib import PCIeNVMeBar
elif os_type == "Windows":
    from pydiskcmd.pypci.windows_pcie_lib import PCIeNVMeBar
else:
    raise NotImplementedError("%s not support" % os_type)
