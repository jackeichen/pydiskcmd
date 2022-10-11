# SPDX-FileCopyrightText: 2014 The python-scsi Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import re
import time
import optparse
import subprocess
from pydiskcmd.system.os_tool import SystemdNotify,get_block_devs
from pydiskcmd.system.log import logger_pydiskhealthd as logger
from pydiskcmd.system.log import syslog_pydiskhealthd as syslog
##
from pydiskcmd.pydiskhealthd.sata_device import ATADevice
from pydiskcmd.pydiskhealthd.nvme_device import NVMeDevice

tool_version = '0.1.0'


def get_disk_context(devices):
    '''
    devices: a dict
    '''
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
                    logger.info("Find new nvme device %s, ID: %s" % (dev_path, dev_context.device_id))
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
                    logger.info("Find new ATA device %s, ID: %s" % (dev_path, dev_context.device_id))
    return devices

def difference_set_methmod(a, b):
    diff_a_b = set(b).difference(set(a))  ## in b but not in a
    diff_b_a = set(a).difference(set(b))  ## in a but not in b
    return list(diff_a_b),list(diff_b_a)

def pydiskhealthd():
    usage="usage: %prog [OPTION] [args...]"
    parser = optparse.OptionParser(usage,version="pydiskhealthd " + tool_version)
    parser.add_option("-t", "--check_interval", type="int", dest="check_interval", action="store", default=3600,
        help="Check inetrval time to check device health, default 1 hour.")
    parser.add_option("", "--check_daemon_running", dest="check_daemon_running", action="store_true", default=True,
        help="If check the pydiskheald daemon runnning, default true.")

    (options, args) = parser.parse_args()
    ## check parameter
    if options.check_daemon_running:
        ##
        proc = subprocess.Popen(["pgrep", "-l", "-f", "pydiskhealthd"], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        proc.wait()
        stdout = proc.stdout.read()
        stderr = proc.stderr.read()
        if proc.returncode == 0:
            content_all = stdout.split("\n")
            running_number = 0
            for c in content_all:
                if c:
                    temp = c.split(' ')
                    progress_id = temp[0]
                    progress_name = ' '.join(temp[1:])
                    if progress_name == "pydiskhealthd":
                        running_number += 1
            ## because you are running the pydiskheal, so count should be >= 2 if another is running
            if running_number > 1:
                print ("pydiskhealthd is running(PID %s)" % progress_id)
                return 1
        else:
            print ("Run pgrep command error, return code: %s" % proc.returncode)
            print (proc.stderr.read())
            return 2
    ## notify
    try:
        notifier = SystemdNotify()
        notifier.notify(READY=1)
    except Exception as e:
        logger.error(str(e))
        syslog.warning(str(e))
    ## check device here
    dev_pool = {}
    ## check start
    while True:
        start_t = time.time()
        ### check device, add or lost
        get_disk_context(dev_pool)
        ### check process Now
        logger.info("Check Device ...")
        for dev_id,dev_context in dev_pool.items():
            if dev_context.device_type == 'nvme':
                ### check smart Now
                dev_context.get_smart_once()
                ## check critical_warning
                if "Critical Warning" in dev_context.smart_attr:
                    smart_attr = dev_context.smart_attr.get("Critical Warning")
                    smart_current = smart_attr.current_value
                    #smart_last = smart_attr.value_list[smart_attr.value_list_head-2]
                    if smart_current:
                        smart_t,smart_value,smart_detail = smart_current
                        if smart_value:
                            message = "Critical Warning detected in disk %s" % dev_context.dev_path
                            syslog.warning(message)
                            logger.warning(message)
                            ## base in spec v1.4
                            if smart_value & 0x01:
                                message = "Device: %s(ID: %s), the available spare capacity has fallen below the threshold!" % (dev_context.dev_path, dev_context.device_id)
                                message += " You may need to replace this disk as soon as possible."
                                syslog.warning(message)
                                logger.warning(message)
                            if smart_value & 0x02:
                                message = "Device: %s(ID: %s), temperature is greater than or equal to an over temperature threshold;" % (dev_context.dev_path, dev_context.device_id)
                                message += " or less than or equal to an under temperature threshold!"
                                syslog.warning(message)
                                logger.warning(message)
                            if smart_value & 0x04:
                                message = "Device: %s(ID: %s), NVM subsystem reliability has been degraded due to" % (dev_context.dev_path, dev_context.device_id)
                                message += " significant media related errors or any internal error that degrades NVM subsystem reliability."
                                syslog.warning(message)
                                logger.warning(message) 
                            if smart_value & 0x08:
                                message = "Device: %s(ID: %s), the media has been placed in read only mode." % (dev_context.dev_path, dev_context.device_id)
                                syslog.error(message)
                                logger.error(message)
                            if smart_value & 0x10:
                                message = "Device: %s(ID: %s), the volatile memory backup device has failed." % (dev_context.dev_path, dev_context.device_id)
                                message += "(Note: only valid if the controller has a volatile memory backup solution)"
                                syslog.warning(message)
                                logger.warning(message)
                            if smart_value & 0x20:
                                message = "Device: %s(ID: %s), the Persistent Memory Region has become read-only or unreliable." % (dev_context.dev_path, dev_context.device_id)
                                syslog.error(message)
                                logger.error(message)
                        else:
                            message = "No Critical Warning in disk %s(ID: %s)" % (dev_context.dev_path, dev_context.device_id)
                            logger.info(message)
                if "Available Spare" in dev_context.smart_attr and "Available Spare Threshold" in dev_context.smart_attr:
                    smart_as_attr = dev_context.smart_attr.get("Available Spare")
                    smart_ast_attr = dev_context.smart_attr.get("Available Spare Threshold")
                    smart_as_current = smart_as_attr.current_value
                    smart_ast_current = smart_ast_attr.current_value
                    if smart_as_current[1] > smart_ast_current[1]:
                        message = "Check Available Spare done in disk %s(ID: %s)" % (dev_context.dev_path, dev_context.device_id)
                        logger.info(message)
                    else:
                        message = "Device: %s(ID: %s), the available spare capacity has fallen below the threshold!" % (dev_context.dev_path, dev_context.device_id)
                        message += " You may need to replace this disk as soon as possible."
                        syslog.warning(message)
                        logger.warning(message)
                if "Percentage Used" in dev_context.smart_attr:
                    smart_attr = dev_context.smart_attr.get("Percentage Used")
                    smart_current = smart_attr.current_value
                    smart_t,smart_value,smart_detail = smart_current
                    if smart_value < 90:
                        message = "Check Percentage Used(used %s) done in disk %s(ID: %s)." % (smart_value, dev_context.dev_path, dev_context.device_id)
                        logger.info(message)
                    elif smart_value < 100:
                        message = "Device: %s(ID: %s), the Percentage Used(used %s) reached >90." % (smart_value, dev_context.dev_path, dev_context.device_id)
                        message += " You may need to replace this disk as soon as possible."
                        syslog.warning(message)
                        logger.warning(message)
                    else:
                        message = "Device: %s(ID: %s), the Percentage Used reached 100." % (dev_context.dev_path, dev_context.device_id)
                        message += " You may need to replace this disk as soon as possible."
                        syslog.warning(message)
                        logger.warning(message)
                if "Media and Data Integrity Errors" in dev_context.smart_attr:
                    smart_attr = dev_context.smart_attr.get("Media and Data Integrity Errors")
                    smart_current = smart_attr.current_value
                    smart_last = smart_attr.value_list[smart_attr.value_list_head-2]
                    if smart_current and smart_last:
                        if smart_current[1] > smart_last[1]:
                            message = "Device: %s(ID: %s), the Media and Data Integrity Errors increased(%s->%s)!" % (dev_context.dev_path, dev_context.device_id, smart_last[1], smart_current[1])
                            message += " Attention for this Device!"
                            syslog.warning(message)
                            logger.warning(message)
                    elif (not smart_last) and smart_current:
                        if smart_current[1] > 0:
                            message = "Device: %s(ID: %s), Init Media and Data Integrity Errors numbers: %s!" % (dev_context.dev_path, dev_context.device_id, smart_current[1])
                            message += " Attention for this Device!"
                            syslog.warning(message)
                            logger.warning(message)
                        else:
                            message = "Check Media and Data Integrity Errors(total %s errors) done in disk %s(ID: %s)." % (smart_current[1], dev_context.dev_path, dev_context.device_id)
                            logger.info(message)
                if "Number of Error Information Log Entries" in dev_context.smart_attr:
                    smart_attr = dev_context.smart_attr.get("Number of Error Information Log Entries")
                    smart_current = smart_attr.current_value
                    smart_last = smart_attr.value_list[smart_attr.value_list_head-2]
                    if smart_current and smart_last:
                        if smart_current[1] > smart_last[1]:
                            message = "Device: %s(ID: %s), the Number of Error Information Log Entries increased(%s->%s)!" % (dev_context.dev_path, dev_context.device_id, smart_last[1], smart_current[1])
                            message += " Attention for this Device!"
                            syslog.warning(message)
                            logger.warning(message)
                    elif (not smart_last) and smart_current:
                        if smart_current[1] > 0:
                            message = "Device: %s(ID: %s), Init Number of Error Information Log Entries numbers: %s!" % (dev_context.dev_path, dev_context.device_id, smart_current[1])
                            message += " Attention for this Device!"
                            syslog.warning(message)
                            logger.warning(message)
                        else:
                            message = "Check Number of Error Information Log Entries(total %s entries) done in disk %s(ID: %s)." % (smart_current[1], dev_context.dev_path, dev_context.device_id)
                            logger.info(message)
                ### PCIe Check
                ## check pcie link status & AER
                if dev_context.pcie_context:
                    ## check link status
                    link_status = dev_context.pcie_context.express_link
                    if link_status.cur_speed != link_status.capable_speed:
                        if dev_context.pcie_report.link_report_times['speed'] == 0:
                            message = "Device: %s(ID: %s), PCIe Speed is %s(downgrade), device capacity is %s." % (dev_context.dev_path, dev_context.device_id, link_status.cur_speed, link_status.capable_speed)
                            message += " Attention for that!"
                            syslog.warning(message)
                            logger.warning(message)
                        dev_context.pcie_report.link_report_times['speed'] += 1
                    if link_status.cur_width != link_status.capable_width:
                        if dev_context.pcie_report.link_report_times['width'] == 0:
                            message = "Device: %s(ID: %s), PCIe Width is x%s(downgrade), device capacity is x%s." % (dev_context.dev_path, dev_context.device_id, link_status.cur_width, link_status.capable_width)
                            message += " Attention for that!"
                            syslog.warning(message)
                            logger.warning(message)
                        dev_context.pcie_report.link_report_times['width'] += 1
                    # check with last time link status
                    if dev_context.pcie_report.last_link_status['speed']:
                        if link_status.cur_speed != dev_context.pcie_report.last_link_status['speed']:  # speed changed
                            message = "Device: %s(ID: %s), PCIe Speed chaned(%s -> %s)." % (dev_context.dev_path, dev_context.device_id, dev_context.pcie_report.last_link_status['speed'], link_status.cur_speed)
                            syslog.info(message)
                            logger.warning(message)
                            dev_context.pcie_report.last_link_status['speed'] = link_status.cur_speed
                    if dev_context.pcie_report.last_link_status['width']:
                        if dev_context.pcie_report.last_link_status['width'] != link_status.cur_width: # width changed
                            message = "Device: %s(ID: %s), PCIe Width chaned(%s -> %s)." % (dev_context.dev_path, dev_context.device_id, dev_context.pcie_report.last_link_status['width'], link_status.cur_width)
                            syslog.info(message)
                            logger.warning(message)
                            dev_context.pcie_report.last_link_status['width'] = link_status.cur_width
                    ## check AER
                    pcie_aer = dev_context.pcie_context.express_aer
                    for error_t,status in pcie_aer["device"]["aer_dev_correctable"].items():
                        if status:
                            if dev_context.pcie_report.aer_ce_report_times[error_t] == 0:
                                message = "Device: %s(ID: %s), PCIe AER occur %s." % (dev_context.dev_path, dev_context.device_id, error_t)
                                message += " Attention for that!"
                                syslog.info(message)
                                logger.warning(message)
                            dev_context.pcie_report.aer_ce_report_times[error_t] += 1
                    for error_t,status in pcie_aer["device"]["aer_dev_nonfatal"].items():
                        if status:
                            if dev_context.pcie_report.aer_nonfatal_report_times[error_t] == 0:
                                message = "Device: %s(ID: %s), PCIe AER occur %s." % (dev_context.dev_path, dev_context.device_id, error_t)
                                message += " Attention for that!"
                                syslog.info(message)
                                logger.warning(message)
                            dev_context.pcie_report.aer_nonfatal_report_times[error_t] += 1
                    for error_t,status in pcie_aer["device"]["aer_dev_fatal"].items():
                        if status:
                            if dev_context.pcie_report.aer_fatal_report_times[error_t] == 0:
                                message = "Device: %s(ID: %s), PCIe AER occur %s." % (dev_context.dev_path, dev_context.device_id, error_t)
                                message += " Attention for that!"
                                syslog.warning(message)
                                logger.warning(message)
                            dev_context.pcie_report.aer_fatal_report_times[error_t] += 1
            ## ATA device check
            elif dev_context.device_type == 'ata':
                dev_context.get_smart_once()
                if 190 in dev_context.smart_attr: ## Airflow_Temperature_Cel
                    Airflow_Temperature_Cel = dev_context.smart_attr[190].current_value[1].raw_value_int
                    logger.info("dev: %s, Airflow_Temperature_Cel is %s" % (dev_context.dev_path, Airflow_Temperature_Cel))
        logger.info("Check done")
        time_left = options.check_interval - time.time() + start_t
        if time_left > 0:
            time.sleep(time_left)
