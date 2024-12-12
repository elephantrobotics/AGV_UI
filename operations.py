# encoding:utf-8
import os
import subprocess
import sys
import threading
import time
import json
import typing as T
from PyQt5.QtCore import QCoreApplication, QTranslator
from PyQt5.QtWidgets import QWidget, QApplication, QMessageBox, QSizePolicy, QMainWindow

import core
from functions.detector import MyAGVStatusDetector
from functions.functional import FunctionalBaseTesting, AGVMotorTesting, AGVLEDTesting, AGVPUMPTesting
from core import Constant, GlobalVar
from core.command import ShellAPI
from core.handler import AgvHandler
from core.style import ButtonStyleEnum
from core.resource import FileResource
from core.console import Console
from core.translate import Translate
from widgets.operation_ui import Ui_Operation as OperationUI
from widgets.color_picker import ColorPickerWidget
from widgets.camera import AGVCameraWidget
from widgets.component_status import ComponentsSet
from pymycobot.myagv import MyAgv

system_model = ShellAPI.cat(Constant.SYSTEM_IDENTIFICATION_FILE)

print(f" * ================================================")
print(f" * Current platform is {system_model}")
print(f" * ================================================")

if system_model.startswith("Raspberry Pi 4"):

    import RPi.GPIO as GPIO

    baudrate = 115200
    comport = "/dev/ttyAMA2"
    suction_pump_pins = (2, 3)
    radar_control_pin = 20
    GlobalVar.camera2D_pipline = 0


elif system_model.startswith("NVIDIA Jetson Nano Developer Kit"):

    import Jetson.GPIO as GPIO

    baudrate = 115200
    comport = "/dev/ttyS0"
    suction_pump_pins = (19, 26)
    radar_control_pin = 20
    GlobalVar.camera2D_pipline = core.gstreamer_pipeline(0)

else:
    raise Exception(" * Current platform is not supported")

GPIO.setmode(GPIO.BCM)
GlobalVar.GPIO = GPIO
GlobalVar.comport = comport
GlobalVar.baudrate = baudrate
GlobalVar.suction_pump_pins = suction_pump_pins
GlobalVar.radar_control_pin = radar_control_pin
GlobalVar.debug = False

_translate = QCoreApplication.translate

agv_chinese_names = {
    0: "前进",
    1: "后退",
    2: "左转",
    3: "右转",
    4: "停止",
    5: "顺时针旋转",
    6: "逆时针旋转"
}


class MyAGVMainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = OperationUI()
        self.label_color = None
        self.led_default = (255, 0, 0)  # red light
        self.agv_handler: T.Optional[AgvHandler] = None
        self.functional_testing: T.Optional[FunctionalBaseTesting, AGVCameraWidget] = None
        self.agv_status_detector: T.Optional[MyAGVStatusDetector] = None
        self.keyboard_flag = False
        self.joystick_flag = False
        self.in_function_testing = False  # 功能检测运行中
        self.flag_all = False
        self.flag_build = False
        self.functional_testing_mapping: T.Dict = {
            Translate.Functional.Led: AGVLEDTesting,
            Translate.Functional.Pump: AGVPUMPTesting,
            Translate.Functional.Motor: AGVMotorTesting,
            Translate.Functional.Camera2D: AGVCameraWidget
        }

        self._app = QApplication.instance()
        self.translator = QTranslator(self)
        self.file_resource = FileResource('assets')
        self.radar_flag = AgvHandler.check_radar_running()
        self.console = Console()

    def setup_ui(self):
        self.ui.setupUi(self)
        self.ui.lineEdit_RGB.setStyleSheet("background:None")
        self.ui.lineEdit_HEX.setStyleSheet("background:None")
        self.ui.color_palette.setVisible(False)
        self.ui.label_value.setVisible(False)
        self.ui.logo_lab.setVisible(False)
        self.ui.menu_widget.setVisible(False)

        self.ui.status_radar.setStyleSheet(ButtonStyleEnum.LightGrey)
        self.ui.status_battery_main.setStyleSheet(ButtonStyleEnum.LightGrey)
        self.ui.status_battery_backup_2.setStyleSheet(ButtonStyleEnum.LightGrey)
        self.ui.status_motor_1.setStyleSheet(ButtonStyleEnum.LightGrey)

        self.ui.functionalComboBoxItems.clear()
        self.ui.functionalComboBoxItems.addItems([
            Translate.Functional.Led,
            Translate.Functional.Pump,
            Translate.Functional.Motor,
            Translate.Functional.Camera2D
        ])

        self.color_painter()
        self.language_initial()
        self.console.set_output(self.ui.loggerLabel)

    def initialization(self):
        if self.try_connect_agv():
            version = self.agv_handler.get_system_version()
            # #####################################################
            self.agv_handler.agv.set_led_mode(1)  # 适配1.0版本, 1.1之后可删除
            self.agv_handler.agv.stop()
            # #####################################################
            self.ui.VersionEdit.setText(version)
            self.status_detecting()
        else:
            self.ui.radar_button.setText(_translate("myAGV", "OFF"))
            self.ui.radar_button.setStyleSheet(ButtonStyleEnum.RED)
            self.ui.radar_button.setChecked(True)

        ipaddress = core.get_localhost()
        self.ui.HostEdit.setText(ipaddress)

        map_nav_params = [
            _translate("myAGV", "Gmapping"),
            _translate("myAGV", "3D Mapping")
        ]
        self.ui.build_map_selection.addItems(map_nav_params)

    def try_connect_agv(self):  # connect agv
        if self.radar_flag:  # open radar
            QMessageBox(
                self,
                _translate("myAGV", "Warning"),
                _translate("myAGV", "Please turn off the radar before using this function.")
            )
        else:
            agv = MyAgv(port=GlobalVar.comport, baudrate=GlobalVar.baudrate, debug=GlobalVar.debug)
            self.agv_handler = AgvHandler(agv=agv, radar_pin=radar_control_pin, suction_pump_pins=suction_pump_pins)
            self.agv_handler.agv.stop()
        return not self.radar_flag

    def color_painter(self):
        self.label_color = QWidget()

        color = ColorPickerWidget(parent=self, color=self.led_default)

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

    def connect_signals(self):
        self.ui.radar_button.clicked.connect(self.radar_control)
        self.ui.basic_control_button.clicked.connect(self.basic_control)

        self.ui.save_map_button.clicked.connect(self.save_map)
        self.ui.open_build_map.clicked.connect(self.open_build_map)

        self.ui.navigation_3d_button.clicked.connect(self.navigation_3d)
        self.ui.navigation_button.clicked.connect(self.map_navigation)

        self.ui.log_clear.clicked.connect(self.clear_log)

        self.ui.languageSelection.currentTextChanged.connect(self.onLanguageChange)
        self.ui.horizontal_Slider.setRange(0, 511)
        self.ui.horizontal_Slider.setValue(511)

        self.ui.startDetectionBtn.clicked.connect(self.start_testing)

        self.ui.Restore_btn.pressed.connect(self.restore_btn)

    def restore_btn(self):
        self.console.echo(_translate("myAGV", "Motor Restore"))

        if self.try_connect_agv():
            self.ui.Restore_btn.setStyleSheet(ButtonStyleEnum.DEEP_GREEN)
            self.agv_handler.agv.restore()

        self.ui.Restore_btn.setStyleSheet(ButtonStyleEnum.GREEN)

    def on_functional_processed(self, parameters: T.Dict[str, T.Any]):
        test_name = parameters.get("test_name")
        if test_name == Translate.Functional.Motor:
            direction = parameters.get("direction")
            self.console.echo(test_name, direction)
        elif test_name == Translate.Functional.Pump:
            behavior = parameters.get("behavior")
            self.console.echo(test_name, behavior)
        elif test_name == Translate.Functional.Led:
            name = parameters.get("name")
            color = parameters.get("color")
            self.console.echo(test_name, name, str(color))

    def on_functional_finished(self, test_name, is_stop=False):
        if is_stop is True:
            self.console.echo(Translate.State.Stop, test_name, Translate.Other.Testing)
        elif isinstance(self.functional_testing, AGVCameraWidget) and not self.functional_testing.opened():
            self.console.echo(Translate.State.Fail, Translate.Other.CameraOpenFailed)
        else:
            self.console.echo(Translate.State.Finish, test_name, Translate.Other.Testing)

        testing_status = self.ui.startDetectionBtn.isEnabled()

        self.functional_testing = None
        self.ui.startDetectionBtn.setChecked(not testing_status)
        self.ui.startDetectionBtn.setText(_translate("myAGV", "Start Detection"))
        self.ui.startDetectionBtn.setStyleSheet(ButtonStyleEnum.BLUE)
        self.ui.functionalComboBoxItems.setDisabled(False)
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
                _translate("myAGV", "Warning"),
                _translate("myAGV", "Please turn off the radar before using this function."),
                QMessageBox.Ok
            )
        elif self.in_function_testing:
            QMessageBox.warning(
                self,
                _translate("myAGV", "Warning"),
                _translate("myAGV", "Please stop the detection before using the led."),
                QMessageBox.Ok
            )
        else:
            if self.agv_handler is not None:
                print(" * Set LED color to: ", r, g, b)
                self.agv_handler.agv.set_led(1, r, g, b)

    def language_initial(self, language: T.Optional[str] = None):
        if language is None:
            language_filepath = self.file_resource.get('translation', 'language.json')
            with open(language_filepath, "r", encoding='utf-8') as f:
                language = json.loads(f.read())["language"]

        self.ui.languageSelection.setCurrentText(language)
        if language == Translate.Language.English:
            self._app.removeTranslator(self.translator)

        elif language == Translate.Language.Chinese:
            language_filepath = self.file_resource.get('translation', 'operations_lang.qm')
            self.translator.load(language_filepath)
            self._app.installTranslator(self.translator)
        self.retranslate_operation()

    def onLanguageChange(self, language: str):
        print(" * Language changed to: ", language)
        language_filepath = self.file_resource.get('translation', 'language.json')
        with open(language_filepath, "w") as f:
            json.dump({"language": language}, f, indent=4)
        self.language_initial()

    def retranslate_operation(self):
        Translate.reload()  # reload the translation file
        self.ui.functionalComboBoxItems.clear()
        self.ui.functionalComboBoxItems.addItems([
            Translate.Functional.Led,
            Translate.Functional.Pump,
            Translate.Functional.Motor,
            Translate.Functional.Camera2D
        ])
        self.functional_testing_mapping: T.Dict = {
            Translate.Functional.Led: AGVLEDTesting,
            Translate.Functional.Pump: AGVPUMPTesting,
            Translate.Functional.Motor: AGVMotorTesting,
            Translate.Functional.Camera2D: AGVCameraWidget
        }
        self.ui.retranslateUi(self)
        self.ui.radar_button.setChecked(self.radar_flag)
        if self.radar_flag is True:
            self.ui.radar_button.setChecked(True)
            self.ui.radar_button.setText(_translate("myAGV", "OFF"))
        else:
            self.ui.radar_button.setText(_translate("myAGV", "ON"))

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
            btn.setEnabled(status)

    def clear_log(self):
        self.ui.loggerLabel.clear()

    def radar_control(self):
        if self.ui.radar_button.isChecked():
            self.agv_status_detector.stop_detector()
            if self.agv_handler is not None:
                self.agv_handler.close()

            time.sleep(0.2)
            # self.ui.startDetectionBtn.setCheckable(False)
            self.ui.startDetectionBtn.setEnabled(False)  # 雷达打开时检测按钮不可使用
            self.ui.startDetectionBtn.setStyleSheet(ButtonStyleEnum.GRAY)
            if self.flag_all:
                return

            self.ui.radar_button.setStyleSheet(ButtonStyleEnum.RED)
            self.ui.radar_button.setText(_translate("myAGV", "OFF"))
            self.console.echo(_translate("myAGV", "Radar open..."))

            # add limit for testing and led
            ComponentsSet.radar_open_close(self.ui, False)
            self.ui.Restore_btn.setEnabled(False)
            self.ui.Restore_btn.setStyleSheet(ButtonStyleEnum.GRAY)

            threading.Thread(target=self.agv_handler.radar_open, daemon=True).start()
            self.ui.status_radar.setStyleSheet(ButtonStyleEnum.LightGreen)
            self.radar_flag = True

        else:
            if self.flag_all:  # other functions are running...
                QMessageBox.warning(
                    self,
                    _translate("myAGV", "Warning"),
                    _translate("myAGV", "Other functions are running."),
                    QMessageBox.Ok
                )
                print(f" * {self.ui.radar_button.isChecked()}")
                self.ui.radar_button.setChecked(True)
                print(f" * {self.ui.radar_button.isChecked()}")
                return
            else:
                self.ui.radar_button.setStyleSheet(ButtonStyleEnum.GREEN)
                self.ui.radar_button.setText(_translate("myAGV", "ON"))
                self.console.echo(_translate("myAGV", "close radar"))
                self.ui.Restore_btn.setEnabled(True)
                self.ui.Restore_btn.setStyleSheet(ButtonStyleEnum.GREEN)
                self.ui.startDetectionBtn.setEnabled(True)  # 雷达打开时检测按钮不可使用
                self.ui.startDetectionBtn.setStyleSheet(ButtonStyleEnum.BLUE)
                try:
                    self.radar_flag = False
                    time.sleep(4)  # 等待2s后，释放检测按钮（可用）
                    ComponentsSet.radar_open_close(self.ui, True)
                    self.ui.status_radar.setStyleSheet(ButtonStyleEnum.LightGrey)
                    threading.Thread(target=self.agv_handler.radar_close, daemon=True).start()
                    self.try_connect_agv()
                    self.status_detecting()
                except Exception as e:
                    self.console.exception(e)

    def basic_control(self):

        control_item_basic = self.ui.basic_control_selection.currentText()

        if self.ui.basic_control_button.isChecked():

            if not self.radar_flag:
                QMessageBox.warning(
                    self,
                    _translate("myAGV", "Warning"),
                    _translate("myAGV", "Radar not open!"),
                    QMessageBox.Ok
                )
                self.ui.basic_control_button.setChecked(False)
                return
            else:
                self.ui.basic_control_button.setStyleSheet(ButtonStyleEnum.RED)
                self.ui.basic_control_button.setText(_translate("myAGV", "OFF"))

                self.ui.basic_control_selection.setEnabled(False)  # 设置下拉框不可选区
                self.flag_all = True

                if control_item_basic == "Keyboard Control" or control_item_basic == "键盘控制":
                    self.keyboard_flag = True
                    try:
                        self.console.echo(_translate("myAGV", "Keyboard open..."))
                        threading.Thread(target=self.keyboard_open, daemon=True).start()
                    except Exception as e:
                        self.console.exception(e)

                elif control_item_basic == "Joystick-Alphabet" or control_item_basic == "手柄控制(字母)":
                    self.joystick_flag = True
                    try:
                        self.console.echo(_translate("myAGV", "Open joystick control..."))
                        joystick_open = threading.Thread(target=self.joystick_open, daemon=True)
                        joystick_open.start()

                    except Exception as e:
                        self.console.exception(e)

                elif control_item_basic == "Joystick-Number" or control_item_basic == "手柄控制(数字)":
                    self.joystick_flag = True
                    try:
                        self.console.echo(_translate("myAGV", "Open joystick control"))
                        joystick_open = threading.Thread(target=self.joystick_open_number, daemon=True)
                        joystick_open.start()
                    except Exception as e:
                        self.console.exception(e)

        else:
            self.ui.basic_control_button.setStyleSheet(ButtonStyleEnum.GREEN)
            self.ui.basic_control_button.setText(_translate("myAGV", "ON"))

            self.ui.basic_control_selection.setEnabled(True)

            self.flag_all = False
            if control_item_basic == "Keyboard Control" or control_item_basic == "键盘控制":
                msg = _translate("myAGV", "Close keyboard control")
                try:

                    self.console.echo(msg)
                    keyboard_run_launch = "myagv_teleop.launch"
                    keyboard_close = threading.Thread(
                        target=self.keyboard_close, args=(keyboard_run_launch,), daemon=True)
                    keyboard_close.start()
                    self.keyboard_flag = False
                except Exception as e:
                    self.console.exception(e)

            elif control_item_basic == "Joystick-Alphabet" or control_item_basic == "手柄控制(字母)":
                self.joystick_flag = False

                msg = _translate("myAGV", "close joystick control")
                try:
                    self.console.echo(msg)
                    joystick_run_launch = "myagv_ps2.launch"
                    joystick_close = threading.Thread(target=self.joystick_close, args=(joystick_run_launch,),
                                                      daemon=True)
                    joystick_close.start()

                except Exception as e:
                    self.console.exception(e)

            elif control_item_basic == "Joystick-Number" or control_item_basic == "手柄控制(数字)":

                msg = _translate("myAGV", "close joystick control")
                try:
                    self.console.echo(msg)
                    joystick_run_launch = "myagv_ps2_number.launch"
                    joystick_close = threading.Thread(
                        target=self.joystick_close_number, args=(joystick_run_launch,), daemon=True)
                    joystick_close.start()

                except Exception as e:
                    self.console.exception(e)

    def save_map(self):
        if not self.radar_flag:
            QMessageBox.warning(
                self,
                _translate("myAGV", "Warning"),
                _translate("myAGV", "Radar not open!"),
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
            open_gmapping_build = threading.Thread(target=self.gmapping_build_open, daemon=True)
            open_gmapping_build.start()

        def gmapping_close():
            close_launch = "myagv_slam_laser.launch"
            close_gmapping_build = threading.Thread(target=self.gmapping_build_close, args=(close_launch,), daemon=True)
            # print("quiuii build map")
            close_gmapping_build.start()

        def cartographer_build():
            open_cart_build = threading.Thread(target=self.cartographer_build_open, daemon=True)
            open_cart_build.start()

        def cartographer_close():
            close_cart_build = threading.Thread(target=self.cartographer_build_close, daemon=True)
            close_cart_build.start()

        build_map_method = self.ui.build_map_selection.currentText()

        if self.ui.open_build_map.isChecked():

            if not self.radar_flag:  # 检测雷达
                QMessageBox.warning(
                    self,
                    _translate("myAGV", "Warning"),
                    _translate("myAGV", "Radar not open!"),
                    QMessageBox.Ok
                )
                self.ui.open_build_map.setChecked(False)
                return

            if not self.keyboard_flag:  # 检测键盘控制
                QMessageBox.warning(
                    self,
                    _translate("myAGV", "Warning"),
                    _translate("myAGV", "Please turn on keyboard control before mapping."),
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

                self.ui.open_build_map.setText(_translate("myAGV", "Close Build Map"))
                self.ui.open_build_map.setStyleSheet(ButtonStyleEnum.RED)

                if build_map_method == "Gmapping":
                    self.console.echo(_translate("myAGV", "Open Gmapping..."))
                    gmapping_build()

                if build_map_method == "Cartographer":
                    self.console.echo(_translate("myAGV", "Open Cartographer..."))
                    cartographer_build()

        else:
            self.ui.open_build_map.setStyleSheet(ButtonStyleEnum.BLUE)
            self.ui.open_build_map.setText(_translate("myAGV", "Open Build Map"))

            if build_map_method == "Gmapping":
                self.console.echo(_translate("myAGV", "Close Gmapping"))
                gmapping_close()

            if build_map_method == "Cartographer":
                self.console.echo(_translate("myAGV", "Close Cartographer"))
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
        if self.ui.navigation_3d_button.isChecked():
            if not self.radar_flag:
                QMessageBox.warning(
                    self,
                    _translate("myAGV", "Warning"),
                    _translate("myAGV", "Radar not open!"),
                    QMessageBox.Ok
                )

                self.ui.navigation_3d_button.setChecked(False)
                return

            else:
                self.ui.build_map_selection.setEnabled(False)  # 建图下拉框不可选
                self.ui.open_build_map.setEnabled(False)  # 打开建图不可选
                self.ui.open_build_map.setStyleSheet(ButtonStyleEnum.GRAY)
                self.ui.navigation_button.setEnabled(False)  # 导航不可选
                self.ui.navigation_button.setStyleSheet(ButtonStyleEnum.GRAY)

                self.ui.navigation_3d_button.setText(_translate("myAGV", "Close 3D Navigation"))
                self.ui.navigation_3d_button.setStyleSheet(ButtonStyleEnum.RED)

                self.console.echo(_translate("myAGV", "Open 3D navigation"))

                self.flag_all = True
                open_navigation = threading.Thread(target=self.navigation_open, daemon=True)
                open_navigation.start()

        else:
            self.ui.build_map_selection.setEnabled(True)
            self.ui.open_build_map.setEnabled(True)
            self.ui.open_build_map.setStyleSheet(ButtonStyleEnum.BLUE)
            self.ui.navigation_button.setEnabled(True)
            self.ui.navigation_button.setStyleSheet(ButtonStyleEnum.BLUE)

            self.ui.navigation_3d_button.setText(_translate("myAGV", "3D Navigation"))
            self.ui.navigation_3d_button.setStyleSheet(ButtonStyleEnum.BLUE)

            self.console.echo(_translate("myAGV", "Close 3D navigation"))
            close_launch = "navigation_active.launch"
            close_navigation = threading.Thread(target=self.navigation_close, args=(close_launch,), daemon=True)
            close_navigation.start()
            self.flag_all = False

    def map_navigation(self):
        if self.ui.navigation_button.isChecked():

            if not self.radar_flag:
                QMessageBox.warning(
                    self,
                    _translate("myAGV", "Warning"),
                    _translate("myAGV", "Radar not open!"),
                    QMessageBox.Ok
                )
                self.ui.navigation_button.setChecked(False)
            elif self.keyboard_flag is False:
                QMessageBox.warning(
                    self,
                    _translate("myAGV", "Warning"),
                    _translate("myAGV", "Keyboard Control not open!"),
                    QMessageBox.Ok
                )
                self.ui.navigation_button.setChecked(False)
            else:
                self.ui.build_map_selection.setEnabled(False)
                self.ui.open_build_map.setEnabled(False)
                self.ui.open_build_map.setStyleSheet(ButtonStyleEnum.GRAY)
                self.ui.navigation_3d_button.setEnabled(False)
                self.ui.navigation_3d_button.setStyleSheet(ButtonStyleEnum.GRAY)

                self.ui.navigation_button.setText(_translate("myAGV", "Close Navigation"))
                self.ui.navigation_button.setStyleSheet(ButtonStyleEnum.RED)

                self.console.echo(_translate("myAGV", "Open navigation"))

                self.flag_all = True
                open_navigation = threading.Thread(target=self.navigation_open, daemon=True)
                open_navigation.start()

        else:
            self.ui.build_map_selection.setEnabled(True)
            self.ui.open_build_map.setEnabled(True)
            self.ui.open_build_map.setStyleSheet(ButtonStyleEnum.BLUE)
            self.ui.navigation_3d_button.setEnabled(True)
            self.ui.navigation_3d_button.setStyleSheet(ButtonStyleEnum.BLUE)

            self.ui.navigation_button.setText(_translate("myAGV", "Navigation"))
            self.ui.navigation_button.setStyleSheet(ButtonStyleEnum.BLUE)
            self.console.echo(_translate("myAGV", "Close navigation"))
            close_launch = "navigation_active.launch"
            close_navigation = threading.Thread(target=self.navigation_close, args=(close_launch,), daemon=True)
            close_navigation.start()
            self.flag_all = False

    def start_testing(self):
        current_testing_item = self.ui.functionalComboBoxItems.currentText()
        print(" * Current testing item: ", current_testing_item)
        if self.ui.startDetectionBtn.isChecked():
            if self.radar_flag:
                return QMessageBox.warning(
                    self,
                    _translate("myAGV", "Warning"),
                    _translate("myAGV", "Please turn off the radar before using this function."),
                    QMessageBox.Ok
                )

            self.in_function_testing = True
            self.ui.startDetectionBtn.setText(_translate("myAGV", "Stop Detection"))
            self.ui.startDetectionBtn.setStyleSheet(ButtonStyleEnum.RED)
            self.ui.functionalComboBoxItems.setDisabled(True)

            self.console.echo(Translate.State.Start, current_testing_item, Translate.Other.Testing)

            AGVFunctionalTester = self.functional_testing_mapping[current_testing_item]
            if current_testing_item == Translate.Functional.Camera2D:
                self.functional_testing = AGVFunctionalTester(test_name=current_testing_item)
                self.functional_testing.finished.connect(self.on_functional_finished)
                self.functional_testing.startup()
            else:
                self.functional_testing = AGVFunctionalTester(test_name=current_testing_item, agv=self.agv_handler.agv)
                self.functional_testing.finished.connect(self.on_functional_finished)
                # self.functional_testing.processed.connect(self.on_functional_processed)
                self.functional_testing.start()
            self.button_status_switch(False)
            ComponentsSet.testing_open_close(self.ui, False)
        else:
            if current_testing_item == Translate.Functional.Camera2D:
                if self.functional_testing is not None and self.functional_testing.isVisible():
                    self.functional_testing.shutdown(True)
            else:
                self.functional_testing.terminate()
                self.on_functional_finished(current_testing_item, True)  # 更新延迟

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

        self.agv_status_detector = MyAGVStatusDetector(self.agv_handler.agv)
        self.agv_status_detector.voltages.connect(voltage_set)
        self.agv_status_detector.battery.connect(battery_set)
        self.agv_status_detector.powers.connect(powers_set)
        self.agv_status_detector.motors.connect(motors_set)
        self.agv_status_detector.start()

    @classmethod
    def keyboard_open(cls):
        # self.flag_all=True
        source_ros = "source /opt/ros/noetic/setup.bash"
        source_workspace = "source /home/er/myagv_ros/devel/setup.bash"
        launch_command = "roslaunch myagv_teleop myagv_teleop.launch"
        # subprocess.run(['gnome-terminal', '-e', f"bash -c '{launch_command}; exec $SHELL'"])
        os.system(
            f"gnome-terminal -e 'bash -c \"{source_ros} && {source_workspace} && {launch_command}; exec bash\"'")

    @classmethod
    def keyboard_close(cls, run_launch):
        close_command = "ps -ef | grep -E " + run_launch + " | grep -v 'grep' | awk '{print $2}' | xargs kill -2"
        subprocess.run(close_command, shell=True)

    @classmethod
    def joystick_open(cls):
        source_ros = "source /opt/ros/noetic/setup.bash"
        source_workspace = "source /home/er/myagv_ros/devel/setup.bash"
        launch_command = "roslaunch myagv_ps2 myagv_ps2.launch"
        subprocess.run(
            ['gnome-terminal', '-e', f"bash -c '{source_ros} && {source_workspace} && {launch_command}; exec $SHELL'"])

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
        source_ros = "source /opt/ros/noetic/setup.bash"
        source_workspace = "source /home/er/myagv_ros/devel/setup.bash"
        launch_command = "roslaunch myagv_navigation myagv_slam_laser.launch"
        subprocess.run(
            ['gnome-terminal', '-e', f"bash -c '{source_ros} && {source_workspace} && {launch_command}; exec $SHELL'"]
        )

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
        source_ros = "source /opt/ros/noetic/setup.bash"
        source_workspace = "source /home/er/myagv_ros/devel/setup.bash"
        launch_command = "rosrun map_server map_saver"
        subprocess.run(
            ['gnome-terminal', '-e', f"bash -c '{source_ros} && {source_workspace} && {launch_command}; exec $SHELL'"])

    @classmethod
    def navigation_open(cls):
        source_ros = "source /opt/ros/noetic/setup.bash"
        source_workspace = "source /home/er/myagv_ros/devel/setup.bash"
        launch_command = "roslaunch myagv_navigation navigation_active.launch"
        subprocess.run(
            ['gnome-terminal', '-e', f"bash -c '{source_ros} && {source_workspace} && {launch_command}; exec $SHELL'"])

    @classmethod
    def navigation_close(cls, run_launch):
        os.system("ps -ef | grep -E rviz" + " | grep -v 'grep' | awk '{print $2}' | xargs kill -2")
        os.system("ps -ef | grep -E " + run_launch + " | grep -v 'grep' | awk '{print $2}' | xargs kill -2")

    def closeEvent(self, event):
        GPIO.cleanup()
        if self.agv_status_detector is not None:
            self.agv_status_detector.stop_detector()


def main():
    app = QApplication(sys.argv)

    main_window = MyAGVMainWindow()
    main_window.setup_ui()
    main_window.connect_signals()
    main_window.initialization()
    main_window.show()

    sys.exit(app.exec())


# 程序入口
if __name__ == "__main__":
    main()
