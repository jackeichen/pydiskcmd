# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later

import os
from pydiskcmdcli import os_type
from .bash_pydiskcmd_completion import get_completion

os_completion_path = "/etc/bash_completion.d/"
os_completion_file = os.path.join(os_completion_path, "bash-pydiskcmd-completion.sh")

def update_pydiskcmd_completion():
    if os.path.exists(os_completion_path):
        ## update bash-pydiskcmd-completion.sh
        if os.path.exists(os_completion_file):
            print ("Will Overwrite Old bash completion")
        with open(os_completion_file, 'w') as f:
            f.write(get_completion())
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
