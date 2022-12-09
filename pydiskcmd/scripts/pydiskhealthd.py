# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import os
import time
import optparse
import subprocess
import traceback
import json
from pydiskcmd.system.os_tool import SystemdNotify,get_block_devs,get_nvme_dev_info,os_type
from pydiskcmd.system.log import logger_pydiskhealthd as logger
from pydiskcmd.system.log import syslog_pydiskhealthd as syslog
from pydiskcmd.exceptions import DeviceTypeError
## 
from pydiskcmd.pydiskhealthd.sata_device import ATADevice
from pydiskcmd.pydiskhealthd.nvme_device import NVMeDevice,AERTrace,AERTraceRL
from pydiskcmd.pydiskhealthd.scsi_device import SCSIDevice
from pydiskcmd.utils.converter import scsi_ba_to_int
from pydiskcmd.pydiskhealthd.some_path import DiskTracePath
##
from pyscsi.pyscsi import scsi_enum_inquiry as INQUIRY
####
## the disk info store path
DisksInfoPath = os.path.join(DiskTracePath, "AllDisksInfo.json")
##
tool_version = '0.1.1'
##
DiskWarningTemp = 60
DiskCriticalTemp = 70
#
DiskCalculatedHealthWarningLevel = 0.3
DiskCalculatedHealthErrorLevel = 0
####

def get_disk_context(devices):
    '''
    devices: a dict , that will contain device object.
    '''
    for dev in get_block_devs(print_detail=False):
        ## Skip nvme device, and scan SATA Or SAS Disk here
        if "nvme" not in dev:
            dev_path = "/dev/%s" % dev
            ### first act as a scsi device
            try:
                dev_context = SCSIDevice(dev_path)
                ## judge the disk if is SATA device, by send an inquiry page=0x89(ATA Infomation)
                i = dev_context.inquiry(INQUIRY.VPD.ATA_INFORMATION)
            ##
            except FileNotFoundError:
                logger.warning("Skip device %s, device is removed." % dev_path)
            except:
                logger.error(traceback.format_exc())
            else:
                if ("identify" in i) and ("general_config" in i['identify']) and ("ata_device" in i['identify']['general_config']) and (i['identify']['general_config']['ata_device'] == 0):
                    ## change device to SATA Device interface
                    dev_context = ATADevice(dev_path)
                    logger.info("Device %s, change from scsi to sata" % dev_path)
                if dev_context.device_id in devices:
                    # check if dev path changed, update it
                    if dev_context.dev_path != devices[dev_context.device_id].dev_path:
                        ## dev path changed, update it to the target
                        logger.warning("Device(ID: %s) path changed from %s to %s" % (dev_context.device_id, devices[dev_context.device_id].dev_path, dev_context.dev_path))
                        devices[dev_context.device_id].dev_path = dev_context.dev_path
                else:
                    dev_context.init_db()
                    devices[dev_context.device_id] = dev_context
                    logger.info("Find new ATA device %s, ID: %s" % (dev_path, dev_context.device_id))
    ## scan nvme device
    for ctrl_id in get_nvme_dev_info():
        dev_path = "/dev/%s" % ctrl_id
        try:
            dev_context = NVMeDevice(dev_path)
        except FileNotFoundError:
            logger.warning("Skip device %s, device is removed." % dev_path)
        except:
            logger.error(traceback.format_exc())
        else:
            if dev_context.device_id in devices:
                # check if dev path changed, update it
                if dev_context.dev_path != devices[dev_context.device_id].dev_path:
                    ## dev path changed, update it to the target
                    logger.warning("Device(ID: %s) path changed from %s to %s" % (dev_context.device_id, devices[dev_context.device_id].dev_path, dev_context.dev_path))
                    devices[dev_context.device_id].dev_path = dev_context.dev_path
            else:
                dev_context.init_db()
                devices[dev_context.device_id] = dev_context
                logger.info("Find new nvme device %s, ID: %s" % (dev_path, dev_context.device_id))
    return devices

def store_all_disks_id(devices):
    '''
    devices: a dict that contain device object.
    '''
    target = [] 
    target = list(devices.keys())
    with open(DisksInfoPath, 'w') as f:
        f.write(json.dumps(target))

def get_all_disks_id():
    '''
    return all disks id
    '''
    if os.path.exists(DisksInfoPath):
        with open(DisksInfoPath, 'r') as f:
            content = f.read()
        if content:
            return json.loads(content)
    return []

def pydiskhealthd():
    usage="usage: %prog [OPTION] [args...]"
    parser = optparse.OptionParser(usage,version="pydiskhealthd " + tool_version)
    parser.add_option("-t", "--check_interval", type="int", dest="check_interval", action="store", default=3600,
        help="Check inetrval time to check device health, default 1 hour.")
    parser.add_option("", "--nvme_aer_t", type="choice", dest="nvme_aer_type", action="store", choices=["loop", "real_time", "off"],default="real_time",
        help="How to check nvme aer with linux trace methmod: loop|real_time|off")
    parser.add_option("", "--check_daemon_running", dest="check_daemon_running", action="store_true", default=True,
        help="If check the pydiskheald daemon runnning, default true.")

    (options, args) = parser.parse_args()
    ## Do not support windows now
    if os_type != "Linux":
        raise NotImplementedError("pydiskhealth cannot run in OS:%s" % os_type)
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
    ## notify systemd here
    try:
        notifier = SystemdNotify()
        notifier.notify(READY=1)
    except Exception as e:
        logger.error(str(e))
        syslog.warning(str(e))
    ## check device here
    dev_pool = {}
    get_disk_context(dev_pool)
    # check if lost disks
    dev_id_list = get_all_disks_id()
    if dev_id_list:
        for k,v in dev_pool.items():
            if k in dev_id_list:
                dev_id_list.remove(k)
            else:
                message = "Found new Disk ID: %s, compared to the last time to run" % k
                syslog.info(message)
                logger.info(message)
        if dev_id_list:
            for i in dev_id_list:
                message = "Lost the Disk ID: %s, compared to the last time to run" % i
                syslog.info(message)
                logger.warning(message)
    ## init aer
    aer_trace = None
    if options.nvme_aer_type == 'loop':
        try:
            # init aer
            aer_trace = AERTrace()
        except:
            pass
    elif options.nvme_aer_type == 'real_time':
        try:
            # init aer
            aer_trace = AERTraceRL()
        except:
            pass
    ## check start
    while True:
        start_t = time.time()
        ### check device, add or lost
        get_disk_context(dev_pool)
        ## store all the disk info
        store_all_disks_id(dev_pool)
        ### check process Now
        logger.info("Check all Device(s) ...")
        ## check every disk
        for dev_id,dev_context in dev_pool.items():
            if dev_context.device_type == 'nvme':
                try:
                ### update log
                    smart_trace,persistent_event_log = dev_context.get_log_once()
                except FileNotFoundError:
                    message = "Device: %s(ID: %s), we lost this device now!" % (dev_context.dev_path, dev_context.device_id)
                    logger.error(message)
                    syslog.info(message)
                    continue  # skip this device 
                ### check smart Now
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
                            message = "Device: %s(ID: %s), No New Critical Warning." % (dev_context.dev_path, dev_context.device_id)
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
                        message = "Device: %s(ID: %s), Check Percentage Used(used %s) done." % (dev_context.dev_path, dev_context.device_id, current_smart.smart_info["Percentage Used"])
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
                            message = "Device: %s(ID: %s), Check Media and Data Integrity Errors(total %s errors) done." % (dev_context.dev_path, dev_context.device_id, current_smart.smart_info["Media and Data Integrity Errors"])
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
                            message = "Device: %s(ID: %s), check Number of Error Information Log Entries(total %s entries) done." % (dev_context.dev_path, dev_context.device_id, smart_current_value_int)
                            logger.info(message)
                    else:
                        if smart_current_value_int > 0:
                            message = "Device: %s(ID: %s), Init Number of Error Information Log Entries numbers: %s!" % (dev_context.dev_path, dev_context.device_id, smart_current_value_int)
                            message += " Attention for that!"
                            syslog.info(message)
                            logger.warning(message)
                        else:
                            message = "Device: %s(ID: %s), Check Number of Error Information Log Entries(total %s entries) done." % (dev_context.dev_path, dev_context.device_id, smart_current_value_int)
                            logger.info(message)
                ### check persistent_event_log
                values = persistent_event_log.diff_trace()
                if values:
                    for event in values:
                        event_type = scsi_ba_to_int(event["event_log_event_header"]["event_type"], 'little')
                        event_timestamp = scsi_ba_to_int(event["event_log_event_header"]["event_timestamp"], 'little')
                        past_t = (persistent_event_log.current_trace_timestamp - event_timestamp) / 1000 ## seconds
                        if event_type == 2:       ## 
                            message = "Device: %s(ID: %s), firmware commit detected in past %.3f seconds." % (dev_context.dev_path, dev_context.device_id, past_t)
                            message1 = "The event log event vendor spec info is %s" % event["vendor_spec_info"]
                            message2 = "The event log event data is %s" % event["event_log_event_data"] #
                            logger.info(message, message1, message2)
                        elif event_type == 3:     ## 
                            message = "Device: %s(ID: %s), timestamp change detected in past %.3f seconds." % (dev_context.dev_path, dev_context.device_id, past_t)
                            message1 = "The event log event vendor spec info is %s" % event["vendor_spec_info"]
                            message2 = "The event log event data is %s" % event["event_log_event_data"] #
                            logger.info(message, message1, message2)
                        elif event_type == 4:     ## 
                            message = "Device: %s(ID: %s), power-on or reset detected in past %.3f seconds." % (dev_context.dev_path, dev_context.device_id, past_t)
                            message1 = "The event log event vendor spec info is %s" % event["vendor_spec_info"]
                            message2 = "The event log event data is %s" % event["event_log_event_data"] #
                            logger.info(message, message1, message2)
                        elif event_type == 5:     ## 
                            message = "Device: %s(ID: %s), NVM subsystem Hardware Error detected in past %.3f seconds." % (dev_context.dev_path, dev_context.device_id, past_t)
                            message1 = "The event log event vendor spec info is %s" % event["vendor_spec_info"]
                            message2 = "The event log event data is %s" % event["event_log_event_data"] #
                            logger.info(message, message1, message2)
                            syslog.info(message, message1, message2)
                        elif event_type == 6:     ## 
                            message = "Device: %s(ID: %s), change namespace detected in past %.3f seconds." % (dev_context.dev_path, dev_context.device_id, past_t)
                            message1 = "The event log event vendor spec info is %s" % event["vendor_spec_info"]
                            message2 = "The event log event data is %s" % event["event_log_event_data"] #
                            logger.info(message, message1, message2)
                        elif event_type == 7:     ## 
                            message = "Device: %s(ID: %s), format NVM Start detected in past %.3f seconds." % (dev_context.dev_path, dev_context.device_id, past_t)
                            message1 = "The event log event vendor spec info is %s" % event["vendor_spec_info"]
                            message2 = "The event log event data is %s" % event["event_log_event_data"] #
                            logger.info(message, message1, message2)
                        elif event_type == 8:     ## 
                            message = "Device: %s(ID: %s), format NVM completion detected in past %.3f seconds." % (dev_context.dev_path, dev_context.device_id, past_t)
                            message1 = "The event log event vendor spec info is %s" % event["vendor_spec_info"]
                            message2 = "The event log event data is %s" % event["event_log_event_data"] #
                            logger.info(message, message1, message2)
                        elif event_type == 9:     ## 
                            message = "Device: %s(ID: %s), sanitize start detected in past %.3f seconds." % (dev_context.dev_path, dev_context.device_id, past_t)
                            message1 = "The event log event vendor spec info is %s" % event["vendor_spec_info"]
                            message2 = "The event log event data is %s" % event["event_log_event_data"] #
                            logger.info(message, message1, message2)
                        elif event_type == 10:    ## 
                            message = "Device: %s(ID: %s), sanitize completion detected in past %.3f seconds." % (dev_context.dev_path, dev_context.device_id, past_t)
                            message1 = "The event log event vendor spec info is %s" % event["vendor_spec_info"]
                            message2 = "The event log event data is %s" % event["event_log_event_data"] #
                            logger.info(message, message1, message2)
                        elif event_type == 11:    ## 
                            message = "Device: %s(ID: %s), set feature detected in past %.3f seconds." % (dev_context.dev_path, dev_context.device_id, past_t)
                            message1 = "The event log event vendor spec info is %s" % event["vendor_spec_info"]
                            message2 = "The event log event data is %s" % event["event_log_event_data"] #
                            logger.info(message, message1, message2)
                        elif event_type == 12:    ## 
                            message = "Device: %s(ID: %s), telemetry log created detected in past %.3f seconds." % (dev_context.dev_path, dev_context.device_id, past_t)
                            message1 = "The event log event vendor spec info is %s" % event["vendor_spec_info"]
                            message2 = "The event log event data is %s" % event["event_log_event_data"] #
                            logger.info(message, message1, message2)
                        elif event_type == 13:    ## 
                            message = "Device: %s(ID: %s), thermal excursion detected in past %.3f seconds." % (dev_context.dev_path, dev_context.device_id, past_t)
                            message1 = "The event log event vendor spec info is %s" % event["vendor_spec_info"]
                            message2 = "The event log event data is %s" % event["event_log_event_data"] #
                            logger.info(message, message1, message2)
                            syslog.info(message, message1, message2)
                ## Record and check Current Tempeture
                if "Composite Temperature" in current_smart.smart_info:
                    temperature = round(current_smart.smart_info["Composite Temperature"] - 273.15)
                    if temperature >= DiskCriticalTemp:
                        message = "Device: %s(ID: %s), Temperature(%s C) rise up to DiskCriticalTemp(%s C)" % (dev_context.dev_path, dev_context.device_id, temperature, DiskCriticalTemp)
                        logger.warning(message)
                        syslog.info(message)
                    elif temperature >= DiskWarningTemp:
                        message = "Device: %s(ID: %s), Temperature(%s C) rise up to DiskWarningTemp(%s C)" % (dev_context.dev_path, dev_context.device_id, temperature, DiskWarningTemp)
                        logger.warning(message)
                        syslog.info(message)
                    else:
                        message = "Device: %s(ID: %s), Temperature is: %s." % (dev_context.dev_path, dev_context.device_id, temperature)
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
                        message = "Device: %s(ID: %s), PCIe Width is %s(downgrade), device capacity is %s." % (dev_context.dev_path, dev_context.device_id, link_status.cur_width, link_status.capable_width)
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
                try:
                    ### get smart once, return smart trace
                    smart_trace = dev_context.get_smart_once()
                except FileNotFoundError:
                    message = "Device: %s(ID: %s), we lost this device now!" % (dev_context.dev_path, dev_context.device_id)
                    logger.error(message)
                    syslog.info(message)
                    continue  # skip this device 
                ### 
                current_smart = smart_trace.current_value  # current_smart is a SmartInfo object
                last_smart = smart_trace.get_cache_last_value()
                message1 = "Device: %s(ID: %s), Calculated Disk Health is %d%%." % (dev_context.dev_path, dev_context.device_id, int(current_smart.disk_health*100))
                logger.debug(message1)
                ## check disk health
                if last_smart:
                    if current_smart.disk_health <= DiskCalculatedHealthWarningLevel and last_smart.disk_health > DiskCalculatedHealthWarningLevel:
                        message1 = "Device: %s(ID: %s), Calculated Disk Health(%d%%) fallen below to %d%%." % (dev_context.dev_path, dev_context.device_id, int(current_smart.disk_health*100), int(DiskCalculatedHealthWarningLevel*100))
                        logger.warning(message1)
                        syslog.info(message1)
                    elif current_smart.disk_health <= DiskCalculatedHealthErrorLevel and last_smart.disk_health > DiskCalculatedHealthErrorLevel:
                        message1 = "Device: %s(ID: %s), Calculated Disk Health(%d%%) fallen below to %d%%." % (dev_context.dev_path, dev_context.device_id, int(current_smart.disk_health*100), int(DiskCalculatedHealthErrorLevel*100))
                        logger.warning(message1)
                        syslog.warning(message1)
                else:
                    message1 = "Device: %s(ID: %s), Init Calculated Disk Health is %d%%." % (dev_context.dev_path, dev_context.device_id, int(current_smart.disk_health*100))
                    logger.info(message1)
                    syslog.info(message1)
                ## check smart start
                for _id,smart_attr in current_smart.smart_info.items():
                    ## check current_smart.value and current_smart.worst with smart thresh
                    if _id in smart_trace.thresh_info and smart_trace.thresh_info[_id] > 0: # valid if thresh value > 0
                        if smart_attr.value <= smart_trace.thresh_info[_id]:
                            if last_smart and last_smart.smart_info[_id].value > smart_trace.thresh_info[_id]:
                                message1 = "Device: %s(ID: %s), smart #ID %s value fall below threshold. " % (dev_context.dev_path, dev_context.device_id, _id)
                                logger.warning(message1)
                                if smart_attr.flag_decode["Pre-fail"]:
                                    syslog.warning(message1)
                                else:
                                    syslog.info(message1)
                            elif not last_smart: # first time to report the message
                                message1 = "Device: %s(ID: %s), smart #ID %s check error(value <= threshold): " % (dev_context.dev_path, dev_context.device_id, _id)
                                if smart_attr.flag_decode["Pre-fail"]:
                                    message2 = "#ID: %s, smart name: %s, Pre-fail, value: %s, threshold: %s" % (smart_attr.id, smart_attr.attr_name, smart_attr.value, smart_trace.thresh_info[_id])
                                    logger.warning(message1, message2)
                                    syslog.warning(message1, message2)
                                else:
                                    message2 = "#ID: %s, smart name: %s, Old_age, value: %s, threshold: %s" % (smart_attr.id, smart_attr.attr_name, smart_attr.value, smart_trace.thresh_info[_id])
                                    logger.warning(message1, message2)
                                    syslog.info(message1, message2)
                            else:    # vs_smart_calculated_value not init Or have report this error, will not duplicate report
                                pass
                        ## check worst value
                        if smart_attr.worst <= smart_trace.thresh_info[_id]:
                            if last_smart and last_smart.smart_info[_id].worst > smart_trace.thresh_info[_id]:
                                message1 = "Device: %s(ID: %s), smart #ID %s worst fall below threshold. " % (dev_context.dev_path, dev_context.device_id, _id)
                                logger.warning(message1)
                                if smart_attr.flag_decode["Pre-fail"]:
                                    syslog.warning(message1)
                                else:
                                    syslog.info(message1)
                            elif not last_smart: # first time to report the message
                                message1 = "Device: %s(ID: %s), smart #ID %s check error(worst <= threshold): " % (dev_context.dev_path, dev_context.device_id, _id)
                                if smart_attr.flag_decode["Pre-fail"]:
                                    message2 = "#ID: %s, smart name: %s, Pre-fail, worst: %s, threshold: %s" % (smart_attr.id, smart_attr.attr_name, smart_attr.worst, smart_trace.thresh_info[_id])
                                    logger.warning(message1, message2)
                                    syslog.warning(message1, message2)
                                else:
                                    message2 = "#ID: %s, smart name: %s, Old_age, worst: %s, threshold: %s" % (smart_attr.id, smart_attr.attr_name, smart_attr.worst, smart_trace.thresh_info[_id])
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
                ## Record and check Current Tempeture
                if 194 in current_smart.smart_info:
                    temperature = (current_smart.smart_info[194].raw_value_int & 0xFFFF)
                    if temperature >= DiskCriticalTemp:
                        message = "Device: %s(ID: %s), Temperature(%s C) rise up to DiskCriticalTemp(%s C)" % (dev_context.dev_path, dev_context.device_id, temperature, DiskCriticalTemp)
                        logger.warning(message)
                        syslog.info(message)
                    elif temperature >= DiskWarningTemp:
                        message = "Device: %s(ID: %s), Temperature(%s C) rise up to DiskWarningTemp(%s C)" % (dev_context.dev_path, dev_context.device_id, temperature, DiskWarningTemp)
                        logger.warning(message)
                        syslog.info(message)
                    else:
                        message = "Device: %s(ID: %s), Temperature is: %s." % (dev_context.dev_path, dev_context.device_id, temperature)
                        logger.info(message)
            else:  # SCSI(SAS) Disk
                pass
        ## check aer for nvme
        if aer_trace and options.nvme_aer_type == 'loop':
            ## check nvme aer now
            aer_trace.get_log_once()
            diff = aer_trace.diff_trace()
            if diff:
                for i in diff:
                    logger.info("AER triggered, below is the details: ")
                    logger.info("-"*30)
                    for k,v in i.items():
                        logger.info("%-10s : %s" % (k, str(v)))
                    logger.info("-"*30)
        ### we will real-time to check aer
        time_left = options.check_interval - time.time() + start_t
        if aer_trace and options.nvme_aer_type == 'real_time':
            while (time_left > 0):
                trace_description = aer_trace.get_once(time_left)
                if trace_description:
                    logger.info("AER triggered, below is the details: ")
                    logger.info("-"*30)
                    for k,v in trace_description.items():
                        logger.info("%-10s : %s" % (k, str(v)))
                    logger.info("-"*30)
                time_left = options.check_interval - time.time() + start_t
        else:  
            ## check done
            logger.info("Check done")
            if time_left > 0:
                time.sleep(time_left)
