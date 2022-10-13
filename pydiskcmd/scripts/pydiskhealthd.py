# SPDX-FileCopyrightText: 2014 The pydiskcmd Authors
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
                smart_trace = dev_context.get_smart_once()
                current_smart = smart_trace.current_value
                last_smart = smart_trace.get_cache_last_value()
                ## check critical_warning
                if "Critical Warning" in current_smart.smart_info:
                    smart_value = current_smart.smart_info["Critical Warning"]
                    if last_smart:
                        last_smart_value = last_smart.smart_info["Critical Warning"]
                        if smart_value != last_smart_value:
                            message = "Critical Warning detected in disk %s." % dev_context.dev_path
                            syslog.info(message)
                            logger.warning(message)
                            ## base in spec v1.4
                            if smart_value & 0x01 and (not last_smart_value & 0x01):
                                message = "Device: %s(ID: %s), the available spare capacity has fallen below the threshold!" % (dev_context.dev_path, dev_context.device_id)
                                message += " You may need to replace this disk as soon as possible."
                                syslog.warning(message)
                                logger.error(message)
                            if smart_value & 0x02 and (not last_smart_value & 0x02):
                                message = "Device: %s(ID: %s), temperature is greater than or equal to an over temperature threshold;" % (dev_context.dev_path, dev_context.device_id)
                                message += " Or less than or equal to an under temperature threshold!"
                                syslog.info(message)
                                logger.error(message)
                            if smart_value & 0x04 and (not last_smart_value & 0x04):
                                message = "Device: %s(ID: %s), NVM subsystem reliability has been degraded due to" % (dev_context.dev_path, dev_context.device_id)
                                message += " significant media related errors or any internal error that degrades NVM subsystem reliability."
                                syslog.warning(message)
                                logger.error(message) 
                            if smart_value & 0x08 and (not last_smart_value & 0x08):
                                message = "Device: %s(ID: %s), the media has been placed in read only mode." % (dev_context.dev_path, dev_context.device_id)
                                syslog.warning(message)
                                logger.error(message)
                            if smart_value & 0x10 and (not last_smart_value & 0x10):
                                message = "Device: %s(ID: %s), the volatile memory backup device has failed." % (dev_context.dev_path, dev_context.device_id)
                                message += "(Note: only valid if the controller has a volatile memory backup solution)"
                                syslog.warning(message)
                                logger.error(message)
                            if smart_value & 0x20 and (not last_smart_value & 0x20):
                                message = "Device: %s(ID: %s), the Persistent Memory Region has become read-only or unreliable." % (dev_context.dev_path, dev_context.device_id)
                                syslog.warning(message)
                                logger.error(message)
                        else:
                            message = "No New Critical Warning in disk %s(ID: %s)" % (dev_context.dev_path, dev_context.device_id)
                            logger.info(message)
                    else:
                        ## base in spec v1.4
                        if smart_value & 0x01:
                            message = "Device: %s(ID: %s), the available spare capacity has fallen below the threshold!" % (dev_context.dev_path, dev_context.device_id)
                            message += " You may need to replace this disk as soon as possible."
                            syslog.warning(message)
                            logger.error(message)
                        if smart_value & 0x02:
                            message = "Device: %s(ID: %s), temperature is greater than or equal to an over temperature threshold;" % (dev_context.dev_path, dev_context.device_id)
                            message += " Or less than or equal to an under temperature threshold!"
                            syslog.info(message)
                            logger.error(message)
                        if smart_value & 0x04:
                            message = "Device: %s(ID: %s), NVM subsystem reliability has been degraded due to" % (dev_context.dev_path, dev_context.device_id)
                            message += " significant media related errors or any internal error that degrades NVM subsystem reliability."
                            syslog.warning(message)
                            logger.error(message) 
                        if smart_value & 0x08:
                            message = "Device: %s(ID: %s), the media has been placed in read only mode." % (dev_context.dev_path, dev_context.device_id)
                            syslog.warning(message)
                            logger.error(message)
                        if smart_value & 0x10:
                            message = "Device: %s(ID: %s), the volatile memory backup device has failed." % (dev_context.dev_path, dev_context.device_id)
                            message += "(Note: only valid if the controller has a volatile memory backup solution)"
                            syslog.warning(message)
                            logger.error(message)
                        if smart_value & 0x20:
                            message = "Device: %s(ID: %s), the Persistent Memory Region has become read-only or unreliable." % (dev_context.dev_path, dev_context.device_id)
                            syslog.warning(message)
                            logger.error(message)
                ## check Available Spare 
                if "Available Spare" in current_smart.smart_info:
                    smart_value = current_smart.smart_info["Available Spare"]
                    if smart_trace.vs_smart_calculated_value:
                        smart_min = smart_trace.vs_smart_calculated_value["Available Spare"].value_int_min
                        ##
                        if (smart_value - smart_min) > 20:
                            t = smart_trace.vs_smart_calculated_value["Available Spare"].time_t - current_smart.time_t
                            message = "Device: %s(ID: %s), the Available Spare fall below >20 in past %s seconds." % (dev_context.dev_path, dev_context.device_id, t)
                            syslog.info(message)
                            logger.info(message)
                ## check Available Spare Threshold
                if "Available Spare Threshold" in current_smart.smart_info:
                    if current_smart.smart_info["Available Spare"] <= current_smart.smart_info["Available Spare Threshold"]:
                        if last_smart:
                            if last_smart.smart_info["Available Spare"] > current_smart.smart_info["Available Spare Threshold"]:
                                message = "Device: %s(ID: %s), the Available Spare fall below Available Spare Threshold." % (dev_context.dev_path, dev_context.device_id)
                                syslog.warning(message)
                                logger.warning(message)
                            elif current_smart.smart_info["Available Spare"] < last_smart.smart_info["Available Spare"]:
                                message = "Device: %s(ID: %s), the Available Spare has fell below Available Spare Threshold, and become worse now." % (dev_context.dev_path, dev_context.device_id)
                                syslog.warning(message)
                                logger.warning(message)
                        else:
                            message = "Device: %s(ID: %s), the Available Spare fall below Available Spare Threshold." % (dev_context.dev_path, dev_context.device_id)
                            syslog.warning(message)
                            logger.warning(message)
                ## check Percentage Used
                if "Percentage Used" in current_smart.smart_info:
                    if current_smart.smart_info["Percentage Used"] < 90:
                        message = "Check Percentage Used(used %s) done in disk %s(ID: %s)." % (current_smart.smart_info["Percentage Used"], dev_context.dev_path, dev_context.device_id)
                        logger.info(message)
                    elif current_smart.smart_info["Percentage Used"] < 100:
                        message = "Device: %s(ID: %s), the Percentage Used(used %s) reached >90." % (dev_context.dev_path, dev_context.device_id, current_smart.smart_info["Percentage Used"])
                        message += " You may need to attention this disk."
                        syslog.info(message)
                        logger.warning(message)
                    else:
                        message = "Device: %s(ID: %s), the Percentage Used reached 100." % (dev_context.dev_path, dev_context.device_id)
                        message += " You may need to replace this disk as soon as possible."
                        syslog.warning(message)
                        logger.warning(message)
                ## check Media and Data Integrity Errors
                if "Media and Data Integrity Errors" in current_smart.smart_info:
                    if smart_trace.if_cached_smart():
                        if current_smart.smart_info["Media and Data Integrity Errors"] > last_smart.smart_info["Media and Data Integrity Errors"]:
                            message = "Device: %s(ID: %s), the Media and Data Integrity Errors increased(%s->%s)!" % (dev_context.dev_path, dev_context.device_id, last_smart.smart_info["Media and Data Integrity Errors"], current_smart.smart_info["Media and Data Integrity Errors"])
                            message += " Attention for this Device!"
                            syslog.info(message)
                            logger.warning(message)
                        else:
                            message = "Device: %s(ID: %s), check the Media and Data Integrity Errors done." % (dev_context.dev_path, dev_context.device_id)
                            logger.info(message)
                    else:
                        if current_smart.smart_info["Media and Data Integrity Errors"] > 0:
                            message = "Device: %s(ID: %s), Init Media and Data Integrity Errors numbers: %s!" % (dev_context.dev_path, dev_context.device_id, current_smart.smart_info["Media and Data Integrity Errors"])
                            syslog.info(message)
                            logger.warning(message)
                        else:
                            message = "Check Media and Data Integrity Errors(total %s errors) done in disk %s(ID: %s)." % (current_smart.smart_info["Media and Data Integrity Errors"], dev_context.dev_path, dev_context.device_id)
                            logger.info(message)
                ## check Number of Error Information Log Entries
                if "Number of Error Information Log Entries" in current_smart.smart_info:
                    smart_current_value_int = current_smart.smart_info["Number of Error Information Log Entries"]
                    if smart_trace.if_cached_smart():
                        smart_last_value_int = last_smart.smart_info["Number of Error Information Log Entries"]
                        if smart_current_value_int > smart_last_value_int:
                            message = "Device: %s(ID: %s), the Number of Error Information Log Entries increased(%s->%s)!" % (dev_context.dev_path, dev_context.device_id, smart_last_value_int, smart_current_value_int)
                            message += " Attention for that!"
                            syslog.info(message)
                            logger.warning(message)
                        else:
                            message = "Check Number of Error Information Log Entries(total %s entries) done in disk %s(ID: %s)." % (smart_current_value_int, dev_context.dev_path, dev_context.device_id)
                            logger.info(message)
                    else:
                        if smart_current_value_int > 0:
                            message = "Device: %s(ID: %s), Init Number of Error Information Log Entries numbers: %s!" % (dev_context.dev_path, dev_context.device_id, smart_current_value_int)
                            message += " Attention for that!"
                            syslog.info(message)
                            logger.warning(message)
                        else:
                            message = "Check Number of Error Information Log Entries(total %s entries) done in disk %s(ID: %s)." % (smart_current_value_int, dev_context.dev_path, dev_context.device_id)
                            logger.info(message)
                ### PCIe Check
                ## check link status
                link_status = dev_context.pcie_context.express_link
                last_link_status  = dev_context.pcie_trace.pcie_link_status
                if last_link_status:
                    if last_link_status.cur_speed != link_status.cur_speed:
                        message = "Device: %s(ID: %s), PCIe Speed change form %s to %s." % (dev_context.dev_path, dev_context.device_id, last_link_status.cur_speed, link_status.cur_speed)
                        message += " Attention for that!"
                        syslog.info(message)
                        logger.warning(message)
                    if last_link_status.cur_width != link_status.cur_width:
                        message = "Device: %s(ID: %s), PCIe Width change form %s to %s." % (dev_context.dev_path, dev_context.device_id, last_link_status.cur_width, link_status.cur_width)
                        message += " Attention for that!"
                        syslog.info(message)
                        logger.warning(message)
                else:
                    if link_status.cur_speed != link_status.capable_speed:
                        message = "Device: %s(ID: %s), PCIe Speed is %s(downgrade), device capacity is %s." % (dev_context.dev_path, dev_context.device_id, link_status.cur_speed, link_status.capable_speed)
                        message += " Attention for that!"
                        syslog.info(message)
                        logger.warning(message)
                    if link_status.cur_width != link_status.capable_width:
                        message = "Device: %s(ID: %s), PCIe Speed is %s(downgrade), device capacity is %s." % (dev_context.dev_path, dev_context.device_id, link_status.cur_width, link_status.capable_width)
                        message += " Attention for that!"
                        syslog.info(message)
                        logger.warning(message) 
                ## check AER
                link_aer = dev_context.pcie_context.express_aer
                last_link_aer = dev_context.pcie_trace.pcie_aer_status
                if last_link_aer:
                    for name,status in link_aer['device']['aer_dev_correctable'].items():
                        if status and (not last_link_aer['device']['aer_dev_correctable'][name]):
                            message = "Device: %s(ID: %s), PCIe AER CE Error %s checked." % (dev_context.dev_path, dev_context.device_id, name)
                            message += " Attention for that!"
                            syslog.info(message)
                            logger.warning(message)
                    for name,status in link_aer['device']['aer_dev_nonfatal'].items():
                        if status and (not last_link_aer['device']['aer_dev_nonfatal'][name]):
                            message = "Device: %s(ID: %s), PCIe AER NonFatal Error %s checked." % (dev_context.dev_path, dev_context.device_id, name)
                            message += " Attention for that!"
                            syslog.info(message)
                            logger.warning(message)
                    for name,status in link_aer['device']['aer_dev_fatal'].items():
                        if status and (not last_link_aer['device']['aer_dev_fatal'][name]):
                            message = "Device: %s(ID: %s), PCIe AER UE(Fatal) Error %s checked." % (dev_context.dev_path, dev_context.device_id, name)
                            message += " Attention for that!"
                            syslog.info(message)
                            logger.warning(message)
                else: # first time to report 
                    for name,status in link_aer['device']['aer_dev_correctable'].items():
                        if status:
                            message = "Device: %s(ID: %s), Init status PCIe AER CE Error %s checked." % (dev_context.dev_path, dev_context.device_id, name)
                            message += " Attention for that!"
                            syslog.info(message)
                            logger.warning(message)
                    for name,status in link_aer['device']['aer_dev_nonfatal'].items():
                        if status:
                            message = "Device: %s(ID: %s), Init status PCIe AER NonFatal Error %s checked." % (dev_context.dev_path, dev_context.device_id, name)
                            message += " Attention for that!"
                            syslog.info(message)
                            logger.warning(message)
                    for name,status in link_aer['device']['aer_dev_fatal'].items():
                        if status:
                            message = "Device: %s(ID: %s), Init status PCIe AER UE(Fatal) Error %s checked." % (dev_context.dev_path, dev_context.device_id, name)
                            message += " Attention for that!"
                            syslog.info(message)
                            logger.warning(message)
                ## update pcie trace now after check
                dev_context.update_pcie_trace()
            ## ATA device check
            elif dev_context.device_type == 'ata':
                ### get smart once, return smart trace
                smart_trace = dev_context.get_smart_once()
                ### 
                current_smart = smart_trace.current_value  # current_smart is a SmartInfo object
                '''
                ### record temperature
                if 190 in smart: ## Airflow_Temperature_Cel
                    Airflow_Temperature_Cel = smart[190].raw_value_int
                    logger.info("dev: %s, Airflow_Temperature_Cel is %s" % (dev_context.dev_path, Airflow_Temperature_Cel))
                '''
                ## check start
                for _id,smart_attr in current_smart.smart_info.items():
                    ## check current_smart.value and current_smart.worst with smart thresh
                    if _id in smart_trace.thresh_info and smart_trace.thresh_info[_id].thresh > 0: # valid if thresh value > 0
                        if smart_attr.value < smart_trace.thresh_info[_id].thresh:
                            if smart_trace.vs_smart_calculated_value and smart_trace.vs_smart_calculated_value[_id].value_int_min > smart_trace.thresh_info[_id].thresh:
                                message1 = "Device: %s(ID: %s), smart #ID %s value fall below threshold. " % (dev_context.dev_path, dev_context.device_id, _id)
                                logger.warning(message1)
                                if smart_attr.flag_decode["Pre-fail"]:
                                    syslog.warning(message1)
                                else:
                                    syslog.info(message1)
                            elif not smart_trace.vs_smart_calculated_value: # first time to report the message
                                message1 = "Device: %s(ID: %s), smart #ID %s check error(value < threshold): " % (dev_context.dev_path, dev_context.device_id, _id)
                                if smart_attr.flag_decode["Pre-fail"]:
                                    message2 = "#ID: %s, smart name: %s, Pre-fail, value: %s, threshold: %s" % (smart_attr.id, smart_attr.attr_name, smart_attr.value, smart_trace.thresh_info[_id].thresh)
                                    logger.warning(message1, message2)
                                    syslog.warning(message1, message2)
                                else:
                                    message2 = "#ID: %s, smart name: %s, Old_age, value: %s, threshold: %s" % (smart_attr.id, smart_attr.attr_name, smart_attr.value, smart_trace.thresh_info[_id].thresh)
                                    logger.warning(message1, message2)
                                    syslog.info(message1, message2)
                            else:    # vs_smart_calculated_value not init Or have report this error, will not duplicate report
                                pass
                        ## check worst value
                        if smart_attr.worst < smart_trace.thresh_info[_id].thresh:
                            if smart_trace.vs_smart_calculated_value and smart_trace.vs_smart_calculated_value[_id].worst_int_min > smart_trace.thresh_info[_id].thresh:
                                message1 = "Device: %s(ID: %s), smart #ID %s worst fall below threshold. " % (dev_context.dev_path, dev_context.device_id, _id)
                                logger.warning(message1)
                                if smart_attr.flag_decode["Pre-fail"]:
                                    syslog.warning(message1)
                                else:
                                    syslog.info(message1)
                            elif not smart_trace.vs_smart_calculated_value: # first time to report the message
                                message1 = "Device: %s(ID: %s), smart #ID %s check error(worst < threshold): " % (dev_context.dev_path, dev_context.device_id, _id)
                                if smart_attr.flag_decode["Pre-fail"]:
                                    message2 = "#ID: %s, smart name: %s, Pre-fail, worst: %s, threshold: %s" % (smart_attr.id, smart_attr.attr_name, smart_attr.worst, smart_trace.thresh_info[_id].thresh)
                                    logger.warning(message1, message2)
                                    syslog.warning(message1, message2)
                                else:
                                    message2 = "#ID: %s, smart name: %s, Old_age, worst: %s, threshold: %s" % (smart_attr.id, smart_attr.attr_name, smart_attr.worst, smart_trace.thresh_info[_id].thresh)
                                    logger.warning(message1, message2)
                                    syslog.info(message1, message2)
                            else:  # vs_smart_calculated_value not init Or have report this error
                                pass
                    ## check fall values
                    #  pre-fail will report every 10 falls, Old_age report every 15 falls
                    if smart_attr.flag_decode["Pre-fail"]:  # pre-fail
                        if smart_trace.vs_smart_calculated_value and (smart_attr.value - smart_trace.vs_smart_calculated_value[_id].value_int_min) > 10:
                            message1 = "Device: %s(ID: %s), smart #ID(Pre-fail) %s value reduce more than 10. " % (dev_context.dev_path, dev_context.device_id, _id)
                            syslog.info(message1)
                            logger.info(message1)
                    else: # Old_age
                        if smart_trace.vs_smart_calculated_value and (smart_attr.value - smart_trace.vs_smart_calculated_value[_id].value_int_min) > 15:
                            message1 = "Device: %s(ID: %s), smart #ID(Old_age) %s value reduce more than 15. " % (dev_context.dev_path, dev_context.device_id, _id)
                            syslog.info(message1)
                            logger.info(message1)
            else:  # SCSI(SAS) Disk
                pass
        logger.info("Check done")
        time_left = options.check_interval - time.time() + start_t
        if time_left > 0:
            time.sleep(time_left)
