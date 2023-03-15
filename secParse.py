import sys
import numpy
import numpy as np


class secParse():

    def __init__(self):
        self.time=0
        self.money=0
        self.benchState=np.empty((0,6), dtype='O')




    def getState(self):

        input_line=input()
        self.time,self.money=input_line.split(" ")
        input_line = input()
        benchNum=int(input_line)
        input_line = input()
        for i in range(benchNum):
            a=np.array(input_line.split(" ")).reshape(1,6)

            self.benchState=np.append(self.benchState,a,axis=0)
            input_line = input()

        while input_line != "OK":


            input_line = input()
    def show(self):
        print(self.benchState)

