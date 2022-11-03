# SPDX-FileCopyrightText: 2014 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import os
import queue
import threading
from pydiskcmd.pynvme.linux_nvme_aer import NVMeAER,KernelNVMeAERTracePIPEFile


class AERTrace(object):
    '''
    We do not need store the aer trace, it usually be cleared every power cycle.
    '''
    def __init__(self):
        ##
        self.aer = NVMeAER()
        ##
        self.last_trace = []
        self.current_trace = []

    def set_log(self, aer_trace):
        if self.current_trace:
            self.last_trace = self.current_trace
            self.current_trace = aer_trace
        else:
            self.current_trace = aer_trace

    def get_log_once(self):
        aer = self.aer.check_trace_once()
        self.set_log(aer)

    def diff_trace(self):
        if self.current_trace:
            result = []
            for i in self.current_trace:
                if i not in self.last_trace:
                    result.append(i)
            return result


class AERTraceRL(NVMeAER):
    def __init__(self):
        super(AERTraceRL, self).__init__()
        ##
        self.__trace_log_pipe_file = KernelNVMeAERTracePIPEFile
        if not os.path.isfile(self.__trace_log_pipe_file):
            raise RuntimeError("No Trace PIPE file!")
        ##
        self.backend_t = None
        self.backend_q = queue.Queue()
        #
        self.start_service()

    def _check_service(self, pipe_file, q):
        with open(pipe_file, 'r') as f:
            while True:
                content = f.readline()
                description = self._decode_trace_by_line(content)
                if description:
                    q.put(description)

    def start_service(self):
        self.backend_t = threading.Thread(target=self._check_service, args=(self.__trace_log_pipe_file, self.backend_q))
        self.backend_t.daemon = True
        self.backend_t.start()

    def get_once(self, timeout):
        description = None
        try:
            description = self.backend_q.get(timeout=timeout)
        except queue.Empty:
            pass
        return description
