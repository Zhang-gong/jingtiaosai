import sys
import numpy as np

"""
数据结构随算法而更新
地图解析，machine中存四个机器位置和方向，
bench[i]存着第i+1柜台位置,位置似乎用处不大，用于后续优化算法时候初始化最优
存在问题：需要对出现的柜台进行顺序编号，位置记录没那么重要，从第一帧他会给。
需要继续做的：柜台状态

联系wzd

"""


class mapParse():

    def __init__(self):
        self.machine = [[-1, 0, 0], [-1, 0, 0], [-1, 0, 0], [-1, 0, 0]]  # x,y,方向，方向向右为0，逆时针0-2pai
        self.bench = [[], [], [], [], [], [], [], [], []]
        self.getMap()
        self.mapDistance = self.crateMapDistance(100, 100)

    def crateMapDistance(self, n, m):
        arr1 = (np.arange(n).reshape(n, 1) * 2) * 0.25 * np.ones((1, m))
        arr2 = (np.arange(m).reshape(1, m) * 2) * 0.25 * np.ones((n, 1))
        return np.sqrt(arr1 ** 2 + arr2 ** 2)

    def getMap(self):
        input_line = input()
        y = 100
        while input_line != "OK":
            x = 0
            for i in input_line:
                x += 1
                if i == '.':
                    continue
                elif i == 'A':
                    if self.machine[0][0] == -1:
                        self.machine[0] = [x, y]
                    elif self.machine[1][0] == -1:
                        self.machine[1] = [x, y]
                    elif self.machine[2][0] == -1:
                        self.machine[2] = [x, y]
                    elif self.machine[3][0] == -1:
                        self.machine[3] = [x, y]

                    # 添加一个机器人
                elif i.isdigit():
                    self.bench[int(i) - 1].append([x, y])
            y -= 1

            input_line = input()
    # def show(self):
    #     for i in self.machine:
    #         print(i)
    #     for i in self.bench:
    #         print(i)
