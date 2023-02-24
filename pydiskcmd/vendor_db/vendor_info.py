# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
###
# VendorInfo:
#    key: should be the id of the disks, (ModelPattern, UUID)
#
#
#
#
#
###
from pydiskcmd.vendor_db.samsung import PM9A3


all_disks = []
all_disks.append(PM9A3)

VendorInfo = {}
for i in all_disks:
    obj = i()
    VendorInfo[obj.match_id] = obj
