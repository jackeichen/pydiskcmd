# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
#
######################################
# author: pydiskcmd Authors
# date: 2025/07/08
#
# code is from arch\alpha\include\uapi\asm\ioctl.h
######################################
from ctypes import sizeof

###
### IOC setting ###
_IOC_NRBITS =	8
_IOC_TYPEBITS =	8

_IOC_SIZEBITS =	13
_IOC_DIRBITS =	3

_IOC_NRMASK =   (1 << _IOC_NRBITS) - 1
_IOC_TYPEMASK = (1 << _IOC_TYPEBITS) - 1
_IOC_SIZEMASK = (1 << _IOC_SIZEBITS) - 1
_IOC_DIRMASK =  (1 << _IOC_DIRBITS) - 1

_IOC_NRSHIFT =	 0
_IOC_TYPESHIFT = _IOC_NRSHIFT + _IOC_NRBITS
_IOC_SIZESHIFT = _IOC_TYPESHIFT + _IOC_TYPEBITS
_IOC_DIRSHIFT =	 _IOC_SIZESHIFT + _IOC_SIZEBITS

# /*
#  * Direction bits _IOC_NONE could be 0, but OSF/1 gives it a bit.
#  * And this turns out useful to catch old ioctl numbers in header
#  * files for us.
#  */
_IOC_NONE = 1
_IOC_WRITE = 2
_IOC_READ = 4
###
_IOC = lambda dir, type, nr, size: (dir  << _IOC_DIRSHIFT) | \
           (type << _IOC_TYPESHIFT) | \
           (nr   << _IOC_NRSHIFT) | \
           (size << _IOC_SIZESHIFT)

_IO = lambda type, nr: _IOC(_IOC_NONE, ord(type), nr, 0)
_IOR = lambda type, nr, size: _IOC(_IOC_READ, ord(type), nr, sizeof(size))
_IOW = lambda type, nr, size: _IOC(_IOC_WRITE, ord(type), nr, sizeof(size))
_IOWR = lambda type, nr, size: _IOC(_IOC_READ|_IOC_WRITE, ord(type), nr, sizeof(size))
