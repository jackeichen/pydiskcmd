# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
class DeviceTypeError(Exception):
    pass

class ExecuteCmdErr(Exception):
    pass

class CommandCheckErr(Exception):
    pass

class SenseDataCheckErr(Exception):
    pass

class CommandReturnStatusError(Exception):
    pass

class CommandNotSupport(Exception):
    pass

class CommandDataStrucError(Exception):
    pass

class BuildNVMeCommandError(Exception):
    pass

class BuildSCSICommandError(Exception):
    pass

class ProtocolSettingError(Exception):
    pass
