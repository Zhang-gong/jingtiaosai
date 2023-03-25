import numpy as np

"""
靠墙判断处理不了0.25 也不行（问题是车就到不了这个坐标啊宽0.4
0.5贴墙效果也很差（不会有个调度跨地图还是边角吧
"""


class crashControl():
    def __init__(self):

        self.nFrameWall = 4  # 预判帧数 对墙
        self.nFrameOthers = 15  # 8相互
        self.threshold2others = (0.53 + self.nFrameOthers * 6 / 50) * 2 * 1.414  # 小车中心dx+dy超过这个值被判定为间隔很远
        self.threshold2crash = 1.2 * 1.2  # 判断相撞临界的平方
        self.threshold2angle = np.pi / 5 * 4  # 相撞一般一顺一逆，极端情况同时顺或逆，临界值
        self.decRate = 2 / 3  # 速度每次降
        self.speedWhenRate = 4
        self.r_wall = 2.4
        self.xmax = 50
        self.xmin = 0
        self.ymax = 50
        self.ymin = 0
        self.avoidCrashTaskList = []  # 避免亲嘴的任务列表,id x,y  比小距离大
        self.CollisionFineTuning = 5  # 碰撞微调系数
        self.fineFlag = 0  # 大于0就是正撞?好像没用

        self.iscrash = False

        self.carState = None
        """ 角速度，线速度x,线速度y，朝向，坐标x 坐标y"""
        self.sportState = np.zeros((4, 2))
        """ speed wspeed"""
        self.sportStateAfter = np.zeros((4, 2))

    def putCarState(self, carState: np.ndarray):
        tmp = carState.copy()
        self.carState = tmp

    def putSportState(self, id, speed, wspeed):
        self.sportState[id][0] = speed
        self.sportState[id][1] = wspeed

    def getSportStateAter(self, id):
        return self.sportStateAfter[id][0], self.sportStateAfter[id][1]

    def judgeAndModify(self):
        # 主要
        self.sportStateAfter = self.sportState
        self.iscrash = False

        self.judge2wall()
        self.judge2others()

    def judge2wall(self):
        nextloc = np.zeros((4, 2))
        for i in range(4):
            # 线速度带符号的
            nextloc[i][0] = float(self.carState[i][4]) + self.threshold2zero((float(self.carState[i][1])))
            nextloc[i][1] = float(self.carState[i][5]) + self.threshold2zero((float(self.carState[i][2])))
            if nextloc[i][0] > 50.1 or nextloc[i][0] < -0.1 or nextloc[i][1] > 50.1 or nextloc[i][1] < 0.1:
                # 出界,线速度1，提前会有终点信息让我0
                self.sportStateAfter[i][0] = 0
                self.iscrash = True

    def judge2others(self):
        list = []
        for i in range(4):
            for j in range(i + 1, 4):
                if abs(float(self.carState[i][4]) - float(self.carState[j][4])) + abs(
                        float(self.carState[i][5]) - float(self.carState[j][5])) < self.threshold2others:
                    list.append([i, j])
        # (i与j存在碰撞风险)
        # 如果方向差绝对值小于pi/2就一个停止，如果方向差值大于则都右转pi且速度为原来2/3
        nextloc = np.zeros((self.nFrameOthers + 1, 4, 2))
        for j in range(self.nFrameOthers + 1):
            for i in range(4):
                nextloc[j][i][0] = float(self.carState[i][4]) + (float(self.carState[i][1]) * (j) / 50)
                nextloc[j][i][1] = float(self.carState[i][5]) + (float(self.carState[i][2]) * (j) / 50)

        for i, j in list:
            modify = False
            for t in range(self.nFrameOthers):
                if abs(nextloc[t][i][0] - nextloc[t][j][0]) ** 2 + abs(
                        nextloc[t][i][1] - nextloc[t][j][1]) ** 2 < self.threshold2crash:
                    modify = True
                    self.iscrash = True
                    break
            if modify:
                Titoj = self.angle(float(self.carState[i][4]), float(self.carState[i][5]),
                                   float(self.carState[j][4]), float(self.carState[j][5]))  # j视角中的i
                if Titoj - float(self.carState[j][3]) > 0:
                    self.sportStateAfter[i][1] = +np.pi
                    self.sportStateAfter[i][0] = self.sportStateAfter[i][1]
                    self.sportStateAfter[j][1] = -np.pi
                    self.sportStateAfter[j][0] = self.sportStateAfter[j][1] * self.decRate

                else:
                    self.sportStateAfter[i][1] = -np.pi
                    self.sportStateAfter[i][0] = self.sportStateAfter[i][1]
                    self.sportStateAfter[j][1] = np.pi
                    self.sportStateAfter[j][0] = self.sportStateAfter[j][1] * self.decRate
                if abs(float(self.carState[i][3]) - float(self.carState[j][3])) > self.threshold2angle:
                    xi = float(self.carState[i][4])
                    yi = float(self.carState[i][5])
                    xj = float(self.carState[j][4])
                    yj = float(self.carState[j][5])
                    dx = xi - xj
                    dy = yi - yj
                    if Titoj - float(self.carState[j][3]) > 0:
                        self.sportStateAfter[i][1] = -np.pi

                        self.avoidCrashTaskList.append(
                            [j, xj + dy * self.CollisionFineTuning, yj - dx * self.CollisionFineTuning])
                        self.avoidCrashTaskList.append(
                            [i, xi - dy * self.CollisionFineTuning, yi + dx * self.CollisionFineTuning])
                    else:
                        self.sportStateAfter[i][1] = np.pi
                        self.avoidCrashTaskList.append(
                            [j, xj - dy * self.CollisionFineTuning, yj + dx * self.CollisionFineTuning])
                        self.avoidCrashTaskList.append(
                            [i, xi + dy * self.CollisionFineTuning, yi - dx * self.CollisionFineTuning])

                self.fineFlag = self.sportStateAfter[i][1] * self.sportStateAfter[j][1]

    def threshold2zero(self, v0):
        return v0 * self.nFrameWall / 50 * self.r_wall + np.sign(
            v0) * 0.5 * self.nFrameWall * self.nFrameWall / 50 * self.r_wall * self.r_wall  # 撞墙临界值

    def angle(self, desx, desy, x, y):
        dx = desx - x
        dy = desy - y
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
