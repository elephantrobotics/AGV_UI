#!/usr/bin/env python3
#encoding=utf-8

import socket
import struct

from end import *
import test_auto_charing
import traceback

from pymycobot.mycobotsocket import MyCobotSocket

from pymycobot.mycobot import MyCobot
import time
import RPi.GPIO as GPIO
import threading


GPIO.setwarnings(False)
GPIO = GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)
GPIO.output(20, 1)
GPIO.output(21, 1)

mycobot_ip = '192.168.123.23'
mycobot_port = 9000

mc = MyCobotSocket(mycobot_ip, mycobot_port)
pump_times = 0


# 移动角度
move_angles = [
    [0, 0, 0, 0, 80, 0],  # init the point
    [-40.31, 2.02, -10.72, -0.08, 80, -54.84],  # point to grab
    [-70.31, 2.02, -10.72, -0.08, 80, -54.84]
]

# 移动坐标
move_coords = [
    [96.5, -101.9, 185.6, 155.25, 19.14, 75.88], # above the red bucket
    [180.9, -99.3, 184.6, 124.4, 30.9, 80.58], # above the green bucket
    [77.4, 122.1, 179.2, 151.66, 17.94, 178.24], # above the blue bucket
    [2.2, 128.5, 171.6, 163.27, 10.58, -147.25] # gray
]

#agv 车上角度
avg_angles= [
    [-2.54, 14.67, -177.36, 0.87, -88.24, -7.73],
    [-159, 20.3, -16.69, 1.84, 77.34, -54.75],
    [-2.72, -4.74, -168.66, 1.14, -96.76, -47.63],
    [-25.13, -5.53, -176.04, 1.23, -84.81, -38.4],
    [12.12, -23.64, -153.8, 1.49, -84.63, -36.12],
    [-3.77, -25.75, -153.1, 1.23, -84.9, -36.38],
    [-19.59, -27.07, -147.12, 2.46, -88.68, -36.38]
]

# place angles
agv_place_angles=[
    [-2.54, 14.67, -177.36, 0.87, -88.24, -7.73],
    [19.07, -16.52, -176.3, 0.43, -79.54, -39.9],
    [-27.94, -18.72, 179.64, 5.36, -70.4, -46.93],
    [-22.67, -23.29, -172.35, 1.14, -83.4, -39.72],
    [12.3, -39.19, -147.65, 2.19, -79.89, -39.72],
    [-5.27, -40.69, -146.6, 2.72, -82.0, -39.99],
    [-17.75, -41.74, -146.86, 0.87, -79.45, -39.9]
]

# down_angles
down_place_angles = [
    [29.44, -19.16, 21.35, 0.61, 33.48, -76.55],
    [-4.74, -20.56, 21.35, 0.26, 43.24, -76.72],
    [-43.33, 13.27, -20.83, 3.51, 53.7, -76.72]
]
server_ip = ''
server_port = '9003'

# 创建一个服务器套接字
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 绑定服务器地址和端口
server_socket.bind((server_ip, server_port))

# 开始监听客户端请求
server_socket.listen()

feed_place = True
pause_clicked = True

    
def move(x, y):
    global pump_times
    global move_angles
    global move_coords
    global avg_angles
    print('x, y',x,y)
    # send Angle to move mecharm 270
    mc.send_angles(move_angles[0], 50)
    time.sleep(2)

    #[x, y, 185.5, -157.73, 22.08, -140.19]
    # send coordinates to move mycobot
    if x <= 180:
        print(1)
        mc.send_coords([x, y, 150, -176.1, 2.4, -125.1], 30, 0) # usb :rx,ry,rz -173.3, -5.48, -57.9
        time.sleep(4)
        
        # mc.send_coords([x, y, 150, 179.87, -3.78, -62.75], 25, 0)
        # time.sleep(3)

        # mc.send_coords([x, y, 105, 179.87, -3.78, -62.75], 25, 0)
        mc.send_coords([x, y, 140, -176.1, 2.4, -125.1], 30, 0)
    else:
        if x > 188:
            x = 174
        else:
            x = x -20
        print(2)
        mc.send_coords([x, y, 175, -164.99, 11.33, -125.91], 30, 0) # [174.6, -3.5, 175.8, -164.99, 11.33, -125.91]
        time.sleep(4)
        
        # mc.send_coords([x, y, 150, 179.87, -3.78, -62.75], 25, 0)
        # time.sleep(3)

        # mc.send_coords([x, y, 105, 179.87, -3.78, -62.75], 25, 0)
        mc.send_coords([x, y, 148, -164.99, 11.33, -125.91], 30, 0)
    time.sleep(4)

    # open pump
    gpio_status(True)
    time.sleep(1.5)
    if pump_times < 6:
        pump_times += 1
    else:
        pump_times = 1

    tmp = []
    while True:
        if not tmp: 
            tmp = mc.get_angles()    
        else:
            break
    time.sleep(0.5)

    print('tmp:', tmp)
    mc.send_angles([tmp[0], 17.22, -32.51, tmp[3], 80, tmp[5]],40) # [18.8, -7.91, -54.49, -23.02, -0.79, -14.76]
    time.sleep(1)
    mc.send_angles([-70, 17.22, -32.51, tmp[3], 80, tmp[5]],40) # [18.8, -7.91, -54.49, -23.02, -0.79, -14.76]
    time.sleep(2.5)
    mc.send_angles([-70, 14.67, -177.36, 0.87, -88.24, -7.73], 40)
    time.sleep(3.5)
    mc.send_angles(avg_angles[0], 40)
    time.sleep(2.5)
    #temp_ang=avg_angles[pump_times][1]
    #avg_angles[pump_times][1] = -10
    #mc.send_angles(avg_angles[pump_times], 40)
    #time.sleep(2.5)
    #avg_angles[pump_times][1] = temp_ang
    print(pump_times)
    print(avg_angles[pump_times])
    if pump_times > 3:
        mc.send_angles([-4.92, -10.81, -151.43, 2.54, -80.15, -10.28],40)
        time.sleep(1.5)
    mc.send_angles(avg_angles[pump_times], 40)
    time.sleep(3)

    # close pump
    gpio_status(False)
    time.sleep(3)
    mc.send_angles([-70, 14.67, -177.36, 0.87, -88.24, -7.73], 40)
    time.sleep(1.5)

    mc.send_angles([-70, 17.22, -32.51, tmp[3], 97, tmp[5]],40) # [18.8, -7.91, -54.49, -23.02, -0.79, -14.76]
    time.sleep(3.5)
    mc.send_angles(move_angles[1], 50)
    time.sleep(3)
        
    
def place():
    pump_times=7
    for i in range(1,pump_times):  
        mc.send_angles(move_angles[1],40)
        time.sleep(3)
        mc.send_angles(move_angles[2],40)
        time.sleep(1)
        mc.send_angles([-70, 14.67, -177.36, 0.87, -88.24, -7.73], 40)
        time.sleep(3.5)
        mc.send_angles([avg_angles[i][0], 14.67, -177.36, 0.87, -88.24, -7.73], 40)
        time.sleep(1.5)
        if i > 3:
            mc.send_angles([avg_angles[i][0], -10.81, -151.43, 2.54, -80.15, -10.28],40)
            time.sleep(1.5)
        mc.send_angles(agv_place_angles[i],40)
        time.sleep(3)
        # open pump
        gpio_status(True)
        time.sleep(2.5)
        ang = agv_place_angles[i][1] + 30
        mc.send_angle(2,ang,40)
        time.sleep(1)
        mc.send_angles([-70, 14.67, -177.36, 0.87, -88.24, -7.73], 40)
        time.sleep(1.5)
        mc.send_angles(move_angles[2],40)
        time.sleep(3.5)
        ang = move_angles[1][2]-30
        mc.send_angle(2,ang,40)
        time.sleep(1.5)
        if i < 3:
            mc.send_angles(down_place_angles[0],40)
        elif i < 5:
            mc.send_angles(down_place_angles[1],40)
        elif i < 7:
            mc.send_angles(down_place_angles[2],40)
        time.sleep(3)
        # close pump
        gpio_status(False)

def gpio_status(flag):
    if flag:
        GPIO.output(20, 0)
        GPIO.output(21, 0)
    else:
        # GPIO.output(20, 1)
        GPIO.output(21, 1)
        
def stop_wait(t):
    """Refresh the software screen in real time during the robot movement"""
    if t * 10 <= 1:
        t = 1
    else:
        t = int(t * 10)

    for i in range(1, t + 1):
        time.sleep(0.1)


def down_position():
    try:
        set_robot_pose = SetRobotPose()
        set_robot_pose.set_pose()
        map_navigation = MapNavigation1()
        map_navigation.navigate()
        map_navigation = MapNavigation2()
        map_navigation.navigate()
        test_auto_charing.init()
        while pause_clicked:
            stop_wait(0.2)

        test_auto_charing.main()
        while pause_clicked:
            stop_wait(0.2)
        place()

        
    except Exception as e:
        print(e)
        e = traceback.format_exc()
        with open('./error.log', 'a+') as f:
            f.write(e)

def feed_position():
    global feed_place
    try:
        map_navigation = MapNavigation3()
        map_navigation.navigate()
        map_navigation = MapNavigation4()
        map_navigation.navigate()
        test_auto_charing.init()
   
        while pause_clicked:
            stop_wait(0.2)
        test_auto_charing.main()
        t = time.time()
        while feed_place:
            responsed()
        while pause_clicked:
            stop_wait(0.2)
        set_robot_pose = SetRobotPose()
        set_robot_pose.set_pose()
    except Exception as e:
        print(e)
        e = traceback.format_exc()
        with open('./error.log', 'a+') as f:
            f.write(e)
            
def responsed():
    global feed_place
    t = time.time()
    while True:
        x = None
        y = None
        # 等待客户端连接
        client_socket, client_address = server_socket.accept()
        print("Connection from {} has been established.".format(client_address))

        # 接收来自客户端的数据
        data = client_socket.recv(1024)
        x, y = struct.unpack('ff', data)
        # print(f"Received data from client: {data.decode()}")
        print("Received data from client: {},{}".format(x, y))
        # 向客户端发送响应
        response = "Data received successfully!"
        client_socket.sendall(response.encode())

        if x and y:
            t = time.time()
            feed_place = True
            move(x, y)
            if not feed_place:
                break
        else:
            if time.time() - t > 10:
                feed_place = False
                break
        response = "Running END!"
        client_socket.sendall(response.encode())
        # 关闭客户端套接字
        client_socket.close()


def run():
    global pause_clicked

    while True:
        # 等待客户端连接
        client_socket, client_address = server_socket.accept()
        print("Connection from {} has been established.".format(client_address))

        # 接收来自客户端的数据
        data = client_socket.recv(1024)
        x, y = struct.unpack('ff', data)
        # print(f"Received data from client: {data.decode()}")
        print("Received data from client: {}, {}".format(x, y))
        # 向客户端发送响应
    

        # 关闭客户端套接字
        client_socket.close()
        if x == 'down':
            # down_position()
            pass
        elif x == 'feed':
            # feed_position()
            pass
        elif x == 'start':
            pause_clicked = False
            # down_position()
        elif x == 'pause':
            pause_clicked = True
            
        else:
            pass
            
        x = None
        y = None
        response = "Running end!"
        client_socket.sendall(response.encode())
        
def myagv_loop_run():
    try:
        for i in range(3):
            down_position()
            feed_position()
    except Exception as e:
        print(e)
        
        
if __name__ == '__main__':
    t = threading.Thread(target=run)
    t.daemon = True
    t.start()
    
    t1 = threading.Thread(target=myagv_loop_run)
    t1.daemon = True
    t1.start()
    