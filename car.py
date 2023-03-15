import numpy
import sys


class car:
    def __init__(self, car_id):
        self.carid = car_id
        self.benchid = -1
        self.goods = -1
        self.tk = 1
        self.ck = 1
        self.wspeed = 0
        self.speed = 0
        self.toward = 0
        self.x = 0
        self.y = 0
        self.is_busy = False
        self.des_x = 0
        self.des_y = 0

    def destination(self, no, type, x, y):
        pass

    def updateState(self):
        pass
