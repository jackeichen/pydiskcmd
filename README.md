<!--
SPDX-FileCopyrightText: 2014 The python-scsi Authors

SPDX-License-Identifier: LGPL-2.1-or-later
-->

pydiskcmd
=========
pydiskcmd is a disk command interface for python3. This is a linux tool
to send command to SATA/SAS/NVMe disk. I develop this tool to familiarize
the command set specs(sata,nvme).

The project is under development now. 


Many thanks from
================
Really appreciate the project python-scsi in github.

* Python-scsi: https://github.com/python-scsi/python-scsi

pcicrawler is a CLI tool to display/filter/export information about PCI or 
PCI Express devices and their topology.

* pcicrawler: https://github.com/facebook/pcicrawler


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


Building and installing
=======================

To build and install from the repository:

    $ pip install .[iscsi,sgio]

You can avoid installing the optional dependencies by omitting the "extras":

    $ pip install .

After your installation, you can use command to enable Linux Bash Completion for 
command pynvme&pysata:

    $ pydiskcmd --en_completion

You can uninstall it by run:

    $ pip uninstall pydiskcmd


Usage
=====
There executable programs should be added to environment variables after installation.

pydiskcmd
---------
It is a program that show and manage pydiskcmd tool. Use bellow command to get help:

    $ pydiskcmd help

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

pydiskhealthd
-------------
This is a Disk Health Monitoring and Reporting tool. See below pydiskhealthd for more detail.
Use bellow command to get help:

    $ pydiskhealthd -h


pydiskhealthd
=============
pydiskhealthd is a Disk Health Monitoring and Reporting tool. It check NVMe PCie Registers 
and smart for nvme disk, smart attributes for sata disk, in a specific time interval(default 1h). 
The pydiskhealthd usually runs in only-one-per-environment mode(default mode). 

Logs maybe Generated when below values changed/set/fall below threshold. These logs may record to 
either syslog or pydiskhealthd running log(in /var/log/pydiskcmd/pydiskhealthd.log), or both of them.

For NVMe Disk:
  
  * PCIe Link Status;
  * PCIe AER Registers;
  * smart values;

For SATA Disk:

  * Smart Pre-fail/Old_age attributes; 

The user(need root) can enable systemd service(pydiskhealthd.service), which make pydiskhealthd running as a 
backend service and start-up service. Enable and start it by: 

    $ pydiskcmd --en_diskhealth_daemon

After that, the user can manage the pydiskhealthd with command "systemctl". Auto start service is recommended:

    $ systemctl enable pydiskhealthd.service


Advanced Usage
==============
You can find some examples about how to use this tool in the dir of pydiskcmd/examples/.
And some scsi tools in the dir of pydiskcmd/tools/, which are from python-scsi.


Email
=====
If any support or ideas, contact me by email: Eric-1128@outlook.com
