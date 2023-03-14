import sys

class output():
    def __init__(self):
        self.forward=[]
        self.rotate=[]
        self.buy=[]
        self.sell=[]
        self.destroy=[]
    def getForward(self,id,speed):
        self.forward.append(["forward "+str(id)+" "+str(speed)])
        return
    
