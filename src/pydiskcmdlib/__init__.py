# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import platform
os_type = platform.system()
import sys
local_byteorder = sys.byteorder
##
from .__version__ import version_format,version
from .pyscsi import *
from .pynvme import *
from .pysata import *
from .pypci import *
from .utils import *
