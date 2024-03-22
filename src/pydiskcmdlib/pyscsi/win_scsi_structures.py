# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import ctypes

SPT_CDB_LENGTH = 32
SPT_SENSE_LENGTH = 32
SPTWB_DATA_LENGTH = 512
##
CDB6GENERIC_LENGTH = 6
CDB10GENERIC_LENGTH = 10
CDB12GENERIC_LENGTH = 12
CDB16GENERIC_LENGTH = 16


# typedef struct ScsiPassThrough
# {
#     unsigned short Length;           /* [x00] */
#     unsigned char ScsiStatus;        /* [x01] */
#     unsigned char PathId;            /* [x02] */
#     unsigned char TargetId;          /* [x03] */
#     unsigned char Lun;               /* [x04] */
#     unsigned char CdbLength;         /* [x05] */
#     unsigned char SenseInfoLength;   /* [x06] */
#     unsigned char DataIn;            /* [x07] */
#     unsigned int DataTransferLength; /* [x0B:0A:09:08] */
#     unsigned int TimeOutValue;       /* [x0F:0E:0D:0C] */
#     unsigned int DataBufferOffset;   /* [x13:12:11:10] */
#     unsigned int SenseInfoOffset;    /* [x17:16:15:14] */
#     unsigned char Cdb[16];           /* [x18...x27] */
# } SCSI_PASS_THROUGH;
class SCSIPassThrough(ctypes.Structure):
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
        ('data_buffer_offset', ctypes.c_uint32),
        ('sense_info_offset', ctypes.c_uint32),
        ('cdb', ctypes.c_ubyte * CDB16GENERIC_LENGTH)
    ]

# struct SCSI_PASS_THROUGH_DIRECT
# {
#     USHORT Length;
#     UCHAR ScsiStatus;
#     UCHAR PathId;
#     UCHAR TargetId;
#     UCHAR Lun;
#     UCHAR CdbLength;
#     UCHAR SenseInfoLength;
#     UCHAR DataIn;
#     ULONG DataTransferLength;
#     ULONG TimeOutValue;
#     PVOID DataBuffer;
#     ULONG SenseInfoOffset;
#     UCHAR Cdb[16];
# };
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
        ('cdb', ctypes.c_ubyte * CDB16GENERIC_LENGTH)
    ]

# typedef struct _SCSI_PASS_THROUGH_DIRECT_WITH_BUFFER {
#     SCSI_PASS_THROUGH_DIRECT sptd;
#     ULONG Filler;  // realign buffer to double word boundary
#     UCHAR ucSenseBuf[SPT_SENSE_LENGTH];
# } SCSI_PASS_THROUGH_DIRECT_WITH_BUFFER, *PSCSI_PASS_THROUGH_DIRECT_WITH_BUFFER;
class SCSIPassThroughDirectWithBuffer(ctypes.Structure):
    """
    Corresponds to the SCSI_PASS_THROUGH_DIRECT_WITH_BUFFER structure in
    <ntddscsi.h> on Windows.
    """
    _fields_ = [
        ('sptd', SCSIPassThroughDirect),
        ('filler', ctypes.c_uint32),
        ('sense', ctypes.c_ubyte * SPT_SENSE_LENGTH)
    ]

# typedef struct _SCSI_PASS_THROUGH_WITH_BUFFERS {
#     SCSI_PASS_THROUGH spt;
#     ULONG Filler;  // realign buffers to double word boundary
#     UCHAR ucSenseBuf[SPT_SENSE_LENGTH];
#     UCHAR ucDataBuf[SPTWB_DATA_LENGTH];
# } SCSI_PASS_THROUGH_WITH_BUFFERS, *PSCSI_PASS_THROUGH_WITH_BUFFERS;
class SCSIPassThroughWithBuffers(ctypes.Structure):
    _fields_ = [
        ('spt', SCSIPassThrough),
        ('filler', ctypes.c_uint32),
        ('sense_buf', ctypes.c_ubyte * SPT_SENSE_LENGTH),
        ('data_buf', ctypes.c_ubyte * SPTWB_DATA_LENGTH)
    ]


# class SCSI_PASS_THROUGH_EX(EasyCastStructure):
#     Version: UInt32
#     Length: UInt32
#     CdbLength: UInt32
#     StorAddressLength: UInt32
#     ScsiStatus: Byte
#     SenseInfoLength: Byte
#     DataDirection: Byte
#     Reserved: Byte
#     TimeOutValue: UInt32
#     StorAddressOffset: UInt32
#     SenseInfoOffset: UInt32
#     DataOutTransferLength: UInt32
#     DataInTransferLength: UInt32
#     DataOutBufferOffset: UIntPtr
#     DataInBufferOffset: UIntPtr
#     Cdb: Byte * 1
class SCSIPassThrougEx(ctypes.Structure):
    _fields_ = [
        ('version', ctypes.c_int32),
        ('length', ctypes.c_int32),
        ('cdb_length', ctypes.c_int32),
        ('stor_address_length', ctypes.c_int32),
        ('scsi_status', ctypes.c_ubyte),
        ('sense_info_length', ctypes.c_ubyte),
        ('data_direction', ctypes.c_ubyte),
        ('reserved', ctypes.c_ubyte),
        ('timeout_value', ctypes.c_uint32),
        ('stor_address_offset', ctypes.c_int32),
        ('sense_info_offset', ctypes.c_uint32),
        ('dataout_transfer_length', ctypes.c_uint32),
        ('datain_transfer_length', ctypes.c_uint32),
        ('dataout_buffer_offset', ctypes.c_size_t),
        ('datain_buffer_offset', ctypes.c_size_t),
        ('cdb', ctypes.c_ubyte * 1),
    ]


# typedef struct STOR_ADDRESS_ALIGN _STOR_ADDR_BTL8 {
#     _Field_range_(STOR_ADDRESS_TYPE_BTL8, STOR_ADDRESS_TYPE_BTL8)
#     USHORT Type;
#     USHORT Port;
#     _Field_range_(STOR_ADDR_BTL8_ADDRESS_LENGTH, STOR_ADDR_BTL8_ADDRESS_LENGTH)
#     ULONG AddressLength;
#     UCHAR Path;
#     UCHAR Target;
#     UCHAR Lun;
#     UCHAR Reserved;
# } STOR_ADDR_BTL8, *PSTOR_ADDR_BTL8;
class StorAddrBtl8(ctypes.Structure):
    _fields_ = [
        ('type', ctypes.c_ushort),
        ('port', ctypes.c_ushort),
        ('address_length', ctypes.c_ulong),
        ('path', ctypes.c_ubyte),
        ('target', ctypes.c_ubyte),
        ('lun', ctypes.c_ubyte),
        ('reserved', ctypes.c_ubyte),
    ]

# typedef struct _SCSI_PASS_THROUGH_WITH_BUFFERS_EX {
#     SCSI_PASS_THROUGH_EX spt;
#     UCHAR ucCdbBuf[SPT_CDB_LENGTH - 1];  // cushion for spt.Cdb
#     ULONG Filler;  // realign buffers to double word boundary
#     STOR_ADDR_BTL8 StorAddress;
#     UCHAR ucSenseBuf[SPT_SENSE_LENGTH];
#     UCHAR ucDataBuf[SPTWB_DATA_LENGTH];  // buffer for DataIn or DataOut
# } SCSI_PASS_THROUGH_WITH_BUFFERS_EX, *PSCSI_PASS_THROUGH_WITH_BUFFERS_EX;
class SCSIPassThroughWithBuffersEx(ctypes.Structure):
    _fields_ = [
        ('spt', SCSIPassThrougEx),
        ('cdb_buf', ctypes.c_ubyte * (SPT_CDB_LENGTH-1)),
        ('filler', ctypes.c_uint32),
        ('stor_address', StorAddrBtl8), 
        ('sense_buf', ctypes.c_ubyte * SPT_SENSE_LENGTH),
        ('data_buf', ctypes.c_ubyte * SPTWB_DATA_LENGTH)
    ]


# class SCSI_PASS_THROUGH_DIRECT_EX(EasyCastStructure):
#     Version: UInt32
#     Length: UInt32
#     CdbLength: UInt32
#     StorAddressLength: UInt32
#     ScsiStatus: Byte
#     SenseInfoLength: Byte
#     DataDirection: Byte
#     Reserved: Byte
#     TimeOutValue: UInt32
#     StorAddressOffset: UInt32
#     SenseInfoOffset: UInt32
#     DataOutTransferLength: UInt32
#     DataInTransferLength: UInt32
#     DataOutBuffer: VoidPtr
#     DataInBuffer: VoidPtr
#     Cdb: Byte * 1
class SCSIPassThrougDirectEx(ctypes.Structure):
    _fields_ = [
        ('version', ctypes.c_int32),
        ('length', ctypes.c_int32),
        ('cdb_length', ctypes.c_int32),
        ('stor_address_length', ctypes.c_int32),
        ('scsi_status', ctypes.c_ubyte),
        ('sense_info_length', ctypes.c_ubyte),
        ('data_direction', ctypes.c_ubyte),
        ('reserved', ctypes.c_ubyte),
        ('timeout_value', ctypes.c_uint32),
        ('stor_address_offset', ctypes.c_int32),
        ('sense_info_offset', ctypes.c_uint32),
        ('dataout_transfer_length', ctypes.c_uint32),
        ('datain_transfer_length', ctypes.c_uint32),
        ('dataout_buffer_offset', ctypes.c_void_p),
        ('datain_buffer_offset', ctypes.c_void_p),
        ('cdb', ctypes.c_ubyte * 1),
    ]

# typedef struct _SCSI_PASS_THROUGH_DIRECT_WITH_BUFFER_EX {
#     SCSI_PASS_THROUGH_DIRECT_EX sptd;
#     UCHAR ucCdbBuf[SPT_CDB_LENGTH - 1];  // cushion for sptd.Cdb
#     ULONG Filler;  // realign buffer to double word boundary
#     STOR_ADDR_BTL8 StorAddress;
#     UCHAR ucSenseBuf[SPT_SENSE_LENGTH];
# } SCSI_PASS_THROUGH_DIRECT_WITH_BUFFER_EX,
#     *PSCSI_PASS_THROUGH_DIRECT_WITH_BUFFER_EX;
class SCSIPassThroughDirectWithBufferEx(ctypes.Structure):
    _fields_ = [
        ('sptd', SCSIPassThrougDirectEx),
        ('cdb_buf', ctypes.c_ubyte * (SPT_CDB_LENGTH-1)),
        ('filler', ctypes.c_uint32),
        ('stor_address', StorAddrBtl8), 
        ('sense_buf', ctypes.c_ubyte * SPT_SENSE_LENGTH),
    ]
