# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from ctypes import (Structure,
                    Union,
                    c_int,
                    c_uint8,
                    c_uint16,
                    c_uint32,
                    c_uint64,
                    c_ubyte,
                    sizeof,
                    c_ulonglong,
                    c_void_p,
                    c_size_t,
                    )

### IOC setting ###
_IOC_NRBITS =	8
_IOC_TYPEBITS =	8

_IOC_SIZEBITS =	14
_IOC_DIRBITS =	2

_IOC_NRMASK =   (1 << _IOC_NRBITS) - 1
_IOC_TYPEMASK = (1 << _IOC_TYPEBITS) - 1
_IOC_SIZEMASK = (1 << _IOC_SIZEBITS) - 1
_IOC_DIRMASK =  (1 << _IOC_DIRBITS) - 1

_IOC_NRSHIFT =	 0
_IOC_TYPESHIFT = _IOC_NRSHIFT + _IOC_NRBITS
_IOC_SIZESHIFT = _IOC_TYPESHIFT + _IOC_TYPEBITS
_IOC_DIRSHIFT =	 _IOC_SIZESHIFT + _IOC_SIZEBITS

_IOC_NONE = 0
_IOC_WRITE = 1
_IOC_READ = 2

def _IOC_TYPECHECK(t):
    return sizeof(t)

def _IOC(dir, type, nr, size):
    return (dir  << _IOC_DIRSHIFT) | \
           (type << _IOC_TYPESHIFT) | \
           (nr   << _IOC_NRSHIFT) | \
           (size << _IOC_SIZESHIFT)

def _IOWR(type, nr, size):
    return _IOC(_IOC_READ|_IOC_WRITE, ord(type), nr, _IOC_TYPECHECK(size))

###
class iovec(Structure):
    _fields_ = [("iov_base", c_void_p), ("iov_len", c_size_t)]
###
def offsetof(_struc: Structure, member: str):
    return getattr(_struc, member).offset
### IOC setting ###
# /*======================================================
# * PERC2/3/4 Passthrough SCSI Command Interface
# *
# * Contents from:
# *  drivers/scsi/megaraid/megaraid_ioctl.h
# *  drivers/scsi/megaraid/mbox_defs.h
# *======================================================*/
#define MEGAIOC_MAGIC   'm'
#define MEGAIOCCMD      _IOWR(MEGAIOC_MAGIC, 0, struct uioctl_t)
MEGAIOC_MAGIC = 'm'

# /* Following subopcode work for opcode == 0x82 */
#define MKADAP(adapno)   (MEGAIOC_MAGIC << 8 | adapno)
#define MEGAIOC_QNADAP     'm'
#define MEGAIOC_QDRVRVER   'e'
#define MEGAIOC_QADAPINFO  'g'
MKADAP = lambda adapno: (MEGAIOC_MAGIC << 8 | adapno)
MEGAIOC_QNADAP = 'm'
MEGAIOC_QDRVRVER = 'e'
MEGAIOC_QADAPINFO = 'g'

#define MEGA_MBOXCMD_PASSTHRU 0x03
MEGA_MBOXCMD_PASSTHRU = 0x03

#define MAX_REQ_SENSE_LEN  0x20
#define MAX_CDB_LEN 10
MAX_REQ_SENSE_LEN = 0x20
MAX_CDB_LEN = 10

# typedef struct
# {
#   uint8_t  timeout : 3;
#   uint8_t  ars : 1;
#   uint8_t  reserved : 3;
#   uint8_t  islogical : 1;
#   uint8_t  logdrv;
#   uint8_t  channel;
#   uint8_t  target;
#   uint8_t  queuetag;
#   uint8_t  queueaction;
#   uint8_t  cdb[MAX_CDB_LEN];
#   uint8_t  cdblen;
#   uint8_t  reqsenselen;
#   uint8_t  reqsensearea[MAX_REQ_SENSE_LEN];
#   uint8_t  numsgelements;
#   uint8_t  scsistatus;
#   uint32_t dataxferaddr;
#   uint32_t dataxferlen;
# } __attribute__((packed)) mega_passthru;
class mega_passthru(Structure):
    _fields_ = [
        ("timeout", c_uint8, 3),
        ("ars", c_uint8, 1),
        ("reserved", c_uint8, 3),
        ("islogical", c_uint8, 1),
        ("logdrv", c_uint8),
        ("channel", c_uint8),
        ("target", c_uint8),
        ("queuetag", c_uint8),
        ("queueaction", c_uint8),
        ("cdb", c_uint8 * MAX_CDB_LEN),
        ("cdblen", c_uint8),
        ("reqsenselen", c_uint8),
        ("reqsensearea", c_uint8 * MAX_REQ_SENSE_LEN),
        ("numsgelements", c_uint8),
        ("scsistatus", c_uint8),
        ("dataxferaddr", c_uint32),
        ("dataxferlen", c_uint32),
    ]
    _pack_ = 1

# typedef struct
# {
#   uint8_t   cmd;
#   uint8_t   cmdid;
#   uint8_t   opcode;
#   uint8_t   subopcode;
#   uint32_t  lba;
#   uint32_t  xferaddr;
#   uint8_t   logdrv;
#   uint8_t   resvd[3];
#   uint8_t   numstatus;
#   uint8_t   status;
# } __attribute__((packed)) megacmd_t;
class megacmd_t(Structure):
    _fields_ = [
        ("cmd", c_uint8),
        ("cmdid", c_uint8),
        ("opcode", c_uint8),
        ("subopcode", c_uint8),
        ("lba", c_uint32),
        ("xferaddr", c_uint32),
        ("logdrv", c_uint8),
        ("resvd", c_uint8 * 3),
        ("numstatus", c_uint8),
        ("status", c_uint8),
    ]
    _pack_ = 1

# typedef union {
#   uint8_t   *pointer;
#   uint8_t    pad[8];
# } ptr_t;
class ptr_t(Union):
    _fields_ = [
        ("pointer", c_uint64),
        ("pad", c_uint8 * 8),
    ]
    _pack_ = 1

# // The above definition assumes sizeof(void*) <= 8.
# // This assumption also exists in the linux megaraid device driver.
# // So define a macro to check expected size of ptr_t at compile time using
# // a dummy typedef.  On size mismatch, compiler reports a negative array
# // size.  If you see an error message of this form, it means that
# // you have an unexpected pointer size on your platform and can not
# // use megaraid support in smartmontools.
# typedef char assert_sizeof_ptr_t[sizeof(ptr_t) == 8 ? 1 : -1];

# struct uioctl_t
# {
#   uint32_t       inlen;
#   uint32_t       outlen;
#   union {
#     uint8_t      fca[16];
#     struct {
#       uint8_t  opcode;
#       uint8_t  subopcode;
#       uint16_t adapno;
#       ptr_t    buffer;
#       uint32_t length;
#     } __attribute__((packed)) fcs;
#   } __attribute__((packed)) ui;
#   megacmd_t     mbox;
#   mega_passthru pthru;
#   ptr_t         data;
# } __attribute__((packed));
class fcs(Structure):
    _fields_ = [
        ("opcode", c_uint8),
        ("subopcode", c_uint8),
        ("adapno", c_uint16),
        ("buffer", ptr_t),
        ("length", c_uint32),
    ]
    _pack_ = 1

class ui(Union):
    _fields_ = [
        ("fca", c_uint8 * 16),
        ("fcs", fcs),
    ]
    _pack_ = 1

class uioctl_t(Structure):
    _fields_ = [
        ("inlen", c_uint32),
        ("outlen", c_uint32),
        ("ui", ui),
        ("mbox", megacmd_t),
        ("pthru", mega_passthru),
        ("data", ptr_t),
    ]

MEGAIOCCMD = _IOWR(MEGAIOC_MAGIC, 0, uioctl_t)

# /*===================================================
# * PERC5/6 Passthrough SCSI Command Interface
# *
# * Contents from:
# *  drivers/scsi/megaraid/megaraid_sas.h
# *===================================================*/
# #define MEGASAS_MAGIC          'M'
# #define MEGASAS_IOC_FIRMWARE   _IOWR(MEGASAS_MAGIC, 1, struct megasas_iocpacket)

# #define MFI_CMD_PD_SCSI_IO        0x04
# #define MFI_CMD_DCMD              0x05
# #define MFI_FRAME_SGL64           0x02
# #define MFI_STAT_OK               0x00
# #define MFI_DCMD_PD_GET_LIST      0x02010000
# /*
# * Number of mailbox bytes in DCMD message frame
# */
# #define MFI_MBOX_SIZE             12
# #define MAX_IOCTL_SGE             16
# #define MFI_FRAME_DIR_NONE        0x0000
# #define MFI_FRAME_DIR_WRITE       0x0008
# #define MFI_FRAME_DIR_READ        0x0010
# #define MFI_FRAME_DIR_BOTH        0x0018

# #define MAX_SYS_PDS               240
MEGASAS_MAGIC = 'M'

MFI_CMD_PD_SCSI_IO = 0x04
MFI_CMD_DCMD = 0x05
MFI_FRAME_SGL64 = 0x02
MFI_STAT_OK = 0x00
MFI_DCMD_PD_GET_LIST = 0x02010000
# Number of mailbox bytes in DCMD message frame
MFI_MBOX_SIZE = 12
MAX_IOCTL_SGE = 16
MFI_FRAME_DIR_NONE = 0x0000
MFI_FRAME_DIR_WRITE = 0x0008
MFI_FRAME_DIR_READ = 0x0010
MFI_FRAME_DIR_BOTH = 0x0018
MAX_SYS_PDS = 240

# struct megasas_sge32 {
#   u32 phys_addr;
#   u32 length;
# } __attribute__ ((packed));
class megasas_sge32(Structure):
    _fields_ = [
        ("phys_addr", c_uint32),
        ("length", c_uint32),
    ]
    _pack_ = 1

# struct megasas_sge64 {
#   u64 phys_addr;
#   u32 length;
# } __attribute__ ((packed));
class megasas_sge64(Structure):
    _fields_ = [
        ("phys_addr", c_uint64),
        ("length", c_uint32),
    ]
    _pack_ = 1

# union megasas_sgl {
#   struct megasas_sge32 sge32[1];
#   struct megasas_sge64 sge64[1];
# } __attribute__ ((packed));
class megasas_sgl(Union):
    _fields_ = [
        ("sge32", megasas_sge32 * 1),
        ("sge64", megasas_sge64 * 1),
    ]
    _pack_ = 1

# struct megasas_header {
#   u8 cmd;           /*00h */
#   u8 sense_len;     /*01h */
#   u8 cmd_status;    /*02h */
#   u8 scsi_status;   /*03h */
#   u8 target_id;     /*04h */
#   u8 lun;           /*05h */
#   u8 cdb_len;       /*06h */
#   u8 sge_count;     /*07h */
#   u32 context;      /*08h */
#   u32 pad_0;        /*0Ch */
#   u16 flags;        /*10h */
#   u16 timeout;      /*12h */
#   u32 data_xferlen; /*14h */
  
# } __attribute__ ((packed));
class megasas_header(Structure):
    _fields_ = [
        ("cmd", c_uint8),
        ("sense_len", c_uint8),
        ("cmd_status", c_uint8),
        ("scsi_status", c_uint8),
        ("target_id", c_uint8),
        ("lun", c_uint8),
        ("cdb_len", c_uint8),
        ("sge_count", c_uint8),
        ("context", c_uint32),
        ("pad_0", c_uint32),
        ("flags", c_uint16),
        ("timeout", c_uint16),
        ("data_xferlen", c_uint32),
    ]
    _pack_ = 1
megasas_header.cmd.offset
# struct megasas_pthru_frame {
#   u8 cmd;            /*00h */
#   u8 sense_len;      /*01h */
#   u8 cmd_status;     /*02h */
#   u8 scsi_status;    /*03h */
#   u8 target_id;      /*04h */
#   u8 lun;            /*05h */
#   u8 cdb_len;        /*06h */
#   u8 sge_count;      /*07h */
#   u32 context;       /*08h */
#   u32 pad_0;         /*0Ch */
#   u16 flags;         /*10h */
#   u16 timeout;       /*12h */
#   u32 data_xfer_len; /*14h */
#   u32 sense_buf_phys_addr_lo; /*18h */
#   u32 sense_buf_phys_addr_hi; /*1Ch */
#   u8 cdb[16];            /*20h */
#   union megasas_sgl sgl; /*30h */
#   } __attribute__ ((packed));
class megasas_pthru_frame(Structure):
    _fields_ = [
        ("cmd", c_uint8),
        ("sense_len", c_uint8),
        ("cmd_status", c_uint8),
        ("scsi_status", c_uint8),
        ("target_id", c_uint8),
        ("lun", c_uint8),
        ("cdb_len", c_uint8),
        ("sge_count", c_uint8),
        ("context", c_uint32),
        ("pad_0", c_uint32),
        ("flags", c_uint16),
        ("timeout", c_uint16),
        ("data_xfer_len", c_uint32),
        ("sense_buf_phys_addr_lo", c_uint32),
        ("sense_buf_phys_addr_hi", c_uint32),
        ("cdb", c_uint8 * 16),
        ("sgl", megasas_sgl),
    ]
    _pack_ = 1

#   union {   /*1Ch */
#     u8 b[12];
#     u16 s[6];
#     u32 w[3];
#   } mbox;
class mbox(Union):
    _fields_ = [
        ("b", c_uint8 * 12),
        ("s", c_uint16 * 6),
        ("w", c_uint32 * 3),
    ]
    _pack_ = 1

# struct megasas_dcmd_frame {
#   u8 cmd;            /*00h */
#   u8 reserved_0;     /*01h */
#   u8 cmd_status;     /*02h */
#   u8 reserved_1[4];  /*03h */
#   u8 sge_count;      /*07h */
#   u32 context;       /*08h */
#   u32 pad_0;         /*0Ch */
#   u16 flags;         /*10h */
#   u16 timeout;  /*12h */
#   u32 data_xfer_len; /*14h */
#   u32 opcode;  /*18h */
#   union {   /*1Ch */
#     u8 b[12];
#     u16 s[6];
#     u32 w[3];
#   } mbox;
#   union megasas_sgl sgl; /*28h */
# } __attribute__ ((packed));
class megasas_dcmd_frame(Structure):
    _fields_ = [
        ("cmd", c_uint8),
        ("reserved_0", c_uint8),
        ("cmd_status", c_uint8),
        ("reserved_1", c_uint8 * 4),
        ("sge_count", c_uint8),
        ("context", c_uint32),
        ("pad_0", c_uint32),
        ("flags", c_uint16),
        ("timeout", c_uint16),
        ("data_xfer_len", c_uint32),
        ("opcode", c_uint32),
        ("mbox", mbox),
        ("sgl", megasas_sgl),
    ]
    _pack_ = 1

#   union {
#     u8 raw[128];
#     struct megasas_header hdr;
#     struct megasas_pthru_frame pthru;
#     struct megasas_dcmd_frame dcmd;
#   } frame;
class frame(Union):
    _fields_ = [
        ("raw", c_uint8 * 128),
        ("hdr", megasas_header),
        ("pthru", megasas_pthru_frame),
        ("dcmd", megasas_dcmd_frame),
    ]
    _pack_ = 1

# struct megasas_iocpacket {
#   u16 host_no;
#   u16 __pad1;
#   u32 sgl_off;
#   u32 sge_count;
#   u32 sense_off;
#   u32 sense_len;
#   union {
#     u8 raw[128];
#     struct megasas_header hdr;
#     struct megasas_pthru_frame pthru;
#     struct megasas_dcmd_frame dcmd;
#   } frame;
#   struct iovec sgl[MAX_IOCTL_SGE];
# } __attribute__ ((packed));
class megasas_iocpacket(Structure):
    _fields_ = [
        ("host_no", c_uint16),
        ("__pad1", c_uint16),
        ("sgl_off", c_uint32),
        ("sge_count", c_uint32),
        ("sense_off", c_uint32),
        ("sense_len", c_uint32),
        ("frame", frame),
        ("sgl", iovec * MAX_IOCTL_SGE),
    ]
    _pack_ = 1

# struct megasas_pd_address {
#   u16 device_id;
#   u16 encl_device_id;
#   u8 encl_index;
#   u8 slot_number;
#   u8 scsi_dev_type; /* 0 = disk */
#   u8 connect_port_bitmap;
#   u64 sas_addr[2];
# }   __attribute__ ((packed));
class megasas_pd_address(Structure):
    _fields_ = [
        ("device_id", c_uint16),
        ("encl_device_id", c_uint16),
        ("encl_index", c_uint8),
        ("slot_number", c_uint8),
        ("scsi_dev_type", c_uint8),
        ("connect_port_bitmap", c_uint8),
        ("sas_addr", c_uint64 * 2),
    ]
    _pack_ = 1

# struct megasas_pd_list {
#   u32 size;
#   u32 count;
#   struct megasas_pd_address addr[MAX_SYS_PDS];
# } __attribute__ ((packed));
class megasas_pd_list(Structure):
    _fields_ = [
        ("size", c_uint32),
        ("count", c_uint32),
        ("addr", megasas_pd_address * MAX_SYS_PDS),
    ]
    _pack_ = 1

# #define MEGASAS_IOC_FIRMWARE   _IOWR(MEGASAS_MAGIC, 1, struct megasas_iocpacket)
MEGASAS_IOC_FIRMWARE = _IOWR(MEGASAS_MAGIC, 1, megasas_iocpacket)
