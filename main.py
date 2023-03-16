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
    # 以下为测试代码
    # outControl = output.output()
    # # time.sleep(30)
    # a = mapParse.mapParse()
    # b = secParse.secParse(a)
    # car0 = car.car(0)
    # car1 = car.car(1)
    # car2 = car.car(2)
    # car3 = car.car(3)
    # sys.stdout.write("OK\n")
    # #第一帧
    # while True:
    #     b.getState()
    #
    #     car0.getState(b.carState[0])  # 可能是第一行把(maybe
    #     car1.getState(b.carState[1])
    #     car2.getState(b.carState[2])
    #     car3.getState(b.carState[3])
    #
    #     # 做决策
    #     # 比如0车去1,1买2  3车去3,5卖6
    #     outControl.putTime(b.time)
    #
    #     speed, wspeed, lasttime = car0.destination(1, 1)
    #     outControl.putForward(0, speed)
    #     outControl.putRotate(0, wspeed)
    #     outControl.putBuy(0)
    #
    #     speed, wspeed, lasttime = car3.destination(3, 5)
    #     outControl.putForward(3, speed)
    #     outControl.putRotate(3, wspeed)
    #     outControl.putSell(3)
    #
    #     outControl.send()