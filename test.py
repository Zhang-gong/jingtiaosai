import mapParse
import time
import secParse
import numpy as np

a = mapParse.mapParse()
b = secParse.secParse(a)
b.getState()

print(b.getCar_id_wspeed(0))
print(b.getBench_closest_xy_type_id(25, 42, -1))
print(b.getBench_closest_xy_type_id(25, 42, 6))
print(b.getBench_lasted_type_id(6))
print(b.getBench_lasted_type_id(-1))
print(b.getBench_id_goodnum_goodState(3, 4))
print(b.getBench_id_goodState(3))
print(b.getCar_closest_xy_id(15, 36.7))
print(b.getCar_closest_xy_id(46.25, 42.25))

# a=secParse.secParse()
# print(a.mapDistance)
# a.getState()
# print(type(a.getCar_id_type(1)))
#


"""
t=time.time()

print(a.getBench_id_type(3))
print(a.getBench_id_loc(3))
print(a.getBench_id_last(3))
print(a.getBench_id_goodState(3))
print(a.getBench_id_outState(3))

print(a.getCar_id_benchid(0))
print(a.getCar_id_type(0))
print(a.getCar_id_tf(0))
print(a.getCar_id_cf(0))
print(a.getCar_id_wspeed(0))
print(a.getCar_id_speed(0))
print(a.getCar_id_toward(0))
print(a.getCar_id_loc(0))

"""
