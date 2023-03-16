import math
import sys
import car
import mapParse
import output
import secParse


class ready_task:
    def __init__(self, bench_type, x, y, buy_or_sell):
        self.bench_type = bench_type
        self.x = x
        self.y = y
        """0是买buy，1是卖sell"""
        self.buy_or_sell = buy_or_sell


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
        t0 = Task(7, None)
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
        self.cars = [car.car(i) for i in range(4)]
        self.task_list_manager = []
        self.sec_map_parse = None
        self.map_parse = None
        """默认从1，2，3开始的任务都是可以直接获取的，所以这个列表只存4，5，6，7开始的任务"""
        self.priority_tasks = []
        self.cars_busy_state = [False, False, False, False]
        self.cars_task_list = [[], [], [], []]
        self.outControl = output.output()

    def update(self):
        self.sec_map_parse.getState()
        self.update_car_info()
        self.update_task_state()
        self.task_distribute()
        self.update_cars_state()
        self.outControl.send()

    def get_map_info(self):
        self.map_parse = mapParse.mapParse()
        self.sec_map_parse = secParse.secParse(self.map_parse)

    def update_task_list_manager(self):
        if len(self.task_list_manager) == 0:
            t = TaskList()
            self.task_list_manager.append(t)

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
                就视为可以被执行，因为后6个默认可以执行，因此只看前四个"""
            for senior_task in task_list.senior_task_list:
                flag = False
                """通过task.from查询所有该种类的工作台中是否有可以执行的（== 0 or <= 50），有就加入队列中"""
                res_list = self.sec_map_parse.getBench_lasted_type_id(senior_task.from_where)
                for bench_state in res_list:
                    if 50 >= int(bench_state[1]) >= 0:
                        """通过bench_id获得bench_location"""
                        x, y = self.sec_map_parse.getBench_id_loc(bench_state[0])
                        tmp_task_1 = ready_task(senior_task.from_where, float(x), float(y), 0)
                        self.priority_tasks.append(tmp_task_1)
                        """获得对应卖的任务,找最近的，缺货的对应工作台"""
                        des_list = self.sec_map_parse.getBench_closest_xy_type_id(x, y, senior_task.des)
                        for des in des_list:
                            des_id = des[0]
                            if not self.sec_map_parse.getBench_id_goodnum_goodState(des_id, senior_task.from_where):
                                des_x, des_y = self.sec_map_parse.getBench_id_loc(des_id)
                                tmp_task_2 = ready_task(senior_task.des, float(des_x), float(des_y), 1)
                                self.priority_tasks.append(tmp_task_2)
                                break
                        flag = True
                        break
                if flag:
                    task_list.senior_task_list.remove(senior_task)

    def task_distribute(self):
        if len(self.priority_tasks) > 0:
            for i in range(len(self.priority_tasks)):
                for j in range(0, 4):
                    """第j辆车，如果不忙"""
                    if not self.cars_busy_state[j]:
                        self.cars_task_list[j].append(self.priority_tasks[i])
                        self.cars_task_list[j].append(self.priority_tasks[i + 1])
                        self.cars_busy_state[j] = True
                        i += 1
                        break

        for i in range(4):
            if not self.cars_busy_state[i]:
                self.get_nearest_available_bench(self.cars[i])

    def update_car_info(self):
        for i in range(4):
            self.cars[i].getState(self.sec_map_parse.carState[i])

    def update_cars_state(self):
        for c in self.cars:
            c_task = self.cars_task_list[c.carid][0]
            sub_x = c_task.x - c.x
            sub_y = c_task.y - c.y
            """是否在目标点"""
            if (sub_x * sub_x + sub_y * sub_y) < 0.16:
                action = c_task.buy_or_sell
                if action == 0:
                    self.outControl.putBuy(c.carid)
                    self.cars_task_list[c.carid].pop(0)
                else:
                    self.outControl.putSell(c.carid)
                    self.cars_task_list[c.carid].pop(0)
                    self.cars_busy_state[c.carid] = False
            if self.cars_busy_state[c.carid]:
                c_task = self.cars_task_list[c.carid][0]
                speed, wspped, lasttime = c.destination(c_task.x, c_task.y)
                self.outControl.putForward(c.carid, speed)

    def update_forward(self):
        """检测和目标点的距离，在一定范围外，加速，内，减速"""
        for c in self.cars:
            x = c.des_x - c.x
            y = c.des_y - c.y
            distance_to_des = x * x + y * y

    def update_toward(self):
        for c in self.cars:
            current_toward = self.sec_map_parse.getCar_id_toward(c.carid)
            target_toward = cul_car_target_toward(c)
            angle_need = (target_toward - float(current_toward)) % math.pi
            c.need_toward = angle_need
            sys.stdout.write('rotate %d %f\n' % (c.carid, angle_need))

    def get_des_task(self, x, y, task):
        tmp_task_2 = None
        des_list = self.sec_map_parse.getBench_closest_xy_type_id(x, y, task.des)
        for des in des_list:
            des_id = des[0]
            if not self.sec_map_parse.getBench_id_goodnum_goodState(int(des_id), task.from_where):
                des_x, des_y = self.sec_map_parse.getBench_id_loc(int(des_id))
                tmp_task_2 = ready_task(task.des, float(des_x), float(des_y), 1)
                return tmp_task_2

        return tmp_task_2

    def get_nearest_available_bench(self, c):
        """
        先获得车的位置，通过下标
        获得离小车最近的，可以拿货的工作台
        :return:
        """
        for task_list in self.task_list_manager:
            nearest = 100000.0
            choose = 0
            tmp_task_1 = ready_task(0, 0, 0, 0)
            for primary_task in task_list.primary_task_list:
                """
                获得最近的任务，通过小车坐标, 任务的类型 ，得到该任务中离小车最近的点，比较所有可以的任务，拿最近的那个
                """
                res_list = self.sec_map_parse.getBench_closest_xy_type_id(c.x, c.y, primary_task.from_where)
                if nearest > float(res_list[0][1]):
                    nearest = float(res_list[0][1])
                    choose = primary_task
                    tmp_task_1.x, tmp_task_1.y = self.sec_map_parse.getBench_id_loc(int(res_list[0][0]))
            if choose == 0:
                continue
            tmp_task_1.x = float(tmp_task_1.x)
            tmp_task_1.y = float(tmp_task_1.y)
            tmp_task_1.bench_type = choose.from_where
            tmp_task_2 = self.get_des_task(tmp_task_1.x, tmp_task_1.y, choose)
            if tmp_task_2 is None:
                continue
            else:
                task_list.primary_task_list.remove(choose)
                self.cars_task_list[c.carid].append(tmp_task_1)
                self.cars_task_list[c.carid].append(tmp_task_2)
                self.cars_busy_state[c.carid] = True
                break
