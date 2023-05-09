# -*- coding: utf-8 -*-
import socket
import struct

# 创建一个服务器套接字
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 绑定服务器地址和端口
server_socket.bind(('192.168.11.164', 8000))

# 开始监听客户端请求
server_socket.listen()

while True:
    # 等待客户端连接
    client_socket, client_address = server_socket.accept()
    print(f"Connection from {client_address} has been established.")

    # 接收来自客户端的数据
    data = client_socket.recv(1024)
    x, y = struct.unpack('ff', data)
    # print(f"Received data from client: {data.decode()}")
    print(f"Received data from client: {x},{y}")
    # 向客户端发送响应
    response = "Data received successfully!"
    client_socket.sendall(response.encode())

    # 关闭客户端套接字
    client_socket.close()
    
    
def move(self, x, y, color):
    print('x, y',x,y)



        # send Angle to move mecharm 270
        self.mc.send_angles(self.move_angles[0], 50)
        time.sleep(2)

        #[x, y, 185.5, -157.73, 22.08, -140.19]
        # send coordinates to move mycobot
        if x <= 180:
            print(1)
            self.mc.send_coords([x, y, 150, -176.1, 2.4, -125.1], 30, 0) # usb :rx,ry,rz -173.3, -5.48, -57.9
            time.sleep(4)

            # self.mc.send_coords([x, y, 150, 179.87, -3.78, -62.75], 25, 0)
            # time.sleep(3)

            # self.mc.send_coords([x, y, 105, 179.87, -3.78, -62.75], 25, 0)
            self.mc.send_coords([x, y, 140, -176.1, 2.4, -125.1], 30, 0)
        else:
            if x > 188:
                x = 174
            else:
                x = x -20
            print(2)
            self.mc.send_coords([x, y, 175, -164.99, 11.33, -125.91], 30, 0) # [174.6, -3.5, 175.8, -164.99, 11.33, -125.91]
            time.sleep(4)

            # self.mc.send_coords([x, y, 150, 179.87, -3.78, -62.75], 25, 0)
            # time.sleep(3)

            # self.mc.send_coords([x, y, 105, 179.87, -3.78, -62.75], 25, 0)
            self.mc.send_coords([x, y, 148, -164.99, 11.33, -125.91], 30, 0)
        time.sleep(4)

        # open pump
        if "dev" in self.robot_m5 or "dev" in self.robot_wio:
            self.pump_on()
        elif "dev" in self.robot_raspi or "dev" in self.robot_jes:
            self.gpio_status(True)
        time.sleep(1.5)
        if self.pump_times < 6:
            self.pump_times += 1
        else:
            self.pump_times = 1

        tmp = []
        while True:
            if not tmp:
                tmp = self.mc.get_angles()
            else:
                break
        time.sleep(0.5)

        print('tmp:', tmp)
        self.mc.send_angles([tmp[0], 17.22, -32.51, tmp[3], 80, tmp[5]],40) # [18.8, -7.91, -54.49, -23.02, -0.79, -14.76]
        time.sleep(1)
        self.mc.send_angles([-70, 17.22, -32.51, tmp[3], 80, tmp[5]],40) # [18.8, -7.91, -54.49, -23.02, -0.79, -14.76]
        time.sleep(2.5)
        self.mc.send_angles([-70, 14.67, -177.36, 0.87, -88.24, -7.73], 40)
        time.sleep(3.5)
        self.mc.send_angles(self.avg_angles[0], 40)
        time.sleep(2.5)
        #temp_ang=self.avg_angles[self.pump_times][1]
        #self.avg_angles[self.pump_times][1] = -10
        #self.mc.send_angles(self.avg_angles[self.pump_times], 40)
        #time.sleep(2.5)
        #self.avg_angles[self.pump_times][1] = temp_ang
        print(self.pump_times)
        print(self.avg_angles[self.pump_times])
        if self.pump_times > 3:
            self.mc.send_angles([-4.92, -10.81, -151.43, 2.54, -80.15, -10.28],40)
            time.sleep(1.5)
        self.mc.send_angles(self.avg_angles[self.pump_times], 40)
        time.sleep(3)

        # close pump
        if "dev" in self.robot_m5 or "dev" in self.robot_wio:
            self.pump_off()
        elif "dev" in self.robot_raspi or "dev" in self.robot_jes:
            self.gpio_status(False)
        time.sleep(3)
        self.mc.send_angles([-70, 14.67, -177.36, 0.87, -88.24, -7.73], 40)
        time.sleep(1.5)

        self.mc.send_angles([-70, 17.22, -32.51, tmp[3], 97, tmp[5]],40) # [18.8, -7.91, -54.49, -23.02, -0.79, -14.76]
        time.sleep(3.5)
        self.mc.send_angles(self.move_angles[1], 50)
        time.sleep(3)
        
    
def place(self):
    self.pump_times=7
    for i in range(1,self.pump_times):  
        self.mc.send_angles(self.move_angles[1],40)
        time.sleep(3)
        self.mc.send_angles(self.move_angles[2],40)
        time.sleep(1)
        self.mc.send_angles([-70, 14.67, -177.36, 0.87, -88.24, -7.73], 40)
        time.sleep(3.5)
        self.mc.send_angles([self.avg_angles[i][0], 14.67, -177.36, 0.87, -88.24, -7.73], 40)
        time.sleep(1.5)
        if i > 3:
            self.mc.send_angles([self.avg_angles[i][0], -10.81, -151.43, 2.54, -80.15, -10.28],40)
            time.sleep(1.5)
        self.mc.send_angles(self.agv_place_angles[i],40)
        time.sleep(3)
        # open pump
        if "dev" in self.robot_m5 or "dev" in self.robot_wio:
            self.pump_on()
        elif "dev" in self.robot_raspi or "dev" in self.robot_jes:
            self.gpio_status(True)
        time.sleep(2.5)
        ang = self.agv_place_angles[i][1] + 30
        self.mc.send_angle(2,ang,40)
        time.sleep(1)
        self.mc.send_angles([-70, 14.67, -177.36, 0.87, -88.24, -7.73], 40)
        time.sleep(1.5)
        self.mc.send_angles(self.move_angles[2],40)
        time.sleep(3.5)
        ang = self.move_angles[1][2]-30
        self.mc.send_angle(2,ang,40)
        time.sleep(1.5)
        if i < 3:
            self.mc.send_angles(self.down_place_angles[0],40)
        elif i < 5:
            self.mc.send_angles(self.down_place_angles[1],40)
        elif i < 7:
            self.mc.send_angles(self.down_place_angles[2],40)
        time.sleep(3)
        # close pump
        if "dev" in self.robot_m5 or "dev" in self.robot_wio:
            self.pump_off()
        elif "dev" in self.robot_raspi or "dev" in self.robot_jes:
            self.gpio_status(False)
        time.sleep(3)
    
