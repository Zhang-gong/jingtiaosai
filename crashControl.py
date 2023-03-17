import numpy as np
"""
输入四个车的坐标，和当前控制信息，来判断下一帧是否碰撞，并返回不碰撞调整
matrix = np.random.rand(4, 10)
a=crashControl.crashControl()

a.putCarState(matrix[4:10])
for i in range(4):
    #调用destination获得两个速度
    speed=i
    wspeed=i
    a.putSportState(i,speed,wspeed)
#数据输入完了
a.judgeAndModify()

speed,wspeed=a.getSportStateAter(2)#返回第2个车的修改
print(speed,wspeed)
#再传给output
"""
class crashControl():
    def __init__(self):

        self.nFrame=3                                       #预判帧数
        self.threshold2others=(0.53+self.nFrame*6/50)*2*1.414                #小车中心dx+dy超过这个值被判定为间隔很远
        self.threshold2crash=0.53*2                                             #判断相撞临界
        self.xmax=50
        self.xmin=0
        self.ymax=50
        self.ymin=0
        self.iscrash=False

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
        #主要
        self.sportStateAfter=self.sportState
        self.iscrash=False

        self.jugde2wall()
        self.judge2others()
        #修改完
        for i in range(4):
            self.putSportState(i,self.sportStateAfter[i][0],self.sportStateAfter[i][1])
        if self.iscrash:
            self.judgeAndModify()
    def judge2wall(self):
        self.nextloc=np.zeros((4,2))
        for i in range(4):
            #线速度带符号的
            self.nextloc[i][0]=self.carState[i][4]+self.threshold2zero(abs(self.carState[i][1]))
            self.nextloc[i][1] =self.carState[i][5] + self.threshold2zero(abs(self.carState[i][2]))
            if self.nextloc[i][0]>50 or self.nextloc[i][0]<0 or self.nextloc[i][1]>50 or self.nextloc[i][1]<0:
            #出界,线速度0
                self.sportStateAfter[i][0]=0
                self.iscrash=True
    def judge2others(self):
        list=[]
        for i in range(4):
            for j in range(i+1,4):
                if abs(self.carState[i][4]-self.carState[j][4])+abs(self.carState[i][5]-self.carState[j][5]) <self.threshold2others:
                    list.append([i,j])
        #(i与j存在碰撞风险)
        #如果方向差绝对值小于pi/2就一个停止，如果方向差值大于则都右转pi且速度为原来2/3
        for i,j in list:
            if abs(self.nextloc[i][0]-self.nextloc[j][0])+abs(self.nextloc[i][1]-self.nextloc[j][1]) <self.threshold2crash:
                self.iscrash = True
                if abs(self.carState[i][3]-self.carState[i][3])<=np.pi/3*2:
                    if self.sportStateAfter[j][0]!=0:
                        self.sportStateAfter[i][0] = 0
                if abs(self.carState[i][3]-self.carState[i][3])>np.pi/3*2:
                    self.sportStateAfter[j][1] =-np.pi
                    self.sportStateAfter[j][0] = self.sportState[j][0]/3*2
                    self.sportStateAfter[i][1] = -np.pi
                    self.sportStateAfter[i][0] = self.sportState[i][0] / 3 * 2


    def threshold2zero(self,v0):
        return v0*self.nFrame-np.sign(v0)*0.5*self.nFrame*self.nFrame # 撞墙临界值