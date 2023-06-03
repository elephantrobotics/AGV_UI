from time import sleep
from pymycobot.mycobot import MyCobot
from pymycobot.mycobotsocket import MyCobotSocket

ip = ''
port = 9000

# mc = MyCobotSocket(ip, port)
# mc.connect()

mc = MyCobot('COM3',115200)

pick_coords = [
    [-108.28, 26.19, 1.66, 2.9, 65.21, -18.45],
    [-74.79, 18.1, 16.08, 1.93, 52.73, 17.22],
    [-103.09, 38.14, -18.54, 1.31, 57.83, -16.69],
    [-78.92, 38.4, -20.83, -0.26, 60.11, 11.86]
]

pick_top = [
    [-109.59, -14.5, 12.83, 1.58, 73.91, 2.1],
    [-77.16, -2.28, 12.48, 4.3, 65.47, 0.35],
    [-107.22, 21.26, -16.34, 3.07, 68.64, -13.0],
    [-83.4, 15.99, -15.9, 0.35, 70.31, 10.98]
]

place_init = [85.42, -43.68, 21.26, -2.54, 34.54, 0]

place_coords = [
    [50.8, -12.3, 20.3, 0.26, 43.76, 0],
    [89.38, -16.87, 21.26, -1.23, 62.13, 0],
    [124.89, -9.22, 22.23, -0.26, 39.11, 0]
]


def pick():
    mc.send_angles([0, 0, 0, 0, 0, 0], 50)
    sleep(3)
    for i in range(4):
        mc.send_angles(pick_top[i], 40)
        sleep(4)
        mc.set_gripper_value(50, 30)
        sleep(1)
        mc.send_angles(pick_coords[i], 20)
        sleep(3)
        mc.set_gripper_value(0, 30)
        sleep(1)
        mc.send_angles(pick_top[i], 40)
        sleep(3)
        mc.send_angles(place_init, 40)
        sleep(4)
        if i == 3:
            mc.send_angles(place_coords[0], 20)
        else:
            mc.send_angles(place_coords[i], 20)
        sleep(3)
        mc.set_gripper_value(50, 30)
        sleep(1)
        mc.send_angles([0, 0, 0, 0, 0, 0], 50)
        sleep(3)
pick()