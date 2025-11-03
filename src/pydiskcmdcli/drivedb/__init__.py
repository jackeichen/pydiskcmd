# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import os
import inspect
from pydiskcmdlib import os_type

def get_drivedb_path():
    return os.path.dirname(inspect.getfile(get_drivedb_path))

drivedb_path = get_drivedb_path()
smart_drivedb_path = os.path.join(drivedb_path, "smart_drivedb.json")
if os_type == 'Linux':
    possible_smart_drivedb_path = (smart_drivedb_path, '/etc/pydiskcmd/smart_drivedb.json')
else:
    possible_smart_drivedb_path = (smart_drivedb_path,)

def load_drivedb_file(json_file=smart_drivedb_path):
    import json
    data=[]
    if os.path.exists(json_file):
        with open(json_file, 'r') as f:
            data = json.loads(f.read())
    return data

class DriveSmartEntryAttr(object):
    def __init__(self, attr):
        self.attr_id = None
        self.attr_raw_type = ''
        self.attr_name = 'Unknown'
        self.attr_disk_type = None
        #
        if len(attr) == 3: 
            self.attr_id = int(attr[0])
            self.attr_raw_type = attr[1]
            self.attr_name = attr[2]
        elif len(attr) == 4:
            self.attr_id = int(attr[0])
            self.attr_raw_type = attr[1]
            self.attr_name = attr[2]
            self.attr_disk_type = attr[3]
        elif len(attr) == 2:
            self.attr_id = int(attr[0])
            self.attr_name = attr[1]

def get_drivedb_entry_by_mn(model, vs_smart_drivedb_path=None):
    import re
    for f in possible_smart_drivedb_path:
        if os.path.exists(f):
            vs_smart_all = load_drivedb_file(json_file=f)
            break
    else:
        raise FileNotFoundError("Can not find any drivedb file")
    if vs_smart_drivedb_path:
        vs_smart_all.extend(load_drivedb_file(json_file=vs_smart_drivedb_path))
    vs_smart = vs_smart_all[1].copy()
    vs_smart_modelregexp = (i["modelregexp"] for i in vs_smart_all)
    for index,pattern in enumerate(vs_smart_modelregexp):
        if re.match(pattern, model):
            vs_attribute = vs_smart["presets"].pop("vs_attribute") # default attribute
            vs_smart.update(vs_smart_all[index])
            vs_attribute.update(vs_smart["presets"]["vs_attribute"])
            vs_smart["presets"]["vs_attribute"] = vs_attribute
    return vs_smart
