# SPDX-FileCopyrightText: 2014 The python-scsi Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import re
import time
import optparse
from pydiskcmd.system.os_tool import SystemdNotify,get_block_devs
from pydiskcmd.system.log import logger_pydiskhealthd as logger
from pydiskcmd.system.log import syslog_pydiskhealthd as syslog
##
from pydiskcmd.pydiskhealthd.sata_device import ATADevice
from pydiskcmd.pydiskhealthd.nvme_device import NVMeDevice

tool_version = '0.0.1'


def get_disk_context():
    devices = {}
    for dev in get_block_devs():
        ## init nvme device
        if "nvme" in dev:
            g = re.match(r"nvme([0-9]+)n([0-9]+)", dev)
            if g:
                ctrl_id = g[1]
                ns_id = g[2]
                ## add to dict
                dev_path = "/dev/nvme%s" % ctrl_id
                dev_context = NVMeDevice(dev_path)
                if dev_context.device_id not in devices:
                    devices[dev_context.device_id] = dev_context
                    logger.info("Find nvme device %s, ID: %s" % (dev_path, dev_context.device_id))
        ## SATA Or SAS Disk here
        else:
            ## judge the disk is SATA Or SAS, by send ATA_identify command
            dev_path = "/dev/%s" % dev
            try:  # try SATA command, ATADevice will send identify command to device
                dev_context = ATADevice(dev_path)
            except: # May be SAS Device, Not support now
                logger.info("Skip device %s, it is not a nvme or SATA Device" % dev_path)
            else:  # send success, it's a SATA Device
                if dev_context.device_id not in devices:
                    devices[dev_context.device_id] = dev_context
                    logger.info("Find ATA device %s, ID: %s" % (dev_path, dev_context.device_id))
    return devices

def difference_set_methmod(a, b):
    diff_a_b = set(b).difference(set(a))  ## in b but not in a
    diff_b_a = set(a).difference(set(b))  ## in a but not in b
    return list(diff_a_b),list(diff_b_a)

def pydiskhealthd():
    usage="usage: %prog [OPTION] [args...]"
    parser = optparse.OptionParser(usage,version="pydiskhealthd " + tool_version)
    parser.add_option("-t", "--check_interval",  type="int", dest="check_interval", action="store", default=3600,
        help="Check inetrval time to check device health, default 1 hour.")

    (options, args) = parser.parse_args()
    ## check parameter
    pass
    ## notify
    try:
        notifier = SystemdNotify()
        notifier.notify(READY=1)
    except Exception as e:
        logger.error(str(e))
        syslog.warning(str(e))
    ## check device here
    dev_pool_last = {}
    ## check start
    while True:
        start_t = time.time()
        ## check device, 
        dev_pool = get_disk_context()
        if dev_pool_last:
            b_has,a_has = difference_set_methmod(dev_pool_last.keys(), dev_pool.keys())
            if b_has:
                logger.info("Found More Device, MN: %s" % ','.join(b_has))
            if a_has:
                logger.warning("Device Lost, MN: %s" % ','.join(a_has))
        dev_pool_last = dev_pool
        ## check process Now
        logger.info("Check Device ...")
        for dev_id,dev_context in dev_pool.items():
            if dev_context.device_type == 'nvme':
                dev_context.get_smart_once()
                attr_error_entry = dev_context.smart_attr.get("Number of Error Information Log Entries")
                logger.info("dev: %s, smart error_entry_num=%s" % (dev_context.dev_path, attr_error_entry.value.current_value))
            elif dev_context.device_type == 'ata':
                dev_context.get_smart_once()
                if 190 in dev_context.smart_attr: ## Airflow_Temperature_Cel
                    Airflow_Temperature_Cel = dev_context.smart_attr[190].current_value[1].raw_value_int
                    logger.info("dev: %s, Airflow_Temperature_Cel is %s" % (dev_context.dev_path, Airflow_Temperature_Cel))
        logger.info("Check done")
        time_left = options.check_interval - time.time() + start_t
        if time_left > 0:
            time.sleep(time_left)
