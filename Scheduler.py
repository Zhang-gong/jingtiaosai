import math
import sys
import time
from crashControl import crashControl
import car
import mapParse
import output
import secParse
import os

TASK_LIST = [[1, 4], [2, 4], [1, 5], [3, 5], [2, 6], [3, 6], [4, 7], [5, 7], [6, 7], [7, 8], [1, 9], [2, 9], [3, 9],
             [4, 9], [5, 9], [6, 9], [7, 9]]

SHOULD_DELETE = []


def if_have_nine(lack_list):
    for i in range(len(lack_list)):
        if lack_list[i] == 9:
            return False
    return True


def pop_task_list(lack_list):
    have_nine = if_have_nine(lack_list)
    while len(lack_list) != 0:
        for i in range(len(TASK_LIST)):
            if lack_list[0] == TASK_LIST[i][0]:
                if SHOULD_DELETE.count(TASK_LIST[i]) == 0:
                    SHOULD_DELETE.append(TASK_LIST[i])
                if TASK_LIST[i][1] == 9 and have_nine:
                    continue
                lack_list.append(TASK_LIST[i][1])
        for i in range(len(TASK_LIST)):
            if lack_list[0] == TASK_LIST[i][1]:
                if SHOULD_DELETE.count(TASK_LIST[i]) == 0:
                    SHOULD_DELETE.append(TASK_LIST[i])
        lack_list.pop(0)
    for i in range(len(SHOULD_DELETE)):
        TASK_LIST.remove(SHOULD_DELETE[i])
    if TASK_LIST.count([1, 4]) > 0:
        if TASK_LIST.count([1, 9]) > 0:
            TASK_LIST.remove([1, 9])
    if TASK_LIST.count([2, 4]) > 0:
        if TASK_LIST.count([2, 9]) > 0:
            TASK_LIST.remove([2, 9])
    if TASK_LIST.count([1, 5]) > 0:
        if TASK_LIST.count([1, 9]) > 0:
            TASK_LIST.remove([1, 9])
    if TASK_LIST.count([3, 5]) > 0:
        if TASK_LIST.count([3, 9]) > 0:
            TASK_LIST.remove([3, 9])
    if TASK_LIST.count([2, 6]) > 0:
        if TASK_LIST.count([2, 9]) > 0:
            TASK_LIST.remove([2, 9])
    if TASK_LIST.count([3, 6]) > 0:
        if TASK_LIST.count([3, 9]) > 0:
            TASK_LIST.remove([3, 9])
    SHOULD_DELETE.clear()


class ready_task:
    def __init__(self, bench_type, x, y, buy_or_sell, bench_id):
        self.bench_type = bench_type
        self.x = x
        self.y = y
        """0是买buy，1是卖sell"""
        self.buy_or_sell = buy_or_sell
        self.bench_id = bench_id


class Task:
    def __init__(self, from_where, des):
        self.from_where = from_where
        self.des = des


class TaskList:
    def __init__(self):
        self.primary_task_list = []
        self.senior_task_list = []
        for task in TASK_LIST:
            if task[0] < 4:
                self.primary_task_list.append(Task(task[0], task[1]))
            else:
                self.senior_task_list.append(Task(task[0], task[1]))


def cul_car_target_toward(c):
    vec_x = c.des_x - c.x
    vec_y = c.des_y - c.y
    vec_len = math.sqrt(vec_x * vec_x + vec_y * vec_y)
    vec_x /= vec_len
    # vec_y /= vec_len
    """和x = 1, y = 0的单位向量求夹角"""
    angle_cos = vec_x
    """返回angle_cos的角度值"""
    return math.acos(angle_cos)


class Scheduler:
    def write_to_log(self):
        # 打开文件
        with open('Log/data_log.txt', 'a') as f:
            # 写入数据
            f.write("the frame is %s \n" % self.sec_map_parse.time)
            for c in self.cars:
                # f.write("the location of the car %d is x = %f y = %f\n" % (c.carid, c.x, c.y))
                f.write(
                    "the length of car %d _task_list's length is %d\n" % (c.carid, len(self.cars_task_list[c.carid])))
                # for car_task in self.cars_task_list[c.carid]:
                #     f.write("task's bench_id is %s bench_type is %d x is %f y is"
                #             " %f action is %d\n" % (
                #                 car_task.bench_id, car_task.bench_type, car_task.x, car_task.y, car_task.buy_or_sell))

            # f.write("des_has_selected len is %d:\n" % len(self.des_has_selected))
            # for des_task in self.des_has_selected:
            #     f.write("des_task id = %s type = %d\n" % (des_task.bench_id, des_task.bench_type))
            f.write("the task list now is :\n")
            f.write("the task list manager now len is %d:\n" % len(self.task_list_manager))

            for task_list in self.task_list_manager:
                f.write("primary list left %d:\n" % len(task_list.primary_task_list))
                f.write("senior list left %d:\n" % len(task_list.senior_task_list))
                for primart_task_list in task_list.primary_task_list:
                    f.write(
                        "primary_task_list from: %d to %d\n" % (primart_task_list.from_where, primart_task_list.des))
                for senior_task_list in task_list.senior_task_list:
                    f.write("senior_task_list from: %d to %d\n" % (senior_task_list.from_where, senior_task_list.des))
            #
            # f.write("the select task list is:\n")
            # for selected in self.start_has_selected:
            #     f.write("start selected task's id = %s:\n" % selected)
            # for selected in self.des_has_selected:
            #     f.write("des selected task's id = %s:\n" % selected.bench_id)
            # f.write("self.priority_tasks len is %d:\n" % len(self.priority_tasks))

            f.write("\n")

    def __init__(self):

        self.cars = [car.car(i) for i in range(4)]
        self.task_list_manager = []
        self.sec_map_parse = None
        self.map_parse = None
        """默认从1，2，3开始的任务都是可以直接获取的，所以这个列表只存4，5，6，7开始的任务"""
        self.priority_tasks = []
        self.cars_busy_state = [False, False, False, False]
        self.cars_task_list = [[], [], [], []]
        self.outControl = output.output()
        """用来存已经被选为目的地的坐标，去重，主要是去重每个任务的起点"""
        self.start_has_selected = []
        self.des_has_selected = []
        """True为算法，False为手动"""
        self.mode = True

        self.crashControler = crashControl()

        self.t_car1 = [[5, 1], [25, 25], [49, 4]]
        self.t_car2 = [[21, 10], [20, 2], [30, 3]]

        self.edge_up = 48
        self.edge_down = 2
        self.edge_left = 2
        self.edge_right = 48
        self.distance_threshold = 1

    def update(self):
        # ("请输入每一帧的地图信息：\n")
        self.outControl.putTime(self.sec_map_parse.time)
        # with open('Log/data_log.txt', 'a') as f:
        #     f.write("frame is : %s \n" % self.sec_map_parse.time)
        # if 5000 > int(self.sec_map_parse.time) > 4000:
        #     with open('Log/data_log.txt', 'a') as f:
        #         f.write("frame is : %s \n" % self.sec_map_parse.time)
        #         f.write("car %d loc is x = %f y = %f\n" % (self.cars[0].carid, self.cars[0].x, self.cars[0].y))
        #         if len(self.cars_task_list[0]) > 0:
        #             f.write("task x = %f, y  = %f\n" % (self.cars_task_list[0][0].x, self.cars_task_list[0][0].y))
        self.sec_map_parse.getState()
        self.update_car_info()
        if self.mode:
            for c in self.cars_busy_state:
                if not c:
                    # with open('Log/data_log.txt', 'a') as f:
                    #     for task_list in self.task_list_manager:
                    #         f.write("primary list left %d:\n" % len(task_list.primary_task_list))
                    #         f.write("senior list left %d:\n" % len(task_list.senior_task_list))
                    #         for primart_task_list in task_list.primary_task_list:
                    #             f.write(
                    #                 "primary_task_list from: %d to %d\n" % (
                    #                     primart_task_list.from_where, primart_task_list.des))
                    #         for senior_task_list in task_list.senior_task_list:
                    #             f.write("senior_task_list from: %d to %d\n" % (
                    #                 senior_task_list.from_where, senior_task_list.des))
                    self.update_task_state()
                    self.task_distribute()
                    break
            # self.update_task_state()
            # self.task_distribute()
            self.update_cars_state()
        else:
            self.hand_input_test()
        self.additional_task()
        self.outControl.send()

    def additional_task(self):
        while len(self.crashControler.avoidCrashTaskList) > 0:
            # with open('Log/data_log.txt', 'a') as f:
            #     f.write("!!!!!!!!!!!!\n")
            crash_list = self.crashControler.avoidCrashTaskList.pop(0)
            if crash_list[1] > 49.75:
                crash_list[1] = 50.0
            if crash_list[2] > 49.75:
                crash_list[2] = 50.0
            if crash_list[1] < 0.25:
                crash_list[1] = 0
            if crash_list[2] < 0.25:
                crash_list[2] = 0
            speed, wspeed, lasttime = self.cars[crash_list[0]].destination(crash_list[1], crash_list[2], 100)
            self.outControl.putForward(crash_list[0], speed)
            self.outControl.putRotate(crash_list[0], wspeed)

    def hand_input_test(self):
        if len(self.t_car1) > 0:
            x_1 = self.t_car1[0][0]
            y_1 = self.t_car1[0][1]
            c = self.cars[0]
            sub_x = c.x - x_1
            sub_y = c.y - y_1
            speed, wspeed, last_time = c.destination(x_1, y_1, distance=1000)
            self.crashControler.putCarState(self.sec_map_parse.carState[:, 4:10])
            self.crashControler.putSportState(0, speed, wspeed)
            self.crashControler.judgeAndModify()
            speed, wspeed = self.crashControler.getSportStateAter(0)  # 返回第零个车的修改
            self.outControl.putForward(c.carid, speed)
            self.outControl.putRotate(c.carid, wspeed)

            if (sub_x * sub_x + sub_y * sub_y) < 0.1:
                self.t_car1.pop(0)

        if len(self.t_car2) > 0:
            x_2 = self.t_car2[0][0]
            y_2 = self.t_car2[0][1]
            c = self.cars[1]
            sub_x = c.x - x_2
            sub_y = c.y - y_2
            speed, wspeed, last_time = c.destination(x_2, y_2, distance=1000)
            self.crashControler.putCarState(self.sec_map_parse.carState[:, 4:10])
            self.crashControler.putSportState(1, speed, wspeed)
            self.crashControler.judgeAndModify()
            speed, wspeed = self.crashControler.getSportStateAter(1)  # 返回第零个车的修改
            self.outControl.putForward(c.carid, speed)
            self.outControl.putRotate(c.carid, wspeed)
            if (sub_x * sub_x + sub_y * sub_y) < 0.1:
                self.t_car2.pop(0)

    def get_map_info(self):
        # if os.path.exists('Log/data_log.txt'):
        #     os.remove('Log/data_log.txt')
        # with open('Log/data_log.txt', 'w') as f:
        #     f.write("__init__\n")
        # print("请输入初始地图：\n")
        self.map_parse = mapParse.mapParse()
        self.sec_map_parse = secParse.secParse(self.map_parse)
        tmp_lack_list = []
        for i in range(len(self.map_parse.bench)):
            if len(self.map_parse.bench[i]) == 0:
                j = i + 1
                tmp_lack_list.append(j)
        pop_task_list(tmp_lack_list)
        # print(TASK_LIST)

    def update_task_list_manager(self):
        """
        每个task_list_manager的一个元素就是一组任务
        :return:
        """
        if len(self.task_list_manager) == 0:
            t = TaskList()
            self.task_list_manager.append(t)
        # print("new task_list_manager")

        for task_list in self.task_list_manager:
            if len(task_list.senior_task_list) == 0 and len(task_list.primary_task_list) == 0:
                self.task_list_manager.remove(task_list)
            break

        length = len(self.task_list_manager)
        if len(self.task_list_manager[length - 1].primary_task_list) < 4:
            t = TaskList()
            self.task_list_manager.append(t)

    def update_task_state(self):
        """
        更新任务状态
        :return:
        """
        if len(TASK_LIST) == 0:
            return
        self.update_task_list_manager()

        for task_list in self.task_list_manager:

            """通过id ， 查询每个任务当前是否有可以被执行的，如果起点的任务中有 == 0 或者剩余时间少于 50帧的时候，
                就视为可以被执行，因为后6个默认可以执行，因此只看前四个 高级任务"""
            for senior_task in task_list.senior_task_list:
                flag = False
                """通过task.from查询所有该种类的工作台中是否有可以执行的（== 0 or <= 50），有就加入队列中"""
                res_list = self.sec_map_parse.getBench_lasted_type_id(senior_task.from_where)
                for bench_state in res_list:
                    # with open('Log/data_log.txt', 'a') as f:
                    #     f.write("bench_id %d left time %d\n" % (int(bench_state[0]), int(bench_state[1])))
                    if int(self.sec_map_parse.getBench_id_outState(int(bench_state[0]))) == 1 or 50 >= int(bench_state[1]) >= 0:
                        """检查重复"""
                        # with open('Log/data_log.txt', 'a') as f:
                        #     f.write("FIND THE RES_LIST\n")
                        if not self.check_if_exist(bench_state[0]):
                            continue
                        """通过bench_id获得bench_location"""
                        # with open('Log/data_log.txt', 'a') as f:
                        #     f.write("FIND 2222\n")
                        x, y = self.sec_map_parse.getBench_id_loc(int(bench_state[0]))
                        tmp_task_1 = ready_task(senior_task.from_where, float(x), float(y), 0, bench_state[0])
                        tmp_task_2 = self.get_des_task(tmp_task_1, senior_task)
                        if tmp_task_2 is not None:
                            self.priority_tasks.append(tmp_task_1)
                            self.priority_tasks.append(tmp_task_2)
                            # with open('Log/data_log.txt', 'a') as f:
                            #     f.write("task_1 type %d task_2 type %d 加入优先队列\n" % (
                            #         tmp_task_1.bench_type, tmp_task_2.bench_type))
                            """去重"""
                            self.start_has_selected.append(tmp_task_1.bench_id)
                            self.des_has_selected.append(tmp_task_2)
                            flag = True
                            # with open('Log/data_log.txt', 'a') as f:
                            #     f.write("FIND 33333\n")

                            break
                if flag:
                    task_list.senior_task_list.remove(senior_task)
                    # with open('Log/data_log.txt', 'a') as f:
                    #     f.write("remove senior task from %d to %d\n" % (senior_task.from_where, senior_task.des))

    def task_distribute(self):
        """
        如果优先处理队列priority_tasks里面有任务了，优先处理
        :return:
        """
        for i in range(4):
            """第j辆车，如果不忙"""
            if len(self.priority_tasks) >= 2:
                if not self.cars_busy_state[i]:
                    # with open('Log/data_log.txt', 'a') as f:
                    #     f.write("choose senior task\n")
                    # self.cars_task_list[i].append(self.priority_tasks[0])
                    tmp_task_1 = self.priority_tasks.pop(0)
                    # self.cars_task_list[i].append(self.priority_tasks[0])
                    tmp_task_2 = self.priority_tasks.pop(0)
                    self.check_if_near_edge(self.cars[i], tmp_task_1, tmp_task_2)
                    self.cars_busy_state[i] = True

        for i in range(4):
            if not self.cars_busy_state[i]:
                # with open('Log/data_log.txt', 'a') as f:
                #     f.write("choose primary task\n")
                self.get_nearest_available_bench(self.cars[i])

    def update_car_info(self):
        for i in range(4):
            self.cars[i].getState(self.sec_map_parse.carState[i])

    def check_if_near_edge(self, c, tmp_task_1, tmp_task_2):
        # with open('Log/data_log.txt', 'a') as f:
        #     # 写入数据
        #     f.write("the frame is %s \n" % self.sec_map_parse.time)
        remain_time = 9000 - int(self.sec_map_parse.time)
        dx_1 = abs(c.x - tmp_task_1.x)
        dy_1 = abs(c.y - tmp_task_1.y)
        dx_2 = abs(tmp_task_2.x - tmp_task_1.x)
        dy_2 = abs(tmp_task_2.y - tmp_task_1.y)
        dx = int(dx_1) * 2
        dy = int(dy_1) * 2
        distance_1 = self.sec_map_parse.map[dx][dy]
        buy_time = distance_1 / 6 + 1
        dx = int(dx_2) * 2
        dy = int(dy_2) * 2
        distance_2 = self.sec_map_parse.map[dx][dy]
        sell_time = distance_2 / 6 + 1
        # with open('Log/data_log.txt', 'a') as f:
        #     f.write("need time %f , remain time %d\n" % (buy_time + sell_time, remain_time))
        need_time = buy_time + sell_time
        if need_time > (remain_time / 50):
            # with open('Log/data_log.txt', 'a') as f:
            #     f.write("don't do it\n")
            return
        if dx_1 < self.distance_threshold < dy_1:
            # with open('Log/data_log.txt', 'a') as f:
            #     f.write("c to t1_left\n")
            if distance_1 > 5:
                if tmp_task_1.x < self.edge_left:
                    # with open('Log/data_log.txt', 'a') as f:
                    #     f.write("1\n")
                    tmp_task = ready_task(0, self.edge_left, c.y, 2, 0)
                    self.cars_task_list[c.carid].insert(0, tmp_task)
                else:
                    if tmp_task_1.x > self.edge_right:
                        # with open('Log/data_log.txt', 'a') as f:
                        #     f.write("2\n")
                        tmp_task = ready_task(0, self.edge_right, c.y, 2, 0)
                        self.cars_task_list[c.carid].insert(0, tmp_task)
        else:
            if dy_1 < self.distance_threshold < dx_1:
                # with open('Log/data_log.txt', 'a') as f:
                #     f.write("c %d to t1 down\n" % c.carid)
                if distance_1 > 5:
                    if tmp_task_1.y < self.edge_down:
                        # with open('Log/data_log.txt', 'a') as f:
                        #     f.write("3\n")
                        tmp_task = ready_task(0, c.x, self.edge_down, 2, 0)
                        self.cars_task_list[c.carid].insert(0, tmp_task)
                    else:
                        if tmp_task_1.y > self.edge_up:
                            # with open('Log/data_log.txt', 'a') as f:
                            #     f.write("c.carid = %d , des is %d\n 4\n" % (c.carid, tmp_task_1.bench_type))
                            tmp_task = ready_task(0, c.x, self.edge_up, 2, 0)
                            self.cars_task_list[c.carid].insert(0, tmp_task)

        self.cars_task_list[c.carid].append(tmp_task_1)
        if dx_2 < self.distance_threshold < dy_2:
            # with open('Log/data_log.txt', 'a') as f:
            #     f.write("t1 to t2 left\n")
            if distance_2 > 5:
                if tmp_task_2.x < self.edge_left:
                    # with open('Log/data_log.txt', 'a') as f:
                    #     f.write("5\n")
                    tmp_task = ready_task(0, self.edge_left, tmp_task_1.y, 2, 0)
                    self.cars_task_list[c.carid].insert(0, tmp_task)
                else:
                    if tmp_task_2.x > self.edge_right:
                        # with open('Log/data_log.txt', 'a') as f:
                        #     f.write("6\n")
                        tmp_task = ready_task(0, self.edge_right, tmp_task_1.y, 2, 0)
                        self.cars_task_list[c.carid].insert(0, tmp_task)
        else:
            if dy_2 < self.distance_threshold < dx_2:
                # with open('Log/data_log.txt', 'a') as f:
                #     f.write("t1 to t2 down\n")
                if distance_2 > 5:
                    if tmp_task_2.y < self.edge_down:
                        # with open('Log/data_log.txt', 'a') as f:
                        #     f.write("7\n")
                        tmp_task = ready_task(0, tmp_task_1.x, self.edge_down, 2, 0)
                        self.cars_task_list[c.carid].insert(0, tmp_task)
                    else:
                        if tmp_task_2.y > self.edge_up:
                            # with open('Log/data_log.txt', 'a') as f:
                            #     f.write("c.carid = %d , des is %d\n 8\n" % (c.carid, tmp_task_2.bench_type))
                            tmp_task = ready_task(0, tmp_task_1.x, self.edge_up, 2, 0)
                            self.cars_task_list[c.carid].insert(0, tmp_task)

        self.cars_task_list[c.carid].append(tmp_task_2)

    def update_cars_state(self):
        # self.write_to_log()
        self.crashControler.putCarState(self.sec_map_parse.carState[:, 4:10])
        for c in self.cars:
            if len(self.cars_task_list[c.carid]) == 0:
                continue
            tmp_task = self.cars_task_list[c.carid][0]
            sub_x = abs(tmp_task.x - c.x)
            sub_y = abs(tmp_task.y - c.y)
            dx = int(sub_x) * 2
            dy = int(sub_y) * 2
            distance = self.sec_map_parse.map[dx][dy]
            if self.cars_busy_state[c.carid]:
                task = self.cars_task_list[c.carid][0]
                speed, wspeed, lasttime = c.destination(task.x, task.y, distance)
                self.crashControler.putSportState(c.carid, speed, wspeed)
                self.crashControler.judgeAndModify()
                speed, wspeed = self.crashControler.getSportStateAter(c.carid)  # 返回第零个车的修改
                self.outControl.putForward(c.carid, speed)
                self.outControl.putRotate(c.carid, wspeed)
            """是否在目标点"""
            if (sub_x * sub_x + sub_y * sub_y) < 0.1:
                task = self.cars_task_list[c.carid][0]
                action = task.buy_or_sell
                if action == 2:
                    self.cars_task_list[c.carid].pop(0)
                    continue
                if action == 0:
                    if int(self.sec_map_parse.getBench_id_outState(int(task.bench_id))) == 0:
                        return
                    self.outControl.putBuy(c.carid)
                    self.cars_task_list[c.carid].pop(0)
                    if self.start_has_selected.count(task.bench_id) > 0:
                        self.start_has_selected.remove(task.bench_id)

                else:
                    self.outControl.putSell(c.carid)
                    self.cars_task_list[c.carid].pop(0)
                    if self.des_has_selected.count(task) > 0:
                        # with open('Log/data_log.txt', 'a') as f:
                        #     f.write("\n SUCCESSFULL POP!!! \n")
                        self.des_has_selected.remove(task)
                    self.cars_busy_state[c.carid] = False

            # self.outControl.putForward(c.carid, lasttime)
            # print("car %d des is x = %f y = %f" % (c.carid, self.cars_task_list[c.carid][0].x,
            # self.cars_task_list[c.carid][0].y))
            # print("car %d des is x = %f y = %f" % (c.carid, self.cars_task_list[c.carid][0].x,
            #    self.cars_task_list[c.carid][0].y))

    def check_des_task_exist(self, sell_goods_type, des_id):
        for i in range(len(self.des_has_selected)):
            des_task = self.des_has_selected[i]
            if int(des_task.bench_id) == int(des_id) and int(sell_goods_type) == int(des_task.bench_type):
                return False
        return True

    def get_des_task(self, tmp_task, task):
        if task.des == 4 or task.des == 5 or task.des == 6 or task.des == 7:
            des_id = self.sec_map_parse.getBench_elsegood_type_id(int(task.des), int(task.from_where), tmp_task.x,
                                                                  tmp_task.y)
            if des_id != -1:
                if self.check_des_task_exist(task.from_where, des_id):
                    des_x, des_y = self.sec_map_parse.getBench_id_loc(int(des_id))
                    tmp_task_2 = ready_task(task.from_where, float(des_x), float(des_y), 1, des_id)
                    return tmp_task_2
        else:
            tmp_task_2 = None
            des_list = self.sec_map_parse.getBench_closest_xy_type_id(tmp_task.x, tmp_task.y, task.des)
            for des in des_list:
                des_id = des[0]
                # with open('Log/data_log.txt', 'a') as f:
                #     f.write("FIND 2222\n")
                """获得对应卖的任务,找最近的，缺货的对应工作台"""
                if not self.sec_map_parse.getBench_id_goodnum_goodState(int(des_id), task.from_where):
                    #
                    # with open('Log/data_log.txt', 'a') as f:
                    #     f.write()
                    if not self.check_des_task_exist(task.from_where, des_id):
                        continue
                    des_x, des_y = self.sec_map_parse.getBench_id_loc(int(des_id))
                    tmp_task_2 = ready_task(task.from_where, float(des_x), float(des_y), 1, des_id)
                    return tmp_task_2

        tmp_task_2 = None
        des_list = self.sec_map_parse.getBench_closest_xy_type_id(tmp_task.x, tmp_task.y, task.des)
        for des in des_list:
            des_id = des[0]
            if not self.sec_map_parse.getBench_id_goodnum_goodState(int(des_id), task.from_where):
                #
                    # with open('Log/data_log.txt', 'a') as f:
                    #     f.write()
                if not self.check_des_task_exist(task.from_where, des_id):
                    continue
                des_x, des_y = self.sec_map_parse.getBench_id_loc(int(des_id))
                tmp_task_2 = ready_task(task.from_where, float(des_x), float(des_y), 1, des_id)
                return tmp_task_2
        return tmp_task_2




    def check_if_exist(self, bench_id):
        if self.start_has_selected.count(bench_id) == 0:
            return True
        return False

    def choose_neatest_loc(self, c, from_where):
        res_list = self.sec_map_parse.getBench_closest_xy_type_id(c.x, c.y, from_where)
        if len(res_list) == 0:
            return None
        for res in res_list:
            if self.check_if_exist(res[0]):
                return res
        return None

    def get_nearest_available_bench(self, c):
        """
        先获得车的位置，通过下标
        获得离小车最近的，可以拿货的工作台
        :return:
        """
        # print(c.x + " " + c.y)
        for task_list in self.task_list_manager:
            nearest = 100000.0
            choose = 0
            tmp_task_1 = ready_task(0, 0, 0, 0, 0)
            for primary_task in task_list.primary_task_list:
                """获得最近的任务，通过小车坐标, 任务的类型 ，得到该任务中离小车最近的点，比较所有可以的任务，拿最近的那个
                这里应该添加一个对比，虽然任务不一样，但是可能小车会选同一个坐标，应该去重"""
                res = self.choose_neatest_loc(c, primary_task.from_where)
                if res is None:
                    break
                # res_list = self.sec_map_parse.getBench_closest_xy_type_id(c.x, c.y, primary_task.from_where)
                # print("primary_task from : " + str(primary_task.from_where) + " " + res[1])
                if nearest > float(res[1]):
                    nearest = float(res[1])
                    choose = primary_task
                    tmp_task_1.x, tmp_task_1.y = self.sec_map_parse.getBench_id_loc(int(res[0]))
                    tmp_task_1.bench_id = res[0]
            if choose == 0:
                continue
            tmp_task_1.x = float(tmp_task_1.x)
            tmp_task_1.y = float(tmp_task_1.y)
            tmp_task_1.bench_type = choose.from_where
            # print("choose :" + str(choose.from_where))
            tmp_task_2 = self.get_des_task(tmp_task_1, choose)
            if tmp_task_2 is None:
                # print("Error,can't find next task, push_back task_1")
                continue
            else:
                self.check_if_near_edge(c, tmp_task_1, tmp_task_2)
                self.start_has_selected.append(tmp_task_1.bench_id)
                self.des_has_selected.append(tmp_task_2)
                task_list.primary_task_list.remove(choose)
                # print('append into car_task_list[%d] two tasks' % c.carid)
                self.cars_busy_state[c.carid] = True
                break
