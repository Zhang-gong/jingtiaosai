import mapParse
import time
t=time.time()
a=mapParse.mapParse()
a.getMap()

a.show()

print(time.time()-t)
