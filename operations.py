# encoding:utf-8

import subprocess
import sys
import threading
import time
import traceback
import socket
import json
from typing import Optional
from PyQt5.QtCore import QCoreApplication, QThread, QTranslator, pyqtSignal
from PyQt5.QtWidgets import QWidget, QApplication, QMessageBox, QSizePolicy, QMainWindow
from operations_UI.AGV_operations_ui import Ui_myAGV
from pymycobot.myagv import MyAgv
from operations_UI.color_picker import ColorCircle
from operations_UI.camera_window import CameraWindow
from operations_UI.component_status import ComponentsSet
import os
import cv2
import RPi.GPIO as GPIO


class ButtonStyleEnum:
    RED = """
            background-color: rgb(198, 61, 47);
            color: rgb(255, 255, 255);
            border-radius: 7px;
            border: 2px groove gray;
            border-style: outset;
            font: 75 9pt "Arial";
        """
    GREEN = """
            background-color: rgb(39, 174, 96);
            color: rgb(255, 255, 255);
            border-radius: 7px;
            border: 2px groove gray;
            border-style: outset;
            font: 75 9pt "Arial";
        """
    BLUE = """
            background-color:rgb(41, 128, 185);
            color: rgb(255, 255, 255);
            border-radius: 10px;
            border: 2px groove gray;
            border-style: outset;
            font: 75 9pt "Arial";
        """
    GRAY = """
            background-color:gray;
            color: rgb(255, 255, 255);
            border-radius: 7px;
            border: 2px groove gray;
            border-style: outset;
            font: 75 9pt "Arial";
        """
    LightGrey = """
            background-color:grey;
            border-radius: 9px;
            border: 1px solid
        """
    LightGreen = """
            background-color:green;
            border-radius: 9px;
            border: 1px solid
        """


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
    def run_in_terminal(cls, command, keep: bool = False):
        if keep:
            subprocess.run(f'gnome-terminal -- bash -c "{command}; exec bash"', shell=True)
        else:
            subprocess.run(f'gnome-terminal -- bash -c \"{command};\"', shell=True)

    @classmethod
    def kill(cls, command):
        command = "ps -ef | grep -E %s | grep -v 'grep' | awk '{print $2}' | xargs kill -2" % command
        subprocess.run(command, shell=True)

    @classmethod
    def alive(cls, command):
        command = "ps -ef | grep -E %s | grep -v 'grep' | wc -l" % command
        return int(cls.check_output(command)) > 0

    @classmethod
    def open_radar(cls):
        cls.run_in_terminal("roslaunch myagv_odometry myagv_active.launch")

    @classmethod
    def close_radar(cls):
        cls.kill("myagv_active.launch")

    @classmethod
    def check_radar_running(cls) -> bool:
        command = "ps -ef | grep -E myagv_active.launch | grep -v 'grep' | wc -l"
        wordcount = cls.check_output(command)
        return int(wordcount) > 0


class myAGV_windows(QMainWindow):

    def __init__(self):
        super().__init__()
        self.label_color = None
        self.ui = Ui_myAGV()
        self.ui.setupUi(self)
        self.ui.color_palette.setVisible(False)
        self.ui.label_value.setVisible(False)
        self.ui.lineEdit_RGB.setStyleSheet("background:None")
        self.ui.lineEdit_HEX.setStyleSheet("background:None")
        self.ui.logo_lab.setVisible(False)
        self.ui.menu_widget.setVisible(False)

        self.led_default = [255, 0, 0]  # red light
        self.my_agv: Optional[MyAgv] = None
        self.function_testing: Optional[AGVFunctionalTesting] = None
        self.agv_status_detector: Optional[MyAGVStatusDetector] = None
        self.radar_flag = False
        self.keyboard_flag = False
        self.joystick_flag = False
        self.in_function_testing = False  # 功能检测运行中
        self.flag_all = False
        self.flag_build = False
        self.camera = None
        self._app = QApplication.instance()
        self.translator = QTranslator(self)

        self.ui_set()
        self.color_painter()
        self.language_initial()

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(21, GPIO.OUT)
        GPIO.output(21, GPIO.HIGH)

        ipaddress = MyAGVStatusDetector.get_ipaddress()
        self.ui.lineEdit.setText(ipaddress)
        self.radar_flag = CommandExecutor.check_radar_running()
        if self.radar_flag is False:
            self.try_connect_agv()
            self.status_detecting()
            self.agv_status_detector.start()
        else:
            self.ui.radar_button.setText(QCoreApplication.translate("myAGV", "OFF"))
            self.ui.radar_button.setStyleSheet(ButtonStyleEnum.RED)
        self.ui.radar_button.setChecked(self.radar_flag)

    def try_connect_agv(self):  # connect agv
        if self.radar_flag:  # open radar
            QMessageBox(
                self,
                QCoreApplication.translate("myAGV", "Warning"),
                QCoreApplication.translate("myAGV", "Please turn off the radar before using this function.")
            )
        else:
            self.my_agv = MyAgv("/dev/ttyAMA2", 115200)
        return not self.radar_flag

    def color_painter(self):
        self.label_color = QWidget()

        color = ColorCircle(self, startupcolor=self.led_default)

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

            self.ui.comboBox_testing.view().setRowHidden(3, True)
            self.ui.build_map_selection.addItems(map_nav_params)

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

            self.ui.status_radar.setStyleSheet(ButtonStyleEnum.LightGrey)
            self.ui.status_battery_main.setStyleSheet(ButtonStyleEnum.LightGrey)
            self.ui.status_battery_backup_2.setStyleSheet(ButtonStyleEnum.LightGrey)
            self.ui.status_motor_1.setStyleSheet(ButtonStyleEnum.LightGrey)

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

            self.ui.Restore_btn.pressed.connect(self.restore_btn)
            self.ui.Restore_btn.released.connect(self.release_style)

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

        current_time = self.get_current_time()
        self.msg_log(QCoreApplication.translate("myAGV", "Motor Restor"), current_time)

        if self.try_connect_agv():
            self.ui.Restore_btn.setStyleSheet("""
                background-color: rgb(31, 140, 77);
                color: rgb(255, 255, 255);
                border-radius: 7px;
                border: 2px groove gray;
                border-style: outset;
                font: 75 9pt "Arial";
            """)
            self.my_agv.restore()

    def testing_finished(self, item, is_stop=False):
        self.try_connect_agv()

        if is_stop is True:
            self.msg_log(
                QCoreApplication.translate("myAGV", "Stop") + item + QCoreApplication.translate("myAGV", " testing"))
        else:
            self.msg_log(
                QCoreApplication.translate("myAGV", "Finish") + item + QCoreApplication.translate("myAGV", " testing"))

        if item == "Pump" or item == "吸泵":
            # stop testing to close pump

            GPIO.output(3, GPIO.HIGH)
            GPIO.output(2, GPIO.LOW)
            time.sleep(0.05)
            GPIO.output(2, GPIO.HIGH)

            # GPIO.cleanup()

        if item == "Motor" or item == "电机":
            self.my_agv._mesg(128, 128, 128)
            self.my_agv.stop()

        if item == "2D Camera" or item == "2D 相机":
            self.camera.close()

        testing_status = self.ui.start_detection_button.isEnabled()
        self.ui.start_detection_button.setChecked(not testing_status)
        self.ui.start_detection_button.setText(QCoreApplication.translate("myAGV", "Start Detection"))
        self.ui.start_detection_button.setStyleSheet(ButtonStyleEnum.BLUE)
        self.ui.comboBox_testing.setDisabled(False)
        self.button_status_switch(True)
        self.in_function_testing = False
        ComponentsSet.testing_open_close(self.ui, True)

    def lighter_set(self, color):
        r = color.red()
        g = color.green()
        b = color.blue()

        rgb_color = f"({r}, {g}, {b})"

        color_hex = color.name()

        self.ui.lineEdit_HEX.setText(color_hex)
        self.ui.lineEdit_RGB.setText(rgb_color)

        if self.radar_flag:  # open radar
            QMessageBox.warning(
                self,
                QCoreApplication.translate("myAGV", "Warning"),
                QCoreApplication.translate("myAGV", "Please turn off the radar before using this function."),
                QMessageBox.Ok
            )
        elif self.in_function_testing:
            QMessageBox.warning(
                self,
                QCoreApplication.translate("myAGV", "Warning"),
                QCoreApplication.translate("myAGV", "Please stop the detection before using the led."),
                QMessageBox.Ok
            )
        else:
            if self.my_agv is not None:
                print(" * Set LED color to: ", r, g, b)
                self.my_agv._mesg([0x01, 0x0A, 0x01])
                self.my_agv.set_led(1, r, g, b)

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
        self.ui.textBrowser.append(f"[{current_time}]{msg}")

    def msg_error(self, msg, current_time: str = None):
        if current_time is None:
            current_time = self.get_current_time()
        with open("error.log", "w") as f:
            f.write(msg)
        self.ui.textBrowser.append(f"[{current_time}]{msg}")

    def radar_control(self):
        if self.ui.radar_button.isChecked():
            self.agv_status_detector.stop_detector()
            if self.my_agv is not None:
                self.my_agv._serial_port.close()

            time.sleep(0.2)
            # self.ui.start_detection_button.setCheckable(False)
            self.ui.start_detection_button.setEnabled(False)  # 雷达打开时检测按钮不可使用
            self.ui.start_detection_button.setStyleSheet(ButtonStyleEnum.GRAY)
            if self.flag_all:
                return

            self.ui.radar_button.setStyleSheet(ButtonStyleEnum.RED)
            self.ui.radar_button.setText(QCoreApplication.translate("myAGV", "OFF"))

            msg = QCoreApplication.translate("myAGV", "Radar open...")
            current_time = self.get_current_time()
            self.msg_log(msg, current_time)

            # add limit for testing and led
            ComponentsSet.radar_open_close(self.ui, False)
            self.ui.Restore_btn.setEnabled(False)
            self.ui.Restore_btn.setStyleSheet(ButtonStyleEnum.GRAY)

            try:
                threading.Thread(target=self.radar_open, daemon=True).start()
                self.radar_flag = True
                self.ui.status_radar.setStyleSheet(ButtonStyleEnum.LightGreen)
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
                print(f" * {self.ui.radar_button.isChecked()}")
                self.ui.radar_button.setChecked(True)
                print(f" * {self.ui.radar_button.isChecked()}")
                return
            else:
                current_time = self.get_current_time()
                self.ui.radar_button.setStyleSheet(ButtonStyleEnum.GREEN)
                self.ui.radar_button.setText(QCoreApplication.translate("myAGV", "ON"))
                self.msg_log(QCoreApplication.translate("myAGV", "close radar"), current_time)
                self.ui.Restore_btn.setEnabled(True)
                self.ui.Restore_btn.setStyleSheet(ButtonStyleEnum.GREEN)
                self.ui.start_detection_button.setEnabled(True)  # 雷达打开时检测按钮不可使用
                self.ui.start_detection_button.setStyleSheet(ButtonStyleEnum.BLUE)
                try:
                    self.radar_flag = False
                    time.sleep(4)  # 等待2s后，释放检测按钮（可用）
                    ComponentsSet.radar_open_close(self.ui, True)
                    # self.ui.start_detection_button.setCheckable(True)
                    self.ui.status_radar.setStyleSheet(ButtonStyleEnum.LightGrey)
                    threading.Thread(target=self.radar_close, daemon=True).start()
                    self.try_connect_agv()
                    self.status_detecting()
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
            else:
                self.ui.basic_control_button.setStyleSheet(ButtonStyleEnum.RED)
                self.ui.basic_control_button.setText(QCoreApplication.translate("myAGV", "OFF"))

                self.ui.basic_control_selection.setEnabled(False)  # 设置下拉框不可选区
                self.flag_all = True

                if control_item_basic == "Keyboard Control" or control_item_basic == "键盘控制":
                    self.keyboard_flag = True
                    try:
                        self.msg_log(QCoreApplication.translate("myAGV", "Keyboard open..."))
                        threading.Thread(target=self.keyboard_open, daemon=True).start()
                    except Exception as e:
                        e = traceback.format_exc()
                        self.msg_error(e)

                elif control_item_basic == "Joystick-Alphabet" or control_item_basic == "手柄控制(字母)":
                    self.joystick_flag = True
                    try:
                        self.msg_log(QCoreApplication.translate("myAGV", "Open joystick control..."))
                        joystick_open = threading.Thread(target=self.joystick_open, daemon=True)
                        joystick_open.start()

                    except Exception as e:
                        e = traceback.format_exc()
                        self.msg_error(e)

                elif control_item_basic == "Joystick-Number" or control_item_basic == "手柄控制(数字)":
                    self.joystick_flag = True
                    try:
                        self.msg_log(QCoreApplication.translate("myAGV", "Open joystick control"))
                        joystick_open = threading.Thread(target=self.joystick_open_number, daemon=True)
                        joystick_open.start()
                    except Exception as e:
                        self.msg_error(e)
                        self.msg_error(traceback.format_exc())

        else:
            self.ui.basic_control_button.setStyleSheet(ButtonStyleEnum.GREEN)
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

                    keyboard_close = threading.Thread(target=self.keyboard_close, args=(keyboard_run_launch,),
                                                      daemon=True)
                    keyboard_close.start()
                    self.keyboard_flag = False
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
                    QMessageBox.OK
                )
                self.ui.open_build_map.setChecked(False)
                return

            else:
                self.ui.build_map_selection.setEnabled(False)  # 建图方式不可选取

                self.ui.navigation_3d_button.setEnabled(False)  # 建图打开后导航均不可用
                self.ui.navigation_3d_button.setStyleSheet(ButtonStyleEnum.GRAY)
                self.ui.navigation_button.setEnabled(False)
                self.ui.navigation_button.setStyleSheet(ButtonStyleEnum.GRAY)

                self.flag_build = True
                self.flag_all = True

                self.ui.open_build_map.setText(QCoreApplication.translate("myAGV", "Close Build Map"))
                self.ui.open_build_map.setStyleSheet(ButtonStyleEnum.RED)

                if build_map_method == "Gmapping":
                    self.msg_log(QCoreApplication.translate("myAGV", "Open Gmapping..."), current_build)
                    gmapping_build()

                if build_map_method == "Cartographer":
                    self.msg_log(QCoreApplication.translate("myAGV", "Open Cartographer..."), current_build)
                    cartographer_build()

        else:
            self.ui.open_build_map.setStyleSheet(ButtonStyleEnum.BLUE)
            self.ui.open_build_map.setText(QCoreApplication.translate("myAGV", "Open Build Map"))

            if build_map_method == "Gmapping":
                self.msg_log(QCoreApplication.translate("myAGV", "Close Gmapping"), current_build)
                gmapping_close()

            if build_map_method == "Cartographer":
                self.msg_log(QCoreApplication.translate("myAGV", "Close Cartographer"), current_build)
                cartographer_close()

            # 关闭建图打开导航按钮

            self.ui.build_map_selection.setEnabled(True)
            self.ui.navigation_3d_button.setEnabled(True)  # 建图关闭后导航可用
            self.ui.navigation_3d_button.setStyleSheet(ButtonStyleEnum.BLUE)
            self.ui.navigation_button.setEnabled(True)
            self.ui.navigation_button.setStyleSheet(ButtonStyleEnum.BLUE)
            self.flag_build = True
            self.flag_all = False

    def navigation_3d(self):

        current_time = self.get_current_time()

        if self.ui.navigation_3d_button.isChecked():
            if not self.radar_flag:
                QMessageBox.warning(
                    self,
                    QCoreApplication.translate("myAGV", "Warning"),
                    QCoreApplication.translate("myAGV", "Radar not open!"),
                    QMessageBox.OK
                )

                self.ui.navigation_3d_button.setChecked(False)
                return

            else:
                self.ui.build_map_selection.setEnabled(False)  # 建图下拉框不可选
                self.ui.open_build_map.setEnabled(False)  # 打开建图不可选
                self.ui.open_build_map.setStyleSheet(ButtonStyleEnum.GRAY)
                self.ui.navigation_button.setEnabled(False)  # 导航不可选
                self.ui.navigation_button.setStyleSheet(ButtonStyleEnum.GRAY)

                self.ui.navigation_3d_button.setText(QCoreApplication.translate("myAGV", "Close 3D Navigation"))
                self.ui.navigation_3d_button.setStyleSheet(ButtonStyleEnum.RED)

                self.msg_log(QCoreApplication.translate("myAGV", "Open 3D navigation"), current_time)

                self.flag_all = True
                open_navigation = threading.Thread(target=self.navigation_open, daemon=True)
                open_navigation.start()

        else:
            self.ui.build_map_selection.setEnabled(True)
            self.ui.open_build_map.setEnabled(True)
            self.ui.open_build_map.setStyleSheet(ButtonStyleEnum.BLUE)
            self.ui.navigation_button.setEnabled(True)
            self.ui.navigation_button.setStyleSheet(ButtonStyleEnum.BLUE)

            self.ui.navigation_3d_button.setText(QCoreApplication.translate("myAGV", "3D Navigation"))
            self.ui.navigation_3d_button.setStyleSheet(ButtonStyleEnum.BLUE)

            self.msg_log(QCoreApplication.translate("myAGV", "Close 3D navigation"), current_time)
            close_launch = "navigation_active.launch"
            close_navigation = threading.Thread(target=self.navigation_close, args=(close_launch,), daemon=True)
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
            else:
                self.ui.build_map_selection.setEnabled(False)
                self.ui.open_build_map.setEnabled(False)
                self.ui.open_build_map.setStyleSheet(ButtonStyleEnum.GRAY)
                self.ui.navigation_3d_button.setEnabled(False)
                self.ui.navigation_3d_button.setStyleSheet(ButtonStyleEnum.GRAY)

                self.ui.navigation_button.setText(QCoreApplication.translate("myAGV", "Close Navigation"))
                self.ui.navigation_button.setStyleSheet(ButtonStyleEnum.RED)

                self.msg_log(QCoreApplication.translate("myAGV", "Open navigation"), current_time)

                self.flag_all = True
                open_navigation = threading.Thread(
                    target=self.navigation_open, daemon=True)
                open_navigation.start()

        else:
            self.ui.build_map_selection.setEnabled(True)
            self.ui.open_build_map.setEnabled(True)
            self.ui.open_build_map.setStyleSheet(ButtonStyleEnum.BLUE)
            self.ui.navigation_3d_button.setEnabled(True)
            self.ui.navigation_3d_button.setStyleSheet(ButtonStyleEnum.BLUE)

            self.ui.navigation_button.setText(QCoreApplication.translate("myAGV", "Navigation"))
            self.ui.navigation_button.setStyleSheet(ButtonStyleEnum.BLUE)
            self.msg_log(QCoreApplication.translate("myAGV", "Close navigation"), current_time)
            close_launch = "navigation_active.launch"
            close_navigation = threading.Thread(target=self.navigation_close, args=(close_launch,), daemon=True)
            close_navigation.start()
            self.flag_all = False

    def start_testing(self):
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
                self.in_function_testing = True
                self.ui.start_detection_button.setText(QCoreApplication.translate("myAGV", "Stop Detection"))
                self.ui.start_detection_button.setStyleSheet(ButtonStyleEnum.RED)
                self.ui.comboBox_testing.setDisabled(True)

                self.msg_log(QCoreApplication.translate("myAGV", "Start ") + item + QCoreApplication.translate("myAGV", "testing"))

                if item == "2D Camera" or item == "2D 相机":
                    self.camera = CameraWindow()
                    self.camera.camera_finish.connect(self.testing_finished)
                    self.camera.show()
                else:
                    self.function_testing = AGVFunctionalTesting(test_name=item, my_agv=self.my_agv)
                    self.function_testing.testing_finish.connect(self.testing_finished)
                    self.button_status_switch(False)
                    ComponentsSet.testing_open_close(self.ui, False)
                    self.function_testing.start()
        else:
            if item in ("2D Camera", "2D 相机"):
                if self.camera is not None and self.camera.isVisible():
                    self.camera.close_window(True)
            else:
                self.function_testing.terminate()
                self.testing_finished(item, True)  # 更新延迟

    def status_detecting(self):

        def voltage_set(vol_1, vol_2):
            self.ui.lineEdit_voltage.setText(str(vol_1))
            self.ui.lineEdit_voltage_backup.setText(str(vol_2))

        def battery_set(b_1, b_2):
            style_sheet = ButtonStyleEnum.LightGreen if b_1 else ButtonStyleEnum.LightGrey
            self.ui.status_battery_main.setStyleSheet(style_sheet)

            style_sheet = ButtonStyleEnum.LightGreen if b_2 else ButtonStyleEnum.LightGrey
            self.ui.status_battery_backup_2.setStyleSheet(style_sheet)

        def powers_set(power_1, power_2):
            self.ui.lineEdit_power.setText(str(power_1))
            self.ui.lineEdit_power_backup.setText(str(power_2))

        def motors_set(status, curr):
            ui_motors = [
                self.ui.electricity_motor1,
                self.ui.electricity_motor2,
                self.ui.electricity_motor3,
                self.ui.electricity_motor4
            ]
            motor_style_status = ButtonStyleEnum.LightGreen if status else ButtonStyleEnum.LightGrey
            self.ui.status_motor_1.setStyleSheet(motor_style_status)

            for el, val in enumerate(zip(ui_motors, curr)):
                val[0].setText(str(val[1]))

        self.agv_status_detector = MyAGVStatusDetector(self.my_agv)
        self.agv_status_detector.voltages.connect(voltage_set)
        self.agv_status_detector.battery.connect(battery_set)
        self.agv_status_detector.powers.connect(powers_set)
        self.agv_status_detector.motors.connect(motors_set)

    @classmethod
    def radar_open(cls):
        GPIO.setmode(GPIO.BCM)
        time.sleep(0.1)
        GPIO.setup(20, GPIO.OUT)
        GPIO.output(20, GPIO.HIGH)
        time.sleep(0.05)
        CommandExecutor.open_radar()

    @classmethod
    def radar_close(cls):
        GPIO.setmode(GPIO.BCM)
        time.sleep(0.1)
        GPIO.setup(20, GPIO.OUT)
        GPIO.output(20, GPIO.LOW)
        time.sleep(0.05)
        CommandExecutor.close_radar()

    @classmethod
    def keyboard_open(cls):
        CommandExecutor.run_in_terminal("cd /home/ubuntu; roslaunch ~/myagv_ros/src/myagv_teleop/launch/myagv_teleop.launch; exec bash")
        os.system("gnome-terminal -e 'bash -c \"cd /home/ubuntu; roslaunch ~/myagv_ros/src/myagv_teleop/launch/myagv_teleop.launch; exec bash\"'")

    @classmethod
    def keyboard_close(cls, run_launch):
        close_command = "ps -ef | grep -E " + run_launch + " | grep -v 'grep' | awk '{print $2}' | xargs kill -2"
        subprocess.run(close_command, shell=True)

    @classmethod
    def joystick_open(cls):
        launch_command = "roslaunch myagv_ps2 myagv_ps2.launch"
        subprocess.run(['gnome-terminal', '-e', f"bash -c '{launch_command}; exec $SHELL'"])

    @classmethod
    def joystick_close(cls, run_launch):
        close_command = "ps -ef | grep -E " + run_launch + " | grep -v 'grep' | awk '{print $2}' | xargs kill -2"
        subprocess.run(close_command, shell=True)

    @classmethod
    def joystick_open_number(cls):
        launch_command = "roslaunch myagv_ps2 myagv_ps2_number.launch"
        subprocess.run(['gnome-terminal', '-e', f"bash -c '{launch_command}; exec $SHELL'"])

    @classmethod
    def joystick_close_number(cls, run_launch):
        close_command = "ps -ef | grep -E " + run_launch + " | grep -v 'grep' | awk '{print $2}' | xargs kill -2"
        subprocess.run(close_command, shell=True)

    @classmethod
    def gmapping_build_open(cls):
        launch_command = "roslaunch myagv_navigation myagv_slam_laser.launch"
        os.system("gnome-terminal -e 'bash -c \"cd /home/ubuntu; roslaunch ~/myagv_ros/src/myagv_navigation/launch/myagv_slam_laser.launch; exec bash\"'")

    @classmethod
    def gmapping_build_close(cls, run_launch):
        os.system("ps -ef | grep -E rviz | grep -v 'grep' | awk '{print $2}' | xargs kill -2")
        os.system("ps -ef | grep -E " + run_launch + " | grep -v 'grep' | awk '{print $2}' | xargs kill -2")

    @classmethod
    def cartographer_build_open(cls):
        launch_command = "roslaunch cartographer_ros demo_myagv.launch"
        subprocess.run(['gnome-terminal', '-e', f"bash -c '{launch_command}; exec $SHELL'"])

    @classmethod
    def cartographer_build_close(cls):
        close_command = "ps -ef | grep -E " + "demo_myagv.launch | grep -v 'grep' | awk '{print $2}' | xargs kill -2"
        os.system("ps -ef | grep -E rviz  | grep -v 'grep' | awk '{print $2}' | xargs kill -2")
        subprocess.run(close_command, shell=True)

    @classmethod
    def save_map_file(cls):
        # cd_command=""
        launch_command = "rosrun map_server map_saver"
        subprocess.run(['gnome-terminal', '-e', f"bash -c '{launch_command}; exec $SHELL'"])
        time.sleep(1)

    @classmethod
    def navigation_open(cls):
        launch_command = "roslaunch myagv_navigation navigation_active.launch"
        subprocess.run(['gnome-terminal', '-e', f"bash -c '{launch_command}; exec $SHELL'"])

    @classmethod
    def navigation_close(cls, run_launch):
        os.system("ps -ef | grep -E rviz" + " | grep -v 'grep' | awk '{print $2}' | xargs kill -2")
        os.system("ps -ef | grep -E " + run_launch + " | grep -v 'grep' | awk '{print $2}' | xargs kill -2")

    def closeEvent(self, event):
        GPIO.cleanup()
        if self.agv_status_detector is not None:
            self.agv_status_detector.stop_detector()


class AGVFunctionalTesting(QThread):  #
    testing_finish = pyqtSignal(str)
    testing_stop = pyqtSignal()

    def __init__(self, my_agv: MyAgv, test_name: str):
        super().__init__()
        self.test = test_name
        self.agv = my_agv

    def motor_testing(self):
        self.agv._mesg(128, 128, 128)
        self.agv.go_ahead(100, 4)
        time.sleep(1)
        self.agv.stop()
        time.sleep(0.05)

        self.agv.retreat(100, 4)
        time.sleep(1)
        self.agv.stop()
        time.sleep(0.05)

        self.agv.pan_left(100, 8)
        time.sleep(1)
        self.agv.stop()
        time.sleep(0.05)

        self.agv.pan_right(100, 8)
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

        self.agv._mesg([0x01, 0x0A, 0x01])
        for key, value in color_dict.items():
            r = int(value[0])
            g = int(value[1])
            b = int(value[2])

            self.agv.set_led(1, r, g, b)
            time.sleep(1)

        self.testing_finish.emit(self.test)

    def Camera_testing(self):
        pass  # todo camera testing...

    def Camera_2D_testing(self):

        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            # print("Can't open camera!")
            exit()

        while True:
            ret, frame = cap.read()

            if not ret:
                # print("Can't read img frame!")
                break

            cv2.imshow('Camera', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        self.testing_finish.emit(self.test)

    def Pump_testing(self):

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(2, GPIO.OUT)
        GPIO.setup(3, GPIO.OUT)

        # open
        GPIO.output(3, GPIO.LOW)
        GPIO.output(2, GPIO.HIGH)

        time.sleep(4)

        # close
        GPIO.output(3, GPIO.HIGH)
        GPIO.output(2, GPIO.LOW)
        time.sleep(0.05)
        GPIO.output(2, GPIO.HIGH)

        self.testing_finish.emit(self.test)

    def run(self) -> None:

        if self.test == QCoreApplication.translate("myAGV", "Motor"):
            self.motor_testing()

        elif self.test == QCoreApplication.translate("myAGV", "LED"):
            self.LED_testing()

        elif self.test == QCoreApplication.translate("myAGV", "Camera"):
            self.Camera_testing()

        elif self.test == QCoreApplication.translate("myAGV", "Pump"):
            self.Pump_testing()


class MyAGVStatusDetector(QThread):
    voltages = pyqtSignal(float, float)
    battery = pyqtSignal(bool, bool)
    powers = pyqtSignal(float, float)
    motors = pyqtSignal(bool, list)

    def __init__(self, my_agv: MyAgv):
        super().__init__()
        self.my_agv = my_agv
        self.detector = True

    def stop_detector(self):
        self.detector = False
        self.battery.emit(0, 0)
        self.voltages.emit(0, 0)
        self.powers.emit(0, 0)
        self.motors.emit(False, [0, 0, 0, 0])
        self.quit()

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

    def get_status_info(self):
        data = self.my_agv.get_mcu_info()
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
        while self.detector is True:
            try:
                self.get_status_info()
                time.sleep(0.2)
            except Exception as e:
                print(e)
                print(traceback.format_exc())


# 程序入口
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = myAGV_windows()
    window.show()
    sys.exit(app.exec())
