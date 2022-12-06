# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from pydiskcmd.system.env_var import os_type    


if os_type == "Windows":
    #####################################
    # Code is from smartie, project in: 
    # https://github.com/TkTech/smartie
    # Author: Tyler Kennedy
    #####################################
    import ctypes 
    ####
    ClientTODevice = 0   # data from client to device
    ClientFROMDevice = 1 # data from device to client
    ####

    class SCSIPassThroughDirect(ctypes.Structure):
        """
        Corresponds to the SCSI_PASS_THROUGH_DIRECT structure in <ntddscsi.h> on
        Windows.
        """
        _fields_ = [
            ('length', ctypes.c_ushort),
            ('scsi_status', ctypes.c_ubyte),
            ('path_id', ctypes.c_ubyte),
            ('target_id', ctypes.c_ubyte),
            ('lun', ctypes.c_ubyte),
            ('cdb_length', ctypes.c_ubyte),
            ('sense_info_length', ctypes.c_ubyte),
            ('data_in', ctypes.c_ubyte),
            ('data_transfer_length', ctypes.c_uint32),
            ('timeout_value', ctypes.c_uint32),
            ('data_buffer', ctypes.c_void_p),
            ('sense_info_offset', ctypes.c_uint32),
            ('cdb', ctypes.c_ubyte * 16)
        ]


    class SCSIPassThroughDirectWithBuffer(ctypes.Structure):
        """
        Corresponds to the SCSI_PASS_THROUGH_DIRECT_WITH_BUFFER structure in
        <ntddscsi.h> on Windows.
        """
        _fields_ = [
            ('sptd', SCSIPassThroughDirect),
            ('filler', ctypes.c_uint32),
            ('sense', ctypes.c_ubyte * 32)
        ]
    
    
elif os_type == "Linux":
    from pyscsi.pyscsi.scsi_command import *

