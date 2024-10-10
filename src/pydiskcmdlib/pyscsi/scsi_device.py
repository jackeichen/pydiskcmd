# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmdlib import os_type
from pydiskcmdlib import log

if os_type == "Windows":
    ########################################
    # Some code is from smartie, project in: 
    # https://github.com/TkTech/smartie
    # Author: Tyler Kennedy
    ########################################
    from pydiskcmdlib.device.win_device import WinIOCTLDevice,ctypes
    from pydiskcmdlib.pyscsi.win_scsi_structures import SCSIPassThroughDirect,SCSIPassThroughDirectWithBuffer
    import pyscsi.pyscsi.scsi_enum_command as scsi_enum_command
    from pyscsi.pyscsi.scsi_sense import SCSICheckCondition
    from pydiskcmdlib.os.win_ioctl_request import IOCTLRequest

    class SCSIDevice(WinIOCTLDevice):
        def __init__(self, 
                     device,
                     readwrite=True,
                     detect_replugged=True):
            log.debug("Opening SCSi device %s, read write flag is %s, detect replugged is %s" % (device, readwrite, detect_replugged))
            self._opcodes = scsi_enum_command.spc
            super(SCSIDevice, self).__init__(device, readwrite, detect_replugged)

        def execute(self, cmd, en_raw_sense=False):
            """
            execute a IOCTL command

            :param cmd: a Command Structure
            """
            log.debug("Sending SCSi Command: %s" % " ".join(["%X" % i for i in cmd.cdb]))
            ## create SCSIPassThroughDirect Or SCSIPassThroughDirectWithBuffer
            # will transfer SCSICommand to windows mode command
            cdb = (ctypes.c_ubyte * 16).from_buffer_copy(
                cmd.cdb.ljust(16, b'\x00')  # noqa
            )

            if cmd.datain:
                direction = 1     ## read from device
                data_transfer_length = len(cmd.datain)
                data_buffer = ctypes.create_string_buffer(data_transfer_length)
            elif cmd.dataout:
                direction = 0     ## write to device
                data_transfer_length = len(cmd.dataout)
                data_buffer = ctypes.create_string_buffer(bytes(cmd.dataout), data_transfer_length)
            else:
                direction = 0
                data_transfer_length = 0
                data_buffer = ctypes.create_string_buffer(b'', 0)
            timeout = 18000
            ## create SCSIPassThroughDirect
            header_sptd = SCSIPassThroughDirect(
                length=ctypes.sizeof(SCSIPassThroughDirect),
                data_in=direction,
                data_transfer_length=data_transfer_length,
                data_buffer=ctypes.addressof(data_buffer),
                cdb_length=len(cmd.cdb),
                cdb=cdb,
                timeout_value=timeout,
                sense_info_length=(
                    SCSIPassThroughDirectWithBuffer.sense.size
                ),
                sense_info_offset=(
                    SCSIPassThroughDirectWithBuffer.sense.offset
                )
            )
            # create SCSIPassThroughDirectWithBuffer
            header_with_buffer = SCSIPassThroughDirectWithBuffer(sptd=header_sptd)
            ## execute
            result = WinIOCTLDevice.execute(self, 
                                            IOCTLRequest.IOCTL_SCSI_PASS_THROUGH_DIRECT.value,   # IOCTL_SCSI_PASS_THROUGH_DIRECT
                                            header_with_buffer,
                                            header_with_buffer)
            ## After execute. will transfer result to Command Structure
            if cmd.datain: 
                cmd.datain = bytearray(data_buffer)
            # SCSICheckCondition(bytearray(header_with_buffer.sense))
            if en_raw_sense:
                cmd.raw_sense_data = bytearray(header_with_buffer.sense)
            log.debug("Sense Data: %s" % " ".join(["%X" % i for i in cmd.raw_sense_data]) if cmd.raw_sense_data else 'NA')
            return cmd

elif os_type == "Linux":
    from pydiskcmdlib.device.Lin_device import LinSGIODevice as SCSIDevice
