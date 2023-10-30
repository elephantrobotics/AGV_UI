#!/usr/bin/env python3
# encoding:utf-8
import os
import socket
import struct
import sys
import threading
import fcntl
import time
import json
import subprocess
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import pyqtSlot, Qt, QPoint,pyqtSignal
from PyQt5.QtGui import QPixmap, QEnterEvent
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QMessageBox

from libraries.pyqtfile.INagv_UI import Ui_AGV_UI as AGV_Window
from netifaces import interfaces, ifaddresses, AF_INET


from scripts.agv_socket_server import MapNavigation
import scripts.agv_socket_server as socket_server


if os.name == "posix":
    import RPi.GPIO as GPIO



class AGV_APP(AGV_Window, QMainWindow, QWidget):

    data_recieve=pyqtSignal(str)
    data_point1=pyqtSignal(list)
    data_point2=pyqtSignal(list)

    def __init__(self):
        super(AGV_APP, self).__init__()
        super(AGV_APP, self).__init__()
        self.setupUi(self)
        self._init_main_window()
        self._initDrag()  # Set the mouse tracking judgment trigger default value
        self.setMouseTracking(True)  # Set widget mouse tracking
        self.widget.installEventFilter(self)  # Initialize event filter
        self.move(350, 10)
        self._init_variable()
        self._init_status()
        self._close_max_min_icon()
        self.min_btn.clicked.connect(self.min_clicked)  # minimize
        self.max_btn.clicked.connect(self.max_clicked)
        self.close_btn.clicked.connect(self.close_clicked)  # close
        self.language_btn.clicked.connect(self.set_language)
        self.agv_connect_btn.clicked.connect(self.open_socket)
        self.save_point.clicked.connect(self.save_points)

        self.pushButton.clicked.connect(self.point_obtain)
        # self._init_point_info()
        self.data_recieve.connect(self.socket_data)
        self.data_point1.connect(self.set_points1)
        self.data_point2.connect(self.set_points2)

        self.cap=None
        # self.mapNavi=MapNavigation()
        self.mapNavi=self.server_socket=None

        self.all_point1=self.all_points2=[]
        self.flag_point=False

        # Initialize window borders
    def _init_main_window(self):
        # Set the form to be borderless
        self.setWindowFlags(Qt.FramelessWindowHint)
        # Set the background to be transparent
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Set software icon
        w = self.logo_lab.width()
        h = self.logo_lab.height()
        self.pix = QPixmap(libraries_path + '/images/logo.png')  # the path to the icon
        self.logo_lab.setPixmap(self.pix)
        self.logo_lab.setScaledContents(True)

        w = self.logo_pic_lab.width()
        h = self.logo_pic_lab.height()
        self.pix = QPixmap(libraries_path + '/images/logo_pic.jpg')  # the path to the icon
        self.logo_pic_lab.setPixmap(self.pix)
        self.logo_pic_lab.setScaledContents(True)
        # Initialize variables

    def _init_variable(self):
        with open(libraries_path + f'/offset/language_AGV.txt', "r", encoding="utf-8") as f:
            lange = f.read()
        self.language = int(lange)  # Control language, 1 is English, 2 is Chinese
        if self.language == 1:
            self.btn_color(self.language_btn, 'green')
        else:
            self.btn_color(self.language_btn, 'blue')
        self.is_language_btn_click = False
        self.agv_IP_text.setText(self.get_IP())

    def _init_status(self):
        self._init_language()

    def _initDrag(self):
        # Set the mouse tracking judgment trigger default value
        self._move_drag = False
        self._corner_drag = False
        self._bottom_drag = False
        self._right_drag = False
    # Close, minimize button display text
    def _close_max_min_icon(self):
        self.min_btn.setStyleSheet("border-image: url({}/images/min.ico);".format(libraries_path))
        self.max_btn.setStyleSheet("border-image: url({}/images/max.ico);".format(libraries_path))
        self.close_btn.setStyleSheet("border-image: url({}/images/close.ico);".format(libraries_path))
    
    def _init_point_info(self):
        goal_list1=[self.X_text,self.Y_text,self.Z_text,self.W_text]
        goal_list2=[self.X_text_3,self.Y_text_3,self.Z_text_3,self.W_text_3]

        try:
            for index,value in enumerate(zip(goal_list1,goal_list2)):
                value[0][index]=socket_server.goal_1[index]
                value[0][index]=socket_server.goal_2[index]
        except Exception:
            print("value is null")


    @pyqtSlot()
    def min_clicked(self):
        # minimize
        self.showMinimized()

    @pyqtSlot()
    def max_clicked(self):
        # Maximize and restore (not used)
        if self.isMaximized():
            self.showNormal()
            # self.max_btn.setStyleSheet("border-image: url({}/AiKit_UI_img/max.png);".format(libraries_path))
            icon_max = QtGui.QIcon()
            icon_max.addPixmap(QtGui.QPixmap(f"{libraries_path}/images/max.ico"), QtGui.QIcon.Normal,
                               QtGui.QIcon.Off)
            self.max_btn.setIcon(icon_max)
            self.max_btn.setIconSize(QtCore.QSize(30, 30))
            self.max_btn.setToolTip("<html><head/><body><p>maximize</p></body></html>")
        else:
            self.showMaximized()
            # self.max_btn.setStyleSheet("border-image: url({}/AiKit_UI_img/nomel.png);".format(libraries_path))
            icon_nomel = QtGui.QIcon()
            icon_nomel.addPixmap(QtGui.QPixmap(f"{libraries_path}/images/nomel.ico"), QtGui.QIcon.Normal,
                                 QtGui.QIcon.Off)
            self.max_btn.setIcon(icon_nomel)
            self.max_btn.setIconSize(QtCore.QSize(30, 30))
            self.max_btn.setToolTip("<html><head/><body><p>recover</p></body></html>")


    def eventFilter(self, obj, event):
        # Event filter, used to solve the problem of reverting to the standard mouse style after the mouse enters other controls
        if isinstance(event, QEnterEvent):
            self.setCursor(Qt.ArrowCursor)
        return super(AGV_APP, self).eventFilter(obj, event)  # Note that MyWindow is the name of the class

    def resizeEvent(self, QResizeEvent):
        # 自定义窗口调整大小事件
        # 改变窗口大小的三个坐标范围
        self._right_rect = [QPoint(x, y) for x in range(self.width() - 5, self.width() + 5)
                            for y in range(self.widget.height() + 20, self.height() - 5)]
        self._bottom_rect = [QPoint(x, y) for x in range(1, self.width() - 5)
                             for y in range(self.height() - 5, self.height() + 1)]
        self._corner_rect = [QPoint(x, y) for x in range(self.width() - 5, self.width() + 100)
                             for y in range(self.height() - 5, self.height() + 1)]

    def mousePressEvent(self, event):
        # 重写鼠标点击的事件
        if (event.button() == Qt.LeftButton) and (event.pos() in self._corner_rect):
            # 鼠标左键点击右下角边界区域
            self._corner_drag = True
            event.accept()
        elif (event.button() == Qt.LeftButton) and (event.pos() in self._right_rect):
            # 鼠标左键点击右侧边界区域
            self._right_drag = True
            event.accept()
        elif (event.button() == Qt.LeftButton) and (event.pos() in self._bottom_rect):
            # 鼠标左键点击下侧边界区域
            self._bottom_drag = True
            event.accept()
        elif (event.button() == Qt.LeftButton) and (event.y() < self.widget.height()):
            # 鼠标左键点击标题栏区域
            self._move_drag = True
            self.move_DragPosition = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, QMouseEvent):
        # 判断鼠标位置切换鼠标手势
        if QMouseEvent.pos() in self._corner_rect:  # QMouseEvent.pos()获取相对位置
            self.setCursor(Qt.SizeFDiagCursor)
        elif QMouseEvent.pos() in self._bottom_rect:
            self.setCursor(Qt.SizeVerCursor)
        elif QMouseEvent.pos() in self._right_rect:
            self.setCursor(Qt.SizeHorCursor)

        # 当鼠标左键点击不放及满足点击区域的要求后，分别实现不同的窗口调整
        # 没有定义左方和上方相关的5个方向，主要是因为实现起来不难，但是效果很差，拖放的时候窗口闪烁，再研究研究是否有更好的实现
        if Qt.LeftButton and self._right_drag:
            # 右侧调整窗口宽度
            self.resize(QMouseEvent.pos().x(), self.height())
            QMouseEvent.accept()
        elif Qt.LeftButton and self._bottom_drag:
            # 下侧调整窗口高度
            self.resize(self.width(), QMouseEvent.pos().y())
            QMouseEvent.accept()
        elif Qt.LeftButton and self._corner_drag:
            #  由于我窗口设置了圆角,这个调整大小相当于没有用了
            # 右下角同时调整高度和宽度
            self.resize(QMouseEvent.pos().x(), QMouseEvent.pos().y())
            QMouseEvent.accept()
        elif Qt.LeftButton and self._move_drag:
            # 标题栏拖放窗口位置
            self.move(QMouseEvent.globalPos() - self.move_DragPosition)
            QMouseEvent.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        # 鼠标释放后，各扳机复位
        self._move_drag = False
        self._corner_drag = False
        self._bottom_drag = False
        self._right_drag = False
        self.setCursor(Qt.ArrowCursor)


    @pyqtSlot()
    def close_clicked(self):
        # turn off an app
        if self.cap:
            self.cap.release()
        
        if self.server_socket:
            self.server_socket.close()
        
        if self.flag_point:
            self.close_terminal()

        

        self.close()
        QApplication.exit()


    def close_terminal(self):

        def close_radar():
            GPIO.setmode(GPIO.BCM)
            time.sleep(0.1)
            GPIO.setup(20, GPIO.OUT)
            GPIO.output(20, GPIO.LOW)

            time.sleep(0.05)

            run_cmd="myagv_active.launch"
            close_command = "ps -ef | grep -E " + run_cmd + " | grep -v 'grep' | awk '{print $2}' | xargs kill -9"
            subprocess.run(close_command, shell=True)
        
        def close_navi():

            run_cmd="navigation_active.launch"
            # close_command = "ps -ef | grep -E " + run_cmd + " | grep -v 'grep' | awk '{print $2}' | xargs kill -9"

            os.system("ps -ef | grep -E rviz" +
                    " | grep -v 'grep' | awk '{print $2}' | xargs kill -9")

            time.sleep(0.2)

            os.system("ps -ef | grep -E " + run_cmd +
                    " | grep -v 'grep' | awk '{print $2}' | xargs kill -9")
        
        close_radar()
        time.sleep(0.2)
        close_navi()

    

    def get_IP(self):
            # IP address get

        ifname = "wlan0"
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        HOST = socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', bytes(ifname,'utf-8')))[20:24])
        PORT = 9000 #default

        print("ip: {} port: {}".format(HOST, PORT))
        print(type(HOST),"Host")

        return HOST
    
    def point_obtain(self):
        
        points=threading.Thread(target=self.open_points,daemon=True)
        points.start()
    
    def open_points(self):
        self.flag_point=True

        def radar_open():
            GPIO.setmode(GPIO.BCM)
            time.sleep(0.1)
            GPIO.setup(20, GPIO.OUT)
            GPIO.output(20, GPIO.HIGH)

            launch_command = "cd ~/myagv_ros | roslaunch myagv_odometry myagv_active.launch"  # 使用ros 打开
            subprocess.run(['gnome-terminal', '-e', f"bash -c '{launch_command}; exec $SHELL'"])

        def navi_open():
            # os.system("gnome-terminal -e 'bash -c \"cd /home/ubuntu; roslaunch ~/myagv_ros/src/myagv_navigation/launch/navigation_active.launch; exec bash\"'")
            launch_command = "roslaunch myagv_navigation navigation_active.launch"  # 使用ros 打开
            subprocess.run(['gnome-terminal', '-e', f"bash -c '{launch_command}; exec $SHELL'"])


        
        
        def get_points():

            all_points_tmp=[]
            position_values = []
            orientation_values = []

            # path='/home/er/Desktop/outout.json'
            

            command = "rostopic echo /initialpose"
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            point_count=1
            while True:
                # print(point_count,"iiii first")
                output_line = process.stdout.readline().decode().strip()
            
                if not output_line:
                    break  

                # print("Output:", output_line) 
                all_points_tmp.append(output_line)

                if output_line=="---":
                    # print(point_count,"iii in ---")
                    print(all_points_tmp,"all for now")

                    index_position=all_points_tmp.index("position:")
                    index_orientation=all_points_tmp.index("orientation:")
                    index_con=index_orientation+5

                    # print(raw_data[index_position],raw_data[index_orientation],raw_data[index_con])

                    for i in range(index_position+1,index_orientation):
                        # print(raw_data[i],"i")
                        value1=all_points_tmp[i].split(":")[1].strip()
                        # print(value,"vv")
                        position_values.append(value1)


                    for j in range(index_orientation+1,index_con):
                        value2=all_points_tmp[j].split(":")[1].strip()
                        #print(value2,"vvvj")
                        orientation_values.append(value2)
                        # print(raw_data[j])

                    deal_data=position_values[:2]+orientation_values[2:]
                    print(point_count,"count") 
                    if point_count%2==0:
                        self.data_point2.emit(deal_data)
                        

                    elif point_count%2==1:
                        self.data_point1.emit(deal_data)

                    all_points_tmp.clear()
                    position_values.clear()
                    orientation_values.clear()

                    point_count+=1
                    # print(point_count,"pp")


            return_code = process.poll()
            if return_code is not None:
                print(f"Command exited with return code: {return_code}")

            stderr_output = process.stderr.read().decode()
            if stderr_output:
                print("Error:", stderr_output)

            
            
        radar_open()
        time.sleep(5)
        navi_open()
        time.sleep(5)
        print("start text")
        get_points()



    def save_points(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))

        path=dir_path+"/points.json"

        print(path,"save_path")

        datas={
            "point1": self.all_point1,
            "point2": self.all_point2
        }


        try:
        # if datas:
            print(datas,"datas",self.all_point1,self.all_point2)
            with open(path,'w') as f:
                json.dump(datas,f,indent=4)
            

            if self.language == 1:
                QMessageBox.information(self, "communication", "Save points file successfully", QMessageBox.Ok)
            else:
                QMessageBox.information(self, "提示", "保存点位文件成功",QMessageBox.Ok)

        except Exception:

            if self.language == 1:
                QMessageBox.information(self, "communication", "Fail to Save the points file", QMessageBox.Ok)
            else:
                QMessageBox.information(self, "提示", "点位文件保存失败",QMessageBox.Ok)

   
    def open_socket(self):
        print("socket_test")
        ip_add=self.agv_IP_text.text()
        port=self.agv_port_text.text()


        if ip_add and port:

            server_address = (ip_add, int(port))
            self.server_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            time.sleep(0.1)
            self.server_socket.bind(server_address)

            run_msg=threading.Thread(target=self.receive_msg)
            run_msg.start()


            if self.language == 1:
                QMessageBox.information(self, "communication", "Successfully openserver", QMessageBox.Ok)
            else:
                    QMessageBox.information(self, "提示", "服务端打开成功",QMessageBox.Ok)
        else:
            if self.language == 1:
                QMessageBox.information(self, "prompt", "The connectionfailed, please check the IP address and confirm that the AGVhas started the server", QMessageBox.Ok)
            else:
                QMessageBox.information(self, "提示", "连接失败，请检查IP地址以确认AGV已经启动服务端", QMessageBox.Ok)

            self.agv_IP_text.setText(self.get_IP())
    

    def socket_data(self,data):
        # print(data,"data-- in emit and signal")
        socket_server.data_actions(data)
    
    def socket_send_msg(self,msg):
        print("send")
        self.connection.send(msg.encode())


    def receive_msg(self):
        self.server_socket.listen(3)
        print("Waitting for connection...")
        self.connection, client_address = self.server_socket.accept()
        print("connected")

        while 1:
            try:
                data = self.connection.recv(1024)
                if not data:
                    break

                print("Get the message", data.decode())

                self.data_recieve.emit(data.decode())

                reply="Reply to"+str(client_address)
                print("flag",socket_server.arrive_feed_flag)
                # self.connection.send(reply.encode())

                if data.decode()=="go_to_feed":
                    time.sleep(1)
                    print(socket_server.arrive_feed_flag,"in bbbb")
                    #  socket_server.arrive_feed_flag==True:
                    reply="arrive_feed"

                    time.sleep(1)
                else:pass
                    # print("1111")
                self.connection.send(reply.encode())
            except Exception:
                self.connection, client_address = self.server_socket.accept()
                print("Error occured")

        print("End")
        self.connection.close()
        self.server_socket.close()
    
    def set_points1(self,points):

        socket_server.goal_1= [tuple(i for i in points)]
        self.all_point1=points
        print(socket_server.goal_1,"goal_1")


        goal_list1=[self.X_text,self.Y_text,self.Z_text,self.W_text]

        try:
            for index,value in enumerate(points):
                goal_list1[index].setText(value)
                
        except Exception:
            print("value is null")


    def set_points2(self,points):

        socket_server.goal_2= [tuple(i for i in points)]
        self.all_point2=points
        print(socket_server.goal_2,"goal_2")

        goal_list2=[self.X_text_3,self.Y_text_3,self.Z_text_3,self.W_text_3]

        try:
            for index,value in enumerate(points):
                goal_list2[index].setText(value)
                
        except Exception:
            print("value is null")





    def btn_color(self, btn, color):
        if color == 'red':
            btn.setStyleSheet("background-color: rgb(231, 76, 60);\n"
                              "color: rgb(255, 255, 255);\n"
                              "border-radius: 10px;\n"
                              "border: 2px groove gray;\n"
                              "border-style: outset;")
        elif color == 'green':
            btn.setStyleSheet("background-color: rgb(39, 174, 96);\n"
                              "color: rgb(255, 255, 255);\n"
                              "border-radius: 10px;\n"
                              "border: 2px groove gray;\n"
                              "border-style: outset;")
        elif color == 'blue':
            btn.setStyleSheet("background-color: rgb(41, 128, 185);\n"
                              "color: rgb(255, 255, 255);\n"
                              "border-radius: 10px;\n"
                              "border: 2px groove gray;\n"
                              "border-style: outset;")
        elif color == 'grey':
            btn.setStyleSheet("background-color:rgb(41, 128, 185);\n"
                              "background-color: rgb(218, 218, 218);\n"
                              "color: rgb(255, 255, 255);\n"
                              "border-radius: 10px;\n"
                              "border: 2px groove gray;\n"
                              "border-style: outset;")

    def set_language(self):
        try:
            self.is_language_btn_click = True
            if self.language == 1:
                self.language = 2
                self.btn_color(self.language_btn, 'blue')
            else:
                self.language = 1
                self.btn_color(self.language_btn, 'green')
            self._init_language()
            self.is_language_btn_click = False
            with open(rf'{libraries_path}/offset/language_AGV.txt', "w",
                      encoding="utf-8") as file:
                file.write(str(self.language))
        except Exception as e:
            print(str(e))


    def _init_language(self):
        _translate = QtCore.QCoreApplication.translate
        if self.language == 2:
            self.title_lab.setText(_translate("AGV_UI", "Elephant Robotics AGV Sand Table"))
            self.connect_lab.setText(_translate("AGV_UI", "Socket服务"))
            self.language_btn.setText(_translate("AGV_UI", "English"))
            self.agv_ip.setText(_translate("AGV_UI", "IP"))
            self.agv_IP_text.setText(_translate("AGV_UI", f"{self.get_IP()}"))
            self.agv_port.setText(_translate("AGV_UI", "端口"))
            self.agv_connect_btn.setText(_translate("AGV_UI", "开启"))
            self.agv_con_lab.setText(_translate("AGV_UI", "定点导航位置"))
            #self.agv_connect_btn_2.setText(_translate("AGV_UI", "保存"))
            self.label_3.setText(_translate("AGV_UI", "目标点1"))
            self.X_lab.setText(_translate("AGV_UI", "X"))
            self.Y_lab.setText(_translate("AGV_UI", "Y"))
            self.Z_lab.setText(_translate("AGV_UI", "Z"))
            self.W_lab.setText(_translate("AGV_UI", "W"))
            self.label_2.setText(_translate("AGV_UI", "目标点2"))
            self.X_lab_3.setText(_translate("AGV_UI", "X"))
            self.Y_lab_3.setText(_translate("AGV_UI", "Y"))
            self.Z_lab_3.setText(_translate("AGV_UI", "Z"))
            self.W_lab_3.setText(_translate("AGV_UI", "W"))
            self.camera_lab_3.setToolTip(_translate("AGV_UI", "放大对应的监控画面"))
            self.camera_lab_3.setText(_translate("AGV_UI", "AGV"))
            self.camera_lab_4.setToolTip(_translate("AGV_UI", "放大对应的监控画面"))
            self.camera_lab_4.setText(_translate("AGV_UI", "Sand Table"))
            self.log_lab.setText(_translate("AGV_UI", "日志"))
            self.clear_log_btn.setText(_translate("AGV_UI", "清除日志"))
        else:
            self.title_lab.setText(_translate("AGV_UI", "Elephant Robotics AGV Sand Table"))
            self.connect_lab.setText(_translate("AGV_UI", "Socket service"))
            self.language_btn.setText(_translate("AGV_UI", "简体中文"))
            self.agv_ip.setText(_translate("AGV_UI", "IP"))
            self.agv_IP_text.setText(_translate("AGV_UI", f"{self.get_IP()}"))
            self.agv_port.setText(_translate("AGV_UI", "Port"))
            self.agv_connect_btn.setText(_translate("AGV_UI", "Open"))
            self.agv_con_lab.setText(_translate("AGV_UI", "point navigation position"))
            #self.agv_connect_btn_2.setText(_translate("AGV_UI", "Save"))
            self.label_3.setText(_translate("AGV_UI", "target point 1"))
            self.X_lab.setText(_translate("AGV_UI", "X"))
            self.Y_lab.setText(_translate("AGV_UI", "Y"))
            self.Z_lab.setText(_translate("AGV_UI", "Z"))
            self.W_lab.setText(_translate("AGV_UI", "W"))
            self.label_2.setText(_translate("AGV_UI", "target point 2"))
            self.X_lab_3.setText(_translate("AGV_UI", "X"))
            self.Y_lab_3.setText(_translate("AGV_UI", "Y"))
            self.Z_lab_3.setText(_translate("AGV_UI", "Z"))
            self.W_lab_3.setText(_translate("AGV_UI", "W"))
            self.camera_lab_3.setText(_translate("AGV_UI", "AGV"))
            self.camera_lab_4.setText(_translate("AGV_UI", "Sand Table"))
            self.log_lab.setText(_translate("AGV_UI", "Log"))
            self.clear_log_btn.setText(_translate("AGV_UI", "Clear"))


# visit resource lib
def resource_path(relative_path):
    # check if Bundle Resource
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

if __name__ == '__main__':
    try:
        libraries_path = resource_path('libraries')
        libraries_path = libraries_path.replace("\\", "/")
        print(libraries_path)
        app = QApplication(sys.argv)
        PC_Window = AGV_APP()
        # PC_Window.open_socket()
        PC_Window.show()

    except Exception as e:
        print(str(e))
    sys.exit(app.exec_())
