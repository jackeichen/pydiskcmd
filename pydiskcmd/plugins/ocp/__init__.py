# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from .cdb_ocp_get_log_page import (SmartExtendedLog,
                                   ErrorRecoveryLog,
                                   )

ocp_plugin = {"SmartExtendedLog": SmartExtendedLog,
              "ErrorRecoveryLog": ErrorRecoveryLog,
              }
