import math
import sys
import car
import mapParse
import secParse

"""
需要解决的问题是：
现在有一个100*100的地图作为输入，地图中有<=50个工作台，4量小车，每个工作台处在不同的位置，小车的移动需要时间
每个工作台具备生产不同产品的功能
每种产品需要购买，并且都可以出售
有的产品生产不需要原料，有的产品需要其他产品作为原料
设计一个算法使得在一定时间内，能够赚取最大利润

一开始的地图数据只能获得工作台和小车的坐标

第一帧的地图信息才会获得小车的朝向，   每秒50帧，         一共9000帧180秒，3分钟
小车要前往目的地，需要 旋转 + 平移

获得小车坐标，判断它是否在忙
    不忙-分配任务 ：
        获得小车当前的位置 
        查看当前哪些任务可以领取——就算当前还没生产好，要加上移动过去的时间（估计），优先拿最贵的7，6，5，4，3，2，1
    忙-
        此时肯定是有目的地的状态（在领取任务的时候分配好了destination），计算和当前目的地的角度差值和距离，适当距离减速，适当距离之外加速，
        角度有差的话（车朝向和 车坐标和目的地向量 的单位化向量 乘积）就要增加自身角速度
        
调度器运行流程：
一开始，通过小车坐标，获取当前在生产的，工作台坐标，找到一个最近的，去领取
领取到了之后，找到最近的，缺该产品的目的地，运输
运输到了之后判断该工作台是否还需要其他产品，找到缺失的最近的产品工作台，去领取
领取到之后，返回工作台
"""


class ready_task:
    def __init__(self, x, y, start):
        self.x = x
        self.y = y
        self.start = start


class Task:
    def __init__(self, from_where, des):
        self.from_where = from_where
        self.des = des
        if self.des == 4 or self.des == 5 or self.des == 6:
            self.can_take = True
        else:
            self.can_take = False


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


"""

"""


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
        self.ready_tasks = []

    def get_map_info(self):
        print("请输入初始地图：\n")
        self.map_parse = mapParse.mapParse()
        self.sec_map_parse = secParse.secParse(self.map_parse)
        pass

    def update_task_state(self):
        """
        更新任务状态
        :return:
        """
        if len(self.task_list_manager) == 0:
            t = TaskList()
            self.task_list_manager.append(t)

        for task_list in self.task_list_manager:

            """通过id ， 查询每个任务当前是否有可以被执行的，如果起点的任务中有 == 0 或者剩余时间少于 50帧的时候，
                就视为可以被执行，因为后6个默认可以执行，因此只看前四个"""
            for senior_task in task_list.senior_task_list:
                flag = False
                """通过task.from查询所有该种类的工作台中是否有可以执行的（== 0 or <= 50），有就加入队列中"""
                res_list = self.sec_map_parse.getBench_lasted_type_id(senior_task.from_where)
                for bench_state in res_list:
                    if bench_state[1] == 0:
                        x, y = self.sec_map_parse.getBench_id_loc(bench_state[0])
                        tmp_task = ready_task(x, y, senior_task.from_where)
                        self.ready_tasks.append(tmp_task)
                if flag:
                    task_list.remove(senior_task)

    def update(self):
        print("请输入每一帧的地图信息：\n")
        self.sec_map_parse.getState()
        self.update_task_state()
        self.update_cars_state()

    def update_cars_state(self):
        for c in self.cars:
            """如果c不忙"""
            if not c.is_busy:
                self.get_nearest_available_bench(c)

        self.update_toward()
        self.update_forward()

    def update_forward(self):
        """检测和目标点的距离，在一定范围外，加速，内，减速"""
        for c in self.cars:
            x = c.des_x - c.x
            y = c.des_y - c.y
            distance_to_des = x*x + y*y


    def update_toward(self):
        for c in self.cars:
            current_toward = self.sec_map_parse.getCar_id_toward(c.carid)
            target_toward = cul_car_target_toward(c)
            angle_need = (target_toward - float(current_toward)) % math.pi
            c.need_toward = angle_need
            sys.stdout.write('rotate %d %f\n' % (c.carid, angle_need))

    def get_nearest_available_bench(self, c):
        """
        先获得车的位置，通过下标
        获得离小车最近的，可以拿货的工作台
        :return:
        """
        c.x, c.y = self.sec_map_parse.getCar_id_loc(c.carid)
        print(c.x + " " + c.y)
        c.x = float(c.x)
        c.y = float(c.y)
        if len(self.ready_tasks) > 0:
            tmp_des = self.ready_tasks[0]
            c.des_x, c.des_y = tmp_des.x, tmp_des.y
            c.is_busy = True
            return

        for task_list in self.task_list_manager:
            nearest = 100000.0
            choose = 0
            for primary_task in task_list.primary_task_list:
                """
                获得最近的任务，通过小车坐标, 任务的类型 ，得到该任务中离小车最近的点，比较所有可以的任务，拿最近的那个
                """
                res_list = self.sec_map_parse.getBench_closest_xy_type_id(c.x, c.y, primary_task.from_where)
                print("primary_task from : " + str(primary_task.from_where) + " " + res_list[0][1])
                if nearest > float(res_list[0][1]):
                    nearest = float(res_list[0][1])
                    choose = primary_task
                    c.des_x, c.des_y = self.sec_map_parse.getBench_id_loc(int(res_list[0][0]))
                    c.des_x = float(c.des_x)
                    c.des_y = float(c.des_y)
            task_list.primary_task_list.remove(choose)
            print("choose :" + str(choose.from_where))
            c.is_busy = True


sch = Scheduler()
sch.get_map_info()
sch.update()

for s in sch.cars:
    print(s.carid)
tl2 = TaskList()
for a in tl2.senior_task_list:
    print(a.can_take)
