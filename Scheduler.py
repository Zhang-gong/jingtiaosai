import math
import sys
import car
import mapParse
import output
import secParse


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
    def __init__(self):
        self.f = open("./out.txt", "w")

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
        self.has_selected = []
        """True为算法，False为手动"""
        self.mode = True

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
        tmp_task_0 = ready_task(bench_type=0, x=5, y=5, buy_or_sell=0, bench_id=0)
        tmp_task_1 = ready_task(bench_type=0, x=10, y=10, buy_or_sell=1, bench_id=0)
        tmp_task_2 = ready_task(bench_type=0, x=15, y=15, buy_or_sell=0, bench_id=0)
        tmp_task_3 = ready_task(bench_type=0, x=20, y=20, buy_or_sell=1, bench_id=0)
        tmp_task_4 = ready_task(bench_type=0, x=25, y=25, buy_or_sell=0, bench_id=0)
        tmp_task_5 = ready_task(bench_type=0, x=35, y=35, buy_or_sell=1, bench_id=0)

        pass

    def get_map_info(self):
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
            t2 = TaskList()
            self.task_list_manager.append(t2)

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
                        tmp_task_1 = ready_task(senior_task.from_where, float(x), float(y), 0, int(bench_state[0]))
                        tmp_task_2 = self.get_des_task(tmp_task_1.x, tmp_task_1.x, senior_task)
                        if tmp_task_2 is not None:
                            self.priority_tasks.append(tmp_task_1)
                            self.priority_tasks.append(tmp_task_2)
                            """去重"""
                            self.has_selected.append((tmp_task_1.x, tmp_task_1.y))
                            flag = True
                            break
                if flag:
                    task_list.senior_task_list.remove(senior_task)

    def task_distribute(self):
        """
        如果优先处理队列priority_tasks里面有任务了，优先处理
        :return:
        """
        if len(self.priority_tasks) > 0:
            for i in range(4):
                """第j辆车，如果不忙"""
                if not self.cars_busy_state[i]:
                    self.cars_task_list[i].append(self.priority_tasks[0])
                    self.priority_tasks.pop(0)
                    self.cars_task_list[i].append(self.priority_tasks[0])
                    self.priority_tasks.pop(0)

        for i in range(4):
            if not self.cars_busy_state[i]:
                self.get_nearest_available_bench(self.cars[i])

    def update_car_info(self):
        for i in range(4):
            self.cars[i].getState(self.sec_map_parse.carState[i])

    def update_cars_state(self):
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
                # c_task = self.cars_task_list[c.carid][0]
                speed, wspeed, lasttime = c.destination(c_task.x, c_task.y, distance)
                self.outControl.putForward(c.carid, speed)
                self.outControl.putRotate(c.carid, wspeed)
            """是否在目标点"""
            if (sub_x * sub_x + sub_y * sub_y) < 0.16:
                # target_id = self.cars_task_list[c.carid][0].bench_id
                # if int(c.benchid) == int(target_id):
                if self.has_selected.count((float(c_task.x), float(c_task.y))) != 0:
                    self.has_selected.remove((float(c_task.x), float(c_task.y)))
                action = c_task.buy_or_sell
                if action == 0:
                    self.outControl.putBuy(c.carid)
                    self.cars_task_list[c.carid].pop(0)

                else:
                    self.outControl.putSell(c.carid)
                    self.cars_task_list[c.carid].pop(0)
                    self.cars_busy_state[c.carid] = False


            # self.outControl.putForward(c.carid, lasttime)
            # print("car %d des is x = %f y = %f" % (c.carid, self.cars_task_list[c.carid][0].x,
            # self.cars_task_list[c.carid][0].y))
            # print("car %d des is x = %f y = %f" % (c.carid, self.cars_task_list[c.carid][0].x,
            #    self.cars_task_list[c.carid][0].y))

    def get_des_task(self, x, y, task):
        tmp_task_2 = None
        des_list = self.sec_map_parse.getBench_closest_xy_type_id(x, y, task.des)
        for des in des_list:
            des_id = des[0]
            """获得对应卖的任务,找最近的，缺货的对应工作台"""
            if not self.sec_map_parse.getBench_id_goodnum_goodState(int(des_id), task.from_where):
                des_x, des_y = self.sec_map_parse.getBench_id_loc(int(des_id))
                tmp_task_2 = ready_task(task.des, float(des_x), float(des_y), 1, int(des_id))
                return tmp_task_2

        return tmp_task_2

    def check_if_exist(self, bench_id):
        x, y = self.sec_map_parse.getBench_id_loc(int(bench_id))
        if self.has_selected.count((float(x), float(y))) == 0:
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
            if choose == 0:
                continue
            tmp_task_1.x = float(tmp_task_1.x)
            tmp_task_1.y = float(tmp_task_1.y)
            tmp_task_1.bench_type = choose.from_where
            # print("choose :" + str(choose.from_where))
            tmp_task_2 = self.get_des_task(tmp_task_1.x, tmp_task_1.y, choose)
            if tmp_task_2 is None:
                # print("Error,can't find next task, push_back task_1")
                continue
            else:
                self.has_selected.append((tmp_task_1.x, tmp_task_1.y))
                task_list.primary_task_list.remove(choose)
                self.cars_task_list[c.carid].append(tmp_task_1)
                self.cars_task_list[c.carid].append(tmp_task_2)
                # print('append into car_task_list[%d] two tasks' % c.carid)
                self.cars_busy_state[c.carid] = True
                break
