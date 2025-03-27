# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from typing import Optional
import ctypes
from pydiskcmdlib.pyscsi.lin_scsi_structures import SCSI_DXFER
from pydiskcmdlib.data_buffer import DataBuffer
from .megaraid_ioctl_structures import (
    megasas_iocpacket,
    uioctl_t,
    MKADAP,
    MEGA_MBOXCMD_PASSTHRU,
    MAX_REQ_SENSE_LEN,
    MFI_MBOX_SIZE,
    MFI_CMD_DCMD,
    MFI_CMD_PD_SCSI_IO,
    MFI_FRAME_DIR_NONE,
    MFI_FRAME_DIR_READ,
    MFI_FRAME_DIR_WRITE,
    megasas_dcmd_frame,
    megasas_pthru_frame,
    offsetof,
)
# from .linux_device import DcmdDevice

def get_buffer_address(buf):
    if isinstance(buf, DataBuffer):
        return buf.addr
    elif isinstance(buf, ctypes.Structure):
        return ctypes.addressof(buf)
    elif isinstance(buf, int) or isinstance(buf, ctypes.c_void_p):
        return buf
    return 0

def get_data_buffer(data_len, from_buffer=None):
    class DataBuffer(ctypes.Structure):
        _fields_ = [("data", ctypes.c_char * data_len),]
    if from_buffer:
        data_buffer = DataBuffer.from_buffer(from_buffer)
    else:
        data_buffer = DataBuffer()
    return data_buffer


class megasas_dcmd_cmd(object):
    def __init__(self, statusp: int=None):
        self.statusp = statusp
        # the _cdb may include command and data_buffer
        self._cdb = megasas_iocpacket()

    @property
    def cdb(self):
        return self._cdb

    def build_command(self, 
                      bus_no: int,
                      opcode: int,
                      buf,
                      bufsize: int,
                      mbox,
                      mboxlen,
                      ):
        if ((mbox != None and (mboxlen == 0 or mboxlen > MFI_MBOX_SIZE)) or 
            (mbox is None and mboxlen != 0)):
            raise ValueError("Invalid mbox and mboxlen")
        ##
        dcmd = self._cdb.frame.dcmd
        self._cdb.host_no = bus_no
        if mbox:
            ctypes.memmove(dcmd.mbox, mbox, mboxlen)
        dcmd.cmd = MFI_CMD_DCMD
        dcmd.timeout = 0
        dcmd.flags = 0
        dcmd.data_xfer_len = bufsize
        dcmd.opcode = opcode
        #
        if bufsize > 0:
            dcmd.sge_count = 1
            dcmd.data_xfer_len = bufsize
            dcmd.sgl.sge32[0].phys_addr = get_buffer_address(buf)
            dcmd.sgl.sge32[0].length = bufsize
            self._cdb.sge_count = 1
            self._cdb.sgl_off = offsetof(megasas_dcmd_frame, 'sgl')
            self._cdb.sgl[0].iov_base = get_buffer_address(buf)
            self._cdb.sgl[0].iov_len = bufsize


class MegasasCmd(object):
    """
    /* Issue passthrough scsi command to PERC5/6 controllers */
    """
    def __init__(self,):
        # the _cdb may include command and data_buffer
        self._cdb = megasas_iocpacket()
        # self._pthru = megasas_pthru_frame()
        # self._uio = megasas_iocpacket()

    @property
    def cdb(self):
        return self._cdb

    @property
    def uio(self):
        return self.cdb

    @property
    def pthru(self) -> megasas_pthru_frame:
        return self.uio.frame.pthru

    def build_command(self, 
                      m_disknum: int,
                      m_hba: int,
                      cdbLen: int,
                      cdb,
                      dataLen: int, 
                      dxfer_dir: int, 
                      data):
        self.pthru.cmd = MFI_CMD_PD_SCSI_IO
        self.pthru.cmd_status = 0xFF
        self.pthru.scsi_status = 0
        self.pthru.target_id = m_disknum
        self.pthru.lun = 0
        self.pthru.cdb_len = cdbLen
        self.pthru.timeout = 0
        if dxfer_dir == SCSI_DXFER.DXFER_NONE.value:
            self.pthru.flags = MFI_FRAME_DIR_NONE
        elif dxfer_dir == SCSI_DXFER.DXFER_FROM_DEVICE.value:
            self.pthru.flags = MFI_FRAME_DIR_READ
        elif dxfer_dir == SCSI_DXFER.DXFER_TO_DEVICE.value:
            self.pthru.flags = MFI_FRAME_DIR_WRITE
        else:
            raise ValueError("Invalid dxfer_dir %d" % dxfer_dir)
        if dataLen > 0:
            self.pthru.sge_count = 1
            self.pthru.data_xfer_len = dataLen
            self.pthru.sgl.sge32[0].phys_addr = get_buffer_address(data)
            self.pthru.sgl.sge32[0].length = dataLen
        #
        for i in range(cdbLen):
            self.pthru.cdb[i] = cdb[i]
        #
        self.uio.host_no = m_hba
        if dataLen > 0:
            self.uio.sge_count = 1
            self.uio.sgl_off = offsetof(megasas_pthru_frame,'sgl')
            self.uio.sgl[0].iov_base = get_buffer_address(data)
            self.uio.sgl[0].iov_len = dataLen


class megadev_cmd(object):
    """
    Issue passthrough scsi commands to PERC2/3/4 controllers.
    """
    def __init__(self,):
        # the _cdb may include command and data_buffer
        self._cdb = uioctl_t()
        # self._pthru = megasas_pthru_frame()
        # self._uio = megasas_iocpacket()

    @property
    def cdb(self):
        return self._cdb

    def build_command(self,
                      m_disknum: int,
                      m_hba: int,
                      cdbLen: int,
                      cdb,
                      dataLen: int,
                      data):
        if m_disknum == 7:
            raise ValueError("Don't issue to the controller(m_disknum=7)")
        self._cdb.inlen = dataLen
        self._cdb.outlen = dataLen
        self._cdb.ui.fcs.opcode = 0x80
        self._cdb.ui.fcs.adapno = MKADAP(m_hba)
        self._cdb.data.pointer = get_buffer_address(data)
        #
        self._cdb.mbox.cmd = MEGA_MBOXCMD_PASSTHRU
        self._cdb.mbox.xferaddr = get_buffer_address(self._cdb.pthru)
        #
        self._cdb.pthru.ars = 1
        self._cdb.pthru.timeout = 2
        self._cdb.pthru.channel = 0
        self._cdb.pthru.target = m_disknum
        self._cdb.pthru.cdblen = cdbLen
        self._cdb.pthru.reqsenselen = MAX_REQ_SENSE_LEN
        self._cdb.pthru.dataxferaddr = get_buffer_address(data)
        self._cdb.pthru.dataxferlen = dataLen
        #
        for i in range(cdbLen):
            self._cdb.pthru.cdb[i] = cdb[i]
        #
        return self._cdb
