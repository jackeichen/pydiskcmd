# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import logging

def Log(logger_name):
    logger = logging.getLogger(logger_name)
    formatter = logging.Formatter('[%(created)f] %(name)s - %(module)s.%(funcName)s: %(message)s')
    logger.setLevel(logging.INFO)
    ## set console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    #
    logger.addHandler(console_handler)
    return logger

def set_debug_mode(logger):
    logger.setLevel(logging.DEBUG)
