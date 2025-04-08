# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import os
import pathlib
import re
import stat
import binascii
import traceback
from pydiskcmdlib.pyscsi.lin_scsi_structures import SCSI_DXFER
from .linux_device import DcmdDevice
from .linux_command import megasas_dcmd_cmd,MegasasCmd,megadev_cmd,get_data_buffer
from .megaraid_ioctl_structures import (
    MFI_DCMD_PD_GET_LIST,
    megasas_pd_list,
    sizeof,
)
from pydiskcmdlib.os.lin_utils import get_host_ids
from pydiskcmdlib import log
from pydiskcmdlib.exceptions import DeviceNotFound,CommandDataStrucError
##
from pyscsi.utils.converter import get_opcode
from pyscsi.pyscsi.scsi_enum_command import spc, sbc
from pydiskcmdlib.utils.converter import translocate_bytearray
from pyscsi.pyscsi.scsi_command import SCSICommand
from pyscsi.pyscsi.scsi_cdb_inquiry import Inquiry
from pyscsi.pyscsi.scsi_cdb_readcapacity16 import ReadCapacity16
from pydiskcmdlib.pysata.ata_cdb_smart import SmartReadData16
from pydiskcmdlib.pysata.ata_cdb_smart import SmartReadThresh16 
from pydiskcmdlib.pysata.ata_cdb_identify import Identify16
from pydiskcmdlib.pysata.ata_cdb_smart import SmartReadLog16
from pydiskcmdlib.pysata.ata_cdb_readlog import ReadLogExt
from pydiskcmdlib import log

# linux_smart_interface::megasas_pd_add_list(int bus_no, smart_device_list & devlist)
# {
#   /*
#   * Keep fetching the list in a loop until we have a large enough
#   * buffer to hold the entire list.
#   */
#   megasas_pd_list * list = 0;
#   for (unsigned list_size = 1024; ; ) {
#     list = reinterpret_cast<megasas_pd_list *>(realloc(list, list_size));
#     if (!list)
#       throw std::bad_alloc();
#     memset(list, 0, list_size);
#     if (megasas_dcmd_cmd(bus_no, MFI_DCMD_PD_GET_LIST, list, list_size, NULL, 0,
#       NULL) < 0) 
#     {
#       free(list);
#       return (-1);
#     }
#     if (list->size <= list_size)
#       break;
#     list_size = list->size;
#   }


def prepare_megaraid_sas_ioctl_node():
    if os.path.exists("/dev/megaraid_sas_ioctl_node") or os.path.exists("/dev/megadev0"):
        return 0
    if not os.path.exists("/proc/devices"):
        return 1
    with open("/proc/devices", "r") as f:
        for line in f.readlines():
            g = re.match(r"(\d+) megaraid_sas_ioctl", line)  # megaraid_sas_ioctl_node
            g1 = re.match(r"(\d+) megadev", line)  # megadev0
            if g:
                mjr = int(g.group(1))
                n1 = len(g.group(0))
                if n1 == 22:
                    node_path = pathlib.Path("/dev/megaraid_sas_ioctl_node")
                    node_path.unlink(missing_ok=True)
                    os.mknod(node_path, mode=stat.S_IFCHR | 0o600, device=os.makedev(mjr, 0))
                    log.debug("Creating /dev/megaraid_sas_ioctl_node = %d", n1)
                    break
            elif g1:
                mjr = int(g1.group(1))
                n1 = len(g1.group(0))
                if n1 == 11:
                    node_path = pathlib.Path("/dev/megadev0")
                    node_path.unlink(missing_ok=True)
                    os.mknod(node_path, mode=stat.S_IFCHR | 0o600, device=os.makedev(mjr, 0))
                    log.debug("Creating /dev/megadev0 = %d", n1)
                    break
    return 0


class linux_megaraid_device(object):
    def __init__(self, bus_no, device_id):
        self._bus_no = bus_no
        self._device_id = device_id

    @property
    def device_id(self):
        return self._device_id

    @property
    def bus_no(self):
        return self._bus_no


class PhysicalDriveBase(object):
    def __init__(self, bus_no, device_id, device=None):
        self._bus_no = bus_no
        self._device_id = device_id
        if device:
            self._dev = device
        else:
            if os.path.exists("/dev/megaraid_sas_ioctl_node"):
                self._dev = DcmdDevice("/dev/megaraid_sas_ioctl_node")
                self.__pt_cmd = self._megasas_cmd
            elif os.path.exists("/dev/megadev0"):
                self._dev = DcmdDevice("/dev/megadev0")
                self.__pt_cmd = self._megadev_cmd
            else:
                raise DeviceNotFound("cannot open /dev/megaraid_sas_ioctl_node or /dev/megadev0")
        ##
        self.sbc_opcodes = sbc
        self.spc_opcodes = spc

    @property
    def device_id(self):
        return self._device_id

    @property
    def bus_no(self):
        return self._bus_no

    def _megasas_cmd(self, cdbLen, cdb, dataLen, data, dxfer_dir):
        cmd = MegasasCmd()
        cmd.build_command(self.device_id, self._bus_no, cdbLen, cdb, dataLen, dxfer_dir, data)
        self._dev.execute_megasas(cmd)
        return cmd

    def _megadev_cmd(self, cdbLen, cdb, dataLen, data, *args):
        cmd = megadev_cmd()
        cmd.build_command(self.device_id, self._bus_no, cdbLen, cdb, dataLen, data)
        self._dev.execute_megadev(cmd)
        return cmd

    def scsi_passthrough_cmd(self, cmd: SCSICommand) -> SCSICommand:
        # Controller rejects Test Unit Ready
        if cmd.opcode == 0:
            return 0
        #  Controller does not return ATA output registers in SAT sense data
        if cmd.opcode == 0xa1 or cmd.opcode == 0x85:
            if (cmd.cdb[2] & (1 << 5)):
                raise CommandDataStrucError("ATA return descriptor not supported by controller firmware")
        #
        if len(cmd.datain) > 0:
            dxfer_dir = SCSI_DXFER.DXFER_FROM_DEVICE.value
            data = cmd.datain
            dataLen = len(cmd.datain)
            data_buffer = get_data_buffer(dataLen, from_buffer=data)
        elif len(cmd.dataout) > 0:
            dxfer_dir = SCSI_DXFER.DXFER_TO_DEVICE.value
            data = cmd.dataout
            dataLen = len(cmd.dataout)
            data_buffer = get_data_buffer(dataLen, from_buffer=data)
        else:
            dxfer_dir = SCSI_DXFER.DXFER_NONE.value
            data = None
            dataLen = 0
            data_buffer = None
        return self.__pt_cmd(len(cmd.cdb), cmd.cdb, dataLen, data_buffer, dxfer_dir)


class SATADrive(PhysicalDriveBase):
    def __init__(self, bus_no, device_id, blocksize=0,  device=None):
        super(SATADrive, self).__init__(bus_no, device_id, device=device)
        self._blocksize = blocksize
        ##
        self.__identify = self.identify().datain
        # Auoto detect blocksize
        if self._blocksize == 0 and self.__identify[213] & 0xC0 == 0x40: # word 106 valid
            if self.__identify[213] & 0x10:
                self._blocksize = int(binascii.hexlify(translocate_bytearray(self.__identify[234:238], 2)),16) * 2
            else:
                self._blocksize = 512

    @property
    def protocal(self):
        return 'SATA'

    @property
    def identify_raw(self):
        return self.__identify

    @property
    def blocksize(self):
        """
        getter method of the blocksize property

        :return: blocksize in bytes
        """
        return self._blocksize

    def inquiry(self,
                evpd=0,
                page_code=0,
                alloclen=96):
        """
        Returns a Inquiry Instance

        :param evpd: a byte indicating if vital product data is supported
        :param page_code: a byte representing a page code for vpd
        :param alloclen: the size of the data_in buffer
        :return: a Inquiry instance
        """
        opcode = self.sbc_opcodes.INQUIRY
        cmd = Inquiry(opcode,
                      evpd=evpd,
                      page_code=page_code,
                      alloclen=alloclen)
        try:
            self.scsi_passthrough_cmd(cmd)
        except Exception as e:
            raise e
        cmd.unmarshall(evpd=evpd)
        return cmd

    def identify(self):
        cmd = Identify16(ck_cond=0)
        self.scsi_passthrough_cmd(cmd)
        cmd.unmarshall()
        return cmd

    def smart_read_data(self, smart_key=None):
        cmd = SmartReadData16(smart_key, ck_cond=0)
        self.scsi_passthrough_cmd(cmd)
        cmd.unmarshall()
        return cmd

    def smart_thread(self):
        cmd = SmartReadThresh16(ck_cond=0)
        self.scsi_passthrough_cmd(cmd)
        return cmd

    def smart_read_log(self, log_address, count):
        cmd = SmartReadLog16(count, log_address, ck_cond=0)
        self.scsi_passthrough_cmd(cmd)
        return cmd

    def read_log(self, log_address, count, page_number=0, feature=0):
        cmd = ReadLogExt(count, log_address, page_number, feature=feature, ck_cond=0)
        self.scsi_passthrough_cmd(cmd)
        return cmd


class SASDrive(PhysicalDriveBase):
    def __init__(self, bus_no, device_id, blocksize=0,  device=None):
        super(SASDrive, self).__init__(bus_no, device_id, device=device)
        self._blocksize = blocksize
        # auto detect blocksize
        if self._blocksize == 0:
            cap = self.readcapacity16().result
            self._blocksize = cap["block_length"]

    @property
    def protocal(self):
        return 'SAS'

    def inquiry(self,
                evpd=0,
                page_code=0,
                alloclen=96):
        """
        Returns a Inquiry Instance

        :param evpd: a byte indicating if vital product data is supported
        :param page_code: a byte representing a page code for vpd
        :param alloclen: the size of the data_in buffer
        :return: a Inquiry instance
        """
        opcode = self.sbc_opcodes.INQUIRY
        cmd = Inquiry(opcode,
                      evpd=evpd,
                      page_code=page_code,
                      alloclen=alloclen)
        try:
            self.scsi_passthrough_cmd(cmd)
        except Exception as e:
            raise e
        cmd.unmarshall(evpd=evpd)
        return cmd

    def readcapacity16(self, **kwargs):
        """
        Returns a ReadCapacity16 Instance

        :param kwargs: a dict with key/value pairs
                       alloc_len = 32, size of requested datain
        :return: a ReadCapacity16 instance
        """
        opcode = next(get_opcode(self.sbc_opcodes, "9E"))
        cmd = ReadCapacity16(opcode=opcode, **kwargs)
        self.scsi_passthrough_cmd(cmd)
        cmd.unmarshall()
        return cmd


class RaidController(object):
    prepare_megaraid_sas_ioctl_node()
    def __init__(self, host_no):
        self._host_no = host_no
        if os.path.exists("/dev/megaraid_sas_ioctl_node"):
            self._dev = DcmdDevice("/dev/megaraid_sas_ioctl_node")
        elif os.path.exists("/dev/megadev0"):
            self._dev = DcmdDevice("/dev/megadev0")
        else:
            raise DeviceNotFound("cannot open /dev/megaraid_sas_ioctl_node or /dev/megadev0")

    def get_pds_info(self):
        cmd = megasas_dcmd_cmd()
        pd_list = megasas_pd_list()
        cmd.build_command(self._host_no, 
                          MFI_DCMD_PD_GET_LIST,
                          pd_list,
                          sizeof(pd_list),
                          None,
                          0)
        self._dev.execute(cmd)
        for i in range(pd_list.count):
            # Peripheral device type = 0: Direct-access device (e.g. magnetic disk)
            if pd_list.addr[i].scsi_dev_type:
                continue
            yield linux_megaraid_device(self._host_no, pd_list.addr[i].device_id)

    def retrieve_pds(self, shared_device=False):
        dev = None
        if shared_device:
            dev = self._dev
        for pd_info in self.get_pds_info():
            try:
                pd = SATADrive(pd_info.bus_no, pd_info.device_id, device=dev)
            except:
                # traceback.print_exc()
                pd = SASDrive(pd_info.bus_no, pd_info.device_id, device=dev)
            yield pd


def get_raid_controllers():
    # getting bus numbers with megasas devices
    # we are using sysfs to get list of all scsi hosts
    host_ids = get_host_ids()
    if host_ids:
        for host_no in host_ids:
            sysfsdir = pathlib.Path(f"/sys/class/scsi_host/host{host_no}/proc_name")
            if sysfsdir.exists():
                with open(sysfsdir, "r") as f:
                    line = f.readline()
                    if line.startswith("megaraid_sas"):
                        log.debug("find megaraid controller %s", host_no)
                        yield RaidController(host_no)
    else:
        for i in range(16):
            temp = RaidController(i)
            try:
                # to judge if a Broadcom Controller
                temp.get_pds()
            except:
                continue
            else:
                log.debug("find megaraid controller %s", i)
                yield temp
