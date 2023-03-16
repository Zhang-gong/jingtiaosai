#!/bin/bash
import sys
import mapParse
import time
import secParse
import numpy as np
import car
import output
from Scheduler import Scheduler

import win32api#win平台get pid,linux请换平台
"""
#以下为linux平台的getpid方法
import os

pid = os.getpid()
print("当前进程的PID是：", pid)
"""

if __name__ == '__main__':

    # 初始化


    pid = win32api.GetCurrentProcessId()
    with open('1.txt', 'w') as f:
        # 获取当前进程的PID
        # 将PID写入文件中
        f.write(str(pid))
        f.close()
    time.sleep(24) #用于查看pid附加进程
    scheduler = Scheduler()
    scheduler.get_map_info()

    sys.stdout.write("OK\n")
    # 第一帧
    while True:

        scheduler.update()
