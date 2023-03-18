import numpy as np
import matplotlib.pyplot as plt
# 初始条件
v0 = 6
dt = 0.02
t = np.arange(0, 50 * dt, dt)
x = np.zeros_like(t)
y = np.zeros_like(t)
vx = np.zeros_like(t)
vy = np.zeros_like(t)
vx[0] = 0
vy[0] = v0
# 计算运动轨迹
for i in range(1, len(t)):
    omega = np.pi / 50 * t[i-1]
    ax = np.pi / 50 * vy[i-1]
    ay = -np.pi / 50 * vx[i-1]
    vx[i] = vx[i-1] + ax * dt
    vy[i] = vy[i-1] + ay * dt
    x[i] = x[i-1] + vx[i] * dt
    y[i] = y[i-1] + vy[i] * dt
# 绘制轨迹图
    plt.plot(x, y)
    plt.xlabel('x')
    plt.ylabel('y')
    plt.show()

