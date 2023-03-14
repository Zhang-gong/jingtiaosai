import sys

class output():
    def __init__(self):
        self.time=0
        self.forward=[]
        self.rotate=[]
        self.buy=[]
        self.sell=[]
        self.destroy=[]
    def getTime(self,time):
        self.time=time
    def getForward(self,id,speed):
        self.forward.append("forward "+str(id)+" "+str(speed)+"\n")
    def getRotate(self,id,speed):
        self.rotate.append("rotate "+str(id)+" "+str(speed)+"\n")
    def getBuy(self,id):
        self.buy.append("buy "+str(id)+"\n")

    def getSell(self, id):
        self.sell.append("sell " + str(id) + "\n")

    def getDestroy(self, id):
        self.destroy.append("destroy " + str(id) + "\n")
    def send(self):
        sys.stdout.write(str(self.time)+"\n")
        for i in self.forward:
            sys.stdout.write(i)
        for i in self.rotate:
            sys.stdout.write(i)
        for i in self.buy:
            sys.stdout.write(i)
        for i in self.sell:
            sys.stdout.write(i)
        for i in self.destroy:
            sys.stdout.write(i)
        sys.stdout.write("OK\n")
        sys.stdout.flush()
