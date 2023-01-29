# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import time
import datetime
from pydiskcmd.pydiskhealthd.default_config import DiskWarningTemp,DiskCriticalTemp

plt_marker = (".", "^", "v", "x", "D", "*", "P")
plt_color =  ("g", "m", "c", "b", "k", "y", "r")
plt_line = ("solid", "dashed", "dashdot", "dotted")
## 
default_used_type = [(None, "r", "dashed"), (None, "y", "dashed")]


def get_style():
    for l in plt_line:
        for m in plt_marker:
            for c in plt_color:
                yield l,c,m

def PlotTemperature(temperature_info, file_name):
    import matplotlib.pyplot as plt
    ## first handle data
    #  find the earliest time
    early_time = time.time()
    latest_time = 0
    for dev_id,dev_info in temperature_info.items():
        ## 
        for t,temperature in dev_info:
            early_time = min(early_time, t)
            latest_time = max(latest_time, t)
    #
    start_t = datetime.datetime.fromtimestamp(early_time).strftime("%Y-%m-%d %H:%M:%S.%f")
    #
    plt.clf()#clear
    #
    style = get_style()
    ##
    for dev_id,dev_info in temperature_info.items():
        try:
            line,color,marker = next(style)
        except StopIteration:
            break
        x_values = []
        y_values = []
        for t,temperature in dev_info:
            x_values.append(int(t-early_time))
            y_values.append(temperature)
        plt.plot(x_values, y_values, linestyle=line, color=color, marker=marker, label=dev_id) # average 
    #
    plt.plot([0, int(latest_time-early_time)], [DiskWarningTemp,DiskWarningTemp], linestyle='dashed', color='y', label='Warning')   # Warning
    plt.plot([0, int(latest_time-early_time)], [DiskCriticalTemp,DiskCriticalTemp], linestyle='dashed', color='r', label='Critical')# Critical
    #
    plt.text(0, 0, start_t, ha='left', color='gray') 
    plt.title('Disk Temperature History')
    plt.xlabel("Time (seconds)")
    plt.ylabel("Temperature (C)")
    plt.grid(True)
    plt.legend()
    ##
    plt.savefig(file_name)
