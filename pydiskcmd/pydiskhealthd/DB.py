# SPDX-FileCopyrightText: 2014 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import os
import base64
from pydiskcmd.pydiskhealthd.some_path import SMARTTracePath
_db_file = os.path.join(SMARTTracePath, "tinydb_trace.json")

_has_tinydb = False
try:
    from tinydb import TinyDB,where
    _has_tinydb = True
except ModuleNotFoundError:
    pass


def encode_byte(b):
    temp = base64.b64encode(b)
    return temp.decode()

def decode_str(string):
    temp = string.encode()
    return base64.b64decode(temp)


class MyTinyTable(object):
    def __init__(self, table, max_entry=10000):
        self.__table = table
        self.__max_entry = max_entry + 2
        ## this is a snapshoot data, flush to database every self.__metadata_flush_num
        self.__metadata_flush_num = 10
        self.__metadata_flush_index = 0
        self.__metadata = {"doc_id": 1, "rollover": False}
        ##
        temp = self.__table.get(doc_id=1)
        if temp:
            self.__metadata.update(temp)
            self._locate_accurate_meta()
        else:
            self.__table.insert(self.__metadata)

    @property
    def table(self):
        return self.__table

    def get_next_doc_id(self, doc_id):
        temp = doc_id + 1
        if temp >= self.__max_entry:
            temp = 2
        return temp

    def _locate_accurate_meta(self):
        doc_id = self.__metadata["doc_id"]
        if doc_id > 1:
            last_doc = self.__table.get(doc_id=doc_id)
            if last_doc and last_doc.get("time"):
                last_doc_time = last_doc["time"]
                el = self.__table.search(where("time") > last_doc_time)
                if el:
                    ## relocate, by search the max time
                    max_time = 0
                    for e in el:
                        max_time = max(max_time, e["time"])
                    ##
                    e = self.__table.get(where('time') == max_time)
                    self.__metadata["doc_id"] = e.doc_id
                    next_doc_id = self.get_next_doc_id(e.doc_id)
                    if self.__table.contains(doc_id=next_doc_id):
                        self.__metadata["rollover"] = True

    def insert(self, d):
        _doc_id = self.get_next_doc_id(self.__metadata["doc_id"])
        if _doc_id <= self.__metadata["doc_id"]:
            self.__metadata["rollover"] = True
        if self.__metadata["rollover"]:
            ## update
            self.__table.update(d, doc_ids=[_doc_id,])
            self.__metadata["doc_id"] = _doc_id
        else:
            self.__metadata["doc_id"] = self.__table.insert(d)
        ## snapshoot a metadata to DB.
        if self.__metadata_flush_index < self.__metadata_flush_num:
            self.__metadata_flush_index += 1
        else:
            self.__table.update(self.__metadata, doc_ids=[1,])
            self.__metadata_flush_index = 0


class MyTinyDB(object):
    def __init__(self, db_file=_db_file, max_entry_per_disk=10000):
        self.__db_file = db_file
        self.__max_entry_per_disk = max_entry_per_disk
        ##
        self.db = TinyDB(self.__db_file)
        ##
        self.__disk_trace_pool = {}

    @property
    def db_file(self):
        return self.__db_file

    def get_table_by_id(self, dev_id):
        if dev_id not in self.__disk_trace_pool:
            self.__disk_trace_pool[dev_id] = MyTinyTable(self.db.table(dev_id), max_entry=self.__max_entry_per_disk)
        return self.__disk_trace_pool.get(dev_id)

    def update_smart(self, dev_id, smart):
        table = self.get_table_by_id(dev_id)
        table.insert(smart)


if _has_tinydb:
    my_tinydb = MyTinyDB()
else:
    my_tinydb = None
