import numpy as np
import sys


class car:
    def __init__(self, car_id):
        self.inbench=0.0002
        self.rotateLimitAc=0.10#0.13#加减速临界角度
        #self.rotateLimitGo = 1.25# 启动临界角度1.25 在使用碰撞控制后不再被需要，，对于近距离的运送，大角度的转弯 可以优化一份针对性的算法，在没有针对性算法前补偿使用
        self.to0speed=0.75#一针到0的速度
        self.stopRotate=0.17#停止临界
        self.closeDesBench=5.0  #判断是否是近距离寻路
        #常量区
        self.carid = car_id
        self.benchid = -1
        self.goods = -1
        self.tk = 1
        self.ck = 1
        self.wspeed = 0
        self.need_toward = 0
        self.speed_x = 0
        self.speed_y = 0
        self.toward = 0
        self.x = 0
        self.y = 0
        self.maxSpeedRadius = 2.3
        self.distance2des=0
        self.fowardFlag=True       #标注，用于判断方向是否对齐
        self.is_busy = False
        self.des_x = 0
        self.des_y = 0
        self.is_carrying = False
        self.backwardFlag = False

    def getState(self, carState):
        self.benchid = int(carState[0])
        self.goods = int(carState[1])
        self.tk = float(carState[2])
        self.ck = float(carState[3])
        self.wspeed = float(carState[4])
        self.speed_x = float(carState[5])
        self.speed_y = float(carState[6])
        self.toward = float(carState[7])
        self.x = float(carState[8])
        self.y = float(carState[9])


    def destination(self, x, y, distance):
        """
        1.0 先转到直线(很小角度)再冲,反回需要打的速度
        :param type:
        :param x:
        :param y:
        :return:
        """
        self.des_x = x
        self.des_y = y
        self.distance2des=distance

        if self.distance2des < self.closeDesBench:   #判断条件为self.distance2des < self.closeDesBench，接上时修改
            speed, wspeed, lasttime=self.calculate_close_speed()
            return speed,wspeed,lasttime
        else:
            wspeed = self.rotate()
            speed = self.straight()
            lasttime = self.lastTime()
            return speed, wspeed, lasttime

    def rotate(self):
        #if (abs(self.speed_x)+abs(self.speed_y))>=0.1 and not self.fowardFlag:
        #    #没到位置，速度先为0先调整方向
        #    return 0

        dT=self.toward-self.angle()
        #0到pi 顺时针 pi到2pi，逆时针 -pi到0逆时针 -2pi到-pi顺时针
        if dT<0:
            dT=dT+np.pi+np.pi
        if dT>np.pi:
            dT=-(2*np.pi-dT)
        #角度修正
        #负的目标需要我逆时针转故返回正
       # print(dT)
       #  if abs(dT)<self.rotateLimitGo:
       #      self.fowardFlag=True
       #  elif abs(dT)>self.rotateLimitGo:
       #      self.fowardFlag=False
       #      pass
        if dT>=self.rotateLimitAc :
            return -np.pi
        elif dT<=-self.rotateLimitAc:
            return np.pi
        else:
            return -dT


    def straight(self):

        #if self.distance2des<=self.inbench:
        #    """如果到位置就减速到0"""
        #    return 1

        # if not self.fowardFlag:
        #     return 1
        #全速前进，不行再说
        return 6


    def lastTime(self):
        if self.fowardFlag or self.distance2des<=0.4:
            return self.distance2des/6
        else:
            return self.distance2des/6+0.4
    def angle(self):
        dx = self.des_x - self.x
        dy = self.des_y - self.y
        try:
            tanT = dy / dx
            T = np.arctan(tanT)

            if tanT > 0:
                if dx < 0:
                    T = T - np.pi
            if tanT <= 0:
                if dx < 0:
                    T = T + np.pi

        except:
            if dy > 0:
                T = np.pi / 2
            else:
                T = -np.pi / 2
        return T



    def calculate_close_speed (self):

      #这个估算
        if abs(self.angle()-self.toward)<=np.pi*3/5:
            if self.distance2des>=2*self.maxSpeedRadius*self.sin(abs(self.angle()-self.toward)):
                wspeed = self.rotate()
                speed = self.straight()
                lasttime = self.lastTime()
        #elif self.distance2des<2*self.maxSpeedRadius*self.sin(abs(self.angle)):
            else:
                wspeed=self.rotate()
                #self.fowardFlag=False
                speed = 1
                lasttime = self.lastTime()
        else:
            if True :#self.distance2des>=2*self.maxSpeedRadius*self.sin(abs(self.angle()-self.toward)):#self.distance2des>=2*self.maxSpeedRadius*self.sin(abs(self.angle()-self.toward)):
                wspeed=self.rotate()
                #self.fowardFlag=False
                speed = 1
                lasttime = self.lastTime()
            # else:
            #     wspeed=-self.backRotate()
            #     speed = self.back()
            #     lasttime = self.lastTime()


        return speed, wspeed,lasttime

    def sin(self,x):
        # 计算sin方法
        x = x * 3.14159265 / 180
        # initialize sum and term
        sinX = 0
        term = x
        # loop until term is small enough
        n = 1
        while abs(term) > 1e-2:
            # add term to sum
            sinX += term
            # update term using recurrence relation
            n += 2
            term = -term * x * x / (n * (n - 1))
        # return sum as the approximation of sin(x)
        return sinX

    def backRotate(self):
        # if self.distance2des<=self.inbench:
        #     """如果到位置就减速到0"""
        #     return 0
        #if (abs(self.speed_x)+abs(self.speed_y))>=0.1 and not self.fowardFlag:
        #    #没到位置，速度先为0先调整方向
        #    return 0

        dT=self.toward-self.angle()
        #0到pi 顺时针 pi到2pi，逆时针 -pi到0逆时针 -2pi到-pi顺时针
        if dT<0:
            dT=dT+np.pi+np.pi
        if dT>np.pi:
            dT=-(2*np.pi-dT)
        #角度修正
        #负的目标需要我逆时针转故返回正
       # print(dT)
       #  if abs(dT)<np.pi-self.rotateLimitGo:
       #      self.backwardFlag=False
       #  elif abs(dT)>np.pi-self.rotateLimitGo:
       #      self.backwardFlag=True
       #      pass
        if dT>=self.rotateLimitAc :
            return -np.pi
        elif dT<=-self.rotateLimitAc:
            return np.pi
        elif dT>self.stopRotate:
            return -np.sign(dT)*self.to0speed
        else:
            return dT
    def back(self):
        # if self.distance2des<=self.inbench:
        #    """如果到位置就减速到0"""
        #    return 1

        if not self.backwardFlag:
            return -0.5
        # 全速前进，不行再说
        return -2

    def decSpeed(self):
        pass