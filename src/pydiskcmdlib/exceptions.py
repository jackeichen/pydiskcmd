# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from typing import Optional

class CodeDescription(object):
    def __init__(self, code, description):
        self.code = code
        self.description = description

class ExitCode(CodeDescription):
    def __init__(self, code: int, description: str):
        super(ExitCode, self).__init__(code, description)
        self.subcode = {}

    def add_sub_code(self, kwargs):
        for k,v in kwargs.items():
            self.subcode[k] = CodeDescription(k, v)

    def get_exit_code(self, subcode: Optional[int]=None) -> int:
        code = self.code
        if subcode in self.subcode:
            code += (subcode << 4)
        return code

    def get_full_descrption(self, message: str,  subcode: Optional[int]=None) -> str:
        return message + \
            " (Based on %s:%#x" % (self.description, self.code) + \
            ", %s:%#x)" % (self.subcode[subcode].description, subcode) if subcode in self.subcode else ")"

# no use, here to show the occupied code/subcode
# Exit code 0 means success
class SuccessCode(ExitCode):
    def __init__(self):
        super(SuccessCode, self).__init__(0, 'Success')
        self.add_sub_code({0: 'Success'})


class CommonErrorCode(ExitCode):
    '''
    code:    0
    subcode: from 1 to 0xF, 0 is used by success
    '''
    def __init__(self):
        super(CommonErrorCode, self).__init__(0, 'Common Error')
        self.add_sub_code({15: 'subcode',})


class DeviceOperationErrorCode(ExitCode):
    def __init__(self):
        super(DeviceOperationErrorCode, self).__init__(3, 'Device Operation Error')
        self.add_sub_code({0: 'Common Error',
                           1: 'Device Not Found',
                           2: 'Device Type Error',
                           3: 'Device Open Failed',
                           15: 'Unknown Error'})


class CommandBuildErrorCode(ExitCode):
    def __init__(self):
        super(CommandBuildErrorCode, self).__init__(4, 'Command Build Error')
        self.add_sub_code({0: 'Common Error',
                           1: 'Command Not Support',
                           2: 'Command Not Implement',
                           3: 'Build SCSI Command Error',
                           4: 'Build ATA Command Error',
                           5: 'Build NVMe Command Error',
                           15: 'Unknown Error'})


class CommandExecuteErrorCode(ExitCode):
    def __init__(self):
        super(CommandExecuteErrorCode, self).__init__(5, 'Command Execute Error')
        self.add_sub_code({0: 'Common Error',
                           1: 'Command Sequence Error',
                           15: 'Unknown Error'})


class CheckCommandReturnStatusErrorCode(ExitCode):
    def __init__(self):
        super(CheckCommandReturnStatusErrorCode, self).__init__(6, 'Check Command Return Status Error')
        self.add_sub_code({0: 'Common Error',
                           1: 'Sense Data Error',   # SCSI Sense Data Error
                           2: 'ATA Status Return Descriptor Error',
                           3: 'CQ Status Field Error',
                           15: 'Unknown Error'})


class CheckCommandReturnDataErrorCode(ExitCode):
    def __init__(self):
        super(CheckCommandReturnDataErrorCode, self).__init__(7, 'Check Command Return Data Error')
        self.add_sub_code({0: 'Common Error',
                           15: 'Unknown Error'})



ExitCodeInfo = {0: CommonErrorCode(),
                # 1: 'reserved for future use', 
                # 2: 'reserved for future use',
                3: DeviceOperationErrorCode(),
                4: CommandBuildErrorCode(),
                5: CommandExecuteErrorCode(),
                6: CheckCommandReturnStatusErrorCode(),
                7: CheckCommandReturnDataErrorCode(),
                # 8: 'reserved for future use',
                # 9: 'reserved for future use',
                # 10: 'reserved for future use',
                # 11: 'reserved for future use',
                }


class BaseError(Exception):
    def __init__(self, message: str, code: int, subcode: Optional[int]=None):
        self.message = message
        # exit_code = (code, subcode)
        self._code = code
        self._subcode = subcode
        self._error_description = ExitCodeInfo.get(self._code)

    def __str__(self):
        if self._error_description:
            return self._error_description.get_full_descrption(self.message, self._subcode)
        else:
            return self.message

    @property
    def exit_code(self):
        return (self._code + (self._subcode << 4) if self._subcode is not None else self._code)


class DeviceTypeError(BaseError):
    def __init__(self, message):
        super(DeviceTypeError, self).__init__(message, 3, 2)

class CommandNotSupport(BaseError):
    def __init__(self, message):
        super(CommandNotSupport, self).__init__(message, 4, 1)

class CommandNotImplement(BaseError):
    def __init__(self, message):
        super(CommandNotSupport, self).__init__(message, 4, 2)

class CommandDataStrucError(BaseError):
    def __init__(self, message):
        super(CommandDataStrucError, self).__init__(message, 4, 0)

class ProtocolSettingError(BaseError):
    def __init__(self, message):
        super(ProtocolSettingError, self).__init__(message, 4, 0)

class BuildSCSICommandError(BaseError):
    def __init__(self, message):
        super(BuildSCSICommandError, self).__init__(message, 4, 3)

class BuildNVMeCommandError(BaseError):
    def __init__(self, message):
        super(BuildNVMeCommandError, self).__init__(message, 4, 5)

class ExecuteCmdErr(BaseError):
    def __init__(self, message):
        super(ExecuteCmdErr, self).__init__(message, 5, 0)

class CommandSequenceError(BaseError):
    def __init__(self, message):
        super(CommandSequenceError, self).__init__(message, 5, 1)

class CommandReturnStatusError(BaseError):
    def __init__(self, message):
        super(CommandReturnStatusError, self).__init__(message, 6, 0)

class SenseDataCheckErr(BaseError):
    def __init__(self, message):
        super(SenseDataCheckErr, self).__init__(message, 6, 1)

class CommandReturnDataError(BaseError):
    def __init__(self, message):
        super(CommandReturnDataError, self).__init__(message, 7, 0)
