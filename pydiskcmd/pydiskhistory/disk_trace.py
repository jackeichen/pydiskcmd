# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmd.pydiskhealthd.DB import all_disk_info,SQLiteDB
from pydiskcmd.pynvme.nvme_spec import nvme_smart_decode
from pydiskcmd.utils.converter import scsi_ba_to_int
from pydiskcmd.pysata.sata_spec import decode_smart_info
##
disk_trace_pool = SQLiteDB()
##  


def get_disk_temperature_history(target_dev_id=None):
    ##
    history = {}
    ##
    disk_in_disk_info = all_disk_info.get_all_disks_id()
    table_in_disk_trace = disk_trace_pool.get_all_tables_name()
    for dev_id in disk_in_disk_info:
        if target_dev_id and dev_id != target_dev_id:
            continue
        if disk_trace_pool.get_table_name_by_dev_id(dev_id) in table_in_disk_trace: ## trace find out
            history[dev_id] = []
            ## get the disk info first
            disk_info = all_disk_info.get_disk_info(dev_id)
            ## Get smart
            for t,smart in disk_trace_pool.get_smart_by_dev_id(dev_id):
                temperature = None
                if disk_info[4] == 1: ## SATA
                    smart_info = decode_smart_info(smart[2:362])
                    if 194 in smart_info:
                        temperature = (smart_info[194].raw_value_int & 0xFFFF)
                elif disk_info[4] == 2: ## nvme
                    smart_info = nvme_smart_decode(smart)
                    # round the temperature tp int
                    temperature = round(scsi_ba_to_int(smart_info.get("Composite Temperature"), 'little')-273.15)
                history[dev_id].append((t,temperature))
    return history


