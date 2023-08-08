#!/usr/bin/env python3
# encoding:utf-8
import os
import socket
import sys
import threading
import time
import select
import cv2
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QPoint
from PyQt5.QtCore import QUrl
from PyQt5.QtCore import pyqtSlot, Qt, pyqtSignal, QThread
from PyQt5.QtGui import QEnterEvent, QPixmap, QImage
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QMessageBox, QDialog, QLabel

from libraries.pyqtfile.agv_UI import Ui_AGV_UI as AGV_Window

from CvDetection.detection import Detector
from R1Control.RobotR1 import RobotR1
from R1Control.VideoCapture3d import VideoCaptureThread


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
        self._close_max_min_icon()
        self.min_btn.clicked.connect(self.min_clicked)  # minimize
        self.max_btn.clicked.connect(self.max_clicked)
        self.close_btn.clicked.connect(self.close_clicked)  # close
        #self.agv_camera_btn.clicked.connect(self.camera_checked)  
        self.feed_camera.clicked.connect(self.robot_camera_status)# feed camera color and depth
        # self.agv_camera.mousePressEvent = self.show_camera_popup
        self.start_btn.setCheckable(True)
        self.start_btn.clicked.connect(self.start_run)
        self.puase_btn.setCheckable(True)
        self.puase_btn.clicked.connect(self.stop_run)
        self.feed_position_ben.setCheckable(True)
        self.feed_position_ben.clicked.connect(self.feed_position)
        self.down_position_btn.setCheckable(True)
        self.down_position_btn.clicked.connect(self.down_position)
        self.feed_complete_btn.setCheckable(True)
        self.feed_complete_btn.clicked.connect(self.feed_complete)
        self.unload_complete_btn.setCheckable(True)
        self.unload_complete_btn.clicked.connect(self.unload_complete)
        self.language_btn.clicked.connect(self.set_language)  # set language

        self.agv_connect_btn.clicked.connect(self.connect)

        # self.agv_camera_btn.setEnabled(False)
        self.agv_camera_btn.setEnabled(False)
        self.start_btn.setEnabled(False)
        self.puase_btn.setEnabled(False)
        self.feed_position_ben.setEnabled(False)
        self.down_position_btn.setEnabled(False)
        self.feed_complete_btn.setEnabled(False)
        self.unload_complete_btn.setEnabled(False)

        self.mc = None
        self.socket_res = None

        # connect to the 270
        self.r1 = RobotR1()

    # Initialize variables
    def _init_variable(self):
        self.cap = cv2.VideoCapture()
        self.camera_status = False
        self.rbt_camera_status = False
        self.pause_clicked = False
        with open(libraries_path + f'/offset/language.txt', "r", encoding="utf-8") as f:
            lange = f.read()
        self.language = int(lange)  # Control language, 1 is English, 2 is Chinese
        if self.language == 1:
            self.btn_color(self.language_btn, 'green')
        else:
            self.btn_color(self.language_btn, 'blue')
        self.is_language_btn_click = False


    # initialization status
    def _init_status(self):
        self._init_language()

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

    @pyqtSlot(QImage)
    def update_image(self, image):
        # 在主线程中更新UI元素
        pixmap = QPixmap.fromImage(image)
        # self.label.setPixmap(pixmap.scaled(640, 480))
        self.agv_camera.setPixmap(pixmap.scaled(320, 240))

        # self.agv_camera.setPixmap(pixmap_color)

    @pyqtSlot(QImage)
    def update_processed_image(self, image):
        # 在主线程中更新UI元素
        pixmap = QPixmap.fromImage(image)
        self.label_2.setPixmap(pixmap.scaled(320, 240))
        # self.label_processed.setPixmap(pixmap.scaled(640, 480))

        # self.label_2.setPixmap(QPixmap.fromImage(depth_show))

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

    def connect(self):
        ip = self.agv_ip_text.text()
        port = self.agv_port_text.text()
        try:
            if ip and port is not None:
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_address = (ip, int(port))
                self.client_socket.connect(server_address)
                t = threading.Thread(target=self.get_res)
                t.start()
                if self.language == 1:
                    QMessageBox.information(self, "communication", "Successfully connected", QMessageBox.Ok)
                else:
                    QMessageBox.information(self, "提示", "连接成功", QMessageBox.Ok)
                self.start_btn.setEnabled(True)
                self.puase_btn.setEnabled(True)
                self.feed_position_ben.setEnabled(True)
                self.down_position_btn.setEnabled(True)
                self.feed_complete_btn.setEnabled(True)
                self.unload_complete_btn.setEnabled(True)
                self.agv_connect_btn.setEnabled((False))
                self.btn_color(self.agv_connect_btn, 'red')
            else:
                if self.language == 1:
                    QMessageBox.information(self, "prompt", "The connection failed, please check the IP address and confirm that the AGV has started the server", QMessageBox.Ok)
                else:
                    QMessageBox.information(self, "提示", "连接失败，请检查IP地址以及确认AGV已经启动服务端", QMessageBox.Ok)

        except Exception as e:
            print(str(e))
            if self.language == 1:
                QMessageBox.information(self, "prompt", "The connection failed, please check the IP address and confirm that the AGV has started the server", QMessageBox.Ok)
            else:
                QMessageBox.information(self, "提示", "连接失败，请检查IP地址以及确认AGV已经启动服务端", QMessageBox.Ok)

    def send_msg(self, msg):
        # 向服务器发送数据
        self.client_socket.send(msg.encode())

    def get_res(self):
        socket_res = self.client_socket.recv(1024).decode()
        while 1:
            read_to_read, _, _ = select.select([self.client_socket], [], [], 1)
            if read_to_read:
                socket_res = self.client_socket.recv(1024).decode()
            time.sleep(0.2)
            #print("-------------------------------------------",socket_res)192.168.1.103
            start_time = time.monotonic()
            if socket_res == 'arrive_feed':
                while self.r1.i < 3:
                    current_time = time.monotonic()
                    self.r1.motion(self.video_thread.capture_thread)
                    time.sleep(1)
                    print("-------------------------------------------",current_time - start_time)
                    if current_time - start_time >= 120:
                        break
                else:
                    self.r1.i = -1
                    send_data = "picking_finished"
                    self.client_socket.send(send_data.encode())
                    socket_res = None
                self.r1.move_end(50, 1)

    def start_run(self):
        """
        开始
        :return:
        """
        # self.pause_clicked = True
        # 检查按钮是否被选中
        if self.start_btn.isChecked():
            self.btn_color(self.start_btn, 'red')
            # print('start run')
            self.send_msg('go_to_feed')
        else:
            self.btn_color(self.start_btn, 'grey')

    def stop_run(self):
        """
        暂停
        :return:
        """
        _translate = QtCore.QCoreApplication.translate
        self.pause_clicked = True
        # 检查按钮是否被选中
        if self.puase_btn.isChecked():
            self.btn_color(self.puase_btn, 'red')
            self.puase_btn.setText(_translate("AGV_UI", "恢复"))
            self.send_msg('stop')
            print('stop run')
        else:
            self.btn_color(self.puase_btn, 'blue')
            self.puase_btn.setText(_translate("AGV_UI", "暂停"))
            self.send_msg('Resume_Stop')
            print('Resume_Stop')

    def feed_position(self):
        """
        上料区
        :return:
        """
        # 检查按钮是否被选中
        if self.feed_position_ben.isChecked():
            self.btn_color(self.feed_position_ben, 'red')
            print('feed-position-btn')
            self.send_msg('single_go_to_feed')
        else:
            self.btn_color(self.feed_position_ben, 'blue')

    def down_position(self):
        """
        下料区
        :return:
        """
        # 检查按钮是否被选中
        if self.down_position_btn.isChecked():
            self.btn_color(self.down_position_btn, 'red')
            print('go_to_unload')
            self.send_msg('single_go_to_unload')
        else:
            self.btn_color(self.down_position_btn, 'blue')

    def feed_complete(self):
        """
        上料完成
        :return:
        """
        # 检查按钮是否被选中
        if self.feed_complete_btn.isChecked():
            self.btn_color(self.feed_complete_btn, 'red')
            print('feed_complete')
            self.send_msg('single_picking_finished')
        else:
            self.btn_color(self.feed_complete_btn, 'blue')

    def unload_complete(self):
        """
        下料完成
        :return:
        """
        # 检查按钮是否被选中
        if self.unload_complete_btn.isChecked():
            self.btn_color(self.unload_complete_btn, 'red')
            print('unload_complete')
            self.send_msg('single_placed_finished')
        else:
            self.btn_color(self.unload_complete_btn, 'blue')

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
        pass
        """Bind camera switch"""
        # try:
        # if not self.rbt_camera_status:

        #     self.video_thread = VideoThread()
        #     self.video_thread.frame_signal.connect(self.update_image)
        #     self.video_thread.processed_frame_signal.connect(self.update_processed_image)
        #     self.video_thread.start()
        #     self.agv_camera_btn.setEnabled(False)

        # except Exception as e:
        #     print(str(e))

    def robot_camera_status(self):
        if not self.rbt_camera_status:
            self.video_thread = VideoThread()
            self.video_thread.frame_signal.connect(self.update_image)
            self.video_thread.processed_frame_signal.connect(self.update_processed_image)
            self.video_thread.start()
            self.feed_camera.setEnabled(False)

    def show_feed_camera(self):
        self.robot_camera.show()
        # self.label_camera1_depth.sh
        self.robot_camera.load(QUrl('http://www.baidu.com'))
        self.robot_camera.setZoomFactor(1.0)
        # 将QWebEngineView控件的内容设置为QLabel控件的背景图片
        # self.robot_camera.setPixmap(self.web_view.grab().scaled(self.robot_camera.width(), self.robot_camera.height()))
        self.rbt_camera_status = True

    def show_agv_camera(self):
        # self.agv_camera.show()
        # self.label_2.show()
        try:
            # time.sleep(0.2)
            # t = threading.Timer(0.02,self.show_agv_camera)
            # t.start()
            pass
        except Exception as e:
            with open('error.log', 'a') as f:
                f.write(e)

    def camera_show(self):
        self.agv_camera.show()
        with open('error.log', 'a') as f:
            f.write('logloglogloglgo')
        while True:
            log = 'start show camera'
            rgb = self.capture_thread.new_color_frame

            rgb_show = QImage(rgb, rgb.shape[1], rgb.shape[0], QImage.Format_RGB888)

            pixmap_color = QPixmap(rgb_show)
            pixmap_color = pixmap_color.scaled(320, 240, Qt.KeepAspectRatio)
            with open('error.log', 'a') as f:
                f.write(rgb)
            self.agv_camera.setPixmap(pixmap_color)

            time.sleep(0.5)

    def show_camera_popup(self):
        self.label_camera1_color.show()
        self.label_camera1_depth.show()
        while True:
            rgb = self.r1.capture_thread.rgb_show
            depth = self.r1.capture_thread.depth_show
            rgb_show = QImage(rgb, rgb.shape[1], rgb.shape[0], QImage.Format_RGB888)
            depth_show = QImage(depth, depth.shape[1], depth.shape[0], QImage.Format_RGB888)
            pixmap_color = QPixmap(rgb_show)
            pixmap_color = pixmap_color.scaled(320, 240, Qt.KeepAspectRatio)
            self.label_camera1_color.setPixmap(pixmap_color)
            self.label_camera1_depth.setPixmap(QPixmap.fromImage(depth_show))
            time.sleep(0.5)

    def stop_wait(self, t):
        """Refresh the software screen in real time during the robot movement"""
        if t * 10 <= 1:
            t = 1
        else:
            t = int(t * 10)

        for i in range(1, t + 1):
            QApplication.processEvents()
            time.sleep(0.1)

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
            with open(rf'{libraries_path}/offset/language.txt', "w",
                      encoding="utf-8") as file:
                file.write(str(self.language))
        except Exception as e:
            print(str(e))

    def _init_language(self):
        _translate = QtCore.QCoreApplication.translate
        if self.language == 1:
            self.camera_lab_5.setText(_translate("AGV_UI", "Connect"))
            self.language_btn.setText(_translate("AGV_UI", "简体中文"))
            self.agv_ip.setText(_translate("AGV_UI", "IP"))
            self.agv_port.setText(_translate("AGV_UI", "PORT"))
            self.agv_connect_btn.setText(_translate("AGV_UI", "Connect"))
            self.camera_lab.setText(_translate("AGV_UI", "Camera"))
            self.agv_camera_btn.setText(_translate("AGV_UI", "AGV Camera"))
            self.feed_camera.setText(_translate("AGV_UI", "Feed Camera"))
            self.agv_con_lab.setText(_translate("AGV_UI", "AGV Control"))
            self.start_btn.setText(_translate("AGV_UI", "Start"))
            self.puase_btn.setText(_translate("AGV_UI", "Pause"))
            self.position_con_lab.setText(_translate("AGV_UI", "Fixed Point Control"))
            self.feed_position_ben.setText(_translate("AGV_UI", "Feeding area"))
            self.down_position_btn.setText(_translate("AGV_UI", "Cutting area"))
            self.feed_complete_btn.setText(_translate("AGV_UI", "Loading completed"))
            self.unload_complete_btn.setText(_translate("AGV_UI", "Cutting completed"))
            self.camera_lab_3.setToolTip(_translate("AGV_UI", "Enlarge the corresponding monitoring screen"))
            self.camera_lab_4.setToolTip(_translate("AGV_UI", "Enlarge the corresponding monitoring screen"))
            self.label.setText(_translate("AGV_UI", "Feed screen："))
        elif self.language == 2:
            self.camera_lab_5.setText(_translate("AGV_UI", "建立连接"))
            self.language_btn.setText(_translate("AGV_UI", "English"))
            self.agv_ip.setText(_translate("AGV_UI", "IP"))
            self.agv_port.setText(_translate("AGV_UI", "PORT"))
            self.agv_connect_btn.setText(_translate("AGV_UI", "连接"))
            self.camera_lab.setText(_translate("AGV_UI", "摄像头"))
            self.agv_camera_btn.setText(_translate("AGV_UI", "AGV摄像头"))
            self.feed_camera.setText(_translate("AGV_UI", "上料区摄像头"))
            self.agv_con_lab.setText(_translate("AGV_UI", "AGV控制"))
            self.start_btn.setText(_translate("AGV_UI", "开始"))
            self.puase_btn.setText(_translate("AGV_UI", "暂停"))
            self.position_con_lab.setText(_translate("AGV_UI", "定点控制"))
            self.feed_position_ben.setText(_translate("AGV_UI", "上料区"))
            self.down_position_btn.setText(_translate("AGV_UI", "下料区"))
            self.feed_complete_btn.setText(_translate("AGV_UI", "上料完成"))
            self.unload_complete_btn.setText(_translate("AGV_UI", "下料完成"))
            self.camera_lab_3.setToolTip(_translate("AGV_UI", "放大对应的监控画面"))
            self.camera_lab_3.setText(_translate("AGV_UI", "AGV"))
            self.camera_lab_4.setToolTip(_translate("AGV_UI", "放大对应的监控画面"))
            self.camera_lab_4.setText(_translate("AGV_UI", "Sand Table"))
            self.label.setText(_translate("AGV_UI", "上料区画面："))

class VideoThread(QThread):
    frame_signal = pyqtSignal(QImage)
    processed_frame_signal = pyqtSignal(QImage)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = False

        self.capture_thread = VideoCaptureThread(Detector("apple"), Detector.FetchType.FETCH.value)
        self.capture_thread.daemon = True
        self.capture_thread.start()

    def run(self):
        self.running = True

        while self.running:
            try:
                time.sleep((0.1))#需修改为标志位
                # rgb转为qt图像
                rgb = self.capture_thread.rgb_show
                rgb_show = QImage(rgb, rgb.shape[1], rgb.shape[0], QImage.Format_RGB888)

                # 发送rgb图像信号给主线程
                self.frame_signal.emit(rgb_show)

                # depth转为qt图像
                depth = self.capture_thread.depth_show
                depth_show = QImage(depth, depth.shape[1], depth.shape[0], QImage.Format_RGB888)

                # 发送depth图像信号给主线程
                self.processed_frame_signal.emit(depth_show)
            except Exception as e:
                print(str(e))

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
