# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later

def enum_find(enum_obj, **kwargs):
    if "value" in kwargs:
        for e in enum_obj:
            if kwargs["value"] == e.value:
                return e
    elif "name" in kwargs:
        for e in enum_obj:
            if kwargs["name"] == e.name:
                return e
