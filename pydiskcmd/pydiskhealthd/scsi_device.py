# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import time
from pydiskcmd.pyscsi.scsi import SCSI
from pydiskcmd.utils import init_device
from pydiskcmd.utils.converter import bytearray2string,translocate_bytearray
from pydiskcmd.exceptions import DeviceTypeError
##
from pyscsi.pyscsi import scsi_enum_inquiry as INQUIRY

def get_dev_id(dev_path):
    ## get device ID
    device_id = None
    ##
    with SCSI(init_device(dev_path, open_t="scsi"), blocksize=512) as d:
        cmd = d.inquiry(evpd=1, page_code=INQUIRY.VPD.UNIT_SERIAL_NUMBER)
        i = cmd.result
    if 'unit_serial_number' in i:
        id_string = bytearray2string(i['unit_serial_number'])
        if id_string:
            device_id = id_string
        else:
            device_id = bytes(i['unit_serial_number'])
    return device_id


class SCSIFeatureStatus(object):
    def __init__(self):
        self.smart = False


class SCSIDeviceBase(object):
    """
    dev_path: the nvme controller device path(ex. /dev/sdb)
    
    """
    def __init__(self, dev_path):
        self.__device_type = 'scsi'
        self.dev_path = dev_path
        ##
        self.scsi_feature_status = SCSIFeatureStatus()
        self.check_feature_support = {}
        ## init device
        self.__model = None
        self.__serial = None
        #
        with SCSI(init_device(self.dev_path, open_t="scsi"), blocksize=512) as d:
            cmd = d.inquiry(evpd=1, page_code=INQUIRY.VPD.UNIT_SERIAL_NUMBER)
            serial_info = cmd.result
            inq_info = d.inquiry().result
        #
        if 'unit_serial_number' in serial_info:
            id_string = bytearray2string(serial_info['unit_serial_number']).strip()
            if id_string:
                self.__serial = id_string
            else:
                for encode_t in ("UTF-8", "GBK", "GB2312"):
                    try:
                        self.__serial = bytes(serial_info['unit_serial_number']).decode(encoding=encode_t)
                    except:
                        pass
                    else:
                        break
        if 'product_identification' in inq_info:
            for encode_t in ("UTF-8", "GBK", "GB2312"):
                try:
                    self.__model = inq_info['product_identification'].decode(encoding=encode_t, errors="strict")
                except:
                    pass
                else:
                    break

    @property
    def device_type(self):
        return self.__device_type

    @property
    def device_id(self):
        return self.__serial.strip().replace("-", "_")

    @property
    def Model(self):
        return self.__model

    @property
    def Serial(self):
        return self.__serial

    def inquiry(self, page_code):
        with SCSI(init_device(dev_path, open_t="scsi"), blocksize=512) as d:
            cmd = d.inquiry(evpd=1, page_code=page_code)
            i = cmd.result
        return i

    def temperature(self):
        '''
        Decode temperature (log page 0xd or 0x2f)
        '''
        from pydiskcmd.pyscsi.scsi_spec import LogSenseAttr
        t = None
        with SCSI(init_device(self.dev_path, open_t="scsi"), blocksize=512) as d:
            cmd = d.logsense(0x0D)
            log_page = LogSenseAttr.get((0x0D,0x00))
            log_page_decode = log_page.decode_value(cmd.datain)
            if log_page_decode['page_code'] == 0x0D and log_page_decode['subpage_code'] == 0:
                for i in log_page_decode["log_parameters"]:
                    if i.get("parameter_code") == 0:
                        t = i.get("parameter_value")[1]
                        break
            if t is None:
                # try 0x2f
                cmd = d.logsense(0x2F)
                log_page = LogSenseAttr.get((0x2F,0x00))
                log_page_decode = log_page.decode_value(cmd.datain)
                if log_page_decode['page_code'] == 0x2F and log_page_decode['subpage_code'] == 0:
                    for i in log_page_decode["log_parameters"]:
                        if i.get("parameter_code") == 0:
                            t = i.get("parameter_value")[3]
                            break
        ##
        return t


class SCSIDevice(SCSIDeviceBase):
    """
    dev_path: the nvme controller device path(ex. /dev/sdb)

    """
    def __init__(self, dev_path, init_db=False):
        super(SCSIDevice, self).__init__(dev_path)
        ##
        self.__media_type = None
        blk_dev_char = self.inquiry(INQUIRY.VPD.BLOCK_DEVICE_CHARACTERISTICS)
        if blk_dev_char.get("medium_rotation_rate") is None:
            raise DeviceTypeError("Unkonwn Device Type %s." % dev_path)
        elif blk_dev_char.get("medium_rotation_rate") == 1:
            self.__media_type = "SSD"
        elif blk_dev_char.get("medium_rotation_rate") > 1:
            self.__media_type = "HDD"
        ##
        if init_db:
            self.init_db()

    def __del__(self):
        ## close device when exit
        self._close()

    def _close(self):
        pass

    def init_db(self):
        pass

    @property
    def MediaType(self):
        return self.__media_type

    @property
    def smart_enable(self):
        return False
