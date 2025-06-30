# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmdlib.utils.converter import encode_dict, decode_bits
from pydiskcmdlib.os.win_ioctl_utils import ATA_DATA_TRANSFER_DIRECTION
from pydiskcmdlib.csmi.win_ioctl_utils import CSMI_SAS_LINK_RATE,STP_Flags
from pydiskcmdlib.csmi.cdb_csmi_sas_stp_passthrough import CSMI_SAS_STP_PASSTHRU
from pydiskcmdlib.exceptions import *


class RSTATAPass12(CSMI_SAS_STP_PASSTHRU):
    '''
    WARNING: Not Tested Now!!! 
             Be careful to use RSTATAPass12!!! 

    RSTCommand for SATA command, initialize the RSTATAPass12 object.

    :param phy_id: The physical ID of the device.
    :param port_id: The port ID of the device.
    :param sas_addr: The SAS address of the device.
    :param command: The ATA command to be sent.
    :param features: The features associated with the ATA command.
    :param lba: The logical block address for the command.
    :param device: The device identifier.
    :param sector_count: The number of sectors to be read or written.
    :param transfer_direction: The direction of data transfer (0 for NO_DATA, 1 for DATA_IN, 2 for DATA_OUT).
    :param data_len: The length of the data to be transferred.
    :param data: The data to be transferred (optional).
    :param connection_rate: The connection rate (default is CSMI_SAS_LINK_RATE_NEGOTIATED).
    '''
    _h2d_register_bitmap = {"FIS_Type": [0xFF, 0],
                            "PM_Port": [0x0F, 1],
                            "C": [0x80, 1],
                            "Command": [0xFF, 2],
                            "Features": [0xFF, 3],
                            "LBA": [0x0FFFFFFF, 4],
                            "Device": [0xFF, 7],
                            "Sector_Count": [0xFF, 12],
                            "Control": [0xFF, 15],
                            }
    _d2h_register_bitmap = {"FIS_Type": [0xFF, 0],
                            "PM_Port": [0x0F, 1],
                            "I": [0x40, 1],
                            "Status": [0xFF, 2],
                            "Error": [0xFF, 3],
                            "LBA": [0x0FFFFFFF, 4],
                            "Device": [0xFF, 7],
                            "Sector_Count": [0xFF, 12],
                            }
    def __init__(self,
                 phy_id,
                 port_id,
                 sas_addr,
                 command,        # ATA Command: command
                 features,       # ATA Command: features
                 lba,            # LBA
                 device,         # device
                 sector_count,   # Sector count
                 transfer_direction,  # 0 for NO_DATA, 1 for DATA_IN, 2 for DATA_OUT
                 data_len,
                 data=None,
                 connection_rate=CSMI_SAS_LINK_RATE.CSMI_SAS_LINK_RATE_NEGOTIATED.value,
                 ):
        raise BuildSCSICommandError("RSTATAPass12 is not supported now")
        if transfer_direction == ATA_DATA_TRANSFER_DIRECTION.NO_DATA.value:
            flags = STP_Flags.CSMI_SAS_STP_PIO.value | STP_Flags.CSMI_SAS_STP_UNSPECIFIED.value
        elif transfer_direction == ATA_DATA_TRANSFER_DIRECTION.DATA_IN.value:
            flags = STP_Flags.CSMI_SAS_STP_PIO.value | STP_Flags.CSMI_SAS_STP_READ.value
        elif transfer_direction == ATA_DATA_TRANSFER_DIRECTION.DATA_OUT.value:
            flags = STP_Flags.CSMI_SAS_STP_PIO.value | STP_Flags.CSMI_SAS_STP_WRITE.value
        else:
            raise BuildSCSICommandError("Invalid transfer_direction")
        # build FIS
        # fis = bytearray(20)
        # fis[0] = 0x27; # Type: host-to-device FIS
        # fis[1] = 0x80; # Bit7: Update command register
        # fis[2] = command
        # fis[3] = features & 0xFF
        # fis[4] = (lba >> 20) & 0xFF
        # fis[5] = (lba >> 12) & 0xFF
        # fis[6] = (lba >> 4) & 0xFF
        # fis[7] = (lba & 0x0F) + (device & 0xF0)
        # fis[12] = sector_count & 0xFF
        fis = bytearray(20)
        fis[0] = 0x27; # Type: host-to-device FIS
        fis[1] = 0x80; # Bit7: Update command register
        fis[2] = command
        fis[3] = features & 0xFF
        fis[4] = (lba & 0xFF)
        fis[5] = ((lba >> 8) & 0xFF)
        fis[6] = ((lba >> 16) & 0xFF)
        fis[7] = ((lba >> 24) & 0x0F) + (device & 0xF0)
        fis[8] = 0
        fis[9] = 0
        fis[10] = 0
        fis[11] = 0
        fis[12] = sector_count & 0xFF
        fis[13] = 0
        #
        CSMI_SAS_STP_PASSTHRU.__init__(self, phy_id, port_id, connection_rate, 
                                       sas_addr, bytes(fis), flags, data_len, data=data,
                                       )
        ##
        self._result = {}

    def _encode_h2d_register(self, **kwargs):
        '''
        Encode the register to FIS
        '''
        fis = bytearray(20)
        encode_dict(kwargs, self._h2d_register_bitmap, fis)
        return fis

    def _decode_d2h_register(self):
        result = {}
        decode_bits(bytes(self.cdb.Status.bStatusFIS), self._d2h_register_bitmap, result)
        if result.get("FIS_Type") != 0x34:
            raise CommandReturnStatusError("Invalid FIS Type(not 0x34)")
        return result

    @property
    def ata_status_return_descriptor(self):
        return self._decode_d2h_register()

    @property
    def datain(self):
        return bytes(self.cdb.bDataBuffer)
    
    @property
    def result(self):
        return self._result

    def get_ata_status_return(self):
        return self.ata_status_return_descriptor

    def check_return_status(self, success_hint=False, fail_hint=True, raise_if_fail=True) -> int:
        result = self._decode_d2h_register()
        ret = result.get("Status") | result.get("Error")
        if ret == 0 and success_hint:
            print ("Command Success")
            print ('')
        if ret!= 0:
            if fail_hint:
                print ("Command failed, and details bellow.")
                print ("- ATA Status:")
                format_string = "  %-12s %s"
                print (format_string % ("Status Field", "Error Field"))
                print (format_string % ("%#x" % result.get("Status"), 
                                        "%#x" % result.get("Error"),
                                        ))
            if raise_if_fail:
                raise CommandReturnStatusError("Command failed, status: %#x, error: %#x" % (result.get("Status"), result.get("Error")))
        return ret


class RSTATAPass16(CSMI_SAS_STP_PASSTHRU):
    '''
    RSTCommand for SATA command
    '''
    _h2d_register_bitmap = {"FIS_Type": [0xFF, 0],
                            "PM_Port": [0x0F, 1],
                            "C": [0x80, 1],
                            "Command": [0xFF, 2],
                            "Features": [0xFF, 3],
                            "LBA": [0xFFFFFF, 4],
                            "Device": [0xFF, 7],
                            "LBA_exp": [0xFFFFFF, 8],
                            "Features_exp": [0xFF, 11],
                            "Sector_Count": [0xFFFF, 12],
                            "Control": [0xFF, 15],
                            }
    _d2h_register_bitmap = {"FIS_Type": [0xFF, 0],
                            "PM_Port": [0x0F, 1],
                            "I": [0x40, 1],
                            "Status": [0xFF, 2],
                            "Error": [0xFF, 3],
                            "LBA": [0xFFFFFF, 4],
                            "Device": [0xFF, 7],
                            "LBA_exp": [0xFFFFFF, 8],
                            "Sector_Count": [0xFFFF, 12],
                            }
    def __init__(self,
                 phy_id: int,
                 port_id: int,
                 sas_addr: bytes,
                 command: int,        # ATA Command: command
                 features: int,       # ATA Command: features
                 lba: int,            # LBA
                 device: int,         # device
                 sector_count: int,   # Sector count
                 transfer_direction: int,  # 0 for NO_DATA, 1 for DATA_IN, 2 for DATA_OUT
                 data_len: int,
                 data=None,
                 connection_rate: int=CSMI_SAS_LINK_RATE.CSMI_SAS_LINK_RATE_NEGOTIATED.value,
                 ):
        if transfer_direction == ATA_DATA_TRANSFER_DIRECTION.NO_DATA.value:
            flags = STP_Flags.CSMI_SAS_STP_PIO.value | STP_Flags.CSMI_SAS_STP_UNSPECIFIED.value
        elif transfer_direction == ATA_DATA_TRANSFER_DIRECTION.DATA_IN.value:
            flags = STP_Flags.CSMI_SAS_STP_PIO.value | STP_Flags.CSMI_SAS_STP_READ.value
        elif transfer_direction == ATA_DATA_TRANSFER_DIRECTION.DATA_OUT.value:
            flags = STP_Flags.CSMI_SAS_STP_PIO.value | STP_Flags.CSMI_SAS_STP_WRITE.value
        else:
            raise ValueError("Invalid transfer_direction")
        # build FIS
        fis = bytearray(20)
        fis[0] = 0x27; # Type: host-to-device FIS
        fis[1] = 0x80; # Bit7: Update command register
        fis[2] = command
        fis[3] = features & 0xFF
        fis[4] = (lba & 0xFF)
        fis[5] = ((lba >> 8) & 0xFF)
        fis[6] = ((lba >> 16) & 0xFF)
        fis[7] = device
        fis[8] = ((lba >> 24) & 0xFF)
        fis[9] = ((lba >> 32) & 0xFF) 
        fis[10] = ((lba >> 40) & 0xFF)
        fis[11] = (features >> 8) & 0xFF
        fis[12] = sector_count & 0xFF
        fis[13] = (sector_count >> 8) & 0xFF
        CSMI_SAS_STP_PASSTHRU.__init__(self, phy_id, port_id, connection_rate, 
                                       sas_addr, bytes(fis), flags, data_len, data=data,
                                       )
        ##
        self._result = {}

    def _encode_h2d_register(self, **kwargs):
        '''
        Encode the register to FIS
        '''
        fis = bytearray(20)
        encode_dict(kwargs, self._h2d_register_bitmap, fis)
        return fis

    def _decode_d2h_register(self):
        result = {}
        decode_bits(bytes(self.cdb.Status.bStatusFIS), self._d2h_register_bitmap, result, byteorder='little')
        return result

    @property
    def ata_status_return_descriptor(self):
        return self._decode_d2h_register()

    @property
    def datain(self):
        return bytes(self.cdb.bDataBuffer)
    
    @property
    def result(self):
        return self._result

    def get_ata_status_return(self):
        # TODO
        return self._decode_d2h_register()

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
        if self.cdb.IoctlHeader.ReturnCode != 0:
            ret = 2
            rc = self.cdb.IoctlHeader.ReturnCode
            if fail_hint:
                print ("IoctlHeader->ReturnCode is %#x" % rc)
            if raise_if_fail:
                raise CommandReturnStatusError('Command Check Error: %#x' % rc)
        ## Level 3. Check ATA returncode: Status and Error field
        result = self._decode_d2h_register()
        if ((result.get("Status") &0x01) | result.get("Error")) != 0:
            ret = 3
            if fail_hint:
                print ("Command failed, and details bellow.")
                print ("- ATA Status:")
                format_string = "  %-12s %s"
                print (format_string % ("Status Field", "Error Field"))
                print (format_string % ("%#x" % result.get("Status"), 
                                        "%#x" % result.get("Error"),
                                        ))
            if raise_if_fail:
                raise CommandReturnStatusError("Command failed, status: %#x, error: %#x" % (result.get("Status"), result.get("Error")))
        ##
        if ret == 0 and success_hint:
            print ("Command Success")
            print ('')
        return ret
