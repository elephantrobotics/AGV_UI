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

from libraries.pyqtfile.INagv_UI import Ui_AGV_UI as AGV_Window


class AGV_APP(AGV_Window, QMainWindow, QWidget):
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

        @pyqtSlot()
        def close_clicked(self):
            # turn off an app
            self.cap.release()
            self.close()
            QApplication.exit()



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
        PC_Window.show()

    except Exception as e:
        print(str(e))
    sys.exit(app.exec_())