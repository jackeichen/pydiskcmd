# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later

import os
import platform
import logging
import logging.handlers
##
os_type = platform.system()
#
lin_log_path = "/var/log/pydiskcmd/"
win_log_path = "C:\\Windows\\Temp\\pydiskcmd\\"


if os_type == "Linux":
    import syslog
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

        def debug(self, *messages):
            for message in messages:
                message = "Debug: " + message
                syslog.syslog(syslog.LOG_DEBUG, message)

        def info(self, *messages):
            for message in messages:
                message = "Info: " + message
                syslog.syslog(syslog.LOG_INFO, message)

        def warning(self, *messages):
            for message in messages:
                message = "Warning: " + message
                syslog.syslog(syslog.LOG_WARNING, message)

        def error(self, *messages):
            for message in messages:
                message = "Error: " + message
                syslog.syslog(syslog.LOG_ERR, message)

        def critical(self, *messages):
            for message in messages:
                message = "Critical: " + message
                syslog.syslog(syslog.LOG_CRIT, message)
else:
    class SysLog(object):
        def __init__(self, ident):
            pass

        def debug(self, *messages):
            pass

        def info(self, *messages):
            pass

        def warning(self, *messages):
            pass

        def error(self, *messages):
            pass

        def critical(self, *messages):
            pass


class RunLog(object):
    if os_type == "Linux":
        LogDir = lin_log_path
    elif os_type == "Windows":
        LogDir = win_log_path
    else:
        LogDir = ""
    ## check log dir, create if not exist
    if LogDir and (not os.path.exists(LogDir)):
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

    def debug(self, *messages):
        for message in messages:
            self._logger.debug(message)

    def info(self, *messages):
        for message in messages:
            self._logger.info(message)

    def warning(self, *messages):
        for message in messages:
            self._logger.warning(message)

    def error(self, *messages):
        for message in messages:
            self._logger.error(message)

    def critical(self, *messages):
        for message in messages:
            self._logger.critical(message)

logger_pydiskhealthd = RunLog("pydiskhealthd")
syslog_pydiskhealthd = SysLog("pydiskhealthd")
