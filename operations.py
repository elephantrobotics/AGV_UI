
# encoding:utf-8

import subprocess
import sys
import threading
import time
import traceback
import socket

from PySide6.QtCore import Signal, QCoreApplication, QObject, QThread,Qt,QSize,QPoint,QTranslator
from PySide6.QtWidgets import QWidget, QApplication, QMessageBox, QFileDialog, QPushButton, QSizePolicy,QLabel,QMainWindow,QSizeGrip
from PySide6.QtGui import QPixmap,QIcon,QEventPoint,QEnterEvent
from operations_UI.AGV_operations_ui import Ui_myAGV
from pymycobot.myagv import MyAgv
from operations_UI.color_picker import ColorCircle
import os

if os.name == "posix":
    import RPi.GPIO as GPIO

lock = False

class myAGV_windows(QMainWindow):

    def __init__(self):
        super().__init__()

        self.ui = Ui_myAGV()
        self.ui.setupUi(self)


        self.ui.color_palette.setVisible(False)

        self.led_default = [255, 0, 0]  # red light

        # self.myagv=None
        self.myagv = MyAgv("/dev/ttyAMA2", 115200)
        self.st=None
        self.status=None
        
        # with open("style.qss", "r") as qss_file:
        #     qss = qss_file.read()
        #     self.setStyleSheet(qss)

        self.color_painter()
        self.ui.max_btn.clicked.connect(self.max_clicked)
        self.ui.min_btn.clicked.connect(self.min_clicked)
        self.ui.close_btn.clicked.connect(self.close_clicked)  
        self._initDrag()


        self.radar_flag = False
        self.keyboard_flag = False
        self.joystick_flag = False

        self.pix = QPixmap(os.getcwd()+'operations_UI/img_UI/logo.ico')
        print(self.pix.size())

        self.red_button="""
            background-color: rgb(198, 61, 47);
            color: rgb(255, 255, 255);
            border-radius: 7px;
            border: 2px groove gray;
            border-style: outset;
            font: 75 9pt "Arial";
        """

        self.green_button="""
            background-color: rgb(39, 174, 96);
            color: rgb(255, 255, 255);
            border-radius: 7px;
            border: 2px groove gray;
            border-style: outset;
            font: 75 9pt "Arial";
        
        """

        self.blue_button="""
            background-color:rgb(41, 128, 185);
            color: rgb(255, 255, 255);
            border-radius: 10px;
            border: 2px groove gray;
            border-style: outset;
            font: 75 9pt "Arial";
        """

        self.light_grey="""
                    background-color:grey;
                    border-radius: 9px;
                    border: 1px solid
        """

        self.light_green="""
                    background-color:green;
                    border-radius: 9px;
                    border: 1px solid
        """
        self.ui.label_value.setVisible(False)
        self.ui.lineEdit_RGB.setStyleSheet("background:None")
        self.ui.lineEdit_HEX.setStyleSheet("background:None")

        self._app=QApplication.instance()
        self.translator = QTranslator(self)
        # self.ui.logo_lab.setPixmap(self.pix)
        # self.ui.logo_lab.setScaledContents(True)
        self.ui.logo_lab.setVisible(False)
        self.ui_window_set()
        self.ui_set()
        


    def color_painter(self):

        self.label_color = QWidget()

        color = ColorCircle(self, [255, 0, 0])

        label_policy = QSizePolicy(QSizePolicy.Preferred,
                                   QSizePolicy.Preferred)
        label_policy.setHeightForWidth(True)
        color.setSizePolicy(label_policy)

        color.setMaximumWidth(150)
        color.setMaximumHeight(150)
        color.setMinimumWidth(150)
        color.setMinimumHeight(150)

        color.currentColorChanged.connect(self.lighter_set)

        self.ui.horizontalLayout_palette.insertWidget(0, color)
        self.ui.horizontal_Slider.valueChanged.connect((lambda x: color.setValue(x / 511)))
        self.ui.horizontalLayout_palette.addWidget(self.label_color)

    def ui_set(self):

        def ui_params():
            """
            set selection choices and style
            """
            language_params = [
                QCoreApplication.translate("myAGV","English"),
                QCoreApplication.translate("myAGV","Chinese")
            ]

            basic_control_params = [
                QCoreApplication.translate("myAGV","Keyboard Control"),
                QCoreApplication.translate("myAGV","Joystick-Alphabet"),
                QCoreApplication.translate("myAGV","Joystick-Number")
            ]

            map_nav_params = [
                QCoreApplication.translate("myAGV","Gmapping"),
                QCoreApplication.translate("myAGV","Cartographer"),
                QCoreApplication.translate("myAGV","3D Mapping")
            ]

            test_params = [
                QCoreApplication.translate("myAGV","Motor"),
                QCoreApplication.translate("myAGV","LED"),
                QCoreApplication.translate("myAGV","3D Camera"),
                QCoreApplication.translate("myAGV","Pump")
            ]

            self.ui.comboBox_language_selection.addItems(language_params)
            self.ui.basic_control_selection.addItems(basic_control_params)
            self.ui.build_map_selection.addItems(map_nav_params)
            self.ui.comboBox_testing.addItems(test_params)



        def ui_buttons():
            self.ui.radar_button.setCheckable(True)
            self.ui.radar_button.setChecked(True)
            self.ui.radar_button.toggle()

            self.ui.basic_control_button.setCheckable(True)
            self.ui.basic_control_button.setChecked(True)
            self.ui.basic_control_button.toggle()

            self.ui.open_build_map.setCheckable(True)
            self.ui.open_build_map.setChecked(True)
            self.ui.open_build_map.toggle()

            self.ui.start_detection_button.setCheckable(True)
            self.ui.start_detection_button.setChecked(True)
            self.ui.start_detection_button.toggle()

            self.ui.navigation_3d_button.setCheckable(True)
            self.ui.navigation_3d_button.setChecked(True)
            self.ui.navigation_3d_button.toggle()

            self.ui.navigation_button.setCheckable(True)
            self.ui.navigation_button.setChecked(True)
            self.ui.navigation_button.toggle()

            self.ui.status_radar.setStyleSheet(self.light_grey)
            self.ui.status_battery_main.setStyleSheet(self.light_grey)
            self.ui.status_battery_backup_2.setStyleSheet(self.light_grey)
            self.ui.status_motor_1.setStyleSheet(self.light_grey)

        def ui_functions():
            self.ui.radar_button.clicked.connect(self.radar_control)
            self.ui.basic_control_button.clicked.connect(self.basic_control)

            self.ui.save_map_button.clicked.connect(self.save_map)
            self.ui.open_build_map.clicked.connect(self.open_build_map)

            self.ui.navigation_3d_button.clicked.connect(self.navigation_3d)
            self.ui.navigation_button.clicked.connect(self.map_navigation)

            self.ui.log_clear.clicked.connect(self.clear_log)

            self.ui.comboBox_language_selection.currentTextChanged.connect(self.language_selection)
            self.ui.horizontal_Slider.setRange(0, 511)
            self.ui.horizontal_Slider.setValue(511)

            self.ui.start_detection_button.clicked.connect(self.start_testing)

            # self.status_deteccting() #todo status checking iii...threading

        ui_params()
        ui_functions()
        ui_buttons()

        self.status_detecting()

    def ui_window_set(self):

        def set_normal_window():

            # Set the form to be borderless
            self.setWindowFlags(Qt.FramelessWindowHint)
            # Set the background to be transparent
            self.setAttribute(Qt.WA_TranslucentBackground)

            w = self.ui.logo_lab.width()
            h = self.ui.logo_lab.height()
            self.pix = QPixmap(libraries_path+'/img_UI/logo.png')
            # self.ui.logo_lab.setPixmap(self.pix)
            # self.ui.logo_lab.setScaledContents(True)

        # Close, minimize button display text
        def _close_max_min_icon():
            self.ui.min_btn.setStyleSheet("border-image: url({}/img_UI/min.ico);".format(libraries_path))
            self.ui.max_btn.setStyleSheet("border-image: url({}/img_UI/max.ico);".format(libraries_path))
            self.ui.close_btn.setStyleSheet("border-image: url({}/img_UI/close.ico);".format(libraries_path))

        set_normal_window()
        _close_max_min_icon()
    
    def min_clicked(self):
        self.showMinimized()
    
    def max_clicked(self):
        if self.isMaximized():
            self.showNormal()

            icon_max = QIcon()
            icon_max.addPixmap(QPixmap("./operations_UI/img_UI/max.ico"), QIcon.Normal, QIcon.Off)
            self.max_btn.setIcon(icon_max)
            self.max_btn.setIconSize(QSize(30, 30))
            self.max_btn.setToolTip("<html><head/><body><p>maximize</p></body></html>")
        else:
            self.showMaximized()
            # self.max_btn.setStyleSheet("border-image: url({}/AiKit_UI_img/nomel.png);".format(libraries_path))
            icon_nomel = QIcon()
            icon_nomel.addPixmap(QPixmap("operations_UI/img_UI/nomel.ico"), QIcon.Normal,
                                 QIcon.Off)
            self.max_btn.setIcon(icon_nomel)
            self.max_btn.setIconSize(QSize(30, 30))
            self.max_btn.setToolTip("<html><head/><body><p>recover</p></body></html>")

    def close_clicked(self):
        self.close()
        QCoreApplication.instance().quit
    
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
        return super(myAGV_windows, self).eventFilter(obj, event)  # Note that MyWindow is the name of the class
        # return QWidget.eventFilter(self, obj, event)  # You can also use this, but pay attention to modifying the window type

    def resizeEvent(self, QResizeEvent):
        # 自定义窗口调整大小事件
        # 改变窗口大小的三个坐标范围
        self._right_rect = [QPoint(x, y) for x in range(self.width() - 5, self.width() + 5)
                            for y in range(self.ui.widget.height() + 20, self.height() - 5)]
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
        elif (event.button() == Qt.LeftButton) and (event.y() < self.ui.widget.height()):
            # 鼠标左键点击标题栏区域
            self._move_drag = True
            self.move_DragPosition = event.globalPos() - self.pos()
            event.accept()

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
        elif (event.button() == Qt.LeftButton) and (event.y() < self.ui.widget.height()):
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


    def stop_init(self, item):
        if item == "LED":
            if self.myagv:
                self.myagv.set_led(1, self.led_default)
        if item == "Pump":
            # stop testing to close pump
            GPIO.output(2, 1)
            GPIO.output(3, 1)

    def testing_finished(self, item):
        current_time = self.get_current_time()
        self.msg_log(QCoreApplication.translate("myAGV","Finishe ") + item + QCoreApplication.translate("myAGV"," testing"), current_time)

        if item=="LED":
            self.myagv.set_led(1,255,0,0)

        self.ui.start_detection_button.setText(QCoreApplication.translate("myAGV","Start Detection"))
        self.ui.comboBox_testing.setDisabled(False)
        self.button_status_switch(True)

    def lighter_set(self, color):

        r = color.red()
        g = color.green()
        b = color.blue()

        rgb_color = f"({r}, {g}, {b})"

        if self.myagv:
            self.myagv.set_led(1, r, g, b)

        hex = color.name()

        self.ui.lineEdit_HEX.setText(hex)
        self.ui.lineEdit_RGB.setText(rgb_color)

    def get_current_time(self):
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        return current_time

    def language_selection(self):
        """
        根据选择语言切换
        :return:
        """
        lang = self.ui.comboBox_language_selection.currentText()

        if lang == "English" or lang == "英文":
            print("----")
            self._app.removeTranslator(self.translator)
            self.ui.retranslateUi(self)
        if lang == "Chinese" or lang == "中文":
            print("======")
            self.translator.load("D:\projects\cc\AGV_UI\operations_lang.qm")
            self._app.installTranslator(self.translator)
            self.ui.retranslateUi(self)

    def button_status_switch(self, status):
        button = [
            self.ui.basic_control_button,
            self.ui.save_map_button,
            self.ui.open_build_map,
            self.ui.navigation_button,
            self.ui.navigation_3d_button,
            self.ui.start_detection_button

        ]

        for btn in button:
            btn.setCheckable(status)

    def clear_log(self):
        self.ui.textBrowser.clear()

    def msg_log(self, msg, current_time):

        msg_log = '[' + str(current_time) + ']' + msg
        self.ui.textBrowser.append(msg_log)

    def msg_error(self, msg, current_time):
        with open("error.log", "w") as f:
            f.write(msg)

        msg_error = '[' + str(current_time) + ']' + msg
        self.ui.textBrowser.append(msg_error)

    def radar_control(self):

        if self.ui.radar_button.isChecked():
            self.ui.radar_button.setStyleSheet(self.red_button)
            self.ui.radar_button.setText(QCoreApplication.translate("myAGV","OFF"))

            # print("open radar set")
            msg = QCoreApplication.translate("myAGV","Radar open...")
            current_time = self.get_current_time()
            self.msg_log(msg, current_time)
            try:
                radar_open = threading.Thread(target=self.radar_open, daemon=True)
                radar_open.start()
                self.radar_flag = True
                self.ui.status_radar.setStyleSheet("""
                background-color:green;
                border-radius: 9px;
                border: 1px solid
                """)

            except Exception as e:
                e = traceback.format_exc()
                self.msg_error(e, current_time)

        else:
            self.ui.radar_button.setStyleSheet(self.green_button)

            self.ui.radar_button.setText(QCoreApplication.translate("myAGV","ON"))

            msg = QCoreApplication.translate("myAGV","close radar")
            current_time = self.get_current_time()
            self.msg_log(msg, current_time)

            try:
                self.radar_flag = False
                if self.radar_flag==False:
                    self.ui.status_radar.setStyleSheet("""
                    background-color:grey;
                    border-radius: 9px;
                    border: 1px solid
                    """)
                close_run_launch = "myagv_active.launch"
                radar_close = threading.Thread(target=self.radar_close, args=(close_run_launch,), daemon=True)
                radar_close.start()

            except Exception as e:
                e = traceback.format_exc()
                self.msg_error(e, current_time)

            # print("close radar set")

    def basic_control(self):

        control_item_basic = self.ui.basic_control_selection.currentText()
        if self.ui.basic_control_button.isChecked():
            self.ui.basic_control_button.setStyleSheet(self.red_button)
            self.ui.basic_control_button.setText(QCoreApplication.translate("myAGV","OFF"))
            self.ui.basic_control_selection.setEnabled(False) # 设置下拉框不可选区

            if control_item_basic == "Keyboard Control" or control_item_basic == "键盘控制":
                self.keyboard_flag = True
                try:
                    print("open key")

                    msg = QCoreApplication.translate("myAGV","Keyboard open...")
                    current_time = self.get_current_time()
                    self.msg_log(msg, current_time)

                    keyboard_open = threading.Thread(target=self.keyboard_open, daemon=True)
                    keyboard_open.start()

                except Exception as e:
                    e = traceback.format_exc()
                    self.msg_error(e, current_time)


            elif control_item_basic == "Joystick-Number" or control_item_basic == "手柄控制(字母)":
                self.joystick_flag = True
                try:
                    # global lock
                    # while lock:
                    #     pass
                    # lock=True

                    print("open joy")
                    msg = QCoreApplication.translate("myAGV","Open joystick control...")
                    current_time = self.get_current_time()
                    self.msg_log(msg, current_time)
                    joystick_open = threading.Thread(target=self.joystick_open, daemon=True)
                    joystick_open.start()

                except Exception as e:
                    e = traceback.format_exc()
                    self.msg_error(e, current_time)

            elif control_item_basic == "Joystick-Number" or control_item_basic == "手柄控制(数字)":
                self.joystick_flag = True
                try:
                    msg = QCoreApplication.translate("myAGV","Open joystick control")
                    current_time = self.get_current_time()
                    self.msg_log(msg, current_time)
                    joystick_open = threading.Thread(target=self.joystick_open_number, daemon=True)
                    joystick_open.start()

                except Exception as e:
                    e = traceback.format_exc()
                    self.msg_error(e, current_time)


        else:

            self.ui.basic_control_button.setStyleSheet(self.green_button)
            self.ui.basic_control_button.setText("OFF")
            self.ui.basic_control_selection.setEnabled(True)

            if control_item_basic == "Keyboard Control" or control_item_basic == "键盘控制":
                self.keyboard_flag = False
                msg = QCoreApplication.translate("myAGV","Close keyboard control")
                current_time = self.get_current_time()
                try:

                    self.msg_log(msg, current_time)
                    keyboard_run_launch = "myagv_teleop.launch"

                    keyboard_close = threading.Thread(target=self.keyboard_close, args=(keyboard_run_launch,),
                                                      daemon=True)
                    keyboard_close.start()

                    print("close key")
                    # lock=False
                except Exception as e:
                    e = traceback.format_exc()
                    self.msg_error(e, current_time)


            elif control_item_basic == "Joystick-Number" or control_item_basic == "手柄控制(字母)":
                self.joystick_flag = False
                # print("close joy")

                msg =QCoreApplication.translate("myAGV","close joystick control")
                current_time = self.get_current_time()

                try:
                    self.msg_log(msg, current_time)

                    joystick_run_launch = "myagv_ps2.launch"
                    joystick_close = threading.Thread(target=self.joystick_close, args=(joystick_run_launch,),
                                                      daemon=True)
                    joystick_close.start()

                except Exception as e:
                    e = traceback.format_exc()
                    self.msg_error(e, current_time)

            elif control_item_basic == "Joystick-Number" or control_item_basic == "手柄控制(数字)":

                msg = QCoreApplication.translate("myAGV","close joystick control")
                current_time = self.get_current_time()

                try:
                    self.msg_log(msg, current_time)

                    joystick_run_launch = "myagv_ps2_number.launch"
                    joystick_close = threading.Thread(target=self.joystick_close_number, args=(joystick_run_launch,),
                                                      daemon=True)
                    joystick_close.start()

                except Exception as e:
                    e = traceback.format_exc()
                    self.msg_error(e, current_time)

    def save_map(self):

        save_map = threading.Thread(target=self.save_map_file, daemon=True)
        save_map.start()

    def open_build_map(self):
        def gmapping_build():
            open_gmapping_build = threading.Thread(target=self.gmapping_build_open, daemon=True)
            open_gmapping_build.start()

        def gmapping_close():
            close_launch = "myagv_slam_laser.launch"
            close_gmapping_build = threading.Thread(target=self.gmapping_build_close, args=(close_launch,), daemon=True)
            close_gmapping_build.start()

        def cartographer_build():
            open_cart_build = threading.Thread(target=self.cartographer_build_open, daemon=True)
            open_cart_build.start()

        def cartographer_close():
            close_cart_build = threading.Thread(target=self.cartographer_build_close, daemon=True)
            close_cart_build.start()

        build_map_method = self.ui.build_map_selection.currentText()



        if self.ui.open_build_map.isChecked():
            # 建图时导航不可用
            self.ui.build_map_selection.setEnabled(False)
            self.ui.navigation_button.setEnabled(False)
            self.ui.navigation_3d_button.setEnabled(False)

            if self.radar_flag:
                self.ui.open_build_map.setText(QCoreApplication.translate("myAGV","Close Build Map"))
                self.ui.open_build_map.setStyleSheet(self.red_button)


            else:
                print("radar not open !")
                QMessageBox.warning(None, "Warning", QCoreApplication.translate("myAGV","Radar not open!"))

            if not self.keyboard_flag:
                pass


            else:
                #     open keyboard
                self.keyboard_flag = True
                print("OOOOOO")
                self.ui.basic_control_selection.setCurrentIndex(0)
                self.ui.basic_control_selection.setEnabled(False)
                self.ui.basic_control_button.setText(QCoreApplication.translate("myAGV","OFF"))

            if build_map_method == "Gmapping": gmapping_build()

            if build_map_method == "Cartographer": cartographer_build()


        else:
            self.ui.open_build_map.setStyleSheet(self.blue_button)
            self.ui.open_build_map.setText(QCoreApplication.translate("myAGV","Open Build Map"))

            # 关闭建图打开导航按钮
            self.ui.build_map_selection.setEnabled(True)
            self.ui.navigation_button.setEnabled(True)
            self.ui.navigation_3d_button.setEnabled(True)

            if build_map_method == "Gmapping": gmapping_close()

            if build_map_method == "Cartographer": cartographer_close()

    def navigation_3d(self):

        if self.ui.navigation_3d_button.isChecked():
            self.ui.build_map_selection.setEnabled(False)  # 建图不可选
            self.ui.open_build_map.setEnabled(False)  # 打开建图不可选
            self.ui.navigation_button.setEnabled(False)  # 导航不可选

            self.ui.navigation_3d_button.setText(QCoreApplication.translate("myAGV","Close 3D Navigation"))
            self.ui.navigation_3d_button.setStyleSheet(self.red_button)

            open_navigation = threading.Thread(target=self.navigation_open, daemon=True)
            open_navigation.start()

        else:
            self.ui.build_map_selection.setEnabled(True)
            self.ui.open_build_map.setEnabled(True)
            self.ui.navigation_button.setEnabled(True)

            self.ui.navigation_3d_button.setText(QCoreApplication.translate("myAGV","3D Navigation"))
            self.ui.navigation_3d_button.setStyleSheet(self.blue_button)

            close_launch = "navigation_active.launch"
            close_navigation = threading.Thread(target=self.navigation_close, args=(close_launch,), daemon=True)
            close_navigation.start()

    def map_navigation(self):

        if self.ui.navigation_button.isChecked():
            self.ui.build_map_selection.setEnabled(False)
            self.ui.open_build_map.setEnabled(False)
            self.ui.navigation_3d_button.setEnabled(False)

            self.ui.navigation_button.setText(QCoreApplication.translate("myAGV","Close Navigation"))
            self.ui.navigation_button.setStyleSheet(self.red_button)

            open_navigation = threading.Thread(target=self.navigation_open, daemon=True)
            open_navigation.start()

        else:
            self.ui.build_map_selection.setEnabled(True)
            self.ui.open_build_map.setEnabled(True)
            self.ui.navigation_3d_button.setEnabled(True)

            self.ui.navigation_button.setText(QCoreApplication.translate("myAGV","Navigation"))
            self.ui.navigation_button.setStyleSheet(self.blue_button)

            close_launch = "navigation_active.launch"
            close_navigation = threading.Thread(target=self.navigation_close, args=(close_launch,), daemon=True)
            close_navigation.start()

    def start_testing(self):
        current_time = self.get_current_time()
        item = self.ui.comboBox_testing.currentText()

        if self.ui.start_detection_button.isChecked():

            self.ui.start_detection_button.setText(QCoreApplication.translate("myAGV","Stop Detection"))
            self.ui.comboBox_testing.setDisabled(True)
            self.msg_log(QCoreApplication.translate("myAGV","Start ") + item + QCoreApplication.translate("myAGV"," testing..."), current_time)

            self.st = Start_testing(item, self.myagv)
            self.st.testing_finish.connect(self.testing_finished)
            self.button_status_switch(False)
            self.st.start()

        else:

            self.ui.comboBox_testing.setDisabled(False)
            self.msg_log(QCoreApplication.translate("myAGV","Stop ") + item + QCoreApplication.translate("myAGV"," testing"), current_time)
            self.st.terminate()
            self.stop_init(item)
            self.button_status_switch(True)

    def status_detecting(self):
        def ip_set(ip_str):
            self.ui.lineEdit.setText(ip_str)

        def voltage_set(vol_1, vol_2):
            self.ui.lineEdit_voltage.setText(str(vol_1))
            self.ui.lineEdit_voltage_backup.setText(str(vol_2))

        def battery_set(b_1, b_2):
            if b_1:
                self.ui.status_battery_main.setStyleSheet("""
                    background-color:green;
                    border-radius: 9px;
                    border: 1px solid
                """)
            else:
                self.ui.status_battery_main.setStyleSheet("""
                    background-color:grey;
                    border-radius: 9px;
                    border: 1px solid
                """)

            if b_2:
                self.ui.status_battery_backup.setStyleSheet("""
                    background-color:green;
                    border-radius: 9px;
                    border: 1px solid
                """)
            else:
                self.ui.status_battery_backup.setStyleSheet("""
                    background-color:grey;
                    border-radius: 9px;
                    border: 1px solid
                """)

        def powers_set(power_1, power_2):
            self.ui.lineEdit_power.setText(str(power_1))
            self.ui.lineEdit_power_backup.setText(str(power_2))

        def motors_set(status):
            if status:
                self.ui.status_motor_1.setStyleSheet(
                    """
                    background-color:green;
                    border-radius: 9px;
                    border: 1px solid
                    """)
            else:
                self.ui.status_motor_1.setStyleSheet(
                    """
                    background-color:grey;
                    border-radius: 9px;
                    border: 1px solid
                    """)

        self.status = status_detect(self.myagv)
        self.status.ipaddress.connect(ip_set)
        self.status.voltages.connect(voltage_set)
        self.status.battery.connect(battery_set)
        self.status.powers.connect(powers_set)
        self.status.motors.connect(motors_set)

        self.status.start()

    # ____for threading start executing

    def radar_open(self):

        launch_command = "roslaunch ./src/myagv_odometry/launch/myagv_active.launch"
        # subprocess.run(launch_command,shell=True)
        subprocess.run(['gnome-terminal', '-e', f"bash -c '{launch_command}; exec $SHELL'"])

    def radar_close(self, run_launch):
        close_command = "ps -ef | grep -E " + run_launch + " | grep -v 'grep' | awk '{print $2}' | xargs kill -9"
        subprocess.run(close_command, shell=True)

    def keyboard_open(self):
        launch_command = "roslaunch ./src/myagv_teleop/launch/myagv_teleop.launch"
        subprocess.run(['gnome-terminal', '-e', f"bash -c '{launch_command}; exec $SHELL'"])

    def keyboard_close(self, run_launch):
        close_command = "ps -ef | grep -E " + run_launch + " | grep -v 'grep' | awk '{print $2}' | xargs kill -9"
        subprocess.run(close_command, shell=True)

    def joystick_open(self):
        launch_command = "roslaunch ./src/myagv_ps2/launch/myagv_ps2.launch"
        # launch_command="roslaunch myagv_ps2 myagv_ps2.launch"
        subprocess.run(['gnome-terminal', '-e', f"bash -c '{launch_command}; exec $SHELL'"])

    def joystick_close(self, run_launch):
        close_command = "ps -ef | grep -E " + run_launch + " | grep -v 'grep' | awk '{print $2}' | xargs kill -9"
        subprocess.run(close_command, shell=True)

    def joystick_open_number(self):
        launch_command = "roslaunch myagv_ps2 myagv_ps2_number.launch"
        subprocess.run(['gnome-terminal', '-e', f"bash -c '{launch_command}; exec $SHELL'"])

    def joystick_close_number(self, run_launch):
        close_command = "ps -ef | grep -E " + run_launch + " | grep -v 'grep' | awk '{print $2}' | xargs kill -9"
        subprocess.run(close_command, shell=True)

    def gmapping_build_open(self):

        self.keyboard_open()
        launch_command = "roslaunch ./src/myagv_navigation/launch/myagv_slam_laser.launch"
        subprocess.run(launch_command, shell=True)

    def gmapping_build_close(self, run_launch):
        close_command = "ps -ef | grep -E " + run_launch + " | grep -v 'grep' | awk '{print $2}' | xargs kill -9"
        subprocess.run(close_command, shell=True)

    def cartographer_build_open(self):
        launch_command = "roslaunch cartographer_ros demo_myagv.launch"
        subprocess.run(['gnome-terminal', '-e', f"bash -c '{launch_command}; exec $SHELL'"])

    def cartographer_build_close(self):

        close_command = "ps -ef | grep -E " + "demo_myagv.launch" + " | grep -v 'grep' | awk '{print $2}' | xargs kill -9"
        subprocess.run(close_command, shell=True)

    def save_map_file(self):
        subprocess.run("rosrun map_server map_saver", shell=True)
        subprocess.run(
            "cp /home/ubuntu/map.pgm /home/ubuntu/myagv_ros/src/myagv_navigation/map/my_map.pgm && cp /home/ubuntu/map.yaml /home/ubuntu/myagv_ros/src/myagv_navigation/map/my_map.yaml")

        current_time = self.get_current_time()
        self.msg_log(QCoreApplication.translate("myAGV","Save successfully!"), current_time)

        QMessageBox.information(None, "",
                                f"Save successfully! \n Save Path:\n /home/ubuntu/myagv_ros/src/myagv_navigation/map/my_map.pgm\n /home/ubuntu/myagv_ros/src/myagv_navigation/map/my_map.yaml")

    def navigation_open(self):

        launch_command = "roslaunch ./src/myagv_navigation/launch/navigation_active.launch"
        subprocess.run(launch_command, shell=True)

    def navigation_close(self, run_launch):
        close_command = "ps -ef | grep -E " + run_launch + " | grep -v 'grep' | awk '{print $2}' | xargs kill -9"
        subprocess.run(close_command, shell=True)

    def closeEvent(self, event):
        if self.status.isRunning():
            self.status.quit()


class Start_testing(QThread):
    testing_finish = Signal(str)
    testing_stop = Signal()

    def __init__(self, testing, myagv):
        super().__init__()

        self.test = testing
        self.agv = myagv

    def motor_testing(self):

        self.agv.go_ahead(130)
        time.sleep(4)

        self.agv.pan_left(130)

        time.sleep(4)

        self.agv.pan_left(130)
        time.sleep(4)

        self.agv.counterclockwise_rotation(130)
        time.sleep(8)

        self.agv.clockwise_rotation(130)
        time.sleep(8)

        self.agv.stop()

        self.testing_finish.emit(self.test)

    def LED_testing(self):
        print("LED Testing...")
        color_list = ["#ff0000", "ff7f00", "ffff00", "00ff00", "00ffff", "0000ff", "8b0ff"]

        color_dict = {
            "red": [255, 0, 0],
            "orange": [255, 128, 0],
            "yellow": [255, 255, 0],
            "green": [0, 255, 0],
            "cyan": [0, 255, 255],
            "blue": [0, 0, 255],
            "purple": [128, 0, 255]
        }

        for key, value in color_dict.items():
            r = int(value[0])
            g = int(value[1])
            b = int(value[2])

            self.agv.set_led(1, r, g, b)
            time.sleep(1)

        self.testing_finish.emit(self.test)

    def Camera_testing(self):
        pass  # todo camera testing...

    def Pump_testing(self):

        print("pump")
        # initialize
        GPIO.setmode(GPIO.BCM)

        GPIO.cleanup()
        GPIO.setup(2, GPIO.OUT)
        GPIO.setup(3, GPIO.OUT)

        # open pump
        GPIO.output(2, 0)
        GPIO.output(3, 0)

        # wait 4s
        time.sleep(4)

        # close pump
        GPIO.output(2, 1)
        GPIO.output(3, 1)

        self.testing_finish.emit(self.test)

    def run(self) -> None:

        if self.test == QCoreApplication.translate("myAGV","Motor"):
            self.motor_testing()

        elif self.test == QCoreApplication.translate("myAGV","LED"):
            self.LED_testing()

        elif self.test == QCoreApplication.translate("myAGV","Camera"):
            self.Camera_testing()

        elif self.test == QCoreApplication.translate("myAGV","Pump"):
            self.Pump_testing()


class status_detect(QThread):
    ipaddress = Signal(str)
    voltages = Signal(float, float)
    battery = Signal(int, int)
    powers = Signal(float, float)
    motors = Signal(bool)

    def __init__(self, agv):
        super().__init__()
        self.agv = agv

    def get_ipaddress(self):
        st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            st.connect(('10.255.255.255', 1))
            IP = st.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            st.close()

        return IP

    def get_info(self):

        # battery
        data = self.agv.get_battery_info()

        batterys = data[0]
        battery_1 = batterys[-2]
        battery_2 = batterys[-1]

        b_1_voltage = data[1]

        b_2_voltage = data[2]

        self.battery.emit(battery_1, battery_2)

        # voltage

        if b_1_voltage:
            # voltage_1 = b_1_voltage
            power_1 =  b_1_voltage / (12.2) * 100

        if b_2_voltage:
            # voltage_2 = b_2_voltage
            power_2 = b_2_voltage / (12.2) * 100


        # print(b_2_voltage,b_1_voltage,power_2,power_1,"thttththt")
        self.voltages.emit(b_1_voltage, b_2_voltage)
        self.powers.emit(round(power_1, 2), round(power_2,2))

    def get_motors_run(self):
        #     motors

        electicity = self.agv.get_motors_current()
        if electicity:
            self.motors.emit(True)
        else:
            self.motors.emit(False)

    def run(self):

        while 1:

            ip = self.get_ipaddress()
            if ip:
                self.ipaddress.emit(ip)
            time.sleep(2)

            self.get_info()
            time.sleep(2)
            self.get_motors_run()
            time.sleep(1)

def resource_path(relative_path):
    # check if Bundle Resource
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# 程序入口
if __name__ == "__main__":
    libraries_path = resource_path('operations_UI')
    libraries_path = libraries_path.replace("\\", "/")
    app = QApplication(sys.argv)

    window = myAGV_windows()
    window.show()
    sys.exit(app.exec())
