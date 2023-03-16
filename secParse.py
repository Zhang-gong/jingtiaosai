import sys
import numpy
import numpy as np
import mapParse

"""
未加入输入结束时候的eof判断
get使用方法
getBench_closest_xy_type_id
getcar或者getbench获取谁的信息，中间的为输入参数，最后的id为返回。详细输入输出见注释

留存了一个粗糙的测试用
"""


class secParse():

    def __init__(self, mapInstance):
        self.carNum = 4
        self.time = 0
        self.money = 0
        self.benchState = np.empty((0, 6))
        self.carState = np.empty((0, 10))
        self.mapInstance = mapInstance
        self.map = mapInstance.mapDistance

    def getState(self):
        self.benchState = np.empty((0, 6))
        self.carState = np.empty((0, 10))

        try:
            input_line = input()
        except:
            exit(0)
        while len(input_line) <= 5:                             #测试用
            input_line = input()
        self.time, self.money = input_line.split(" ")
        input_line = input()
        benchNum = int(input_line)
        input_line = input()
        for i in range(benchNum):
            a = np.array(input_line.split(" ")).reshape(1, 6)
            self.benchState = np.append(self.benchState, a, axis=0)
            input_line = input()
        for i in range(self.carNum):
            a = np.array(input_line.split(" ")).reshape(1, 10)
            self.carState = np.append(self.carState, a, axis=0)
            input_line = input()
        while input_line != "OK":
            input_line = input()
        sys.stdin.flush()

    def getBench_id_loc(self, id):
        """
        :param id:bench的id
        :return: （x,y）坐标
        """
        return self.benchState[id][1], self.benchState[id][2]

    def getBench_id_type(self, id):
        """
        :param id: bench的id
        :return: 工作台类型type
        """

        return self.benchState[id][0]

    def getBench_id_last(self, id):
        """
        :param id:  bench的id
        :return: 作台升剩余工作时间，-1表示未生产，0表示生产阻塞，》=0表示剩余帧数
        """

        return self.benchState[id][3]

    def getBench_id_goodnum_goodState(self, id, goodnum):
        """
        :param id:   bench的id
        :param goodnum:  判断是否有货物的编号
        :return:  有就是True，没有就是Flase
        """
        k = int(self.benchState[id][4])
        n = 1 << goodnum
        k = k % n
        if k / (n >> 1) >= 1:
            return True
        else:
            return False

    def getBench_id_goodState(self, id):
        """
        :param id: bench的id
        :return: 返回一个二进制表示
        """
        return self.benchState[id][4]

    def getBench_id_outState(self, id):
        """

        :param id: bench的id
        :return: 0无1有
        """
        return self.benchState[id][5]

    def getBench_closest_xy_type_id(self, x, y, typel):
        """

        :param x:  指定x
        :param y:  指定y
        :param typel: 指导工作台-1为所有工作台
        :return: 同时返回标号和距离
        """
        list = []
        for i in self.benchState:
            cx = float(i[1])
            cy = float(i[2])
            dx = int(abs(cx - x) * 2)
            dy = int(abs(cy - y) * 2)
            list.append(self.map[dx][dy])

        arr = self.benchState
        arr = np.insert(arr, 0, values=np.arange(self.benchState.shape[0]) + 1, axis=1)
        arr = np.insert(arr, 1, values=np.array(list), axis=1)

        arr_sorted = arr[arr[:, 1].argsort()]
        if typel == -1:
            arr_sorted = arr_sorted[:, [0, 1]]
            return arr_sorted
        else:
            tmp = np.empty((0, 8))
            for i in arr_sorted:
                if int(i[2]) == typel:
                    tmp = np.append(tmp, i.reshape(1, 8), axis=0)
            tmp = tmp[:, [0, 1]]
            return tmp

    def getBench_lasted_type_id(self, typel):
        """

        :param typel: 对应种类的工作台，-1表示所有工作台
        :return:  返回工作台序号和剩余时间
        """
        arr = np.insert(self.benchState, 0, values=np.arange(self.benchState.shape[0]) + 1, axis=1)
        arr_sorted = arr[arr[:, 4].argsort()]
        if typel == -1:
            arr_sorted = arr_sorted[:, [0, 4]]
            return arr_sorted
        else:
            tmp = np.empty((0, 7))
            for i in arr_sorted:
                if int(i[1]) == typel:
                    tmp = np.append(tmp, i.reshape(1, 7), axis=0)
            tmp = tmp[:, [0, 4]]
            return tmp

        # 同时返回标号时间
        pass

    def getCar_id_benchid(self, id):
        """
        :param id: car 的id
        :return:-1：表示当前没有处于任何工作台附近
                     [0,工作台总数-1] ：表示某工作台的下
                    标，从 0 开始，按输入顺序定。当前机
                    器人的所有购买、出售行为均针对该工
                    作台进行。
        """
        return self.carState[id][0]

    def getCar_id_type(self, id):
        """
        :param id:  car 的id
        :return:
                    范围[0,7]。
                     0 表示未携带物品。
                     1-7 表示对应物品。
        """
        return self.carState[id][1]

    def getCar_id_tf(self, id):
        """

        :param id:  car 的id
        :return: 携带物品时为[0.8, 1]的浮点数，不携带物品
                 时为 0
        """
        return self.carState[id][2]

    def getCar_id_cf(self, id):
        """
        :param id:  car 的id
        :return:    携带物品时为[0.8, 1]的浮点数，不携带物品
                    时为 0。
        """
        return self.carState[id][3]

    def getCar_id_wspeed(self, id):
        """

        :param id: car 的id
        :return: 单位：弧度/秒。
                     正数：表示逆时针。
                     负数：表示顺时针。
        """
        return self.carState[id][4]

    def getCar_id_speed(self, id):
        """

        :param id: car 的id
        :return: 由二维向量描述线速度，单位：米/秒
        """
        return self.carState[id][5], self.carState[id][6]

    def getCar_id_toward(self, id):
        """

        :param id: car 的id
        :return:弧度，范围[-π,π]。方向示例：
                 0：表示右方向。
                 π/2：表示上方向。
                 -π/2：表示下方向。
        """
        return self.carState[id][7]

    def getCar_id_loc(self, id):
        """

        :param id: car 的id
        :return:
        """
        return self.carState[id][8], self.carState[id][9]

    def getCar_closest_xy_id(self, x, y):
        """

        :param id: car 的id
        :param x: 目标x
        :param y: 目标y
        :return: 返回小车距离排序
        """
        list = []
        for i in self.carState:
            cx = float(i[8])
            cy = float(i[9])
            dx = int(abs(cx - x) * 2)
            dy = int(abs(cy - y) * 2)
            list.append(self.map[dx][dy])

        arr = self.carState
        arr = np.insert(arr, 0, values=np.arange(self.carState.shape[0]) + 1, axis=1)
        arr = np.insert(arr, 1, values=np.array(list), axis=1)

        arr_sorted = arr[arr[:, 1].argsort()]

        arr_sorted = arr_sorted[:, [0, 1]]
        return arr_sorted

        # 同时返回标号和距离
        pass

    def show(self):
        print(self.benchState)
        print(self.carState)
