# SPDX-FileCopyrightText: 2014 The python-scsi Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import os
import syslog
import logging
import logging.handlers


class SysLog(object):
    def __init__(self, ident):
        self.__ident = ident
        ##
        self.__log_opened = False
        self._init_logger()

    def __del__(self):
        self._close_logger()

    def _init_logger(self):
        if not self.__log_opened:
            syslog.openlog(self.__ident)
            self.__log_opened = True

    def _close_logger(self):
        if self.__log_opened:
            syslog.closelog()
            self.__log_opened = False

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
    LogDir = "/var/log/pydiskcmd/"
    ## check log dir, create if not exist
    if not os.path.exists(LogDir):
        os.makedirs(LogDir)
    ## init
    def __init__(self, logger_name="pydiskcmd"):
        self._logger = logging.getLogger(logger_name)
        self._formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self._logger.setLevel(logging.DEBUG)
        ## self._logger.setLevel(logging.INFO)
        log_file = os.path.join(RunLog.LogDir, "%s.log" % logger_name)
        ## set FileHandler
        self._file_handler = logging.handlers.TimedRotatingFileHandler(filename=log_file,
                                                                       when='D',
                                                                       interval=7,
                                                                       backupCount=8,
                                                                       delay=True,
                                                                       encoding='utf-8',
                                                                       )
        self._file_handler.setFormatter(self._formatter)
        self._logger.addHandler(self._file_handler)

    def debug(self, message):
        return self._logger.debug(message)

    def info(self, message):
        return self._logger.info(message)

    def warning(self, message):
        return self._logger.warning(message)

    def error(self, message):
        return self._logger.error(message)

    def critical(self, message):
        return self._logger.critical(message)

logger_pydiskhealthd = RunLog("pydiskhealthd")
syslog_pydiskhealthd = SysLog("pydiskhealthd")
