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
        self.add_sub_code({0: 'Subcode 0x0',
                           1: 'Subcode 0x1',
                           2: 'Subcode 0x2',
                           3: 'Subcode 0x3',
                           4: 'Subcode 0x4',
                           5: 'Subcode 0x5',
                           6: 'Subcode 0x6',
                           7: 'Subcode 0x7',
                           8: 'Subcode 0x8',
                           9: 'Subcode 0x9',
                           10: 'Subcode 0xa',
                           11: 'Subcode 0xb',
                           12: 'Subcode 0xc',
                           13: 'Subcode 0xd',
                           14: 'Subcode 0xe',
                           15: 'Subcode 0xf',})


class FunctionErrorCode(ExitCode):
    def __init__(self):
        super(FunctionErrorCode, self).__init__(13, 'Function Error')
        self.add_sub_code({0: 'Common Error',
                           1: 'Function Not Implement',
                           15: 'Unknown Error',})

ExitCodeInfo = {13: FunctionErrorCode(),
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


class UserDefinedError(BaseError):
    def __init__(self, message, subcode):
        super(UserDefinedError, self).__init__(message, 14, subcode)

class FunctionNotImplementError(BaseError):
    def __init__(self, message):
        super(FunctionNotImplementError, self).__init__(message, 13, 1)

