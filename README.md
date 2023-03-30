<!--
SPDX-FileCopyrightText: 2022 The python-scsi Authors

SPDX-License-Identifier: LGPL-2.1-or-later
-->

pydiskcmd
=========
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
codes from github.


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

| OS                    | arc | SCSI | ATA | NVME |
|-----------------------|-----|------|-----|------|
| CentOS/RHEL 7.6       | x64 | Y    | Y   | Y    |
| CentOS/RHEL 8.4       | x64 | Y    | Y   | Y    |
| RHEL 9.1              | x64 | Y    | Y   | Y    |
| Windows 10 Pro        | x64 | Y    | Y   | Y    |
| Windows Server 2019   | x64 | Y    | Y   | T    |
| Windows Server 2022   | x64 | Y    | Y   | T    |

Y: support, N: Non-support, D: Developing, T: Under Testing

Note:

    * Only some of the commands are tested, Do Not guarantee all the other commands work;
    * This tool should work in Linux&Windows, but may be incompatible in OS other than this Support List;
    * Support Direct-Connection/HBA Mode/JBOD Mode, RAID Mode is not support.


Building and installing
=======================

Python3 Module Requirements:

    * setuptools_scm
    * pyscsi(Need download the latest python-scsi from github)

Extra Python3 Module Requirements by Linux:

    * cython-sgio(Need by pyscsi, download latest version from github)
    * pcicrawler

Sofware Requirements:

    * python3
    * python3-devel(only for linux)

To build and install from the repository:

    $ pip install .

After your installation, you can use command to enable or update Linux Bash 
Completion for command pynvme&pysata&pyscsi(Only for Linux):

    $ pydiskutils --enable=cmd_completion

You can uninstall it by run:

    $ pip uninstall pydiskcmd


Usage
=====
Five executable programs should be added to environment variables after installation.

pydiskutils
-----------
It is a program that show and manage pydiskcmd tool. Use bellow command to get help:

    $ pydiskutils --help

pynvme
------
It is a program similar to nvme-cli, with some limitted commands inside. Use bellow
command to get help:

    $ pynvme help

pysata
------
It is a sata command tool, to send ATA command to SATA Disk, with some limitted 
commands inside. Use bellow command to get help:

    $ pysata help

pyscsi
------
It is a scsi command tool, to send scsi command to SAS Disk, with some limitted 
commands inside. Use bellow command to get help:

    $ pyscsi help

pydiskhealthd
-------------
This is a Disk Health Monitoring and Reporting tool only for Linux. See below pydiskhealthd 
for more detail. Use bellow command to get help:

    $ pydiskhealthd -h


pydiskhealthd
=============
pydiskhealthd is a Disk Health Monitoring and Reporting tool. It check NVMe PCie Registers 
and smart for nvme disk, smart attributes for sata disk, in a specific time interval(default 1h). 
The pydiskhealthd usually runs in only-one-per-environment mode(default mode). 

Logs maybe Generated when below values changed/set/fall below threshold. These logs may record to 
either syslog(Linux in/var/log/message, Windows Not Implement) or pydiskhealthd running log(Linux 
in /var/log/pydiskcmd/pydiskhealthd.log or windows in C:\Windows\Temp\pydiskcmd\pydiskhealthd.log), 
or both of them.

For NVMe Disk:
  
  * PCIe Link Status(Only in Linux);
  * PCIe AER Registers(Only in Linux);
  * smart values;
  * Persistent Event Logs;
  * AER Event Check(Only in Linux);

The tool provide a real-time NVMe Asynchronous Event Request check by reading Linux trace file(Need Enable 
Linux Trace function). You can set the event you want to trigger it by sending nvme set-feature command. 
Examples(set temperature warning):

    $ pynvme get-feature /dev/nvme0 -f 0x0B 

and the value is 0x100 now, set the Critical Warning temperature check:

    $ pynvme set-feature /dev/nvme0 -f 0x0B -v 0x102

For SATA Disk:

  * Smart Pre-fail/Old_age attributes; 

The user(need root) can enable systemd service(pydiskhealthd.service), which make pydiskhealthd running as a 
backend service and start-up service. Enable and start it by: 

    $ pydiskutils --enable=auto_startup 

After that, the linux user can manage the pydiskhealthd with task name "pydiskhealthd".

Linux:

    $ systemctl status pydiskhealthd.service

Or Windows:

`> schtasks /Query /TN pydiskhealthd`



Advanced Usage
==============
You can find some examples about how to use this tool in the dir of pydiskcmd/examples/.

NVMe Command 
------------
Example to build and run your own NVMe command in Linux.

```
### nvme format command
## <Command> is the wrapper of raw command data structure, you can find it in pydiskcmd/pynvme/nvme_command,
#  <build_command> is the methmod to build cdw data structure
##
from pydiskcmd.pynvme.nvme_command import LinCommand,build_int_by_bitmap
## for running your own command in device, and get the result.
from pydiskcmd.utils import init_device

CmdOPCode = 0x80 # nvme format command OP code, see nvme spec
IOCTL_REQ = LinCommand.linux_req.get("NVME_IOCTL_ADMIN_CMD") # NVME_IOCTL_ADMIN_CMD Code type

class Format(LinCommand): 
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
        super(Format, self).__init__(IOCTL_REQ)
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

SATA Command
------------
Example to build and run your own SATA command in Linux Or Windows.

```
### Send an Identify command to SATA Disk
## pydiskcmd send SATA command by scsi passthrough12 or passthrough16 command
## This will import a suitable SCSIDevice depends on your OS,
#  The SCSIDevice help to send the command to device and get the result from the device
from pydiskcmd.utils import init_device
## ATACommand16 is the wrapper of ATA command, it help to build your own command
#  You can read ACS-3 about the ATA command set, and
#  read SAT-5 to make out how to translate from ATA command to SCSI passthrough command
from pydiskcmd.pysata.ata_command import ATACommand16


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

identify_cmd = Identify16()
with init_device("/dev/sdb", open_t='scsi') as d:
    d.execute(identify_cmd, en_raw_sense=True)
## Get the Result
# Handle the Command execute sense data
#  SAT-5 to make out ata_return_descriptor
ata_return_descriptor = cmd.ata_status_return_descriptor
print ("Command return Status:", ata_return_descriptor.get("status"))
# Get the datain, that read from device 
print ("Identify data read from device is:")
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


Support
=======
If any support or ideas, open an issue, or contact author by email: Eric-1128@outlook.com
