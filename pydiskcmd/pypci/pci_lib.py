'''
Copyright (c) Facebook, Inc. and its affiliates.

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
'''
from pydiskcmd.system.os_tool import os_type
if os_type == "Linux":
    from pci_lib import *
    EXPRESS_SPEED.update({5: "32GT/s", 6: "64GT/s"})
else:
    raise NotImplementedError("OS: %s Not supoort Now!")

