import ctypes
import fcntl

from pydiskcmdlib.sgio.constants import SG_INFO_OK_MASK, SG_INFO_OK, SG_IO, TIMEOUT
from pydiskcmdlib.sgio.constants import SG_DXFER_TO_DEV, SG_DXFER_FROM_DEV, SG_DXFER_NONE
from pydiskcmdlib.sgio.errors import UnspecifiedError, CheckConditionError
from pydiskcmdlib import log

# interface_id = ord('S')
InterfaceID = 83

class CheckConditionError(Exception):
    """The target is reporting an error.

    Send a Request Sense command to retrieve error information.

    See https://en.wikipedia.org/wiki/SCSI_check_condition for details.
    """

    def __init__(self, sense):
        super(CheckConditionError, self).__init__(
            'SCSI Check Condition: %s' % sense.hex()
        )
        self.sense = sense


class UnspecifiedError(Exception):
    """Something went wrong."""


class sgioHdr(ctypes.Structure):
    """
    This structure descibed in scsi/sg.h
    """
    _pack_ = 1
    _fields_ = [
        ('interface_id', ctypes.c_int),
        ('dxfer_direction', ctypes.c_int),
        ('cmd_len', ctypes.c_ubyte),
        ('mx_sb_len', ctypes.c_ubyte),
        ('iovec_count', ctypes.c_ushort),
        ('dxfer_len', ctypes.c_uint),
        ('dxferp', ctypes.c_void_p),
        ('cmdp', ctypes.c_void_p),
        ('sbp', ctypes.c_void_p),
        ('timeout', ctypes.c_uint),
        ('flags', ctypes.c_uint),
        ('pack_id', ctypes.c_int),
        ('usr_ptr', ctypes.c_void_p),
        ('status', ctypes.c_ubyte),
        ('masked_status', ctypes.c_ubyte),
        ('msg_status', ctypes.c_ubyte),
        ('sb_len_wr', ctypes.c_ubyte),
        ('host_status', ctypes.c_ushort),
        ('driver_status', ctypes.c_ushort),
        ('resid', ctypes.c_int),
        ('duration', ctypes.c_uint),
        ('info', ctypes.c_uint)]


def execute(
    fid,
    cdb: bytearray,
    data_out: bytearray,
    data_in: bytearray,
    max_sense_data_length: int = 32,
    return_sense_buffer: bool = False
    ):

    if data_out is not None and len(data_out) and data_in is not None and len(data_in):
        raise NotImplemented('Indirect IO is not suported')
    elif data_out is not None and len(data_out):
        dxfer_direction = SG_DXFER_TO_DEV
        # For check if not bytearray data
        if not isinstance(data_out, bytearray):
            data_out = bytearray(data_out)
        data_buffer = data_out
    elif data_in is not None and len(data_in):
        dxfer_direction = SG_DXFER_FROM_DEV
        if not isinstance(data_in, bytearray):
            raise RuntimeError("Bytearray data_in is need")
        data_buffer = data_in
    else:
        dxfer_direction = SG_DXFER_NONE
        data_buffer = []

    if data_buffer is not None and data_buffer:
        c_buffer = ctypes.c_char * len(data_buffer)
        dxferp = ctypes.addressof(c_buffer.from_buffer(data_buffer))
    else:
        dxferp = 0

    sense_buffer = ctypes.create_string_buffer(max_sense_data_length)
    sbp = ctypes.addressof(sense_buffer)

    cdb_buffer = ctypes.c_char * len(cdb)
    cmdp = ctypes.addressof(cdb_buffer.from_buffer(cdb))

    io_hdr = sgioHdr(interface_id=InterfaceID, dxfer_direction=dxfer_direction,
                       cmd_len=len(cdb),
                       mx_sb_len=max_sense_data_length, iovec_count=0,
                       dxfer_len=len(data_buffer),
                       dxferp=dxferp,
                       cmdp=cmdp,
                       sbp=sbp, timeout=TIMEOUT,
                       flags=0, pack_id=0, usr_ptr=None, status=0, masked_status=0,
                       msg_status=0, sb_len_wr=0, host_status=0, driver_status=0,
                       resid=0, duration=0, info=0)


    result = fcntl.ioctl(fid.fileno(), SG_IO, io_hdr)
    if result < 0:
        raise OSError('ioctl failed')

    if io_hdr.info & SG_INFO_OK_MASK != SG_INFO_OK:
        log.debug("SGIO: SG_INFO: %#x, sb_len_wr: %d, resid: %d" % ((io_hdr.info & SG_INFO_OK_MASK), io_hdr.sb_len_wr, io_hdr.resid))
        log.debug("SGIO: sense data: %s" % bytes(sense_buffer))
        if io_hdr.sb_len_wr > 0:
            raise CheckConditionError(bytes(sense_buffer[:io_hdr.sb_len_wr]))
        else:
            log.debug("SGIO: host_status: %#x, driver_status: %#x, scsi status: %#x" % (io_hdr.host_status, io_hdr.driver_status, io_hdr.status))
            if io_hdr.status == 0:
                # Very Strange case for some vendors, that when do smart read data and smart read threshold data,
                # one fo these command will return host_status: 0x102, driver_status: 0x1600, scsi status: 0x0.
                # or host_status: 0x0, driver_status: 0x0, scsi status: 0x0, .etc.
                # Only check scsi status, this work around may leave out a real error. 
                pass
            else:
                raise UnspecifiedError()
    # Return the actual transfer written and any sense we got.
    if return_sense_buffer:
        return io_hdr.resid, bytes(sense_buffer)
    else:
        return io_hdr.resid
