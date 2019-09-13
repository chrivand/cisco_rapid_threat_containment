#!/usr/lib/pybhon3

import psutil
import os

for pid in psutil.pids():
    p = psutil.Process(pid)
    if (p.name() == "rtcMain.py"):
        print("Found RTC Process with pid {}".format(str(pid)))
        print(p.cmdline())
    
