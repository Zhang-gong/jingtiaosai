import math
import sys
import time
from crashControl import crashControl
import car
import mapParse
import output
import secParse
import os


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
        t1 = Task(4, 7)
        t3 = Task(5, 7)
        t2 = Task(6, 7)
        t4 = Task(1, 4)
        t5 = Task(2, 4)
        t6 = Task(1, 5)
        t7 = Task(3, 5)
        t8 = Task(2, 6)
        t9 = Task(3, 6)
        t0 = Task(7, 8)
        self.primary_task_list = [t4, t5, t6, t7, t8, t9]
        self.senior_task_list = [t0, t1, t2, t3]


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
                f.write("the location of the car %d is x = %f y = %f\n" % (c.carid, c.x, c.y))
                f.write(
                    "the length of car %d _task_list's length is %d\n" % (c.carid, len(self.cars_task_list[c.carid])))
                for car_task in self.cars_task_list[c.carid]:
                    f.write("task's bench_id is %s bench_type is %d x is %f y is"
                            " %f action is %d\n" % (
                                car_task.bench_id, car_task.bench_type, car_task.x, car_task.y, car_task.buy_or_sell))

            f.write("the task list now is :\n")
            for task_list in self.task_list_manager:
                f.write("primary list left:\n")
                for primart_task_list in task_list.primary_task_list:
                    f.write(
                        "primary_task_list from: %d to %d\n" % (primart_task_list.from_where, primart_task_list.des))
                f.write("senior list left:\n")
                for senior_task_list in task_list.senior_task_list:
                    f.write("senior_task_list from: %d to %d\n" % (senior_task_list.from_where, senior_task_list.des))

            f.write("the select task list is:\n")
            for selected in self.start_has_selected:
                f.write("start selected task's id = %s:\n" % selected)
            for selected in self.des_has_selected:
                f.write("des selected task's id = %s:\n" % selected)
            f.write("self.priority_tasks len is %d:\n" % len(self.priority_tasks))

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
        self.start_bench_type = []
        """True为算法，False为手动"""
        self.mode = True

        self.crashControler = crashControl()

        self.t_car1 = [[0.75, 30], [6, 0.75], [10, 2]]
        self.t_car2 = [[10, 2], [10, 48], [0.5, 49]]

    def update(self):
        # ("请输入每一帧的地图信息：\n")
        self.outControl.putTime(self.sec_map_parse.time)
        self.sec_map_parse.getState()
        self.update_car_info()
        if self.mode:
            self.update_task_state()
            self.task_distribute()
            self.update_cars_state()
        else:
            self.hand_input_test()
        self.outControl.send()

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

        length = len(self.task_list_manager)
        if len(self.task_list_manager[length - 1].primary_task_list) < 4:
            t = TaskList()
            self.task_list_manager.append(t)

    def update_task_state(self):
        """
        更新任务状态
        :return:
        """
        self.update_task_list_manager()

        for task_list in self.task_list_manager:

            """通过id ， 查询每个任务当前是否有可以被执行的，如果起点的任务中有 == 0 或者剩余时间少于 50帧的时候，
                就视为可以被执行，因为后6个默认可以执行，因此只看前四个 高级任务"""
            for senior_task in task_list.senior_task_list:
                flag = False
                """通过task.from查询所有该种类的工作台中是否有可以执行的（== 0 or <= 50），有就加入队列中"""
                res_list = self.sec_map_parse.getBench_lasted_type_id(senior_task.from_where)
                for bench_state in res_list:
                    if 50 >= int(bench_state[1]) >= 0:
                        """检查重复"""
                        if not self.check_if_exist(bench_state[0]):
                            continue
                        """通过bench_id获得bench_location"""
                        x, y = self.sec_map_parse.getBench_id_loc(int(bench_state[0]))
                        tmp_task_1 = ready_task(senior_task.from_where, float(x), float(y), 0, bench_state[0])
                        tmp_task_2 = self.get_des_task(tmp_task_1, senior_task)
                        if tmp_task_2 is not None:
                            self.priority_tasks.append(tmp_task_1)
                            self.priority_tasks.append(tmp_task_2)
                            """去重"""
                            self.start_has_selected.append(tmp_task_1.bench_id)
                            self.start_bench_type.append(tmp_task_1.bench_type)
                            self.des_has_selected.append(tmp_task_2.bench_id)
                            flag = True
                            break
                if flag:
                    task_list.senior_task_list.remove(senior_task)

    def task_distribute(self):
        """
        如果优先处理队列priority_tasks里面有任务了，优先处理
        :return:
        """
        if len(self.priority_tasks) >= 2:
            for i in range(4):
                """第j辆车，如果不忙"""
                if not self.cars_busy_state[i]:
                    self.cars_task_list[i].append(self.priority_tasks[0])
                    self.priority_tasks.pop(0)
                    self.cars_task_list[i].append(self.priority_tasks[0])
                    self.priority_tasks.pop(0)
                    self.cars_busy_state[i] = True

        for i in range(4):
            if not self.cars_busy_state[i]:
                self.get_nearest_available_bench(self.cars[i])

    def update_car_info(self):
        for i in range(4):
            self.cars[i].getState(self.sec_map_parse.carState[i])

    def update_cars_state(self):
        #self.write_to_log()
        for c in self.cars:
            if len(self.cars_task_list[c.carid]) == 0:
                continue
            c_task = self.cars_task_list[c.carid][0]
            sub_x = c_task.x - c.x
            sub_y = c_task.y - c.y
            dx = int(abs(sub_x)) * 2
            dy = int(abs(sub_y)) * 2
            distance = self.sec_map_parse.map[dx][dy]
            if self.cars_busy_state[c.carid]:
                c_task = self.cars_task_list[c.carid][0]
                if self.sec_map_parse.time == 5000:
                    self.f.close()
                speed, wspeed, lasttime = c.destination(c_task.x, c_task.y, distance)
                self.crashControler.putCarState(self.sec_map_parse.carState[:, 4:10])
                self.crashControler.putSportState(c.carid, speed, wspeed)
                self.crashControler.judgeAndModify()
                speed, wspeed = self.crashControler.getSportStateAter(c.carid)  # 返回第零个车的修改
                self.outControl.putForward(c.carid, speed)
                self.outControl.putRotate(c.carid, wspeed)
            """是否在目标点"""
            if (sub_x * sub_x + sub_y * sub_y) < 0.1:
                action = c_task.buy_or_sell
                if action == 0:
                    self.outControl.putBuy(c.carid)
                    self.cars_task_list[c.carid].pop(0)
                    if self.start_has_selected.count(c_task.bench_id) > 0:
                        self.start_has_selected.remove(c_task.bench_id)
                        self.start_bench_type.remove(c_task.bench_type)

                else:
                    self.outControl.putSell(c.carid)
                    self.cars_task_list[c.carid].pop(0)
                    if self.des_has_selected.count(c_task.bench_id) > 0:
                        self.des_has_selected.remove(c_task.bench_id)
                    self.cars_busy_state[c.carid] = False

            # self.outControl.putForward(c.carid, lasttime)
            # print("car %d des is x = %f y = %f" % (c.carid, self.cars_task_list[c.carid][0].x,
            # self.cars_task_list[c.carid][0].y))
            # print("car %d des is x = %f y = %f" % (c.carid, self.cars_task_list[c.carid][0].x,
            #    self.cars_task_list[c.carid][0].y))

    def get_des_task(self, tmp_task, task):
        tmp_task_2 = None
        des_list = self.sec_map_parse.getBench_closest_xy_type_id(tmp_task.x, tmp_task.y, task.des)
        for des in des_list:
            des_id = des[0]
            """获得对应卖的任务,找最近的，缺货的对应工作台"""
            if not self.sec_map_parse.getBench_id_goodnum_goodState(int(des_id), task.from_where):
                #
                if self.des_has_selected.count(des_id) > 0 and self.start_bench_type.count(tmp_task.bench_type) > 0:
                    continue
                des_x, des_y = self.sec_map_parse.getBench_id_loc(int(des_id))
                tmp_task_2 = ready_task(task.des, float(des_x), float(des_y), 1, des_id)
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
                self.start_has_selected.append(tmp_task_1.bench_id)
                self.start_bench_type.append(tmp_task_1.bench_type)
                self.des_has_selected.append(tmp_task_2.bench_id)
                task_list.primary_task_list.remove(choose)
                self.cars_task_list[c.carid].append(tmp_task_1)
                self.cars_task_list[c.carid].append(tmp_task_2)
                # print('append into car_task_list[%d] two tasks' % c.carid)
                self.cars_busy_state[c.carid] = True
                break
