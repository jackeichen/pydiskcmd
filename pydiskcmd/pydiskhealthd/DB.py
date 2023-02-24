# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import os
import json
import time
import base64
import sqlite3
from pydiskcmd.pydiskhealthd.some_path import DiskTracePath

#####
_sqlite3_db_file = os.path.join(DiskTracePath, "sqlite3_disk_trace.db")
_sqlite3_diskinfo_file = os.path.join(DiskTracePath, "sqlite3_disk_info.db")
_LastActiveDiskFile = os.path.join(DiskTracePath, "LastActiveDisks.json")
#####

def encode_byte(b):
    temp = base64.b64encode(b)
    return temp.decode()

def decode_str(string):
    temp = string.encode()
    return base64.b64decode(temp)


class SQLiteTable(object):
    '''
    Must create table first 
    '''
    def __init__(self, parent, table_name, max_entry=2000):
        self.__cursor = parent._cursor
        self.__conn = parent._conn
        self.__table_name = table_name
        self.__max_entry = max_entry
        ##
        self.__current_id = 0
        self.__current_tag = 0
        self.__roll_over = False
        ##
        self._table_init()

    @property
    def next_id(self):
        temp = self.__current_id + 1
        if temp >= self.__max_entry:
            temp = 0
        return temp

    @property
    def dev_id(self):
        return self.__table_name[1:]

    def run_sql(self, sql, args=(), commit=False):
        try:
            ##
            self.__cursor.execute(sql, args)
        except:
            import traceback
            traceback.print_exc()
            self.__conn.rollback()
            return 1
        else:
            ##
            if commit:
                self.__conn.commit()
        return 0

    def _table_init(self):
        ## usually first to check it by timestamp;
        sql = '''SELECT max(timestamp),ID,value_tag from %s
              ''' % self.__table_name
        self.__cursor.execute(sql)
        res = self.__cursor.fetchall()
        ## it should be only one result here,
        #  but still get the last one.
        if res[-1] and res[-1][0] is not None:  # it's Not a empty table
            timestamp,self.__current_id,self.__current_tag = res[-1]
            ## to ensure it is the last value to update
            #  get the next id content
            sql = '''SELECT timestamp,ID,value_tag from %s WHERE ID = %d;
                  ''' % (self.__table_name, self.next_id)
            self.__cursor.execute(sql)
            res = self.__cursor.fetchone()
            if res and res[1] is not None:  # Full of max_entry
                next_timestamp,next_id,next_tag = res
                ## the tag 
                if self.__current_tag > next_tag and (self.__current_tag - next_tag) == 1:
                    ## do nothing, locate done
                    pass
                elif self.__current_tag == next_tag and next_id == 0: ## 
                    ## do nothing, locate done
                    pass
                else:  # we need locate more, the timestamp may changed by user.
                    ## We Do Not use timestamp to judge, 
                    sql = '''SELECT COUNT(*) FROM %s;
                          ''' % self.__table_name
                    self.__cursor.execute(sql)
                    res = self.__cursor.fetchone()
                    if res and res[0] == self.__max_entry:  # Full of max_entry, seek by tag
                        sql = '''SELECT timestamp,ID,value_tag from %s WHERE ID = %d OR ID = %d;
                              ''' % (self.__table_name, 0, self.__max_entry-1)
                        self.__cursor.execute(sql)
                        res = self.__cursor.fetchall()
                        temp_tag = 0
                        for i in res:
                            if i[2] is not None:
                                if temp_tag == 255 and i[2] == 0:
                                    temp_tag = 0
                                else:
                                    temp_tag = max(temp_tag, i[2])
                        ## now we get the max value_tag, continue locate
                        sql = '''SELECT timestamp,max(ID),value_tag from %s WHERE value_tag = %d;
                              ''' % (self.__table_name, temp_tag)
                        self.__cursor.execute(sql)
                        timestamp,self.__current_id,self.__current_tag = self.__cursor.fetchone()
                    else:   # not full of max_entry, seek by ID
                        sql = '''SELECT timestamp,ID,value_tag from %s WHERE ID = %d;
                              ''' % (self.__table_name, res[0]-1)
                        self.__cursor.execute(sql)
                        timestamp,self.__current_id,self.__current_tag = self.__cursor.fetchone()
            else:   # Not full of max_entry
                pass  # do nothing, locate done
        else:   # it's a empty table
            pass # do nothing, locate done
        ## set roll over
        if self.__current_tag == 0 and self.__current_id < self.__max_entry:
            self.__roll_over = False
        else:
            self.__roll_over = True

    def update_dev_info(self, timestamp, smart, last_persistent_log=None):
        ## Get next ID
        next_id = self.__current_id + 1
        current_tag = self.__current_tag
        roll_over = self.__roll_over
        if next_id >= self.__max_entry: # roll over
            roll_over = True
            next_id = 0
            current_tag += 1
            if current_tag > 255:
                current_tag = 0
        #####
        if smart:
            if roll_over:
                sql = '''UPDATE %s
                         set value_tag = %d,timestamp = %f,smart = %s
                         WHERE ID = %d
                      ''' % (self.__table_name, current_tag, timestamp, '?', next_id)
            else:
                sql = '''INSERT INTO %s (ID,value_tag,timestamp,smart)
                         VALUES (%d, %d, %f, %s)
                      ''' % (self.__table_name, next_id, current_tag, timestamp, '?')
            ###
            if self.run_sql(sql, args=(sqlite3.Binary(smart),), commit=False) == 0:
                self.__current_id = next_id
                self.__current_tag = current_tag
                self.__roll_over = roll_over
            elif not roll_over: ## timestamp may not right
                sql = '''UPDATE %s
                         set value_tag = %d,timestamp = %f,smart = %s
                         WHERE ID = %d
                      ''' % (self.__table_name, current_tag, timestamp, '?', next_id)
                if self.run_sql(sql, args=(sqlite3.Binary(smart),), commit=False) == 0:
                    self.__current_id = next_id
                    self.__current_tag = current_tag
                    self.__roll_over = roll_over
        if last_persistent_log:
            sql = '''UPDATE %s
                     set last_persistent = %s
                     WHERE ID = %d
                  ''' % (self.__table_name, '?', next_id)
            self.run_sql(sql, args=(sqlite3.Binary(last_persistent_log),), commit=False)
        self.__conn.commit()

    def get_dev_current_info(self):
        sql = '''SELECT timestamp,smart,last_persistent from %s WHERE ID = %d;
              ''' % (self.__table_name, self.__current_id)
        self.__cursor.execute(sql)
        res = self.__cursor.fetchone()
        return res

    def iter_dev_smart(self):
        sql = '''SELECT timestamp,smart from %s ORDER BY timestamp asc;
              ''' % self.__table_name
        self.__cursor.execute(sql)
        while True:
            temp = self.__cursor.fetchone()
            if temp is None:
                break
            yield temp

    def get_dev_smart_history(self):
        sql = '''SELECT timestamp,smart from %s ORDER BY timestamp asc;
              ''' % self.__table_name
        self.__cursor.execute(sql)
        return self.__cursor.fetchall()


class SQLiteDB(object):
    _disk_trace_pool = {}
    def __init__(self, db_path=_sqlite3_db_file, max_entry_per_disk=2000):
        self.__db_path = db_path
        self.__max_entry_per_disk = max_entry_per_disk
        ##
        self._conn = sqlite3.connect(self.__db_path)
        self._cursor = self._conn.cursor()

    @property
    def disk_trace_pool(self):
        return SQLiteDB._disk_trace_pool

    def get_table_name_by_dev_id(self, dev_id):
        return "S%s" % dev_id

    def _init_table_by_id(self, dev_id):
        table_name = self.get_table_name_by_dev_id(dev_id)
        ## first try to create a table
        # do nothing if exist
        sql = '''CREATE TABLE IF NOT EXISTS %s(
                 ID  INT  PRIMARY KEY     NOT NULL,
                 value_tag  INT  NOT NULL,
                 timestamp  REAL  NOT NULL,
                 smart  BLOB  NOT NULL,
                 last_persistent  BLOB);
              ''' % table_name
        self._cursor.execute(sql)
        self._conn.commit()
        return SQLiteTable(self, table_name, max_entry=self.__max_entry_per_disk)

    def get_table_by_id(self, dev_id):
        if dev_id not in self.disk_trace_pool:
            self.disk_trace_pool[dev_id] = self._init_table_by_id(dev_id)
        return self.disk_trace_pool.get(dev_id)

    def get_all_tables_name(self):
        sql = "select name from sqlite_master where type='table' order by name"
        self._cursor.execute(sql)
        tables = self._cursor.fetchall()
        return [i[0] for i in tables]

    def get_table_by_dev_id(self, dev_id):
        if dev_id in self.disk_trace_pool:
            return self.disk_trace_pool.get(dev_id)
        else:
            return self._init_table_by_id(dev_id)

    def get_smart_by_dev_id(self, dev_id):
        table = self.get_table_by_dev_id(dev_id)
        return table.iter_dev_smart()

    def get_all_disks_smart(self):
        target = {}
        for dev_id in self.get_all_tables_name():
            temp = self.get_table_by_dev_id(dev_id)
            target[dev_id] = temp.get_dev_smart_history()
        return target

    def update_all_tables_time(self, time_changed):
        for table_name in self.get_all_tables_name():
            ## 
            sql = "SELECT timestamp from %s;" % table_name
            self._cursor.execute(sql)
            ## it may use many memory?
            values = self._cursor.fetchall()
            #
            while True:
                temp = self._cursor.fetchone()
                if not temp:
                    break
                ID,timestamp = temp
                sql = "UPDATE %s set timestamp = ?" % table_name
                self._cursor.executemany(sql, ((val[0]-time_changed,) for val in values))
        # commit the change
        self._conn.commit()


class SQLiteDBDiskInfo(object):
    '''
    Table Descriptor:
    
    1. AllDiskDescriptor
       DevID:     Device ID that unique in every disk, is Serial now
       Model:     Device Model Name
       Serial:    Deivce Serial name
       MediaType: int, 0->HDD, 1->SSD,255->Unknown
       Protocal:  int, 0-> SCSI(SAS), 1-> SATA, 2-> NVMe,255->Unknown
       CreateDate:float, create date 
    
    2. LastActiveDisk
    
    '''
    def __init__(self, db_path=_sqlite3_diskinfo_file):
        self.__db_path = db_path
        ##
        self._conn = sqlite3.connect(self.__db_path)
        self._cursor = self._conn.cursor()
        ##
        self._init_db()

    def _init_db(self):
        table_name = "AllDiskDescriptor"
        sql = '''CREATE TABLE IF NOT EXISTS %s(
                 DevID  TEXT  NOT NULL,
                 Model  TEXT  NOT NULL,
                 Serial  TEXT  NOT NULL,
                 MediaType  INT  NOT NULL,
                 Protocal  INT  NOT NULL,
                 CreateDate  REAL  NOT NULL);
              ''' % table_name
        self._cursor.execute(sql)
        self._conn.commit()

    def store_last_disks_id(self, devs):
        '''
        Store the target devs id to json file
        
        devices: a list that contain device ids.
        '''
        with open(_LastActiveDiskFile, 'w') as f:
            f.write(json.dumps(devs))

    def get_last_store_disks_id(self):
        '''
        return a list of all disks id that stored by func: store_last_disks_id
        '''
        target = []
        if os.path.exists(_LastActiveDiskFile):
            with open(_LastActiveDiskFile, 'r') as f:
                content = f.read()
                if content:
                    target = json.loads(content)
        return target

    def get_all_disks_id(self):
        '''
        get all the disks in table AllDiskDescriptor
        
        return: a list of all disks id
        '''
        sql = "SELECT DevID from AllDiskDescriptor"
        self._cursor.execute(sql)
        temp = self._cursor.fetchall()
        return [i[0] for i in temp]

    def update_disk_info(self, 
                         disk_id, 
                         **kwargs):
        if not self.get_disk_info(disk_id):  ## Add
            sql = """INSERT INTO AllDiskDescriptor (DevID,Model,Serial,MediaType,Protocal,CreateDate)
                     VALUES ('%s', '%s', '%s', %d, %d, %f)
                  """ % (disk_id,
                         kwargs.get("Model"),
                         kwargs.get("Serial"),
                         kwargs.get("MediaType"),
                         kwargs.get("Protocal"),
                         float(time.time()),
                        )
            self._cursor.execute(sql)
            self._conn.commit()
            return 0
        return 1

    def get_disk_info(self, disk_id):
        sql = "SELECT * from AllDiskDescriptor WHERE DevID = '%s'" % disk_id
        self._cursor.execute(sql)
        return self._cursor.fetchone()


## init sqlite3 DB
all_disk_info = SQLiteDBDiskInfo()
disk_trace_pool = SQLiteDB()
##
