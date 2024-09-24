# encoding:utf-8
import os
from typing import Optional

import cv2
import subprocess
import sys
import threading
import time
import traceback
import socket
import json

from PyQt5.QtCore import pyqtSignal, QCoreApplication, QThread, QTranslator
from PyQt5.QtWidgets import QWidget, QApplication, QMessageBox, QSizePolicy, QMainWindow
from operations_UI.Ui_AGV_operations import Ui_myAGV
from pymycobot import MyAgv
from operations_UI.color_picker import ColorCircle
from operations_UI.component_status import ComponentsSet

if os.name == "posix":
    import RPi.GPIO as GPIO

Ros_flag = False


class CommandExecutor:
    
    @classmethod
    def check_output(cls, command) -> str:
        output = ''
        try:
            output = subprocess.check_output(command, shell=True)
        except subprocess.CalledProcessError as e:
            print(f"Command execution failed: {e}")
            traceback.print_exc()
        finally:
            if output:
                print(f" * Command output: {output}")
                return output.decode("utf-8").strip()
            else:
                return output
        
    @classmethod
    def check_radar_running(cls) -> bool:
        wordcount = cls.check_output("ps -ef | grep -E myagv_active.launch | grep -v 'grep' | wc -l")
        return int(wordcount) > 0


class MyAGVTesttoolApplication(QMainWindow):   # 测试工具

    def __init__(self):
        super().__init__()
        self.ui = Ui_myAGV()
        self.ui.setupUi(self)
        self.ui.color_palette.setVisible(False)
        self.led_default = [255, 0, 0]  # red light
        self._app = QApplication.instance()
        self.translator = QTranslator(self)
        self.agv_handler = None
        self.function_controller = None
        self.agv_status_detector: Optional[AGVStatusDetector] = None
        self.label_color = None

        self.radar_flag = False             # 雷达启动标识
        self.keyboard_flag = False          # 键盘启动标识
        self.joystick_flag = False          # 操纵杆启动标识
        self.flag_led = False               # led灯启动标识
        self.flag_all = False               # 全部启动标识
        self.flag_build = False             # 构建地图启动标识
        self.camera = None                  # 相机启动标识
        self.is_function_testing = False    # 是否处于功能检测中

        self.red_button = """
            background-color: rgb(198, 61, 47);
            color: rgb(255, 255, 255);
            border-radius: 7px;
            border: 2px groove gray;
            border-style: outset;
            font: 75 9pt "Arial";
        """

        self.green_button = """
            background-color: rgb(39, 174, 96);
            color: rgb(255, 255, 255);
            border-radius: 7px;
            border: 2px groove gray;
            border-style: outset;
            font: 75 9pt "Arial";
        """

        self.blue_button = """
            background-color:rgb(41, 128, 185);
            color: rgb(255, 255, 255);
            border-radius: 10px;
            border: 2px groove gray;
            border-style: outset;
            font: 75 9pt "Arial";
        """

        self.grey_button = """
            background-color: #7F8487;
            color: rgb(255, 255, 255);
            border-radius: 10px;
            border: 2px groove gray;
            border-style: outset;
            font: 75 9pt "Arial";
        """

        self.light_grey = """
            background-color:grey;
            border-radius: 9px;
            border: 1px solid
        """

        self.light_green = """
            background-color:green;
            border-radius: 9px;
            border: 1px solid
        """

    def initialize(self):
        QComboBoxStyle = "border: 0.5px solid grey; background: white;color: black;"

        self.color_painter()
        self.ui.comboBox_testing.setStyleSheet(QComboBoxStyle)
        self.ui.comboBox_language_selection.setStyleSheet(QComboBoxStyle)
        self.ui.basic_control_selection.setStyleSheet(QComboBoxStyle)
        self.ui.build_map_selection.setStyleSheet(QComboBoxStyle)

        self.ui.label_value.setVisible(False)
        self.ui.lineEdit_RGB.setStyleSheet("background:None")
        self.ui.lineEdit_HEX.setStyleSheet("background:None")

        self.ui.logo_lab.setVisible(False)
        self.ui.menu_widget.setVisible(False)
        self.ui_set()

        self.status_detecting()
        self.language_initial()

        running = CommandExecutor.check_radar_running()     # 检测雷达是否打开
        if running:
            print(" * isChecked", self.ui.radar_button.isChecked())
            self.ui.radar_button.setChecked(True)
            print(" * isChecked", self.ui.radar_button.isChecked())
            self.ui.start_detection_button.setCheckable(False)
            self.ui.start_detection_button.setStyleSheet(self.grey_button)
            self.ui.Restore_btn.setCheckable(False)
            self.ui.Restore_btn.setStyleSheet(self.grey_button)
            self.ui.radar_button.setStyleSheet(self.red_button)
            self.ui.radar_button.setText(QCoreApplication.translate("myAGV", "OFF"))
        else:
            self.try_connect_agv()
            if self.agv_status_detector is not None:
                self.agv_status_detector.agv = self.agv_handler

        global Ros_flag
        Ros_flag = running
        self.radar_flag = running
        print(" * Radar status: ", running)

        view = self.ui.comboBox_testing.view()
        view.setRowHidden(3, True)
        GPIO.setmode(GPIO.BCM)

        if not self.radar_flag and self.agv_status_detector is not None:
            print(" * Auto start status detector ...")
            self.agv_status_detector.start()
        else:
            print(" * Radar is on, status detector is not started.")
        ip_str = AGVStatusDetector.get_ipaddress()
        print(" * IP address: ", ip_str)
        self.ui.lineEdit.setText(ip_str)

    def try_connect_agv(self):
        if self.radar_flag is True:  # open radar
            QMessageBox.warning(
                self,
                QCoreApplication.translate("myAGV", "Warning"),
                QCoreApplication.translate("myAGV", "Please turn off the radar before using this function.")
            )
        else:
            self.agv_handler = MyAgv("/dev/ttyS0", 115200)
        return self.radar_flag is False

    @classmethod
    def set_button_status(cls, button_ui, status, color):
        button_ui.setEnabled(status)
        button_ui.setStyleSheet(color)

    def color_painter(self):
        self.label_color = QWidget()

        color = ColorCircle(self, [255, 0, 0])

        label_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
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
                QCoreApplication.translate("myAGV", "English"),
                QCoreApplication.translate("myAGV", "Chinese")
            ]

            basic_control_params = [
                QCoreApplication.translate("myAGV", "Keyboard Control"),
                QCoreApplication.translate("myAGV", "Joystick-Alphabet"),
                QCoreApplication.translate("myAGV", "Joystick-Number")
            ]

            map_nav_params = [
                QCoreApplication.translate("myAGV", "Gmapping"),
                # QCoreApplication.translate("myAGV", "Cartographer"),
                QCoreApplication.translate("myAGV", "3D Mapping")
            ]

            test_params = [
                QCoreApplication.translate("myAGV", "Motor"),
                QCoreApplication.translate("myAGV", "LED"),
                QCoreApplication.translate("myAGV", "3D Camera"),
                QCoreApplication.translate("myAGV", "Pump")
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

            self.ui.comboBox_language_selection.currentTextChanged.connect(self.language_change)  # todo add langua
            self.ui.horizontal_Slider.setRange(0, 511)
            self.ui.horizontal_Slider.setValue(511)

            self.ui.start_detection_button.clicked.connect(self.start_testing)

            # self.ui.Restore_btn.pressed.connect(self.restore_btn)
            # self.ui.Restore_btn.released.connect(self.release_style)
            self.ui.Restore_btn.clicked.connect(self.restore_btn)

        ui_params()
        ui_functions()
        ui_buttons()

    def release_style(self):
        self.ui.Restore_btn.setStyleSheet("""
                background-color: rgb(39, 174, 96);
                color: rgb(255, 255, 255);
                border-radius: 7px;
                border: 2px groove gray;
                border-style: outset;
                font: 75 9pt "Arial";
            """)

    def restore_btn(self):
        if self.radar_flag:  # open radar
            QMessageBox.warning(
                self,
                QCoreApplication.translate("myAGV", "Warning"),
                QCoreApplication.translate("myAGV", "Please turn off the radar before using this function."),
                QMessageBox.Ok
            )
            return

        self.msg_log(QCoreApplication.translate("myAGV", "Motor Restore"))
        if self.try_connect_agv():
            self.ui.Restore_btn.setStyleSheet("""
                background-color: rgb(31, 140, 77);
                color: rgb(255, 255, 255);
                border-radius: 7px;
                border: 2px groove gray;
                border-style: outset;
                font: 75 9pt "Arial";
            """)
            self.agv_handler.restore()
            self.release_style()

    def testing_finished(self, item: str, is_stop: bool = False):
        self.try_connect_agv()

        if is_stop is True:
            self.msg_log(QCoreApplication.translate("myAGV", "Stop") + item + QCoreApplication.translate("myAGV", " testing"))
        else:
            self.msg_log(QCoreApplication.translate("myAGV", "Finish") + item + QCoreApplication.translate("myAGV", " testing"))

        if item == "LED" or item == "LED灯":  # TODO 可更新:
            self.flag_led = False  # LED light testing finished, remaining the current light
            # self.agv_handler.set_led(1, 255, 0, 0)
        if item == "Pump" or item == "吸泵":
            # stop testing to close pump

            GPIO.output(26, GPIO.HIGH)  # 关闭吸泵
            time.sleep(0.05)
            GPIO.output(19, GPIO.LOW)  # 关闭气阀
            time.sleep(0.05)
            GPIO.output(19, GPIO.HIGH)  # 气阀状态还原
            time.sleep(0.05)

        if item == "Motor" or item == "电机":
            self.agv_handler.stop()

        if item == "2D Camera" or item == "2D 相机":
            # self.camera.close()
            cmd = 'camera_testing.py'
            os.system("ps -ef | grep -E " + cmd + " | grep -v 'grep' | awk '{print $2}' | xargs kill -9")

        testing_status = self.ui.start_detection_button.isEnabled()
        self.ui.start_detection_button.setChecked(not testing_status)
        self.ui.start_detection_button.setText(QCoreApplication.translate("myAGV", "Start Detection"))
        self.ui.comboBox_testing.setDisabled(False)
        self.button_status_switch(True)
        self.is_function_testing = False
        ComponentsSet.testing_open_close(self.ui, True)

    def lighter_set(self, color):
        r = color.red()
        g = color.green()
        b = color.blue()

        rgb_color = f"({r}, {g}, {b})"

        hex = color.name()

        self.ui.lineEdit_HEX.setText(hex)
        self.ui.lineEdit_RGB.setText(rgb_color)

        if self.radar_flag is True and self.isVisible() is True:  # open radar

            QMessageBox.warning(
                self,
                QCoreApplication.translate("myAGV", "Warning"),
                QCoreApplication.translate("myAGV", "Please turn off the radar before using this function."),
                QMessageBox.Ok
            )
        elif self.flag_led:
            QMessageBox.warning(
                self,
                QCoreApplication.translate("myAGV", "Warning"),
                QCoreApplication.translate("myAGV", "Please stop the detection before using the led."),
                QMessageBox.Ok
            )
        elif self.is_function_testing:
            QMessageBox.warning(
                self,
                QCoreApplication.translate("myAGV", "Warning"),
                QCoreApplication.translate("myAGV", "Functional detection is performing, please wait for it to complete!"),
                QMessageBox.Ok
            )
        else:
            if not self.flag_led and self.agv_handler is not None:
                self.agv_handler.set_led(1, r, g, b)

    @classmethod
    def get_current_time(cls):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

    def language_initial(self):
        with open("translation/language.json", "r", encoding='utf-8') as f:
            language = json.loads(f.read())
        lang = language["language"]
        self.language_selection(lang)

    def language_change(self):
        lang_write = ""
        lang = self.ui.comboBox_language_selection.currentText()
        if lang == "English" or lang == "英语":
            lang_write = "en"
        if lang == "Chinese" or lang == "中文":
            lang_write = "zh_CN"

        data = {"language": lang_write}
        with open("translation/language.json", "w") as f:
            json.dump(data, f, indent=4)
        self.language_initial()

    def retranslateUi(self):
        self.ui.retranslateUi(self)
        self.ui.radar_button.setChecked(self.radar_flag)
        if self.radar_flag is True:
            self.ui.radar_button.setChecked(True)
            self.ui.radar_button.setText(QCoreApplication.translate("myAGV", "OFF"))
        else:
            self.ui.radar_button.setText(QCoreApplication.translate("myAGV", "ON"))

    def language_selection(self, lang):
        """
        根据选择语言切换
        :return:
        """
        if lang == "en" or lang == "英文":
            self._app.removeTranslator(self.translator)
            self.retranslateUi()
        if lang == "zh_CN" or lang == "中文":
            self.translator.load("translation/operations_lang.qm")
            self._app.installTranslator(self.translator)
            self.retranslateUi()

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

    def msg_log(self, msg, current_time=None):
        if current_time is None:
            current_time = self.get_current_time()
        msg_log = '[' + str(current_time) + ']' + msg
        self.ui.textBrowser.append(msg_log)

    def msg_error(self, msg, current_time):
        with open("error.log", "w") as f:
            f.write(msg)

        msg_error = '[' + str(current_time) + ']' + msg
        self.ui.textBrowser.append(msg_error)

    def radar_control(self):
        global Ros_flag
        if self.ui.radar_button.isChecked():
            self.agv_status_detector.quit()

            Ros_flag = True
            time.sleep(0.2)

            self.ui.start_detection_button.setCheckable(False)  # 雷达打开时检测按钮不可使用
            self.ui.start_detection_button.setStyleSheet(self.grey_button)
            self.ui.Restore_btn.setCheckable(False)
            self.ui.Restore_btn.setStyleSheet(self.grey_button)
            if self.flag_all:
                return

            self.ui.radar_button.setStyleSheet(self.red_button)
            self.ui.radar_button.setText(QCoreApplication.translate("myAGV", "OFF"))

            msg = QCoreApplication.translate("myAGV", "Radar open...")
            current_time = self.get_current_time()
            self.msg_log(msg, current_time)

            # add limit for testing and led
            ComponentsSet.radar_open_close(self.ui, False)

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
            if self.flag_all:  # other functions are running...
                QMessageBox.warning(
                    self,
                    QCoreApplication.translate("myAGV", "Warning"),
                    QCoreApplication.translate("myAGV", "Other functions are running."),
                    QMessageBox.Ok
                )
                self.ui.radar_button.setChecked(True)
                return
            else:

                self.ui.radar_button.setStyleSheet(self.green_button)

                self.ui.radar_button.setText(QCoreApplication.translate("myAGV", "ON"))

                msg = QCoreApplication.translate("myAGV", "close radar")
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
                    Ros_flag = False
                    time.sleep(4)  # 等待2s后，释放检测按钮（可用）
                    ComponentsSet.radar_open_close(self.ui, True)
                    self.ui.start_detection_button.setCheckable(True)
                    self.ui.start_detection_button.setStyleSheet(self.blue_button)
                    self.ui.Restore_btn.setCheckable(True)
                    self.ui.Restore_btn.setStyleSheet(self.green_button)
                    self.try_connect_agv()
                    self.agv_status_detector.agv = self.agv_handler
                    self.agv_status_detector.start()

                except Exception as e:
                    e = traceback.format_exc()
                    self.msg_error(e, current_time)

                # print("close radar set")

    def basic_control(self):

        control_item_basic = self.ui.basic_control_selection.currentText()

        if self.ui.basic_control_button.isChecked():

            if not self.radar_flag:
                QMessageBox.warning(
                    self,
                    QCoreApplication.translate("myAGV", "Warning"),
                    QCoreApplication.translate("myAGV", "Radar not open!"),
                    QMessageBox.Ok
                )
                self.ui.basic_control_button.setChecked(False)
                return
                # print(self.radar_flag, "basic_control radar not")
            else:
                # print(self.radar_flag, "basic_control radar yes")
                self.ui.basic_control_button.setStyleSheet(self.red_button)
                self.ui.basic_control_button.setText(
                    QCoreApplication.translate("myAGV", "OFF"))

                self.ui.basic_control_selection.setEnabled(False)  # 设置下拉框不可选区
                self.flag_all = True

                if control_item_basic == "Keyboard Control" or control_item_basic == "键盘控制":
                    self.keyboard_flag = True
                    try:
                        # self.flag_all=True
                        msg = QCoreApplication.translate("myAGV", "Keyboard open...")
                        current_time = self.get_current_time()
                        self.msg_log(msg, current_time)

                        keyboard_open = threading.Thread(
                            target=self.keyboard_open, daemon=True)
                        keyboard_open.start()

                    except Exception as e:
                        # self.flag_all=False
                        e = traceback.format_exc()
                        self.msg_error(e, current_time)

                elif control_item_basic == "Joystick-Alphabet" or control_item_basic == "手柄控制(字母)":
                    self.joystick_flag = True
                    try:
                        # self.flag_all=True
                        msg = QCoreApplication.translate("myAGV", "Open joystick control...")
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
                        msg = QCoreApplication.translate("myAGV", "Open joystick control")
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
            self.ui.basic_control_button.setText(
                QCoreApplication.translate("myAGV", "ON"))

            self.ui.basic_control_selection.setEnabled(True)

            self.flag_all = False
            if control_item_basic == "Keyboard Control" or control_item_basic == "键盘控制":

                msg = QCoreApplication.translate(
                    "myAGV", "Close keyboard control")
                current_time = self.get_current_time()
                try:

                    self.msg_log(msg, current_time)
                    keyboard_run_launch = "myagv_teleop.launch"

                    keyboard_close = threading.Thread(target=self.keyboard_close, args=(keyboard_run_launch,), daemon=True)
                    keyboard_close.start()
                    self.keyboard_flag = False
                    # print("close key")
                except Exception as e:
                    e = traceback.format_exc()
                    self.msg_error(e, current_time)

            elif control_item_basic == "Joystick-Alphabet" or control_item_basic == "手柄控制(字母)":
                self.joystick_flag = False
                # print("close joy")

                msg = QCoreApplication.translate(
                    "myAGV", "close joystick control")
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

                msg = QCoreApplication.translate(
                    "myAGV", "close joystick control")
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
            QMessageBox.warning(
                self,
                QCoreApplication.translate("myAGV", "Warning"),
                QCoreApplication.translate("myAGV", "Radar not open!"),
                QMessageBox.Ok
            )
            self.ui.save_map_button.setChecked(False)
            return
        else:
            self.flag_all = True
            save_map = threading.Thread(target=self.save_map_file, daemon=True)
            save_map.start()
            self.flag_all = False

    def open_build_map(self):
        def gmapping_build():
            open_gmapping_build = threading.Thread(
                target=self.gmapping_build_open, daemon=True)
            open_gmapping_build.start()

        def gmapping_close():
            close_launch = "myagv_slam_laser.launch"
            close_gmapping_build = threading.Thread(
                target=self.gmapping_build_close, args=(close_launch,), daemon=True)
            # print("quiuii build map")
            close_gmapping_build.start()

        def cartographer_build():
            open_cart_build = threading.Thread(
                target=self.cartographer_build_open, daemon=True)
            open_cart_build.start()

        def cartographer_close():
            close_cart_build = threading.Thread(
                target=self.cartographer_build_close, daemon=True)
            close_cart_build.start()

        build_map_method = self.ui.build_map_selection.currentText()

        current_build = self.get_current_time()

        # keyboard_flag=False

        if self.ui.open_build_map.isChecked():

            if not self.radar_flag:  # 检测雷达
                QMessageBox.warning(
                    self,
                    QCoreApplication.translate("myAGV", "Warning"),
                    QCoreApplication.translate("myAGV", "Radar not open!"),
                    QMessageBox.Ok
                )
                self.ui.open_build_map.setChecked(False)
                return

            if not self.keyboard_flag:  # 检测键盘控制
                QMessageBox.warning(
                    self,
                    QCoreApplication.translate("myAGV", "Warning"),
                    QCoreApplication.translate("myAGV", "Please turn on keyboard control before mapping."),
                    QMessageBox.Ok
                )
                self.ui.open_build_map.setChecked(False)
                return

            else:
                self.ui.build_map_selection.setEnabled(False)  # 建图方式不可选取
                self.ui.navigation_3d_button.setEnabled(False)  # 建图打开后导航均不可用
                self.ui.navigation_3d_button.setStyleSheet(self.grey_button)
                self.ui.navigation_button.setEnabled(False)
                self.ui.navigation_button.setStyleSheet(self.grey_button)

                self.flag_build = True
                self.flag_all = True

                self.ui.open_build_map.setText(
                    QCoreApplication.translate("myAGV", "Close Build Map"))
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
                    self.msg_log(QCoreApplication.translate(
                        "myAGV", "Open Gmapping..."), current_build)
                    gmapping_build()

                if build_map_method == "Cartographer":
                    self.msg_log(QCoreApplication.translate(
                        "myAGV", "Open Cartographer..."), current_build)
                    cartographer_build()

        else:
            self.ui.open_build_map.setStyleSheet(self.blue_button)
            self.ui.open_build_map.setText(
                QCoreApplication.translate("myAGV", "Open Build Map"))

            if build_map_method == "Gmapping":
                self.msg_log(QCoreApplication.translate(
                    "myAGV", "Close Gmapping"), current_build)
                gmapping_close()

            if build_map_method == "Cartographer":
                self.msg_log(QCoreApplication.translate(
                    "myAGV", "Close Cartographer"), current_build)
                cartographer_close()

            # 关闭建图打开导航按钮

            self.ui.build_map_selection.setEnabled(True)
            self.ui.navigation_3d_button.setEnabled(True)  # 建图关闭后导航可用
            self.ui.navigation_3d_button.setStyleSheet(self.blue_button)
            self.ui.navigation_button.setEnabled(True)
            self.ui.navigation_button.setStyleSheet(self.blue_button)

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

        current_time = self.get_current_time()

        if self.ui.navigation_3d_button.isChecked():

            # if self.flag_build:
            #     QMessageBox.warning(None,
            #                         QCoreApplication.translate("myAGV", "Warning"),
            #                         QCoreApplication.translate("myAGV",
            #                                                    "Please turn off mapping before using this function."),
            #                         QMessageBox.Ok)

            if not self.radar_flag:
                QMessageBox.warning(
                    self,
                    QCoreApplication.translate("myAGV", "Warning"),
                    QCoreApplication.translate("myAGV", "Radar not open!"),
                    QMessageBox.Ok
                )

                self.ui.navigation_3d_button.setChecked(False)
                return

            else:
                self.ui.build_map_selection.setEnabled(False)  # 建图下拉框不可选
                self.ui.open_build_map.setEnabled(False)  # 打开建图不可选
                self.ui.navigation_button.setEnabled(False)  # 导航不可选

                self.ui.navigation_3d_button.setText(
                    QCoreApplication.translate("myAGV", "Close 3D Navigation"))
                self.ui.navigation_3d_button.setStyleSheet(self.red_button)

                self.msg_log(QCoreApplication.translate(
                    "myAGV", "Open 3D navigation"), current_time)

                self.flag_all = True
                open_navigation = threading.Thread(
                    target=self.navigation_open, daemon=True)
                open_navigation.start()

        else:
            self.ui.build_map_selection.setEnabled(True)
            self.ui.open_build_map.setEnabled(True)
            self.ui.navigation_button.setEnabled(True)

            self.ui.navigation_3d_button.setText(
                QCoreApplication.translate("myAGV", "3D Navigation"))
            self.ui.navigation_3d_button.setStyleSheet(self.blue_button)

            self.msg_log(QCoreApplication.translate(
                "myAGV", "Close 3D navigation"), current_time)

            close_launch = "navigation_active.launch"
            close_navigation = threading.Thread(
                target=self.navigation_close, args=(close_launch,), daemon=True)
            close_navigation.start()
            self.flag_all = False

    def map_navigation(self):
        current_time = self.get_current_time()

        if self.ui.navigation_button.isChecked():

            if not self.radar_flag:
                QMessageBox.warning(
                    self,
                    QCoreApplication.translate("myAGV", "Warning"),
                    QCoreApplication.translate("myAGV", "Radar not open!"),
                    QMessageBox.Ok
                )
                self.ui.navigation_button.setChecked(False)

            elif self.keyboard_flag is False:
                QMessageBox.warning(
                    self,
                    QCoreApplication.translate("myAGV", "Warning"),
                    QCoreApplication.translate("myAGV", "Keyboard Control not open!"),
                    QMessageBox.Ok
                )
                self.ui.navigation_button.setChecked(False)
                return
            else:
                self.ui.build_map_selection.setEnabled(False)
                self.ui.open_build_map.setEnabled(False)
                self.ui.open_build_map.setStyleSheet(self.grey_button)
                self.ui.navigation_3d_button.setEnabled(False)
                self.ui.navigation_3d_button.setStyleSheet(self.grey_button)

                self.ui.navigation_button.setText(
                    QCoreApplication.translate("myAGV", "Close Navigation"))
                self.ui.navigation_button.setStyleSheet(self.red_button)

                self.msg_log(QCoreApplication.translate(
                    "myAGV", "Open navigation"), current_time)

                self.flag_all = True
                open_navigation = threading.Thread(
                    target=self.navigation_open, daemon=True)
                open_navigation.start()

        else:
            self.ui.build_map_selection.setEnabled(True)
            self.ui.open_build_map.setEnabled(True)
            self.ui.open_build_map.setStyleSheet(self.blue_button)
            self.ui.navigation_3d_button.setEnabled(True)
            self.ui.navigation_3d_button.setStyleSheet(self.blue_button)

            self.ui.navigation_button.setText(QCoreApplication.translate("myAGV", "Navigation"))
            self.ui.navigation_button.setStyleSheet(self.blue_button)
            self.msg_log(QCoreApplication.translate("myAGV", "Close navigation"), current_time)
            close_launch = "navigation_active.launch"
            close_navigation = threading.Thread(
                target=self.navigation_close, args=(close_launch,), daemon=True)
            # print("navagation_start_close ---iiii")
            close_navigation.start()
            self.flag_all = False

    def ss(self, item):
        pass

    # print(item, "iii")
    @classmethod
    def translate(cls, text: str, context: str = "myAGV") -> str:
        return QCoreApplication.translate(context, text)

    def start_testing(self):
        current_time = self.get_current_time()
        item = self.ui.comboBox_testing.currentText()

        if self.ui.start_detection_button.isChecked():
            if self.radar_flag:
                QMessageBox.warning(
                    self,
                    QCoreApplication.translate("myAGV", "Warning"),
                    QCoreApplication.translate("myAGV", "Please turn off the radar before using this function."),
                    QMessageBox.Ok
                )

            else:
                self.is_function_testing = True
                self.ui.start_detection_button.setText(QCoreApplication.translate("myAGV", "Stop Detection"))

                self.ui.comboBox_testing.setDisabled(True)

                self.msg_log(
                    QCoreApplication.translate("myAGV", "Start ") +
                    item +
                    QCoreApplication.translate("myAGV", " testing ..."),
                    current_time
                )

                self.function_controller = FunctionCheckController(item, self.agv_handler)
                self.function_controller.testing_finish.connect(self.testing_finished)
                self.button_status_switch(False)

                if item == "LED" or item == "LED灯":
                    self.flag_led = True

                ComponentsSet.testing_open_close(self.ui, False)

                self.function_controller.start()
        else:
            # todo testing is running add warning

            if item == "2D Camera":
                self.testing_finished("2D Camera")
            elif self.function_controller:
                self.function_controller.terminate()
                self.testing_finished(item, is_stop=True)  # 更新延迟
            else:
                pass

    def status_detecting(self):  # TODO add status radar-flag
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

        def motors_set(status, curr):
            ui_motors = [self.ui.electricity_motor1, self.ui.electricity_motor2,
                         self.ui.electricity_motor3, self.ui.electricity_motor4]

            if status:
                self.ui.status_motor_1.setStyleSheet(
                    """
                    background-color:green;
                    border-radius: 9px;
                    border: 1px solid
                    """)
                # self.ui.electricity_display.setText(curr)
            else:
                self.ui.status_motor_1.setStyleSheet(
                    """
                    background-color:grey;
                    border-radius: 9px;
                    border: 1px solid
                    """)
                # self.ui.electricity_display.setText(curr)

            for el, val in enumerate(zip(ui_motors, curr)):
                val[0].setText(str(val[1]))

        self.agv_status_detector = AGVStatusDetector(agv=self.agv_handler)
        self.agv_status_detector.ipaddress.connect(ip_set)
        self.agv_status_detector.voltages.connect(voltage_set)
        self.agv_status_detector.battery.connect(battery_set)
        self.agv_status_detector.powers.connect(powers_set)
        self.agv_status_detector.motors.connect(motors_set)

    def radar_open(self):
        def radar_high():
            GPIO.setmode(GPIO.BCM)
            time.sleep(0.1)
            GPIO.setup(20, GPIO.OUT)
            GPIO.output(20, GPIO.HIGH)

        radar_high()
        time.sleep(0.05)
        launch_command = "roslaunch myagv_odometry myagv_active.launch"  # 使用ros 打开
        subprocess.run(['gnome-terminal', '-e', f"bash -c '{launch_command}; exec $SHELL'"])

    def radar_close(self, run_launch):
        def radar_low():
            GPIO.setmode(GPIO.BCM)
            time.sleep(0.1)
            GPIO.setup(20, GPIO.OUT)
            GPIO.output(20, GPIO.LOW)

        radar_low()
        time.sleep(0.05)

        close_command = "ps -ef | grep -E " + run_launch + " | grep -v 'grep' | awk '{print $2}' | xargs kill -2"
        subprocess.run(close_command, shell=True)

    def keyboard_open(self):
        # self.flag_all=True
        launch_command = "roslaunch myagv_teleop myagv_teleop.launch"
        # subprocess.run(['gnome-terminal', '-e', f"bash -c '{launch_command}; exec $SHELL'"])
        os.system(
            "gnome-terminal -e 'bash -c \"roslaunch ~/myagv_ros/src/myagv_teleop/launch/myagv_teleop.launch; exec bash\"'")

    def keyboard_close(self, run_launch):
        close_command = "ps -ef | grep -E " + run_launch + \
                        " | grep -v 'grep' | awk '{print $2}' | xargs kill -2"
        subprocess.run(close_command, shell=True)
        # self.flag_all=False

    def joystick_open(self):
        launch_command = "roslaunch myagv_ps2 myagv_ps2.launch"
        # launch_command="roslaunch myagv_ps2 myagv_ps2.launch"
        subprocess.run(
            ['gnome-terminal', '-e', f"bash -c '{launch_command}; exec $SHELL'"])

    def joystick_close(self, run_launch):
        close_command = "ps -ef | grep -E " + run_launch + \
                        " | grep -v 'grep' | awk '{print $2}' | xargs kill -2"
        subprocess.run(close_command, shell=True)

    def joystick_open_number(self):
        launch_command = "roslaunch myagv_ps2 myagv_ps2_number.launch"
        subprocess.run(
            ['gnome-terminal', '-e', f"bash -c '{launch_command}; exec $SHELL'"])

    def joystick_close_number(self, run_launch):
        close_command = "ps -ef | grep -E " + run_launch + \
                        " | grep -v 'grep' | awk '{print $2}' | xargs kill -2"
        subprocess.run(close_command, shell=True)

    def gmapping_build_open(self):
        launch_command = "roslaunch myagv_navigation myagv_slam_laser.launch"

        os.system(
            "gnome-terminal -e 'bash -c \"roslaunch ~/myagv_ros/src/myagv_navigation/launch/myagv_slam_laser.launch; exec bash\"'")

        # subprocess.run(['gnome-terminal', '-e', f"bash -c '{launch_command}; exec $SHELL'"])

    def gmapping_build_close(self, run_launch):
        close_command = "ps -ef | grep -E " + run_launch + \
                        " | grep -v 'grep' | awk '{print $2}' | xargs kill -2"
        # subprocess.run(close_command, shell=True)

        os.system("ps -ef | grep -E rviz" +
                  " | grep -v 'grep' | awk '{print $2}' | xargs kill -2")

        os.system("ps -ef | grep -E " + run_launch +
                  " | grep -v 'grep' | awk '{print $2}' | xargs kill -2")

    def cartographer_build_open(self):
        launch_command = "roslaunch cartographer_ros demo_myagv.launch"
        subprocess.run(
            ['gnome-terminal', '-e', f"bash -c '{launch_command}; exec $SHELL'"])

    def cartographer_build_close(self):

        close_command = "ps -ef | grep -E " + "demo_myagv.launch" + \
                        " | grep -v 'grep' | awk '{print $2}' | xargs kill -2"

        os.system("ps -ef | grep -E rviz" +
                  " | grep -v 'grep' | awk '{print $2}' | xargs kill -2")
        subprocess.run(close_command, shell=True)

    def save_map_file(self):
        # cd_command=""
        launch_command = "rosrun map_server map_saver"
        subprocess.run(
            ['gnome-terminal', '-e', f"bash -c '{launch_command}; exec $SHELL'"])

    def navigation_open(self):
        launch_command = "roslaunch myagv_navigation navigation_active.launch"
        subprocess.run(
            ['gnome-terminal', '-e', f"bash -c '{launch_command}; exec $SHELL'"])

    def navigation_close(self, run_launch):
        close_command = "ps -ef | grep -E " + run_launch + \
                        " | grep -v 'grep' | awk '{print $2}' | xargs kill -2"

        os.system("ps -ef | grep -E rviz" +
                  " | grep -v 'grep' | awk '{print $2}' | xargs kill -2")

        os.system("ps -ef | grep -E " + run_launch +
                  " | grep -v 'grep' | awk '{print $2}' | xargs kill -2")
        # subprocess.run(close_command, shell=True)

    def closeEvent(self, event):
        if self.agv_status_detector is not None:
            self.agv_status_detector.terminate()
        GPIO.cleanup()
        print("Closed")
        

class FunctionCheckController(QThread):   # 功能检测控制器
    testing_finish = pyqtSignal(str)
    testing_stop = pyqtSignal()

    def __init__(self, testing: str, agv: MyAgv):
        super().__init__()
        self.test = testing
        self.agv = agv

    def motor_testing(self):

        self.agv.go_ahead(100, 4)
        time.sleep(1)
        self.agv.stop()
        time.sleep(0.05)

        self.agv.retreat(100, 4)
        time.sleep(1)
        self.agv.stop()
        time.sleep(0.05)

        self.agv.pan_left(100, 4)
        time.sleep(1)
        self.agv.stop()
        time.sleep(0.05)

        self.agv.pan_right(100, 4)
        time.sleep(1)
        self.agv.stop()
        time.sleep(0.05)

        self.agv.counterclockwise_rotation(100, 8)
        time.sleep(1)
        self.agv.stop()
        time.sleep(0.05)

        self.agv.clockwise_rotation(100, 8)
        time.sleep(1)
        self.agv.stop()

        self.testing_finish.emit(self.test)

    def LED_testing(self):
        # print("LED Testing...")
        color_list = ["#ff0000", "ff7f00", "ffff00",
                      "00ff00", "00ffff", "0000ff", "8b0ff"]

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
        os.system(
            "gnome-terminal -e 'bash -c \"sudo python /home/er/AGV_UI/operations_UI/camera_testing.py; exec bash\"'"
        )
        time.sleep(6)
        self.testing_finish.emit(self.test)

    def Camera_2D_testing(self):

        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("Can't open camera!")
            exit()

        while True:
            ret, frame = cap.read()

            if not ret:
                print("Can't read img frame!")
                break

            cv2.imshow('Camera', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        self.testing_finish.emit(self.test)

    def Pump_testing(self):

        # print("pump")

        # try:
        # GPIO.cleanup()
        # except Exception:pass

        GPIO.setup(19, GPIO.OUT)
        GPIO.setup(26, GPIO.OUT)

        time.sleep(0.1)

        GPIO.output(26, GPIO.LOW)  # 打开吸泵
        time.sleep(0.05)
        GPIO.output(19, GPIO.HIGH)  # 打开气阀

        # wait 4s
        time.sleep(4)

        # close pump
        GPIO.output(26, GPIO.HIGH)  # 关闭吸泵
        time.sleep(0.05)
        GPIO.output(19, GPIO.LOW)  # 关闭气阀
        time.sleep(0.05)
        GPIO.output(19, GPIO.HIGH)  # 气阀状态还原
        time.sleep(0.05)

        self.testing_finish.emit(self.test)

    def run(self) -> None:

        if self.test == QCoreApplication.translate("myAGV", "Motor"):
            # TODO add radar connections
            self.motor_testing()

        elif self.test == QCoreApplication.translate("myAGV", "LED"):
            self.LED_testing()

        elif self.test == QCoreApplication.translate("myAGV", "2D Camera"):
            self.Camera_testing()

        elif self.test == QCoreApplication.translate("myAGV", "Pump"):
            self.Pump_testing()


class AGVStatusDetector(QThread):
    """
    状态检测线程
    """
    ipaddress = pyqtSignal(str)
    voltages = pyqtSignal(float, float)
    battery = pyqtSignal(bool, bool)
    powers = pyqtSignal(float, float)
    motors = pyqtSignal(bool, list)

    def __init__(self, agv: MyAgv, parent=None):
        super().__init__(parent=parent)
        self.agv = agv

    @classmethod
    def get_ipaddress(cls):
        st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            st.connect(('10.255.255.255', 1))
            IP = st.getsockname()[0]
        except Exception as e:
            print(e)
            IP = '127.0.0.1'
        finally:
            st.close()

        return IP

    @classmethod
    def calculate_amount_of_power(cls, voltage):
        """计算电池电量"""
        return round((voltage - 9) / (12 - 9) * 100, 2)

    def get_info(self):
        data = self.agv.get_mcu_info()
        if not data:
            return

        # 电池状态 【电池2接入、电池1接入、适配器接入、充电桩接入、电池2充电灯， 电池1充电灯】
        battery_status = list(map(lambda n: int(n) == 1, data[9]))
        battery1 = battery_status[1]
        battery2 = battery_status[0]
        self.battery.emit(battery1, battery2)

        # 电机电流
        motors = data[12:16]
        # status = all(motor for motor in motors)
        self.motors.emit(bool(data), motors)

        battery_voltage_1 = data[10]  # 电池1电压
        battery_voltage_2 = data[11]  # 电池2电压

        battery_level_1 = 0.00  # 电池1电量
        battery_level_2 = 0.00  # 电池2电量
        if int(battery1) and battery_voltage_1:
            battery_level_1 = self.calculate_amount_of_power(battery_voltage_1)

        if int(battery2) and battery_voltage_2:
            battery_level_2 = self.calculate_amount_of_power(battery_voltage_1)

        self.voltages.emit(battery_voltage_1, battery_voltage_2)
        self.powers.emit(battery_level_1, battery_level_2)

    def run(self):
        global Ros_flag
        time.sleep(0.2)
        while self.agv:
            if Ros_flag is True:
                break
            try:
                self.get_info()
                time.sleep(0.2)
            except Exception as e:
                print(e)
                print(traceback.format_exc())


# 程序入口
if __name__ == "__main__":
    app = QApplication(sys.argv)
    testtool = MyAGVTesttoolApplication()
    testtool.initialize()
    testtool.show()
    sys.exit(app.exec())
