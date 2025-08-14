from pydiskcmdlib.command_utils import CommandWrapperPro
from pydiskcmdlib.os import win_ioctl_request
from pydiskcmdlib.os.win_ioctl_structures import SRB_IO_CONTROL_LEN
from .win_ioctl_structures import REMAPPORT_IOCTL_GET_DEVICE_LOCATION
from .win_ioctl_utils import (
    INTELRMP_SIGNATURE,
    IOCTL_REMAPPORT_GET_DEVICE_LOCATION,
    REMAPPORT_IOCTL_GET_DEVICE_LOCATION_VERSION,
    REMAPPORT_GET_DEVICE_LOCATION_STATUS,
    )
from pydiskcmdlib.exceptions import *

class RemapportGetDeviceLocation(CommandWrapperPro):
    '''
    This API is used to get the physical location of the storage device owned by RST driver. 
    The location information includes the bus type, the device type, the physical slot number, 
    the physical port number, and the physical function number.

    Note: This API is introduced in Intel® RST 18.0 release to provide a user space application 
    with the information about the physical location of the storage device owned by RST 
    driver. 
    Suggest to check the RST version by CC_CSMI_SAS_GET_DRIVER_INFO, before send this command.
    
    Limitations: 
    1. API works for Intel® RST controlled storage devices (NVMe* or Intel® SATA)
    2. API works for passthrough device and also for the device that is a member of 
       logical volume for example, NGSA or RAID0
    '''
    _req_id: int = win_ioctl_request.IOCTLRequest.IOCTL_SCSI_MINIPORT.value
    def __init__(self, path_id, target_id, lun, timeout=30):
        CommandWrapperPro.__init__(self, REMAPPORT_IOCTL_GET_DEVICE_LOCATION)
        ##
        header = {'HeaderLength': SRB_IO_CONTROL_LEN,
                  'Signature': INTELRMP_SIGNATURE,
                  'Timeout': timeout,
                  'ControlCode': IOCTL_REMAPPORT_GET_DEVICE_LOCATION,
                  'ReturnCode': 0,
                  'Length': self.cdb_raw_struc_len-SRB_IO_CONTROL_LEN, 
                 }
        #
        self.build_command(srbIoControl=header,
                           Version=REMAPPORT_IOCTL_GET_DEVICE_LOCATION_VERSION,
                           Size=self.cdb_raw_struc_len,
                           PathId=path_id,
                           TargetId=target_id,
                           Lun=lun,
                           )

    def check_return_status(self, success_hint=False, fail_hint=True, raise_if_fail=True) -> int:
        ret = 0
        ## level 1. Check the IOCTL execute return code
        if self.ioctl_result is not None and self.ioctl_result == 0:
            ret = 1
            import ctypes # noqa: F401
            if fail_hint:
                print (str(ctypes.WinError(ctypes.get_last_error())))
            if raise_if_fail:
                raise ctypes.WinError(ctypes.get_last_error())
        ## Level 2. Check SRB_IO_CONTROL ReturnCode field
        if self.cdb.Header.ReturnCode != REMAPPORT_GET_DEVICE_LOCATION_STATUS.GetLocationSuccess.value:
            ret = 2
            rc = self.cdb.Header.ReturnCode
            if fail_hint:
                print ("SrbIoCtrl->ReturnCode is %#x(%s)" % (rc, REMAPPORT_GET_DEVICE_LOCATION_STATUS(rc).name))
            if raise_if_fail:
                raise CommandReturnStatusError('Command Check Error: %#x(%s)' % (rc, REMAPPORT_GET_DEVICE_LOCATION_STATUS(rc).name))
        ##
        if ret == 0 and success_hint:
            print ("Command Success")
            print ('')
        return ret
