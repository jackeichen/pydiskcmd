# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later

import os
import shutil
import inspect
from pydiskcmd.system.env_var import os_type

os_completion_path = "/etc/bash_completion.d/"
os_completion_file = os.path.join(os_completion_path, "bash-pydiskcmd-completion.sh")

def update_pydiskcmd_completion():
    BasePath = os.path.dirname(inspect.getfile(update_pydiskcmd_completion))
    bash_pydiskcmd_completion = os.path.join(BasePath, "bash-pydiskcmd-completion.sh")
    ## upload
    if os.path.exists(os_completion_path):
        ## update bash-pydiskcmd-completion.sh
        if os.path.exists(os_completion_file):
            print ("Remove Old bash completion")
            os.remove(os_completion_file)
        shutil.copy(bash_pydiskcmd_completion, os_completion_path)
        ## then do the source
        os.system("source /usr/share/bash-completion/bash_completion")
        ##
        print ("Update script bash completion done!")
    else:
        print ("Skip update script bash completion")
    return

def enable_win_completion():
    raise NotImplementedError("Windows Function Not Ready")

def enable_cmd_completion():
    if os_type == "Linux":
        update_pydiskcmd_completion()
    elif os_type == "Windows":
        enable_win_completion()
    else:
        raise NotImplementedError("OS %s Not support" % os_type)
