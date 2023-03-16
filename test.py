import mapParse
import time
import secParse
import numpy as np
import car
import output
n=100
m=100
arr1 = (np.arange(n).reshape(n, 1) * 2) * 0.25 * np.ones((1, m))
arr2 = (np.arange(m).reshape(1, m) * 2) * 0.25 * np.ones((n, 1))
map=np.sqrt(arr1 ** 2 + arr2 ** 2)


desx=2
desy=4

n=3.14/50


car0 = car.car(0)
car0.speed_y=0
car0.toward=0+n*36+(0.75+0.5+0.25)*n
car0.x=3
car0.y=3


dx = int(abs(desx - car0.x) * 2)
dy = int(abs(desy - car0.y) * 2)


print(car0.destination(desx,desy,map[dx][dy]))

# outControl = output.output()
# a = mapParse.mapParse()
# b = secParse.secParse(a)
# car0=car.car(0)
# car1=car.car(1)
# car2=car.car(2)
# car3=car.car(3)
#
# #第一帧
# b.getState()
# car0.getState(b.carState[0])#可能是第一行把(maybe
# car1.getState(b.carState[1])
# car2.getState(b.carState[2])
# car3.getState(b.carState[3])
#
# #做决策
# #比如0车去1,1买2  3车去3,5卖6
# outControl.putTime(b.time)
#
# speed,wspeed,lasttime=car0.destination(1,1)
# outControl.putForward(0,speed)
# outControl.putRotate(0,wspeed)
# outControl.putBuy(0)
#
# speed,wspeed,lasttime=car3.destination(3,5)
# outControl.putForward(3,speed)
# outControl.putRotate(3,wspeed)
# outControl.putSell(3)
#
#
# outControl.send()
# #第一帧结束