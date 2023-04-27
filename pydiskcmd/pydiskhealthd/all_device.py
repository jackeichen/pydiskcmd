# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import traceback
from pydiskcmd.pydiskhealthd.scsi_device import SCSIDeviceBase,SCSIDevice
from pydiskcmd.pydiskhealthd.sata_device import ATADeviceBase,ATADevice
## nvme for windows is not ready now
_has_nvme_device = True
from pydiskcmd.pydiskhealthd.nvme_device import NVMeDeviceBase,NVMeDevice
from pyscsi.pyscsi import scsi_enum_inquiry as INQUIRY
##
from pydiskcmd.system.env_var import os_type

def scan_device(debug=True, logger=None):
    '''
    How we detect the disk protocal NVMe,SCSI or SATA?

    May different methmod to get the disk types in different OSs. But this function will do:
    1. First act the disk as nvme device, and send nvme identify controller command(manual command).
       It will be NVMe when the command succes and break, otherwise goes next;
    2. Then act the disk as SCSI device, and send SCSI inquir command(manual command).
       It will be SCSI when the command succes, and continue to next; 
    3. At last act the disk as ATA device, and send ATA identify command(manual command).
       It will be ATA when the command succes, otherwise SCSI device; 

    So it is Non-OS dependence methmod to detect disk type
    '''
    def debug_info(message, info_t="debug"):
        if debug:
            if logger:
                if info_t == "debug":
                    logger.debug(message)
                elif info_t == "info":
                    logger.info(message)
                elif info_t == "warning":
                    logger.warning(message)
                elif info_t == "error":
                    logger.error(message)
                elif info_t == "critical":
                    logger.critical(message)
            else:
                print (message)
    if os_type == 'Linux':
        from pydiskcmd.system.lin_os_tool import get_block_devs,get_nvme_dev_info
        for dev in get_block_devs(print_detail=False):
            ## Skip nvme device, and scan SATA Or SAS Disk here
            if "nvme" not in dev:
                dev_path = "/dev/%s" % dev
                ### first act as a scsi device
                try:
                    dev_context = SCSIDeviceBase(dev_path)
                ##
                except FileNotFoundError:
                    message = "Skip device %s, device is removed." % dev_path
                    debug_info(message, 'warning')
                except:
                    debug_info(traceback.format_exc(), 'error')
                else:
                    ## judge the disk if is a SATA device
                    try:
                        dev_context = ATADeviceBase(dev_path)
                        message = "Device %s, change from scsi to sata" % dev_path
                        debug_info(message)
                    except:
                        pass
                    yield dev_context
        # scan nvme device
        for ctrl_id in get_nvme_dev_info():
            dev_path = "/dev/%s" % ctrl_id
            try:
                dev_context = NVMeDeviceBase(dev_path)
            except FileNotFoundError:
                message = "Skip device %s, device is removed." % dev_path
                debug_info(message, 'warning')
            except:
                debug_info(traceback.format_exc(), 'error')
            else:
                yield dev_context
    elif os_type == 'Windows':
        from pydiskcmd.system.win_os_tool import scan_all_physical_drive
        for dev_path in scan_all_physical_drive():
            ## first connect device by nvme
            try:
                dev_context = NVMeDeviceBase(dev_path)
            except FileNotFoundError:
                message = "Skip device %s, device is removed." % dev_path
                debug_info(message, 'warning')
                continue
            except:
                # debug_info(traceback.format_exc(), 'debug')
                pass
            else:
                yield dev_context
            ## then connect device by scsi
            try:
                dev_context = SCSIDeviceBase(dev_path)
            except FileNotFoundError:
                message = "Skip device %s, device is removed." % dev_path
                debug_info(message, 'warning')
                continue
            except:
                debug_info(traceback.format_exc())
            else:
                ## judge the disk if a SATA device
                try:
                    dev_context = ATADeviceBase(dev_path)
                    message = "Device %s, change from scsi to sata" % dev_path
                    debug_info(message)
                except:
                    pass
                yield dev_context
    else:
        raise NotImplementedError("OS %s not support!" % os_type)
