<!--
SPDX-FileCopyrightText: 2022 The pydiskcmd Authors

SPDX-License-Identifier: LGPL-2.1-or-later
-->

Important
=========
pydiskcmd remove pydiskhealthd in version 0.3.0, it may become a separate project 
in the future. For the reason: Need more effort to maintain a mixed-function project, 
and pydiskhealthd need more dependencies.

If you still want to use it, keep your tool version less than 0.3.0.


pydiskcmd
=========

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/jackeichen/pydiskcmd)

pydiskcmd is a disk command tool for python3. It can send command to SATA/SAS/NVMe 
disk, as also as monitor the disk health.

In Linux, there is some tools to handle disk, like hdparm,smartctl,nvme-cli 
and etc. But I still hope to develop a tool to cover all the sata,sas,nvme disks.
It should be easily installed and should be able to send raw commands to target 
disks, provide a high-level API to build raw command with different protocal. 
Besides, it could monitor the health of the disks, especially take full advantage 
of NVMe(which offer a better monitoring mechanism). 

While in Windows, rarely find out an open source user level disk tool. I hope it 
is convenient to handle a disk in windows as if it is in Linux.

This project is more of a code collection, it was born and grow in the open source 
projects from github.

Why pydiskcmd
-------------
The pydiskcmd is easily installed. In most case, all you need is the python environment. 
Benefit from python (a cross-platform and high-level programming language) and OS level 
ioctl support, installing pydiskcmd Does Not need to configure the compiling environment
(like C/C++ code). The long-term work in the development is to reduce the sofware dependency, 
to make installation as simple as possible.

The pydiskcmdlib provides a flexible and friendly middle-level API, as well as some low-level 
components to use. With the help of it, user could build their own raw command, send it to 
device and get the result. To archive this goal, more detailed documentation may be considered 
in the future. Whether you hope to test your storage device in protocal test or want to develop 
a disk utility tool, pydiskcmdlib will be a good choice.

pydiskcmdcli(pynvme/pysata/pyscsi included) is different with hdparm,sdparm and etc. The above 
tools is more like a command utility for a certain purpose, the pydiskcmdcli provides raw-command 
from spec without union. For example, the user cannot directly set the write-caching by the client 
tool, the equivalent command will be set-feature or mode-select.

Disadvantages
-------------
Compared to the compiled language, python code may take up more time and memory to run, and need 
more size in packaged program(i.e. program packaged by pyinstaller). Most of the time is consumed 
by loading the code in first use.

| Test item             | Used Time(milliseconds) | Description                   |
|-----------------------|-------------------------| ----------------------------- |
| Load pydiskcmdlib     | 35.99839                | Only load module pydiskcmdlib |
| Load pydiskcmdcli     | 36.59582                | Only load module pydiskcmdcli |
| NVMe.id_ctrl()        | 0.138521                | run NVMe.id_ctrl() after pydiskcmdlib loaded |
| pynvme id-ctrl        | 69                      | run pynvme id-ctl <device>, include print data |

The test uses CentOS Stream 9 with python 3.9, and get the average value in 5 times.


License
=======
pydiskcmd is distributed under LGPLv2.1.
Please see the LICENSE file for the full license text.


Getting the sources
===================
The module(source) is hosted at https://github.com/jackeichen/pydiskcmd

You can use git to checkout the latest version of the source code using:

    $ git clone git@github.com:jackeichen/pydiskcmd.git

It is also available as a downloadable zip archive from:

    https://github.com/jackeichen/pydiskcmd/archive/master.zip


Support List
============

OS Support
---------

| OS                    | arc | SCSI | ATA | NVME |
|-----------------------|-----|------|-----|------|
| CentOS/RHEL 7.6       | x64 | Y    | Y   | Y    |
| CentOS/RHEL 8.4       | x64 | Y    | Y   | Y    |
| RHEL 9.1              | x64 | Y    | Y   | Y    |
| SUSE 15 SP5           | x64 | Y    | Y   | Y    |
| Ubuntu 22.04          | x64 | Y    | Y   | Y    |
| Debian 10             | x64 | Y    | Y   | Y    |
| Fedora Workstation 40 | x64 | Y    | Y   | Y    |
| Windows 10 Pro        | x64 | Y    | Y   | Y    |
| Windows 11            | x64 | Y    | Y   | Y    |
| Windows Server 2019   | x64 | Y    | Y   | Y    |
| Windows Server 2022   | x64 | Y    | Y   | Y    |

Y: support, N: Non-support, D: Developing, T: Under Testing

Note:

    * Only some of the commands are tested, Do Not guarantee all the other commands work;
    * This tool should work in Linux&Windows, but may be incompatible in OS other than this Support List;
    * Windows only support some of the get-feature/get-log/idenfity commands;
    * Support Direct-Connection/HBA Mode/JBOD Mode, RAID Mode is not supported.

RAID/HBA Support
----------------
Only HBA Card and RAID JBOD mode under test. Limited support RAID Mode.

The configuration should matrixed support with smartie. See raid_support_matrix_with_smartie.txt for 
details.

| RAID/HBA Adapter   | OS under test| SCSI Supported | ATA Supported |
|--------------------|--------------|----------------|---------------|
| Broadcom RAID 9440 | CentOS 8.4   | Yes            | Yes           |
| Broadcom RAID 9560 | CentOS 8.4   | Yes            | Yes           |
| Broadcom HBA  9500 | CentOS 8.4   | Yes            | Yes           |
| ThinkSystem   930  | CentOS 8.4   | Yes            | Yes           |
| ThinkSystem   940  | CentOS 8.4   | Yes            | Yes           |
| ThinkSystem   4350 | CentOS 8.4   | Yes            | Yes           |
| ThinkSystem   5350 | CentOS 8.4   | Yes            | Yes           |

Broadcom RAID
-------------
The bellow command is avaliable in ThinkSystem 940, as well as Broadcom RAID 9440 and 9560.

  * SCSI inquiry
  * SATA identify&smart_read_data

More commands is on the way.

Note:

    * Only some log page and identify is tested, which command support denpends on the card driver;
    * May need update driver if error occurs;

Feature support
---------------

| Feature            | OS under test       | NVMe Supported | ATA Supported |
|--------------------|---------------------|----------------|---------------|
| [Intel VROC]       | Windows Server 2019 | T              | N             |
| [Intel RST]        | Windows 10          | D              | T             |

Y: support, N: Non-support, D: Developing, T: Under Testing


Building and installing
=======================

Sofware Requirements:

    * python3(Required)

Python3 Module Requirements:

    * cython-sgio(Optional, can skip, but need latest version from github if used in linux)

Online build and install from the repository:

    $ git clone git@github.com:jackeichen/pydiskcmd.git
    $ pip install .

After your installation, you can use command to enable or update Linux Bash 
Completion for command pynvme&pysata&pyscsi(Only for Linux):

    $ pynvme cli-autocmd

You can uninstall it by run:

    $ pip uninstall pydiskcmd

No pip
------
If you are in the environment that pip Not Installed, you can install by run:

    $ cd pydiskcmd
    $ python3 setup.py install

And you could manually create smart drivedb in Linux by:

    $ mkdir /etc/pydiskcmd
    $ cp src/pydiskcmdcli/drivedb/smart_drivedb.json /etc/pydiskcmd/


Documents
=========

No time to fix up the docs right now, you may ask DeepWiki to find something useful.


Usage
=====
Three executable programs should be added to environment variables after installation.

pynvme
------
It is a program similar to nvme-cli, with some limitted commands inside. Use bellow
command to get help:

    $ pynvme help

```
pynvme-0.3.6
usage: pynvme <command> [<device>] [<args>]

The '<device>' may be either an NVMe character device (ex: /dev/nvme0) or an
nvme block device (ex: /dev/nvme0n1) in Linux, while PhysicalDrive<X> in Windows.

The following are all implemented sub-commands:
  list                  List all NVMe devices and namespaces on machine
  list-subsys           List nvme subsystems
  list-ns               Send NVMe Identify List, display structure
  list-ctrl             Send NVMe Identify Controller List, display structure
  id-ctrl               Send NVMe Identify Controller
  id-ns                 Send NVMe Identify Namespace, display structure
  id-uuid               Send NVMe Identify UUID List, display structure
  create-ns             Creates a namespace with the provided parameters
  delete-ns             Deletes a namespace from the controller
  attach-ns             Attaches a namespace to requested controller(s)
  detach-ns             Detaches a namespace from requested controller(s)
  get-log               Generic NVMe get log, returns log in raw format
  smart-log             Retrieve SMART Log, show it
  error-log             Retrieve Error Log, show it
  commands-se-log       Retrieve Commands Supported and Effects Log, and show it
  fw-log                Retrieve FW Log, show it
  sanitize-log          Retrieve Sanitize Log, show it
  self-test-log         Retrieve the SELF-TEST Log, show it
  telemetry-log         Retrieve the Telemetry Log, show it
  persistent-event-log  Get persistent event log from device
  reset                 Resets the controller
  subsystem-reset       Resets the subsystem
  fw-download           Download new firmware
  fw-commit             Verify and commit firmware to a specific slot
  get-feature           Get feature and show the resulting value
  set-feature           Set a feature and show the resulting value
  format                Format namespace with new block format
  sanitize              Submit a sanitize command
  device-self-test      Perform the necessary tests to observe the performance
  pcie                  Get device PCIe status, show it(Obseleted, see plugin pci)
  show-regs             Shows the controller registers or properties. Requires character device
  flush                 Submit a flush command, return results
  read                  Submit a read command, return results
  verify                Submit a verify command, return results
  write                 Submit a write command, return results
  write-zeroes          Submit a write zeroes command, return results
  write-uncor           Submit a write uncorrectable command, return results
  compare               Submit a Compare command, return results
  dsm                   Submit a Data Set Management command, return results
  get-lba-status        Submit a Get LBA Status command, return results
  version               Shows the program version
  help                  Display this help

See 'pynvme help <command>' or 'pynvme <command> --help' for more information on a sub-command

The following are all installed plugin extensions:
  ocp                   OCP cloud SSD extensions
  vroc                  Windows NVMe VROC support
  pci                   Linux PCIe SSD extensions
  mi                    NVMe-MI extensions

The following are pynvme cli management interface:
  cli-info              Shows pynvme information
  cli-autocmd           Enable or Update the command completion

See 'pynvme <plugin> help' for more information on a plugin
```

pysata
------
It is a sata command tool, to send ATA command to SATA Disk, with some limitted 
commands inside. Use bellow command to get help:

    $ pysata help

```
pysata-0.3.6
usage: pysata <command> [<device>] [<args>]

The '<device>' is usually a character device (ex: /dev/sdb or physicaldrive1).

The following are all implemented sub-commands:
  list                        List all SATA devices on machine
  check-PowerMode             Check Disk Power Mode
  accessible-MaxAddress       Send Accessible Max Address command
  identify                    Get identify information
  self-test                   Start a disk self test
  set-feature                 Send set feature to device
  trusted-receive             Send trusted receive to device
  smart                       Get smart information
  smart-return-status         Get the reliability status of the device
  read-log                    Get the GPL Log and show it
  write-log                   Send write log command
  smart-read-log              Get the smart Log and show it
  sanitize                    Send sanitize command
  standby                     Send standby command
  read                        Send a read command to disk
  read-sectors                Send a read sector(s) command to disk
  read-verify-sector          Send read verify sector(s) command
  write                       Send a write command to disk
  write-uncorrectable         Send a write uncorrectable command to disk
  flush                       Send a flush command to disk
  trim                        Send a trim command to disk
  download-fw                 Download firmware to target disk
  version                     Shows the program version
  help                        Display this help

The following are all installed plugin extensions:
  megaraid                    MegaRAID Linux extensions
  rst                         Intel RAID RST Windows extensions

The following are pysata cli management interface:
  cli-info                    Shows pysata information
  cli-autocmd                 Enable or Update the command completion

See 'pysata help <command>' or 'pysata <command> --help' for more information on a sub-command
```

pyscsi
------
It is a scsi command tool, to send scsi command to SAS Disk, with some limitted 
commands inside. Use bellow command to get help:

    $ pyscsi help

```
pyscsi 0.3.6
usage: pyscsi <sub-command> [<device>] [<args>]

The '<device>' is usually a character device (ex: /dev/sdb or physicaldrive1).

The following are all implemented sub-commands:
  list                        List all SCSI devices on machine
  inq                         Send scsi inquiry command
  getlbastatus                Get LBA Status from target SCSI device
  readcap                     Read capacity from target SCSI device
  luns                        Send Report Luns commandc to target SCSI device
  mode-sense                  Send Mode Sense command to target SCSI device
  log-sense                   Send Log Sense command to target SCSI device
  cdb-passthru                Submit an arbitrary SCSI command, return results
  se-protocol-in              Submit SECURITY PROTOCOL IN command, return results
  smart-simulate              Retrieve different logs, return simulate smart
  sync                        Synchronize cache to non-volatile cache, as known as flush
  read                        Send a read command to disk
  write                       Send a write command to disk
  version                     Shows the program version
  help                        Display this help

The following are all installed plugin extensions:
  parse-cmd                   Parse the CDB and sense code
  lenovo                      Lenovo disk plugin(for Private Release)
  csmi                        Common Storage Management Interface (CSMI) plugin
  megaraid                    MegaRAID extensions

The following are pyscsi cli management interface:
  cli-info                   Shows pyscsi information
  cli-autocmd                Enable or Update the command completion

See 'pyscsi help <command>' or 'pyscsi <command> --help' for more information on a sub-command
```


Advanced Usage
==============
You can find some examples about how to use this tool in the dir of pydiskcmd/examples/.

Build Your Own Command 
----------------------
Example to build and run your own NVMe command in Linux.

```
### nvme format command
## <NVMeCommand> is the wrapper of raw command data structure, you can find it in pydiskcmdlib/pynvme/nvme_command,
#  <build_command> is the methmod to build cdw data structure
##
from pydiskcmdlib.pynvme.nvme_command import NVMeCommand,build_int_by_bitmap
from pydiskcmdlib.pynvme.linux_nvme_command import IOCTLRequest
## for running your own command in device, and get the result.
from pydiskcmdlib.utils import init_device

CmdOPCode = 0x80 # nvme format command OP code, see nvme spec

class Format(NVMeCommand):
    _req_id = IOCTLRequest.NVME_IOCTL_ADMIN_CMD.value  # define yourself request ID, admin or nvme command

    def __init__(self, 
                 lbaf,            # the lbaf to format, see nvme spec
                 mset=0,          # the mset to format, see nvme spec
                 pi=0,            # the pi to format, see nvme spec
                 pil=1,           # the pil to format, see nvme spec
                 ses=0,           # the ses to format, see nvme spec
                 nsid=0xFFFFFFFF, # the nsid to format, see nvme spec
                 timeout=600000): # timeout(millisecond) in IOCTL request
        ## build command cdw10
        #  this is a key-value dict input:
        #    key: the name of value
        #    value: (the bit-map of value, Byte offset in DWord, value to set)
        ##
        cdw10 = build_int_by_bitmap({"lbaf": (0x0F, 0, lbaf), # the location of lbaf in cdw10, see nvme spec
                                     "mset": (0x10, 0 ,mset), # the location of mset in cdw10, see nvme spec
                                     "pi": (0xE0, 0, pi),     # the location of pi in cdw10, see nvme spec
                                     "pil": (0x01, 1, pil),   # the location of pil in cdw10, see nvme spec
                                     "ses": (0x0E, 1, ses)})  # the location of ses in cdw10, see nvme spec
        ##
        super(Format, self).__init__()
        # build command
        self.build_command(opcode=CmdOPCode,
                           nsid=nsid,
                           cdw10=cdw10,
                           timeout_ms=timeout)

cmd = Format(0, nsid=1) ## format namespace 1 to lbaf 0
with init_device('/dev/nvme1', open_t='nvme') as d: ## open a nvme device: /dev/nvme1
    d.execute(cmd)
## Get the command result-> 
print (cmd.cq_cmd_spec) # Command Specific Status Values, see nvme spec
SC,SCT = cmd.check_return_status() # Get Command Status Code and Status Code Type
print ("Command Status Code=%d, Status Code Type=%d" % (SC,SCT))
```

Example to build and run your own SATA command in Linux Or Windows.

```
### Send an Identify command to SATA Disk
## pydiskcmdlib send SATA command by scsi passthrough12 or passthrough16 command
## This will import a suitable SCSIDevice depends on your OS,
#  The SCSIDevice help to send the command to device and get the result from the device
from pydiskcmdlib.utils import init_device
## ATACommand16 is the wrapper of ATA command, it help to build your own command
#  You can read ACS-3 about the ATA command set, and
#  read SAT-5 to make out how to translate from ATA command to SCSI passthrough command
from pydiskcmdlib.pysata.ata_command import ATACommand16


class Identify16(ATACommand16): 
    def __init__(self):
        ##
        # count is not used by idedntify in ATA command set,
        # so use it in ATAPassthrouh16, for setting transfer length
        ##
        ATACommand16.__init__(self,
                              0,         # fetures field
                              1,         # count field
                              0,         # lba field
                              0,         # device field
                              0xec,      # command field
                              0x04,      # protocal field
                              2,         # t_length field
                              1)         # t_dir field 

cmd = Identify16()
with init_device("/dev/sdb", open_t='scsi') as d:
    d.execute(cmd, en_raw_sense=True)
## Get the Result
# Handle the Command execute sense data
#  SAT-5 to make out ata_return_descriptor
ata_return_descriptor = cmd.ata_status_return_descriptor
print ("Command return Status:", ata_return_descriptor.get("status"))
# Get the datain, that read from device 
print ("Identify data read from device is:")
print (cmd.datain)
```

Example to build and run your own SCSI command in Linux Or Windows. It is a little different from
NVMe Or SATA, the methmod is from the project python-scsi.

```
from pyscsi.pyscsi.scsi_command import SCSICommand
from pyscsi.pyscsi.scsi_enum_command import mmc, sbc, smc, spc, ssc
from pydiskcmdlib.utils import init_device

class Read16(SCSICommand):
    ## You need define the _cdb_bits to build cdb

    _cdb_bits = {
        "opcode": [0xFF, 0],
        "rdprotect": [0xE0, 1],
        "dpo": [0x10, 1],
        "fua": [0x08, 1],
        "rarc": [0x04, 1],
        "lba": [0xFFFFFFFFFFFFFFFF, 2],
        "group": [0x1F, 14],
        "tl": [0xFFFFFFFF, 10],
    }

    def __init__(
        self, lba, tl, rdprotect=0, dpo=0, fua=0, rarc=0, group=0
    ):
        """
        initialize a new instance

        :param lba: Logical Block Address
        :param tl: transfer length
        :param rdprotect=0:
        :param dpo=0:
        :param fua=0:
        :param rarc=0:
        :param group=0:
        """
        ##
        # This command is sbc command->READ_16, usually get by inquiry command, and
        # and the device is 512 byte logical format.
        ##
        opcode = sbc.READ_16
        blocksize= 512
        ## Build command
        SCSICommand.__init__(self, opcode, 0, blocksize * tl)

        self.cdb = self.build_cdb(
            opcode=self.opcode.value,
            lba=lba,
            tl=tl,
            rdprotect=rdprotect,
            dpo=dpo,
            fua=fua,
            rarc=rarc,
            group=group,
        )
## send command: 4k read from LBA 0 to LBA 7
cmd = Read16(0, 8)
## Execute Command
with init_device("/dev/sdb", open_t='scsi') as d:
    d.execute(cmd)
## Get the result
print (cmd.datain)
```


Acknowledgements
================
Really appreciate the project python-scsi in github.

* Python-scsi: https://github.com/python-scsi/python-scsi

pcicrawler is a CLI tool to display/filter/export information about PCI or 
PCI Express devices and their topology.

* pcicrawler: https://github.com/facebook/pcicrawler

smartie is a pure-python library for getting basic disk information such as 
model, serial number, disk health, temperature, etc...

* smartie: https://github.com/TkTech/smartie

Communicate with NVMe SSD using Windows' inbox device driver

* nvmetool-win: https://github.com/ken-yossy/nvmetool-win

NVMe management command line interface.

* nvme-cli: https://github.com/linux-nvme/nvme-cli

pyPCIe provides a quick way to read/write registers in PCIe Base Address Register (BAR) regions.

* pyPCIe: https://github.com/heikoengel/pyPCIe

A python/construct wrapper for sgio to replace cython-sgio

* https://github.com/goodes/python-sgio

A tool to control and monitor storage systems using the Self-Monitoring, Analysis and Reporting 
Technology System (SMART) built into most modern ATA/SATA, SCSI/SAS and NVMe disks

* https://github.com/smartmontools/smartmontools


Reference Documents
===================
* https://community.intel.com/cipcp26785/attachments/cipcp26785/devcloud/9717/1/743971_Intel_VROC_IOCTLs_UG_Rev1p0.pdf


Support
=======
If any support or ideas, open an issue, or contact author by email: Eric-1128@outlook.com


[Intel VROC]: https://graidtech.com/vroc
[Intel RST]: https://www.intel.com/content/www/us/en/support/products/55005/technologies/intel-rapid-storage-technology-intel-rst.html
