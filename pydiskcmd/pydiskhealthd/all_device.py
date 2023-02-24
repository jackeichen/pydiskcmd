# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import traceback
from pydiskcmd.pydiskhealthd.scsi_device import SCSIDeviceBase,SCSIDevice
from pydiskcmd.pydiskhealthd.sata_device import ATADeviceBase,ATADevice
## nvme for windows is not ready now
_has_nvme_device = True
try:
    from pydiskcmd.pydiskhealthd.nvme_device import NVMeDeviceBase,NVMeDevice
except:
    _has_nvme_device = False
from pyscsi.pyscsi import scsi_enum_inquiry as INQUIRY
##
from pydiskcmd.system.env_var import os_type

def scan_device(debug=True, logger=None):
    def debug_info(message, info_t="debug"):
        if debug:
            if logger:
                if info_t == "dedbug":
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
            if _has_nvme_device: 
                try:
                    dev_context = NVMeDeviceBase(dev_path)
                except NotImplementedError:
                    message = "Detect nvme device %s, but it is not support." % dev_path
                    debug_info(message)
                except FileNotFoundError:
                    message = "Skip device %s, device is removed." % dev_path
                    debug_info(message, 'warning')
                except:
                    debug_info(traceback.format_exc(), 'error')
                else:
                    yield dev_context
            ## then connect device by scsi
            try:
                dev_context = SCSIDeviceBase(dev_path)
            except FileNotFoundError:
                message = "Skip device %s, device is removed." % dev_path
                debug_info(message, 'warning')
            except:
                debug_info(traceback.format_exc())
            else:
                ## judge the disk if is a SATA device
                try:
                    dev_context = ATADeviceBase(dev_path)
                    message = "Device %s, change from scsi to sata" % dev_path
                    debug_info(message)
                except:
                    pass
                yield dev_context
    else:
        raise NotImplementedError("OS %s not support!" % os_type)
