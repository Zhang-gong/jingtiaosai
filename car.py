import numpy
import sys
import secParse


class car:
    def __init__(self, car_id):
        self.carid = car_id
        self.benchid = -1
        self.goods = -1
        self.tk = 1
        self.ck = 1
        self.wspeed = 0
        self.speed_x = 0
        self.speed_y=0
        self.toward = 0
        self.x = 0
        self.y = 0

        self.is_busy = False
        self.des_x = 0
        self.des_y = 0
    def getCarState(self,carState,is_busy):

        self.benchid = int(carState[0])
        self.goods =  int(carState[1])
        self.tk =  float(carState[2])
        self.ck =  float(carState[3])
        self.wspeed =  float(carState[4])
        self.speed_x =  float(carState[5])
        self.speed_y =  float(carState[6])
        self.toward =  float(carState[7])
        self.x =  float(carState[8])
        self.y =  float(carState[9])

        self.is_busy=is_busy




    def destination(self, type, x, y):

        """
        1.0 先转到直线(很小角度)再冲,反回需要打的速度
        :param type:
        :param x:
        :param y:
        :return:
        """
        self.des_x = x
        self.des_y = y

        speed=self.straight()
        wspped=self.rotate()
        return speed,wspped
    def rotate(self):
        return 0
    def straight(self):
        return 0
