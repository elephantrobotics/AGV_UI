
# encoding:utf-8

import subprocess
import sys
import threading
import time
import traceback
import socket
import json

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

        self.myagv=None
        self.myagv = MyAgv("/dev/ttyAMA2", 115200)
        self.st=None
        self.status=None

        self.color_painter()

        self.radar_flag = False
        self.keyboard_flag = False
        self.joystick_flag = False

        self.flag_all=False
        self.flag_build=False

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

        self.grey_button="""
            background-color:rgb(41, 128, 185);
            color: #7F8487;
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

        self.ui.logo_lab.setVisible(False)
        self.ui.menu_widget.setVisible(False)
        self.ui_set()

        self.status_detecting()

        self.language_initial()
        # self.ui.comboBox_language_selection.currentTextChanged.connect(self.language_change)

        if not self.radar_flag:
            self.status.start()

    def connections_agv(self):
        if self.radar_flag: #open radar
            QMessageBox(None,"Warning","Please turn off the radar before using this function.")
            return False
        else:
            self.myagv=MyAgv("/dev/ttyAMA2", 115200)
            return self.myagv

    def connections(self):
        time.sleep(2)
        self.myagv=MyAgv("/dev/ttyAMA2", 115200)


    def set_button_status(self,button_ui,status,color):
        button_ui.setEnabled(status)
        button_ui.setStyleSheet(color)

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

            # self.ui.comboBox_language_selection.addItems(language_params)
            # self.ui.basic_control_selection.addItems(basic_control_params)
            self.ui.build_map_selection.addItems(map_nav_params)
            # self.ui.comboBox_testing.addItems(test_params)



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

            self.ui.comboBox_language_selection.currentTextChanged.connect(self.language_change) #todo add langua
            self.ui.horizontal_Slider.setRange(0, 511)
            self.ui.horizontal_Slider.setValue(511)

            self.ui.start_detection_button.clicked.connect(self.start_testing)


        ui_params()
        ui_functions()
        ui_buttons()



    def testing_finished(self, item):
        self.connections()

        current_time = self.get_current_time()
        self.msg_log(QCoreApplication.translate("myAGV","Finish ") + item + QCoreApplication.translate("myAGV"," testing"), current_time)

        if item=="LED":
            self.myagv.set_led(1, 255,0,0)
        if item == "Pump":
            # stop testing to close pump
            GPIO.output(2, 1)
            GPIO.output(3, 1)

        if item=="Motor":
            self.myagv.stop()

        self.ui.start_detection_button.setText(QCoreApplication.translate("myAGV","Start Detection"))
        self.ui.comboBox_testing.setDisabled(False)
        self.button_status_switch(True)


    def lighter_set(self, color):

        r = color.red()
        g = color.green()
        b = color.blue()

        rgb_color = f"({r}, {g}, {b})"

        hex = color.name()

        self.ui.lineEdit_HEX.setText(hex)
        self.ui.lineEdit_RGB.setText(rgb_color)

        if self.radar_flag: #open radar
            QMessageBox(None,"Warning","Please turn off the radar before using this function.")
        else:
            self.myagv=MyAgv("/dev/ttyAMA2", 115200)
            self.myagv.set_led(1, r, g, b)


    def get_current_time(self):
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        return current_time

    def language_initial(self):
        with open("translation/language.json","r",encoding='utf-8') as f:
            language=json.loads(f.read())
        lang=language["language"]
        print("read")
        self.language_selection(lang)

    def language_change(self):

        lang_write=""
        lang=self.ui.comboBox_language_selection.currentText()
        # print(lang,"lang in change",lang_write)
        if lang == "English" or lang == "英语":
            lang_write="en"
        if lang == "Chinese" or lang == "中文":
            lang_write="zh_CN"

        # print(lang_write,"in")
        data={
            "language": lang_write
        }
        with open("translation/language.json","w") as f:
            json.dump(data,f,indent=4)
        print("write")
        self.language_initial()


    def language_selection(self,lang):
        """
        根据选择语言切换
        :return:
        """

        print("set lang")

        if lang == "en" or lang == "英文":
            print("----English")
            self._app.removeTranslator(self.translator)
            self.ui.retranslateUi(self)
        if lang == "zh_CN" or lang == "中文":
            print("=====Chinese")
            self.translator.load("translation/operations_lang.qm")
            self._app.installTranslator(self.translator)
            self.ui.retranslateUi(self)


    def button_status_switch(self, status):
        button = [
            self.ui.basic_control_button,
            self.ui.save_map_button,
            self.ui.open_build_map,
            self.ui.navigation_button,
            self.ui.navigation_3d_button
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
            self.status.quit()
            print("quit")
            time.sleep(0.1)

            self.ui.start_detection_button.setCheckable(False)  # 雷达打开时检测按钮不可使用

            if self.flag_all: return

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
            if self.flag_all: #other functions are running...
                QMessageBox.warning(None,
                                    QCoreApplication.translate("myAGV", "Warning"),
                                    QCoreApplication.translate("myAGV",
                                                               "Other functions are running."),
                                    QMessageBox.Ok)

                self.ui.radar_button.setChecked(True)
                return
            else:

                self.ui.radar_button.setStyleSheet(self.green_button)

                self.ui.radar_button.setText(QCoreApplication.translate("myAGV","ON"))

                msg = QCoreApplication.translate("myAGV","close radar")
                current_time = self.get_current_time()
                self.msg_log(msg, current_time)

                try:
                    self.ui.status_radar.setStyleSheet("""
                        background-color:grey;
                        border-radius: 9px;
                        border: 1px solid
                        """)
                    close_run_launch = "myagv_active.launch"
                    radar_close = threading.Thread(target=self.radar_close, args=(close_run_launch,), daemon=True)
                    radar_close.start()

                    self.radar_flag = False
                    time.sleep(4) #等待2s后，释放检测按钮（可用）
                    self.ui.start_detection_button.setCheckable(True)
                    self.status.start()


                except Exception as e:
                    e = traceback.format_exc()
                    self.msg_error(e, current_time)

                # print("close radar set")

    def basic_control(self):

        control_item_basic = self.ui.basic_control_selection.currentText()

        if self.ui.basic_control_button.isChecked():

            if not self.radar_flag:
                QMessageBox.warning(None, "Warning", QCoreApplication.translate("myAGV", "Radar not open!"),

                                    QMessageBox.Ok)
                self.ui.basic_control_button.setChecked(False)
                return
                print(self.radar_flag,"basic_control radar not")
            else:
                print(self.radar_flag,"basic_control radar yes")
                self.ui.basic_control_button.setStyleSheet(self.red_button)
                self.ui.basic_control_button.setText(QCoreApplication.translate("myAGV","OFF"))

                self.ui.basic_control_selection.setEnabled(False) # 设置下拉框不可选区
                self.flag_all=True

                if control_item_basic == "Keyboard Control" or control_item_basic == "键盘控制":
                    self.keyboard_flag = True
                    try:
                        # self.flag_all=True
                        msg = QCoreApplication.translate("myAGV","Keyboard open...")
                        current_time = self.get_current_time()
                        self.msg_log(msg, current_time)

                        keyboard_open = threading.Thread(target=self.keyboard_open, daemon=True)
                        keyboard_open.start()

                    except Exception as e:
                        # self.flag_all=False
                        e = traceback.format_exc()
                        self.msg_error(e, current_time)


                elif control_item_basic == "Joystick-Alphabet" or control_item_basic == "手柄控制(字母)":
                    self.joystick_flag = True
                    try:
                        # self.flag_all=True
                        msg = QCoreApplication.translate("myAGV","Open joystick control...")
                        current_time = self.get_current_time()
                        self.msg_log(msg, current_time)
                        joystick_open = threading.Thread(target=self.joystick_open, daemon=True)
                        joystick_open.start()

                    except Exception as e:
                        # self.flag_all=False
                        e = traceback.format_exc()
                        self.msg_error(e, current_time)

                elif control_item_basic == "Joystick-Number" or control_item_basic == "手柄控制(数字)":
                    self.joystick_flag = True
                    try:
                        # self.flag_all=True
                        msg = QCoreApplication.translate("myAGV","Open joystick control")
                        current_time = self.get_current_time()
                        self.msg_log(msg, current_time)
                        joystick_open = threading.Thread(target=self.joystick_open_number, daemon=True)
                        joystick_open.start()

                    except Exception as e:
                        # self.flag_all=False
                        e = traceback.format_exc()
                        self.msg_error(e, current_time)


        else:
            self.ui.basic_control_button.setStyleSheet(self.green_button)
            self.ui.basic_control_button.setText(QCoreApplication.translate("myAGV","ON"))

            self.ui.basic_control_selection.setEnabled(True)

            self.flag_all = False
            if control_item_basic == "Keyboard Control" or control_item_basic == "键盘控制":

                msg = QCoreApplication.translate("myAGV","Close keyboard control")
                current_time = self.get_current_time()
                try:

                    self.msg_log(msg, current_time)
                    keyboard_run_launch = "myagv_teleop.launch"

                    keyboard_close = threading.Thread(target=self.keyboard_close, args=(keyboard_run_launch,),
                                                      daemon=True)
                    keyboard_close.start()
                    self.keyboard_flag = False
                    print("close key")
                    # lock=False
                except Exception as e:
                    e = traceback.format_exc()
                    self.msg_error(e, current_time)


            elif control_item_basic == "Joystick-Alphabet" or control_item_basic == "手柄控制(字母)":
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
        if not self.radar_flag:

            QMessageBox.warning(None, "Warning", QCoreApplication.translate("myAGV", "Radar not open!"),

                                QMessageBox.Ok)
            self.ui.save_map_button.setChecked(False)
            return
        else:
            self.flag_all=True
            save_map = threading.Thread(target=self.save_map_file, daemon=True)
            save_map.start()
            self.flag_all=False

    def open_build_map(self):
        def gmapping_build():
            open_gmapping_build = threading.Thread(target=self.gmapping_build_open, daemon=True)
            open_gmapping_build.start()

        def gmapping_close():
            close_launch = "myagv_slam_laser.launch"
            close_gmapping_build = threading.Thread(target=self.gmapping_build_close, args=(close_launch,), daemon=True)
            print("quiuii build map")
            close_gmapping_build.start()

        def cartographer_build():
            open_cart_build = threading.Thread(target=self.cartographer_build_open, daemon=True)
            open_cart_build.start()

        def cartographer_close():
            close_cart_build = threading.Thread(target=self.cartographer_build_close, daemon=True)
            close_cart_build.start()

        build_map_method = self.ui.build_map_selection.currentText()

        current_build=self.get_current_time()

        # keyboard_flag=False

        if self.ui.open_build_map.isChecked():

            if not self.radar_flag: #检测雷达
                QMessageBox.warning(None, "Warning", QCoreApplication.translate("myAGV", "Radar not open!"),

                                    QMessageBox.Ok)
                self.ui.open_build_map.setChecked(False)
                return


            if not self.keyboard_flag: #检测键盘控制
                QMessageBox.warning(None,
                                    QCoreApplication.translate("myAGV", "Warning"),
                                    QCoreApplication.translate("myAGV",
                                                               "Please turn on keyboard control before mapping."),
                                                               QMessageBox.Ok)
                self.ui.open_build_map.setChecked(False)
                return


            else:
                self.ui.build_map_selection.setEnabled(False) #建图方式不可选取

                self.ui.navigation_3d_button.setEnabled(False)  #建图打开后导航均不可用
                self.ui.navigation_button.setEnabled(False)

                self.flag_build=True
                self.flag_all=True

                self.ui.open_build_map.setText(QCoreApplication.translate("myAGV", "Close Build Map"))
                self.ui.open_build_map.setStyleSheet(self.red_button)



                    #     open keyboard
                    # keyboard_flag = True


                    # self.ui.basic_control_selection.setCurrentIndex(0) #设置键盘控制
                    # self.ui.basic_control_button.setEnabled(False) #设置按钮不可点击
                    # self.ui.basic_control_selection.setEnabled(False) #基本控制不可选
                    # self.ui.basic_control_button.setText(QCoreApplication.translate("myAGV", "OFF"))

                    # keyboard_open_build = threading.Thread(target=self.keyboard_open, daemon=True)
                    # keyboard_open_build.start()


                if build_map_method == "Gmapping":
                    self.msg_log(QCoreApplication.translate("myAGV", "Open Gmapping..."), current_build)
                    gmapping_build()

                if build_map_method == "Cartographer":
                    self.msg_log(QCoreApplication.translate("myAGV", "Open Cartographer..."), current_build)
                    cartographer_build()



        else:
            self.ui.open_build_map.setStyleSheet(self.blue_button)
            self.ui.open_build_map.setText(QCoreApplication.translate("myAGV","Open Build Map"))

            if build_map_method == "Gmapping":
                self.msg_log(QCoreApplication.translate("myAGV", "Close Gmapping"), current_build)
                gmapping_close()

            if build_map_method == "Cartographer":
                self.msg_log(QCoreApplication.translate("myAGV", "Close Cartographer"), current_build)
                cartographer_close()

            # 关闭建图打开导航按钮

            self.ui.build_map_selection.setEnabled(True)
            self.ui.navigation_3d_button.setEnabled(True)  #建图关闭后导航可用
            self.ui.navigation_button.setEnabled(True)


            # if keyboard_flag:

            #     close_launch=("myagv_teleop.launch")
            #     keyboard_close_build = threading.Thread(target=self.keyboard_close, args=(close_launch,),
            #                                           daemon=True)
            #     keyboard_close_build.start()

            #     keyboard_flag=False


            #     # self.ui.basic_control_selection.setCurrentIndex(0) #设置键控制
            #     self.ui.basic_control_selection.setEnabled(True) #基本控制可选
            #     self.ui.basic_control_button.setEnabled(True) #设置按钮可以点击
            #     self.ui.basic_control_button.setText(QCoreApplication.translate("myAGV", "ON"))

            # else:pass




            self.flag_build = True
            self.flag_all = False

    def navigation_3d(self):

        current_time=self.get_current_time()

        if self.ui.navigation_3d_button.isChecked():

            # if self.flag_build:
            #     QMessageBox.warning(None,
            #                         QCoreApplication.translate("myAGV", "Warning"),
            #                         QCoreApplication.translate("myAGV",
            #                                                    "Please turn off mapping before using this function."),
            #                         QMessageBox.Ok)

            if not self.radar_flag:
                QMessageBox.warning(None, "Warning", QCoreApplication.translate("myAGV", "Radar not open!"),
                                    QMessageBox.Ok)

                self.ui.navigation_3d_button.setChecked(False)
                return

            else:
                self.ui.build_map_selection.setEnabled(False)  # 建图下拉框不可选
                self.ui.open_build_map.setEnabled(False)  # 打开建图不可选
                self.ui.navigation_button.setEnabled(False)  # 导航不可选

                self.ui.navigation_3d_button.setText(QCoreApplication.translate("myAGV","Close 3D Navigation"))
                self.ui.navigation_3d_button.setStyleSheet(self.red_button)

                self.msg_log(QCoreApplication.translate("myAGV", "Open 3D navigation"),current_time)

                self.flag_all=True
                open_navigation = threading.Thread(target=self.navigation_open, daemon=True)
                open_navigation.start()

        else:
            self.ui.build_map_selection.setEnabled(True)
            self.ui.open_build_map.setEnabled(True)
            self.ui.navigation_button.setEnabled(True)

            self.ui.navigation_3d_button.setText(QCoreApplication.translate("myAGV","3D Navigation"))
            self.ui.navigation_3d_button.setStyleSheet(self.blue_button)

            self.msg_log(QCoreApplication.translate("myAGV", "Close 3D navigation",),current_time)


            close_launch = "navigation_active.launch"
            close_navigation = threading.Thread(target=self.navigation_close, args=(close_launch,), daemon=True)
            close_navigation.start()
            self.flag_all=False

    def map_navigation(self):
        current_time=self.get_current_time()

        if self.ui.navigation_button.isChecked():
            # if self.flag_build:
            #     QMessageBox.warning("",
            #                         QCoreApplication.translate("myAGV", "Warning"),
            #                         QCoreApplication.translate("myAGV", "Please turn off mapping before using this function."),
            #                         QMessageBox.Ok)
            if not self.radar_flag:
                QMessageBox.warning(None, "Warning", QCoreApplication.translate("myAGV", "Radar not open!"),QMessageBox.Ok)

                self.ui.navigation_button.setChecked(False)
                return


            else:
                self.ui.build_map_selection.setEnabled(False)
                self.ui.open_build_map.setEnabled(False)
                self.ui.navigation_3d_button.setEnabled(False)

                self.ui.navigation_button.setText(QCoreApplication.translate("myAGV", "Close Navigation"))
                self.ui.navigation_button.setStyleSheet(self.red_button)

                self.msg_log(QCoreApplication.translate("myAGV", "Open navigation"),current_time)

                self.flag_all = True
                open_navigation = threading.Thread(target=self.navigation_open, daemon=True)
                open_navigation.start()

        else:
            self.ui.build_map_selection.setEnabled(True)
            self.ui.open_build_map.setEnabled(True)
            self.ui.navigation_3d_button.setEnabled(True)

            self.ui.navigation_button.setText(QCoreApplication.translate("myAGV","Navigation"))
            self.ui.navigation_button.setStyleSheet(self.blue_button)
            self.msg_log(QCoreApplication.translate("myAGV", "Close navigation", current_time))
            close_launch = "navigation_active.launch"
            close_navigation = threading.Thread(target=self.navigation_close, args=(close_launch,), daemon=True)
            close_navigation.start()
            self.flag_all=False

    def start_testing(self):
        current_time = self.get_current_time()
        item = self.ui.comboBox_testing.currentText()

        if self.ui.start_detection_button.isChecked():

            if self.radar_flag:
                QMessageBox.warning(None, "Warning", QCoreApplication.translate("myAGV", "Please turn off the radar before using this function."),

                                    QMessageBox.Ok)
                self.ui.start_detection_button.setChecked(False)
                return

            else:

                self.ui.start_detection_button.setText(QCoreApplication.translate("myAGV","Stop Detection"))

                self.ui.comboBox_testing.setDisabled(True)

                self.msg_log(QCoreApplication.translate("myAGV","Start ") + item + QCoreApplication.translate("myAGV"," testing..."), current_time)


                # self.flag_all=True
                # if self.connections_agv():
                # self.connections()
                self.st = Start_testing(item, None)
                self.st.testing_finish.connect(self.testing_finished)
                self.button_status_switch(False)
                self.st.start()
                # else:
                #     print("No connection")

        else:
            # todo testing is running add warning
            self.st.terminate()
            # print("before execute finish")
            self.testing_finished(item) #更新延迟
            # print("after execure dinis")

            # self.flag_all=False

            # self.ui.comboBox_testing.setDisabled(False)
            # self.button_status_switch(True)

    def status_detecting(self): #TODO add status radar-flag
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
                self.ui.status_battery_backup_2.setStyleSheet("""
                    background-color:green;
                    border-radius: 9px;
                    border: 1px solid
                """)
            else:
                self.ui.status_battery_backup_2.setStyleSheet("""
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

        self.status = status_detect()
        self.status.ipaddress.connect(ip_set)
        self.status.voltages.connect(voltage_set)
        self.status.battery.connect(battery_set)
        self.status.powers.connect(powers_set)
        self.status.motors.connect(motors_set)

        # self.status.start()

    # ____for threading start executing

    def radar_open(self):

        def radar_high():
            GPIO.setmode(GPIO.BCM)
            time.sleep(0.1)
            GPIO.setup(20, GPIO.OUT)
            GPIO.output(20, GPIO.HIGH)

        radar_high()
        time.sleep(0.05)
        launch_command = "cd ~/myagv_ros | roslaunch myagv_odometry myagv_active.launch" # 使用ros 打开
        subprocess.run(['gnome-terminal', '-e', f"bash -c '{launch_command}; exec $SHELL'"])


    def radar_close(self, run_launch):
        def radar_low():
            GPIO.setmode(GPIO.BCM)
            time.sleep(0.1)
            GPIO.setup(20, GPIO.OUT)
            GPIO.output(20, GPIO.LOW)

        radar_low()
        time.sleep(0.05)

        close_command = "ps -ef | grep -E " + run_launch + " | grep -v 'grep' | awk '{print $2}' | xargs kill -9"
        subprocess.run(close_command, shell=True)

    def keyboard_open(self):
        # self.flag_all=True
        launch_command = "cd ~/myagv_ros | roslaunch myagv_teleop myagv_teleop.launch"
        # subprocess.run(['gnome-terminal', '-e', f"bash -c '{launch_command}; exec $SHELL'"])
        os.system("gnome-terminal -e 'bash -c \"cd /home/ubuntu; roslaunch ~/myagv_ros/src/myagv_teleop/launch/myagv_teleop.launch; exec bash\"'")

    def keyboard_close(self, run_launch):
        close_command = "ps -ef | grep -E " + run_launch + " | grep -v 'grep' | awk '{print $2}' | xargs kill -9"
        subprocess.run(close_command, shell=True)
        # self.flag_all=False

    def joystick_open(self):
        launch_command = "cd ~/myagv_ros | roslaunch myagv_ps2 myagv_ps2.launch"
        # launch_command="roslaunch myagv_ps2 myagv_ps2.launch"
        subprocess.run(['gnome-terminal', '-e', f"bash -c '{launch_command}; exec $SHELL'"])

    def joystick_close(self, run_launch):
        close_command = "ps -ef | grep -E " + run_launch + " | grep -v 'grep' | awk '{print $2}' | xargs kill -9"
        subprocess.run(close_command, shell=True)

    def joystick_open_number(self):
        launch_command = "cd ~/myagv_ros | roslaunch myagv_ps2 myagv_ps2_number.launch"
        subprocess.run(['gnome-terminal', '-e', f"bash -c '{launch_command}; exec $SHELL'"])

    def joystick_close_number(self, run_launch):
        close_command = "ps -ef | grep -E " + run_launch + " | grep -v 'grep' | awk '{print $2}' | xargs kill -9"
        subprocess.run(close_command, shell=True)

    def gmapping_build_open(self):
        launch_command = "cd ~/myagv_ros | roslaunch myagv_navigation myagv_slam_laser.launch"

        os.system("gnome-terminal -e 'bash -c \"cd /home/ubuntu; roslaunch ~/myagv_ros/src/myagv_navigation/launch/myagv_slam_laser.launch; exec bash\"'")

        # subprocess.run(['gnome-terminal', '-e', f"bash -c '{launch_command}; exec $SHELL'"])

    def gmapping_build_close(self, run_launch):


        close_command = "ps -ef | grep -E " + run_launch + " | grep -v 'grep' | awk '{print $2}' | xargs kill -9"
        # subprocess.run(close_command, shell=True)

        os.system("ps -ef | grep -E rviz" +
                  " | grep -v 'grep' | awk '{print $2}' | xargs kill -9")

        os.system("ps -ef | grep -E " + run_launch +
                  " | grep -v 'grep' | awk '{print $2}' | xargs kill -9")

    def cartographer_build_open(self):
        launch_command = "cd ~/myagv_ros | roslaunch cartographer_ros demo_myagv.launch"
        subprocess.run(['gnome-terminal', '-e', f"bash -c '{launch_command}; exec $SHELL'"])


    def cartographer_build_close(self): #TODO 内置ros 未更新，无相关文件；未检测

        close_command = "ps -ef | grep -E " + "demo_myagv.launch" + " | grep -v 'grep' | awk '{print $2}' | xargs kill -9"

        os.system("ps -ef | grep -E rviz" +
                  " | grep -v 'grep' | awk '{print $2}' | xargs kill -9")
        subprocess.run(close_command, shell=True)


    def save_map_file(self):
        # cd_command=""
        launch_command="rosrun map_server map_saver"
        subprocess.run(['gnome-terminal', '-e', f"bash -c '{launch_command}; exec $SHELL'"])
        subprocess.run(
            "cp /home/ubuntu/map.pgm /home/ubuntu/myagv_ros/src/myagv_navigation/map/my_map.pgm && cp /home/ubuntu/map.yaml /home/ubuntu/myagv_ros/src/myagv_navigation/map/my_map.yaml")

        current_time = self.get_current_time()
        self.msg_log(QCoreApplication.translate("myAGV","Save successfully!"), current_time)

        QMessageBox.information(None, "",
                                f"Save successfully! \n Save Path:\n /home/ubuntu/myagv_ros/src/myagv_navigation/map/my_map.pgm\n /home/ubuntu/myagv_ros/src/myagv_navigation/map/my_map.yaml")

    def navigation_open(self):

        launch_command = "cd ~/myagv_ros | roslaunch myagv_navigation navigation_active.launch"

        os.system("gnome-terminal -e 'bash -c \"cd /home/ubuntu; roslaunch ~/myagv_ros/src/myagv_navigation/launch/navigation_active.launch; exec bash\"'")

        # subprocess.run(launch_command, shell=True)

    def navigation_close(self, run_launch):
        close_command = "ps -ef | grep -E " + run_launch + " | grep -v 'grep' | awk '{print $2}' | xargs kill -9"

        os.system("ps -ef | grep -E rviz" +
                  " | grep -v 'grep' | awk '{print $2}' | xargs kill -9")

        os.system("ps -ef | grep -E " + run_launch +
                  " | grep -v 'grep' | awk '{print $2}' | xargs kill -9")
        # subprocess.run(close_command, shell=True)

    def closeEvent(self, event):
        print("Closed")
        self.status.terminate()


class Start_testing(QThread): #
    testing_finish = Signal(str)
    testing_stop = Signal()

    def __init__(self, testing, myagv):
        super().__init__() #TODO 断开雷达后会会有延迟，需多尝试几次

        self.test = testing
        self.agv = MyAgv("/dev/ttyAMA2", 115200)

    def motor_testing(self):

        self.agv.go_ahead(100)
        time.sleep(4)

        self.agv.pan_left(100)

        time.sleep(4)

        self.agv.pan_left(100)
        time.sleep(4)

        self.agv.counterclockwise_rotation(100)
        time.sleep(8)

        self.agv.clockwise_rotation(100)
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
#TODO add radar connections
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
    battery = Signal(bool, bool)
    powers = Signal(float, float)
    motors = Signal(bool)

    def __init__(self):
        super().__init__()
        self.agv = MyAgv("/dev/ttyAMA2",115200)

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
        for i in range(5):

            data = self.agv.get_battery_info()
            if data:
                break

        batterys = data[0]
        battery_1 = batterys[1]
        battery_2 = batterys[0]


        b_1_voltage = data[1]

        b_2_voltage = data[2]

        print(data,batterys,battery_1,battery_2,"batterys")
        self.battery.emit(int(battery_1), int(battery_2)) #todo 已修复电池插入后的显示问题

        # voltage
        power_1=power_2=0
        if b_1_voltage:
            # voltage_1 = b_1_voltage
            power_1 =  b_1_voltage / (12.2) * 100

        if b_2_voltage:
            # voltage_2 = b_2_voltage
            power_2 = b_2_voltage / (12.2) * 100


        print(power_2,power_1,"power 1/ power 2")
        time.sleep(0.2)
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

        while self.agv:

            try:

                ip = self.get_ipaddress()
                if ip:
                    self.ipaddress.emit(ip)
                time.sleep(2)

                self.get_info()
                time.sleep(2)
                self.get_motors_run()
                time.sleep(1)
            except Exception as e:pass

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
