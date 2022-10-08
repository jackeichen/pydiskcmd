# SPDX-FileCopyrightText: 2014 The python-scsi Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import syslog
import logging
import logging.handlers


class SysLog(object):
    log_opened = False
    def __init__(self):
        self.__ident = "pydiskhealthd"
        self._init_logger()

    def __del__(self):
        self._close_logger()

    def _init_logger(self):
        if not SysLog.log_opened:
            syslog.openlog(self.__ident)
            SysLog.log_opened = True

    def _close_logger(self):
        if SysLog.log_opened:
            syslog.closelog()
            SysLog.log_opened = False

    def debug(self, message):
        message = "Debug: " + message
        return syslog.syslog(syslog.LOG_DEBUG, message)

    def info(self, message):
        message = "Info: " + message
        return syslog.syslog(syslog.LOG_INFO, message)

    def warning(self, message):
        message = "Warning: " + message
        return syslog.syslog(syslog.LOG_WARNING, message)

    def error(self, message):
        message = "Error: " + message
        return syslog.syslog(syslog.LOG_ERR, message)

    def critical(self, message):
        message = "Critical: " + message
        return syslog.syslog(syslog.LOG_CRIT, message)


class RunLog(object):
    def __init__(self):
        self._logger = logging.getLogger('pydiskhealthd')
        self._formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self._logger.setLevel(logging.DEBUG)
        ## self._logger.setLevel(logging.INFO)
        self._file_handler = logging.handlers.TimedRotatingFileHandler(filename="pydiskhealthd.log",
                                                                       delay=True,
                                                                       encoding='utf-8'
                                                                       )
        self._file_handler.setFormatter(self._formatter)
        self._logger.addHandler(self._file_handler)

    def debug(self, message):
        return self._logger.debug(syslog.LOG_DEBUG, message)

    def info(self, message):
        return self._logger.info(syslog.LOG_INFO, message)

    def warning(self, message):
        return self._logger.warning(syslog.LOG_WARNING, message)

    def error(self, message):
        return self._logger.error(syslog.LOG_ERR, message)

    def critical(self, message):
        return self._logger.critical(syslog.LOG_CRIT, message)
