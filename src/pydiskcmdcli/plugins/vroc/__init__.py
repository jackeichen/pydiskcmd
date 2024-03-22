# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from .scan_nvme_raid_controller import (
    VROC_ENABLE,
    scan_nvme_raid_controller,
)

vroc_plugin = {"scan_nvme_raid_controller": scan_nvme_raid_controller,
               }
