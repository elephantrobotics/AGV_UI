#! /usr/bin/env pyhton3
# encoding:utf-8
import math
import os
import sys
import threading
import time

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
from pymycobot.mypalletizer import MyPalletizer
from pymycobot.ultraArm import ultraArm
from agv_UI import Ui_AGV_UI as AGV_Window
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


    # Initialize variables
    def _init_variable(self):
        self.cap = cv2.VideoCapture()
        self.camera_status = False
        self.rbt_camera_status = False
        pass

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
        self.pix = QPixmap(libraries_path + '/logo.png')  # the path to the icon
        self.logo_lab.setPixmap(self.pix)
        self.logo_lab.setScaledContents(True)

        w = self.logo_pic_lab.width()
        h = self.logo_pic_lab.height()
        self.pix = QPixmap(libraries_path + '/logo_pic.png')  # the path to the icon
        self.logo_pic_lab.setPixmap(self.pix)
        self.logo_pic_lab.setScaledContents(True)


    # Close, minimize button display text
    def _close_max_min_icon(self):
        self.min_btn.setStyleSheet("border-image: url({}/min.ico);".format(libraries_path))
        self.max_btn.setStyleSheet("border-image: url({}/max.ico);".format(libraries_path))
        self.close_btn.setStyleSheet("border-image: url({}/close.ico);".format(libraries_path))

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
            icon_max.addPixmap(QtGui.QPixmap("./max.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.max_btn.setIcon(icon_max)
            self.max_btn.setIconSize(QtCore.QSize(30, 30))
            self.max_btn.setToolTip("<html><head/><body><p>maximize</p></body></html>")
        else:
            self.showMaximized()
            # self.max_btn.setStyleSheet("border-image: url({}/AiKit_UI_img/nomel.png);".format(libraries_path))
            icon_nomel = QtGui.QIcon()
            icon_nomel.addPixmap(QtGui.QPixmap("./nomel.ico"), QtGui.QIcon.Normal,
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
            t = threading.Thread(target=self.show_feed_camera())
            t.start()
            # if not self.rbt_camera_status:
            #     print(1)
            # else:
            #     print(2)
            #     # self.robot_camera.setPixmap(None)
            #     self.web_view.load(QUrl('about:blank'))
            #     # t.join()
            self.rbt_camera_status=False
        except Exception as e:
            print(str(e))

    def show_feed_camera(self):
        self.robot_camera.load(QUrl('http://192.168.11.191:200'))
        # self.robot_camera.load(QUrl('http://www.baidu.com'))
        self.robot_camera.setZoomFactor(1.0)
        # 将QWebEngineView控件的内容设置为QLabel控件的背景图片
        # self.robot_camera.setPixmap(self.web_view.grab().scaled(self.robot_camera.width(), self.robot_camera.height()))
        self.rbt_camera_status=True


    def show_agv_camera(self):
        if not self.camera_status:
            self.open_camera()
        try:
            while self.camera_status:
                _, frame = self.cap.read()
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
        libraries_path = resource_path('')
        libraries_path = libraries_path.replace("\\", "/")
        print(libraries_path)
        app = QApplication(sys.argv)
        AGV_window = AGV_APP()
        AGV_window.show()
    except Exception as e:
            print(str(e))
    sys.exit(app.exec_())
