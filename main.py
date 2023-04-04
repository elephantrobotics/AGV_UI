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
        # self.mc = MyCobotSocket(self.mycobot_ip, self.mycobot_port)
        
        self.agv_ip = ''
        self.agv_port = 9002

        # 上料区是否有新木块放置
        self.feed_place = True
        # 上料区吸取次数
        self.pump_times = 0

        # 创建一个服务器套接字
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # 绑定服务器地址和端口
        self.server_socket.bind((self.pc_ip, self.pc_port))

        # 开始监听客户端请求
        self.server_socket.listen()

        # self.t_agv = threading.Thread(target=self.myagv_loop_run)
        # self.t_agv.daemon = True
        # self.t_agv.start()
            
    def socket_connect(self, x, y=0):
        import socket

        # 创建一个客户端套接字
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # 连接服务器
        server_address = (self.agv_ip, self.agv_port)
        client_socket.connect(server_address)

        data = struct.pack('ff', x, y)

        # 向服务器发送数据
        client_socket.sendall(data)

        # 接收来自服务器的响应
        response = client_socket.recv(1024)
        print(f"Received response from server: {response.decode()}")

        # 关闭客户端套接字
        client_socket.close()
    def moved(self, x, y):
        print('x, y', x, y)
        
        self.socket_connect(x, y)


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
        self.socket_connect('start')

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
        self.socket_connect('pause')

    def down_position(self):
        """
        下料区
        :return:
        """
        print('down-position-btn')
        self.socket_connect('down')
        # import socket

        # # 创建一个客户端套接字
        # client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # # 连接服务器
        # server_address = (self.agv_ip, self.agv_port)
        # client_socket.connect(server_address)
        # x = 0
        # y = 0
        # data = struct.pack('ff', x, y)

        # # 向服务器发送数据
        # client_socket.sendall(data)

        # # 接收来自服务器的响应
        # response = client_socket.recv(1024)
        # print(f"Received response from server: {response.decode()}")

        # # 关闭客户端套接字
        # client_socket.close()

    def feed_position(self):
        """
        上料区
        :return:
        """
        print('feed-position-btn')
        self.socket_connect('feed')
        # import socket

        # # 创建一个客户端套接字
        # client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # # 连接服务器
        # server_address = (self.agv_ip, self.agv_port)
        # client_socket.connect(server_address)
        # x = -1
        # y = -1
        # data = struct.pack('ff', x, y)

        # # 向服务器发送数据
        # client_socket.sendall(data)

        # # 接收来自服务器的响应
        # response = client_socket.recv(1024)
        # print(f"Received response from server: {response.decode()}")

        # # 关闭客户端套接字
        # client_socket.close()
        

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
