#!/usr/bin/env python3
# encoding:utf-8
import math
import os
import socket
import struct
import sys
import threading
import time
import traceback

import cv2
import numpy as np
import serial
import serial.tools.list_ports
from PyQt5 import QtCore, QtGui, QtWidgets, QtWebEngineWidgets
from PyQt5.QtCore import QPoint
from PyQt5.QtCore import pyqtSlot, Qt, QCoreApplication
from PyQt5.QtGui import QEnterEvent, QPixmap, QImage
from PyQt5.QtWidgets import QMainWindow, QApplication, QInputDialog, QWidget, QMessageBox, QDialog, QLabel
from pymycobot.mycobot import MyCobot
from pymycobot.mycobotsocket import MyCobotSocket
from libraries.pyqtfile.agv_UI import Ui_AGV_UI as AGV_Window
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
from scripts.end import *
from scripts import test_auto_charing


class AGV_APP(AGV_Window, QMainWindow, QWidget):
    def __init__(self):
        super(AGV_APP, self).__init__()
        self.setupUi(self)
        self._init_main_window()
        self._initDrag()  # Set the mouse tracking judgment trigger default value
        self.setMouseTracking(True)  # Set widget mouse tracking
        self.widget.installEventFilter(self)  # Initialize event filter
        self.move(350, 10)
        self._init_variable()
        self._init_status()
        self.min_btn.clicked.connect(self.min_clicked)  # minimize
        self.max_btn.clicked.connect(self.max_clicked)
        self.close_btn.clicked.connect(self.close_clicked)  # close
        self.agv_camera_btn.clicked.connect(self.camera_checked)
        self.feed_camera.clicked.connect(self.robot_camera_status)
        self.agv_camera.mousePressEvent = self.show_camera_popup

        self.start_btn.clicked.connect(self.start_run)
        self.puase_btn.clicked.connect(self.pause_run)
        self.feed_position_ben.clicked.connect(self.feed_position)
        self.down_position_btn.clicked.connect(self.down_position)
        self.start_btn.setEnabled(False)

        self.pc_ip = ''
        self.pc_port = 9001
        self.mc = None
        self.mycobot_ip = '192.168.123.23'
        self.mycobot_port = 9000
        self.mc = MyCobotSocket(self.mycobot_ip, self.mycobot_port)

        # 上料区是否有新木块放置
        self.feed_place = True
        # 上料区吸取次数
        self.pump_times = 0

        import RPi.GPIO as GPIO
        GPIO.setwarnings(False)
        self.GPIO = GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(20, GPIO.OUT)
        GPIO.setup(21, GPIO.OUT)
        GPIO.output(20, 1)
        GPIO.output(21, 1)

        # 移动角度
        self.move_angles = [
            [0, 0, 0, 0, 80, 0],  # init the point
            [-40.31, 2.02, -10.72, -0.08, 80, -54.84],  # point to grab
            [-70.31, 2.02, -10.72, -0.08, 80, -54.84]
        ]

        # 移动坐标
        self.move_coords = [
            [96.5, -101.9, 185.6, 155.25, 19.14, 75.88],  # above the red bucket
            [180.9, -99.3, 184.6, 124.4, 30.9, 80.58],  # above the green bucket
            [77.4, 122.1, 179.2, 151.66, 17.94, 178.24],  # above the blue bucket
            [2.2, 128.5, 171.6, 163.27, 10.58, -147.25]  # gray
        ]

        # agv 车上角度
        self.avg_angles = [
            [-2.54, 14.67, -177.36, 0.87, -88.24, -7.73],
            [-159, 20.3, -16.69, 1.84, 77.34, -54.75],
            [-2.72, -4.74, -168.66, 1.14, -96.76, -47.63],
            [-25.13, -5.53, -176.04, 1.23, -84.81, -38.4],
            [12.12, -23.64, -153.8, 1.49, -84.63, -36.12],
            [-3.77, -25.75, -153.1, 1.23, -84.9, -36.38],
            [-19.59, -27.07, -147.12, 2.46, -88.68, -36.38]
        ]

        # place angles
        self.agv_place_angles = [
            [-2.54, 14.67, -177.36, 0.87, -88.24, -7.73],
            [19.07, -16.52, -176.3, 0.43, -79.54, -39.9],
            [-27.94, -18.72, 179.64, 5.36, -70.4, -46.93],
            [-22.67, -23.29, -172.35, 1.14, -83.4, -39.72],
            [12.3, -39.19, -147.65, 2.19, -79.89, -39.72],
            [-5.27, -40.69, -146.6, 2.72, -82.0, -39.99],
            [-17.75, -41.74, -146.86, 0.87, -79.45, -39.9]
        ]

        # down_angles
        self.down_place_angles = [
            [29.44, -19.16, 21.35, 0.61, 33.48, -76.55],
            [-4.74, -20.56, 21.35, 0.26, 43.24, -76.72],
            [-43.33, 13.27, -20.83, 3.51, 53.7, -76.72]
        ]
        # 创建一个服务器套接字
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # 绑定服务器地址和端口
        self.server_socket.bind((self.pc_ip, self.pc_port))

        # 开始监听客户端请求
        self.server_socket.listen()

        self.t_agv = threading.Thread(target=self.myagv_loop_run)
        self.t_agv.daemon = True
        self.t_agv.start()

    def myagv_loop_run(self):
        try:
            for i in range(3):
                self.down_position()
                self.feed_position()
        except Exception as e:
            print(e)

    def moved(self, x, y):
        print('x, y', x, y)
        # send Angle to move mecharm 270
        self.mc.send_angles(self.move_angles[0], 50)
        time.sleep(2)

        # [x, y, 185.5, -157.73, 22.08, -140.19]
        # send coordinates to move mycobot
        if x <= 180:
            print(1)
            self.mc.send_coords([x, y, 150, -176.1, 2.4, -125.1], 30, 0)  # usb :rx,ry,rz -173.3, -5.48, -57.9
            time.sleep(4)

            # self.mc.send_coords([x, y, 150, 179.87, -3.78, -62.75], 25, 0)
            # time.sleep(3)

            # self.mc.send_coords([x, y, 105, 179.87, -3.78, -62.75], 25, 0)
            self.mc.send_coords([x, y, 140, -176.1, 2.4, -125.1], 30, 0)
        else:
            if x > 188:
                x = 174
            else:
                x = x - 20
            print(2)
            self.mc.send_coords([x, y, 175, -164.99, 11.33, -125.91], 30,
                                0)  # [174.6, -3.5, 175.8, -164.99, 11.33, -125.91]
            time.sleep(4)

            # self.mc.send_coords([x, y, 150, 179.87, -3.78, -62.75], 25, 0)
            # time.sleep(3)

            # self.mc.send_coords([x, y, 105, 179.87, -3.78, -62.75], 25, 0)
            self.mc.send_coords([x, y, 148, -164.99, 11.33, -125.91], 30, 0)
        time.sleep(4)

        # open pump
        self.gpio_status(True)
        time.sleep(1.5)
        if self.pump_times < 4:
            self.pump_times += 1
        else:
            self.feed_place = False
            self.pump_times = 1

        tmp = []
        while True:
            if not tmp:
                tmp = self.mc.get_angles()
            else:
                break
        time.sleep(0.5)

        print('tmp:', tmp)
        self.mc.send_angles([tmp[0], 17.22, -32.51, tmp[3], 80, tmp[5]],
                            40)  # [18.8, -7.91, -54.49, -23.02, -0.79, -14.76]
        time.sleep(1)
        self.mc.send_angles([-70, 17.22, -32.51, tmp[3], 80, tmp[5]],
                            40)  # [18.8, -7.91, -54.49, -23.02, -0.79, -14.76]
        time.sleep(2.5)
        self.mc.send_angles([-70, 14.67, -177.36, 0.87, -88.24, -7.73], 40)
        time.sleep(3.5)
        self.mc.send_angles(self.avg_angles[0], 40)
        time.sleep(2.5)
        # temp_ang=self.avg_angles[self.pump_times][1]
        # self.avg_angles[self.pump_times][1] = -10
        # self.mc.send_angles(self.avg_angles[self.pump_times], 40)
        # time.sleep(2.5)
        # self.avg_angles[self.pump_times][1] = temp_ang
        print(self.pump_times)
        print(self.avg_angles[self.pump_times])
        if self.pump_times > 3:
            self.mc.send_angles([-4.92, -10.81, -151.43, 2.54, -80.15, -10.28], 40)
            time.sleep(1.5)
        self.mc.send_angles(self.avg_angles[self.pump_times], 40)
        time.sleep(3)

        # close pump
        self.gpio_status(False)
        time.sleep(3)
        self.mc.send_angles([-70, 14.67, -177.36, 0.87, -88.24, -7.73], 40)
        time.sleep(1.5)

        self.mc.send_angles([-70, 17.22, -32.51, tmp[3], 97, tmp[5]],
                            40)  # [18.8, -7.91, -54.49, -23.02, -0.79, -14.76]
        time.sleep(3.5)
        self.mc.send_angles(self.move_angles[1], 50)
        time.sleep(3)

    def place(self):

        self.pump_times = 4
        for i in range(1, self.pump_times):
            self.mc.send_angles(self.move_angles[1], 40)
            time.sleep(3)
            self.mc.send_angles(self.move_angles[2], 40)
            time.sleep(1)
            self.mc.send_angles([-70, 14.67, -177.36, 0.87, -88.24, -7.73], 40)
            time.sleep(3.5)
            self.mc.send_angles([self.avg_angles[i][0], 14.67, -177.36, 0.87, -88.24, -7.73], 40)
            time.sleep(1.5)
            if i > 3:
                self.mc.send_angles([self.avg_angles[i][0], -10.81, -151.43, 2.54, -80.15, -10.28], 40)
                time.sleep(1.5)
            self.mc.send_angles(self.agv_place_angles[i], 40)
            time.sleep(3)
            # open pump
            self.gpio_status(True)
            time.sleep(2.5)
            ang = self.agv_place_angles[i][1] + 30
            self.mc.send_angle(2, ang, 40)
            time.sleep(1)
            self.mc.send_angles([-70, 14.67, -177.36, 0.87, -88.24, -7.73], 40)
            time.sleep(1.5)
            self.mc.send_angles(self.move_angles[2], 40)
            time.sleep(3.5)
            ang = self.move_angles[1][2] - 30
            self.mc.send_angle(2, ang, 40)
            time.sleep(1.5)
            if i == 0:
                self.mc.send_angles(self.down_place_angles[0], 40)
            elif i == 1:
                self.mc.send_angles(self.down_place_angles[1], 40)
            else:
                self.mc.send_angles(self.down_place_angles[2], 40)
            time.sleep(3)
            # close pump
            self.gpio_status(False)

    def gpio_status(self, flag):
        if flag:
            GPIO.output(20, 0)
            GPIO.output(21, 0)
        else:
            # GPIO.output(20, 1)
            GPIO.output(21, 1)

    def responsed(self):
        t = time.time()
        while True:
            x = None
            y = None
            # 等待客户端连接
            client_socket, client_address = self.server_socket.accept()
            print(f"Connection from {client_address} has been established.")

            # 接收来自客户端的数据
            data = client_socket.recv(1024)
            x, y = struct.unpack('ff', data)
            # print(f"Received data from client: {data.decode()}")
            print(f"Received data from client: {x},{y}")
            # 向客户端发送响应
            response = "Data received successfully!"
            client_socket.sendall(response.encode())

            if x and y:
                t = time.time()
                self.feed_place = True
                self.moved(x, y)
                if not self.feed_place:
                    break

            else:
                if time.time() - t > 10:
                    self.feed_place = False
                    break

            response = "Running END!"
            client_socket.sendall(response.encode())
            # 关闭客户端套接字
            client_socket.close()

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

    def start_run(self):
        """
        开始
        :return:
        """
        print('start run')
        self.pause_clicked = False
        self.btn_color(self.start_btn, 'red')
        self.start_btn.setEnabled(False)
        self.btn_color(self.puase_btn, 'blue')
        self.puase_btn.setEnabled(True)

    def pause_run(self):
        """
        暂停
        :return:
        """
        print('pause run')
        self.pause_clicked = True
        self.btn_color(self.start_btn, 'blue')
        self.start_btn.setEnabled(True)
        self.btn_color(self.puase_btn, 'red')
        self.puase_btn.setEnabled(False)

    def down_position(self):
        """
        下料区
        :return:
        """
        print('down-position-btn')
        try:
            set_robot_pose = SetRobotPose()
            set_robot_pose.set_pose()
            map_navigation = MapNavigation1()
            map_navigation.navigate()
            map_navigation = MapNavigation2()
            map_navigation.navigate()
            test_auto_charing.init()
            while self.pause_clicked:
                self.stop_wait(0.2)

            test_auto_charing.main()
            self.place()
            while self.pause_clicked:
                self.stop_wait(0.2)
        except Exception as e:
            print(e)
            e = traceback.format_exc()
            with open('./error.log', 'a+') as f:
                f.write(e)

    def feed_position(self):
        """
        上料区
        :return:
        """
        print('feed-position-btn')
        try:
            map_navigation = MapNavigation3()
            map_navigation.navigate()
            map_navigation = MapNavigation4()
            map_navigation.navigate()
            test_auto_charing.init()
            while self.pause_clicked:
                self.stop_wait(0.2)
            test_auto_charing.main()
            t = time.time()
            while self.feed_place:
                self.responsed()
            while self.pause_clicked:
                self.stop_wait(0.2)
            set_robot_pose = SetRobotPose()
            set_robot_pose.set_pose()
        except Exception as e:
            print(e)
            e = traceback.format_exc()
            with open('./error.log', 'a+') as f:
                f.write(e)

    # Initialize variables
    def _init_variable(self):
        self.cap = cv2.VideoCapture()
        self.camera_status = False
        self.rbt_camera_status = False
        self.pause_clicked = False

    # initialization status
    def _init_status(self):
        pass

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
        self.pix = QPixmap(libraries_path + '/images/logo_pic.png')  # the path to the icon
        self.logo_pic_lab.setPixmap(self.pix)
        self.logo_pic_lab.setScaledContents(True)

    # Close, minimize button display text
    def _close_max_min_icon(self):
        self.min_btn.setStyleSheet("border-image: url({}/images/min.ico);".format(libraries_path))
        self.max_btn.setStyleSheet("border-image: url({}/images/max.ico);".format(libraries_path))
        self.close_btn.setStyleSheet("border-image: url({}/images/close.ico);".format(libraries_path))

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
            icon_max.addPixmap(QtGui.QPixmap(f"{libraries_path}/images/max.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
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

    @pyqtSlot()
    def close_clicked(self):
        # turn off an app
        self.cap.release()
        self.close()
        QApplication.exit()

    def _initDrag(self):
        # Set the mouse tracking judgment trigger default value
        self._move_drag = False
        self._corner_drag = False
        self._bottom_drag = False
        self._right_drag = False

    def _initDrag(self):
        # Set the mouse tracking judgment trigger default value
        self._move_drag = False
        self._corner_drag = False
        self._bottom_drag = False
        self._right_drag = False

    def eventFilter(self, obj, event):
        # Event filter, used to solve the problem of reverting to the standard mouse style after the mouse enters other controls
        if isinstance(event, QEnterEvent):
            self.setCursor(Qt.ArrowCursor)
        return super(AGV_APP, self).eventFilter(obj, event)  # Note that MyWindow is the name of the class
        # return QWidget.eventFilter(self, obj, event)  # You can also use this, but pay attention to modifying the window type

    # def mousePressEvent(self, event):
    #     # Rewrite mouse click event
    #     if (event.button() == Qt.LeftButton) and (event.y() < self.widget.height()):
    #         # Click the left mouse button on the title bar area
    #         self._move_drag = True
    #         self.move_DragPosition = event.globalPos() - self.pos()
    #         event.accept()
    #
    # def mouseMoveEvent(self, QMouseEvent):
    #     try:
    #         if Qt.LeftButton and self._move_drag:
    #             # title bar drag and drop window position
    #             self.move(QMouseEvent.globalPos() - self.move_DragPosition)
    #             QMouseEvent.accept()
    #     except Exception as e:
    #         self.loger.info(e)
    #
    # def mouseReleaseEvent(self, QMouseEvent):
    #     # After the mouse is released, each trigger resets
    #     self._move_drag = False

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

    def open_camera(self):
        QApplication.processEvents()
        self.camera_status = True
        flag = self.cap.open(1)  # Get the serial number of the camera to open
        if not flag:  # Flag indicates whether the camera is successfully opened
            self.close_camera()
            return

    def close_camera(self):
        """turn off the camera"""
        try:
            self.camera_status = False
            self.cap.release()  # free video stream
            self.agv_camera.clear()
            self._init_variable()
        except Exception as e:
            print(str(e))

    def camera_checked(self):
        """Bind camera switch"""
        if not self.camera_status:
            self.show_agv_camera()
        else:
            self.close_camera()

    def robot_camera_status(self):
        try:
            if not self.rbt_camera_status:
                t = threading.Thread(target=self.show_feed_camera())
                print(self.rbt_camera_status)
                t.start()
                print(1)
            else:
                print(2)
                # self.robot_camera.setPixmap(None)
                self.robot_camera.load(QUrl('about:blank'))
                self.robot_camera.setZoomFactor(0.5)
                # t.join()
                self.rbt_camera_status = False
        except Exception as e:
            print(str(e))

    def show_feed_camera(self):
        self.robot_camera.load(QUrl('http://192.168.11.191:200'))
        # self.robot_camera.load(QUrl('http://www.baidu.com'))
        self.robot_camera.setZoomFactor(1.0)
        # 将QWebEngineView控件的内容设置为QLabel控件的背景图片
        # self.robot_camera.setPixmap(self.web_view.grab().scaled(self.robot_camera.width(), self.robot_camera.height()))
        self.rbt_camera_status = True

    def show_agv_camera(self):
        if not self.camera_status:
            self.open_camera()
        try:
            while self.camera_status:
                _, frame = self.cap.read()
                frame = cv2.resize(frame, (510, 360))
                # deal img
                QApplication.processEvents()
                show = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Convert the read video data into QImage format
                showImage = QtGui.QImage(show.data, show.shape[1], show.shape[0], show.shape[1] * 3,
                                         QtGui.QImage.Format_RGB888)
                # Display the QImage in the Label that displays the video
                self.agv_camera.setPixmap(QtGui.QPixmap.fromImage(showImage))
        except Exception as e:
            print(str(e))

    def show_camera_popup(self, event):
        try:
            self.camera_status = False
            if event.button() == Qt.LeftButton:
                enlarged_dialog = QDialog(self)
                enlarged_label = QLabel(enlarged_dialog)
                enlarged_label.setAlignment(Qt.AlignCenter)
                enlarged_dialog.setWindowTitle("Enlarged Camera")
                enlarged_dialog.setGeometry(300, 50, 1280, 960)
                enlarged_label.setGeometry(0, 0, 1280, 960)

                def on_close():
                    self.camera_status = True
                    print(self.camera_status)
                    self.show_agv_camera()

                enlarged_dialog.finished.connect(on_close)
                enlarged_dialog.show()
                while True:
                    ret, frame = self.cap.read()
                    if ret:
                        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        img = cv2.resize(img, (1280, 960))
                        h, w, ch = img.shape
                        bytesPerLine = ch * w
                        qImg = QImage(img.data, w, h, bytesPerLine, QImage.Format_RGB888)
                        pixmap = QPixmap.fromImage(qImg)
                        enlarged_label.setPixmap(pixmap)
                    QApplication.processEvents()
        except Exception as e:
            print(str(e))

    def stop_wait(self, t):
        """Refresh the software screen in real time during the robot movement"""
        if t * 10 <= 1:
            t = 1
        else:
            t = int(t * 10)

        for i in range(1, t + 1):
            QApplication.processEvents()
            time.sleep(0.1)


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
        AGV_window = AGV_APP()
        AGV_window.show()
    except Exception as e:
        print(str(e))
    sys.exit(app.exec_())
