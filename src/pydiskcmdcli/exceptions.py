# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from typing import Optional
from pydiskcmdlib.exceptions import (ExitCode,
                                     CommandNotSupport,     # used by pynvme
                                     CommandSequenceError,  # used by pynvme
)


class UserDefinedErrorCode(ExitCode):
    def __init__(self):
        super(UserDefinedErrorCode, self).__init__(14, 'User Defined Error')
        self.add_sub_code({0: 'Subcode',
                           1: 'Subcode',
                           2: 'Subcode',
                           3: 'Subcode',
                           4: 'Subcode',
                           5: 'Subcode',
                           6: 'Subcode',
                           7: 'Subcode',
                           8: 'Subcode',
                           9: 'Subcode',
                           10: 'Insufficient Privileges',
                           11: 'Operation Canceled',
                           12: 'KeyboardInterrupt Detect',
                           13: 'Subcode',
                           14: 'Subcode',
                           15: 'Unknown Error',})


class FunctionErrorCode(ExitCode):
    def __init__(self):
        super(FunctionErrorCode, self).__init__(13, 'Function Error')
        self.add_sub_code({0: 'Common Error',
                           1: 'Function Not Implement',
                           15: 'Unknown Error',})


class NonpydiskcmdErrorCode(ExitCode):
    def __init__(self):
        super(NonpydiskcmdErrorCode, self).__init__(1, 'Non-pydiskcmd Error')
        self.add_sub_code({0: 'Common Error',})

# no use, here to show the occupied code/subcode
# Exit code 2 means Command Parameters Error
class CommandParametersErrorCode(ExitCode):
    def __init__(self):
        super(CommandParametersErrorCode, self).__init__(2, 'Command Parameters Error')
        self.add_sub_code({0: 'CLI Programe Error'})


ExitCodeInfo = {1: NonpydiskcmdErrorCode(),
                13: FunctionErrorCode(),
                14: UserDefinedErrorCode(),
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


class NonpydiskcmdError(BaseError):
    def __init__(self, message):
        super(NonpydiskcmdError, self).__init__(message, 1, 0)

class UserDefinedError(BaseError):
    def __init__(self, message, subcode):
        super(UserDefinedError, self).__init__(message, 14, subcode)

class FunctionNotImplementError(BaseError):
    def __init__(self, message):
        super(FunctionNotImplementError, self).__init__(message, 13, 1)
