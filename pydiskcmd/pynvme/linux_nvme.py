from fcntl import ioctl
from pydiskcmd.pynvme.command_return import CommandDecoder 
##
##from pystorage.pynvme.command_structure import CmdStructure


NVME_IOCTL_ADMIN_CMD = 0xC0484E41
NVME_IOCTL_IO_CMD = 0xC0484E43


def submit(req, dev, cmd_structure):
    CmdResult = CommandDecoder()
    CmdResult.status = ioctl(dev.fileno(), req, cmd_structure)
    CmdResult.cmd_spec = cmd_structure.result
    if cmd_structure._data_buf is not None:
        CmdResult.data = bytes(cmd_structure._data_buf)
    if cmd_structure._metadata_buf is not None:
        CmdResult.meta_data = bytes(cmd_structure._metadata_buf)
    return CmdResult

def execute_admin_cmd(dev, cmd_structure):
    return submit(NVME_IOCTL_ADMIN_CMD, dev, cmd_structure)

def execute_io_cmd(dev, cmd_structure):
    return submit(NVME_IOCTL_IO_CMD, dev, cmd_structure)
