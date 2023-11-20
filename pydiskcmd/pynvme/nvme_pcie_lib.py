# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmd.system.os_tool import os_type

if os_type == "Linux":
    from pydiskcmd.pypci.linux_pcie_lib import NVMePCIe,PCIeNVMeBar
elif os_type == "Linux":
    from pydiskcmd.pypci.windows_pcie_lib import NVMePCIe,PCIeNVMeBar
else:
    raise NotImplementedError("%s Not Support" % os_type)
