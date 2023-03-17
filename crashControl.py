import numpy as np
"""
输入四个车的坐标，和当前控制信息，来判断下一帧是否碰撞，并返回不碰撞调整
matrix = np.random.rand(4, 10)
a=crashControl.crashControl()

a.putCarState(matrix[:,4:10])
for i in range(4):
    #调用destination获得两个速度
    speed=i
    wspeed=i
    a.putSportState(i,speed,wspeed)
#数据输入完了
a.judgeAndModify()

speed,wspeed=a.getSportStateAter(2)#返回第零个车的修改
print(speed,wspeed)
#再传给output
"""
class crashControl():
    def __init__(self):
        self.carState=None
        """ 角速度，线速度x,线速度y，朝向，坐标x 坐标y"""
        self.sportState=np.zeros((4,2))
        """ speed wspeed"""
        self.sportStateAfter=np.zeros((4,2))
    def putCarState(self,carState: np.ndarray):
        tmp=carState.copy()
        self.carState=tmp

    def putSportState(self,id,speed,wspeed):
        self.sportState[id][0]=speed
        self.sportState[id][1]=wspeed
    def getSportStateAter(self,id):
        return self.sportStateAfter[id][0],self.sportStateAfter[id][1]
    def judgeAndModify(self):
        self.sportStateAfter=self.sportState