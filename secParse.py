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
        goodnum+=1
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
        arr = np.insert(arr, 0, values=np.arange(self.benchState.shape[0]) , axis=1)
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
        arr = np.insert(self.benchState, 0, values=np.arange(self.benchState.shape[0]) , axis=1)
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
    def getBench_elsegood_type_id(self, target_typel,self_typel,x,y):

        backid=-1
        """

        :param : 目标工作台带的类型，和自己的类型
        :xy 当前坐标
        :return:  返回序号，第一顺序含有其他最多，第二顺序距离
        
        """

        if target_typel==7:
            #如果说目标类型7
            f_old=0#记录当前选定台的最大材料素 最大3
            flag = False#如果没找到目标工作台，它有其他材料  为false
            close_list = self.getBench_closest_xy_type_id(x, y, target_typel)
            #获取列表，按距离排序，0是id
            for i in close_list:
                if int(self.getBench_id_last(int(i[0]))) == -1:
                    #他要没生产我才可考虑
                    if(self_typel==4 or self.getBench_id_goodnum_goodState(int(i[0]), 4)):
                    #我自己是，或者他有（456统一考虑）
                        f1=1
                    else:
                        f1=0
                    if (self_typel == 5 or self.getBench_id_goodnum_goodState(int(i[0]), 5)):
                        f2 = 1
                    else:
                        f2 = 0
                    if (self_typel == 6 or self.getBench_id_goodnum_goodState(int(i[0]), 6)):
                        f3 = 1
                    else:
                        f3 = 0
                    f=f1+f2+f3
                    #f 越大越优先考虑，可能有漏洞，暂未想到
                    if not self.getBench_id_goodnum_goodState(int(i[0]), self_typel):
                        #目标工作台缺我的话
                        if f>f_old:
                            #如果现在这个就绪数量大于我，更新
                            backid=int(i[0])
                            f_old=f
                            flag = True



        else:
            #如果目标类型456，输入注意控制
            elsegood=target_typel-self_typel-1
            #我的好伙伴的数字，这个应该没问题
            flag=False
            close_list=self.getBench_closest_xy_type_id(x,y,target_typel)
            #i[0]benchid，同上列表

            for i in close_list:
                distance=1
                if int(self.getBench_id_last(int(i[0])))==-1 and  self.getBench_id_goodnum_goodState(int(i[0]),elsegood)and not self.getBench_id_goodnum_goodState(int(i[0]),self_typel):

                    #如果他没生产，他有我的好伙伴，他没我，我就去
                    flag=True
                    backid=int(i[0])
                    break
                    # if distance>=20:
                    #     return 0
                    #防止被拐卖到偏远山区生产
        if not flag:
            #针对456的（7应该不会进来）没找到好伙伴那就挑个最近的没生产的缺我的
            close_list = self.getBench_closest_xy_type_id(x, y, target_typel)
            for i in close_list:
                if int(self.getBench_id_last(int(i[0]))) == -1 and not self.getBench_id_goodnum_goodState(int(i[0]), self_typel):
                    backid = int(i[0])
                    break


        return  int(backid)


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
        arr = np.insert(arr, 0, values=np.arange(self.carState.shape[0]), axis=1)
        arr = np.insert(arr, 1, values=np.array(list), axis=1)

        arr_sorted = arr[arr[:, 1].argsort()]

        arr_sorted = arr_sorted[:, [0, 1]]
        return arr_sorted

        # 同时返回标号和距离
        pass

    def show(self):
        pass
        print(self.benchState)
        print(self.carState)