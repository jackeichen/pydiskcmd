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


License
=======
Python-scsi is distributed under LGPLv2.1
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

You can uninstall it by run:

    $ pip uninstall pydiskcmd


Usage
=====
Two executable program should be added to environment variables after installation.

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


Advanced Usage
==============
You can find some examples about how to use this tool in dir examples.
And some scsi tools in dir tools, which are from python-scsi.
