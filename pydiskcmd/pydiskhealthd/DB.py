# SPDX-FileCopyrightText: 2014 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import os
import base64
import sqlite3
from pydiskcmd.pydiskhealthd.some_path import DiskTracePath

#####
_sqlite3_db_file = os.path.join(DiskTracePath, "sqlite3_disk_trace.db")
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

    def get_dev_temperature_history(self):
        sql = '''SELECT timestamp,smart from %s;
              ''' % self.__table_name
        self.__cursor.execute(sql)
        return self.__cursor.fetchone()


class SQLiteDB(object):
    def __init__(self, db_path=_sqlite3_db_file, max_entry_per_disk=2000):
        self.__db_path = db_path
        self.__max_entry_per_disk = max_entry_per_disk
        ##
        self._conn = sqlite3.connect(self.__db_path)
        self._cursor = self._conn.cursor()
        ##
        self.__disk_trace_pool = {}

    @property
    def disk_trace_pool(self):
        return self.__disk_trace_pool

    def get_table_by_id(self, dev_id):
        table_name = "S%s" % dev_id
        if dev_id not in self.__disk_trace_pool:
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
            ##
            self.__disk_trace_pool[dev_id] = SQLiteTable(self, table_name, max_entry=self.__max_entry_per_disk)
        return self.__disk_trace_pool.get(dev_id)

## init sqlite3 DB
disk_trace_pool = SQLiteDB()
##
