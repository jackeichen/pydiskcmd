# sg.h

# /* synchronous SCSI command ioctl, (only in version 3 interface) */
# #define SG_IO 0x2285   /* similar effect as write() followed by read() */
from pydiskcmdlib.os.lin_ioctl_request import IOCTLRequest
SG_IO = IOCTLRequest.SG_IO_IOCTL.value

# /* following 'info' values are "or"-ed together */
# #define SG_INFO_OK_MASK 0x1
# #define SG_INFO_OK 0x0          /* no sense, host nor driver "noise" */
# #define SG_INFO_CHECK 0x1       /* something abnormal happened */
SG_INFO_OK_MASK = 0x1
SD_INFO_OK = 0x0
SG_INFO_CHECK = 0x1


# /* Use negative values to flag difference from original sg_header structure */
# #define SG_DXFER_NONE (-1)      /* e.g. a SCSI Test Unit Ready command */
# #define SG_DXFER_TO_DEV (-2)    /* e.g. a SCSI WRITE command */
# #define SG_DXFER_FROM_DEV (-3)  /* e.g. a SCSI READ command */
# #define SG_DXFER_TO_FROM_DEV (-4) /* treated like SG_DXFER_FROM_DEV with the
# 				   additional property than during indirect
# 				   IO the user buffer is copied into the
# 				   kernel buffers before the transfer */
# #define SG_DXFER_UNKNOWN (-5)   /* Unknown data direction */

SG_DXFER_NONE = -1
SG_DXFER_TO_DEV = -2
SG_DXFER_FROM_DEV = -3
SG_DXFER_TO_FROM_DEV = -4
SG_DXFER_UNKNOWN = -5


TIMEOUT = 1800000