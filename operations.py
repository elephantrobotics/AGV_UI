# encoding:utf-8
import logging
import os
import subprocess
import sys
import threading
import json
import typing as T
from PyQt5.QtCore import QCoreApplication, QTranslator
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication, QMessageBox, QSizePolicy, QMainWindow, QDesktopWidget

from functions import Functional
from functions.detector import MyAGVStatusDetector
from functions.functional import FunctionalBaseTesting, AGVMotorTesting, AGVLEDTesting, AGVPUMPTesting

from core import GlobalVar, GpioHandler, utils, Command
from core.handler import AgvHandler
from core.style import ButtonStyleEnum
from core.resource import FileResource
from core.console import QConsoleHandler
from core.translate import Translate

from config import LoggingConfiger

from widgets.operation_ui import Ui_Operation as OperationUI
from widgets.color_picker import ColorPickerWidget
from widgets.camera import AGVCameraWidget
from widgets.component_status import ComponentsSet
from widgets.prompt import QPrompt

GpioHandler.setmode(GpioHandler.BCM)
GpioHandler.setup(GlobalVar.radar_control_pin, GpioHandler.IN)
_translate = QCoreApplication.translate


class MyAGVMainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = OperationUI()
        self.color_picker: T.Optional[ColorPickerWidget] = None
        self.agv_handler: T.Optional[AgvHandler] = None
        self.functional_testing: T.Optional[FunctionalBaseTesting, AGVCameraWidget] = None
        self.agv_status_detector: T.Optional[MyAGVStatusDetector] = None

        # flag
        self.keyboard_flag = False
        self.joystick_flag = False
        self.in_function_testing = False  # 功能检测运行中
        self.flag_all = False   # 记录当雷达关闭时， 是否还存在运行的ros节点
        self.flag_build = False
        self.is_radar_running: T.Optional[bool] = None  # 雷达状态

        # mapping
        self.functional_testing_mapping: T.Dict = {
            Translate.Functional.Led: AGVLEDTesting,
            Translate.Functional.Pump: AGVPUMPTesting,
            Translate.Functional.Motor: AGVMotorTesting,
            Translate.Functional.Camera2D: AGVCameraWidget
        }

        # handler
        self.led_default = (255, 0, 0)  # red light
        self._app = QApplication.instance()
        self.translator = QTranslator(self)
        self.file_resource = FileResource('assets')
        self.console = logging.getLogger()
        self.prompt = QPrompt()

    def setup_ui(self):
        self.ui.setupUi(self)

        # Displayed in the middle of the screen
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2)

        self.ui.lineEdit_RGB.setStyleSheet("background:None")
        self.ui.lineEdit_HEX.setStyleSheet("background:None")
        self.ui.color_palette.setVisible(False)
        self.ui.label_value.setVisible(False)
        self.ui.logo_lab.setVisible(False)
        self.ui.menu_widget.setVisible(False)

        self.ui.status_battery_main.setStyleSheet(ButtonStyleEnum.LightGrey)
        self.ui.status_battery_backup_2.setStyleSheet(ButtonStyleEnum.LightGrey)
        self.ui.status_motor_1.setStyleSheet(ButtonStyleEnum.LightGrey)

        self.ui.functional_items.clear()
        self.ui.functional_items.addItems([
            Translate.Functional.Led,
            Translate.Functional.Pump,
            Translate.Functional.Motor,
            Translate.Functional.Camera2D
        ])

        formatter = logging.Formatter(
            fmt=LoggingConfiger.Console.message_format,
            datefmt=LoggingConfiger.Console.timestamp_format
        )
        console_handle = QConsoleHandler(formatter=formatter, level=LoggingConfiger.Console.level, parent=self)
        console_handle.outputted.connect(self.on_console_output)
        self.console.addHandler(console_handle)
        self.setup_color_picker()

    def setup_color_picker(self):
        label_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        label_policy.setHeightForWidth(True)

        color = ColorPickerWidget(parent=self, color=self.led_default)
        color.setSizePolicy(label_policy)
        color.setMaximumWidth(150)
        color.setMaximumHeight(150)
        color.setMinimumWidth(150)
        color.setMinimumHeight(150)

        self.color_picker = color
        self.ui.horizontalLayout_palette.insertWidget(0, color)
        self.ui.color_brightness_slider.valueChanged.connect((lambda x: color.setValue(x / 511)))

    def retranslate_operation(self):
        Translate.reload()  # reload the translation file
        self.ui.functional_items.clear()
        self.ui.functional_items.addItems([
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
        if self.is_radar_running is True:
            self.ui.radar_button.setText(_translate("myAGV", "OFF"))
        else:
            self.ui.radar_button.setText(_translate("myAGV", "ON"))

    def language_initial(self, language: T.Optional[str] = None):
        if language is None:
            language_filepath = self.file_resource.get('translation', 'language.json')
            with open(language_filepath, "r", encoding='utf-8') as f:
                language = json.loads(f.read())["language"]

        self.ui.languageSelection.currentTextChanged.disconnect(self.onLanguageChange)

        if language == Translate.Language.English or language in ("英文", "English"):
            self._app.removeTranslator(self.translator)
            self.retranslate_operation()
            self.ui.languageSelection.setCurrentText("English")

        elif language == Translate.Language.Chinese or language in ("中文", 'Chinese'):
            language_filepath = self.file_resource.get('translation', 'operations_lang.qm')
            self.translator.load(language_filepath)
            self._app.installTranslator(self.translator)

            self.retranslate_operation()
            self.ui.languageSelection.setCurrentText("中文")
        self.ui.languageSelection.currentTextChanged.connect(self.onLanguageChange)

    def onLanguageChange(self, language: str):
        language_filepath = self.file_resource.get('translation', 'language.json')
        with open(language_filepath, "w") as f:
            json.dump({"language": language}, f, indent=4)
        self.language_initial(language)

    def update_radar_status(self, is_running: T.Optional[bool] = None):
        if is_running is not None:
            self.is_radar_running = is_running
        else:
            is_running = self.is_radar_running

        if is_running is True:
            self.color_picker.setEnabled(False)
            self.ui.start_detection_btn.setEnabled(False)
            self.ui.start_detection_btn.setStyleSheet(ButtonStyleEnum.GRAY)
            self.ui.color_brightness_slider.setEnabled(False)
            self.ui.restore_btn.setEnabled(False)
            self.ui.restore_btn.setStyleSheet(ButtonStyleEnum.GRAY)

            self.ui.status_radar.setStyleSheet(ButtonStyleEnum.LightGreen)
            self.ui.radar_button.setText(_translate("myAGV", "OFF"))
            self.ui.radar_button.setStyleSheet(ButtonStyleEnum.RED)
            self.ui.radar_button.setChecked(True)

            if self.agv_status_detector is not None:
                self.agv_status_detector.stop_detector()

            if self.agv_handler is not None:
                self.agv_handler.close()

        else:
            self.color_picker.setEnabled(True)
            self.ui.restore_btn.setEnabled(True)
            self.ui.restore_btn.setStyleSheet(ButtonStyleEnum.GREEN)
            self.ui.start_detection_btn.setEnabled(True)
            self.ui.start_detection_btn.setStyleSheet(ButtonStyleEnum.BLUE)
            self.ui.color_brightness_slider.setEnabled(True)

            self.ui.status_radar.setStyleSheet(ButtonStyleEnum.LightGrey)
            self.ui.radar_button.setText(_translate("myAGV", "ON"))
            self.ui.radar_button.setStyleSheet(ButtonStyleEnum.GREEN)
            self.ui.radar_button.setChecked(True)

            self.connect_agv_handler()
            self.set_color_picker_handle()
            self.status_detecting()

    def check_function_testing(self):
        if self.in_function_testing:
            self.prompt.warning(
                _translate("myAGV", "Warning"),
                _translate("myAGV", "Please stop the detection before using the led."),
            )
        return self.in_function_testing

    def check_radar_running(self, running: bool = True):
        """
        检查雷达是否在运行
        :param running: True 在运行, False 未运行
        :return:
        """
        if self.is_radar_running is True and running is True:
            self.prompt.warning(
                _translate("myAGV", "Warning"),
                _translate("myAGV", "Please turn off the radar before using this function.")
            )
            return True

        if self.is_radar_running is False and running is False:
            self.prompt.warning(
                _translate("myAGV", "Warning"),
                _translate("myAGV", "Radar not open!"),
            )
            return True
    
    def connect_agv_handler(self):
        if self.agv_handler is None:
            self.agv_handler = AgvHandler(port=GlobalVar.comport, baudrate=GlobalVar.baudrate, debug=GlobalVar.debug)
            version = self.agv_handler.get_system_version()
            self.ui.VersionEdit.setText(version)

            # #####################################################
            if version == '1.0':
                self.agv_handler.set_led_mode(1)  # 适配1.0版本, 1.1之后可删除
                self.agv_handler.stop()
            # #####################################################
        else:
            self.agv_handler.open()
            
    def initialization(self):
        self.prompt.set_parent(self)

        ipaddress = utils.get_localhost()
        self.ui.HostEdit.setText(ipaddress)

        self.ui.build_map_selection.addItems([
            _translate("myAGV", "Gmapping"),
            _translate("myAGV", "3D Mapping")
        ])

        is_high = GpioHandler.ishigh(GlobalVar.radar_control_pin)
        is_running = Command.alive("myagv_active.launch")
        if is_high is True:
            self.console.info(_translate("myAGV", "Radar is running."))
        else:
            self.console.warning(_translate("myAGV", "Radar is not running."))

        if is_running is True:
            self.console.info(_translate("myAGV", "The topic of radar has been published."))
        else:
            self.console.warning(_translate("myAGV", "The topic of radar has not been published."))

        if is_running and is_high:
            self.ui.status_radar.setStyleSheet(ButtonStyleEnum.GREEN)

        self.is_radar_running = is_running and is_high
        self.update_radar_status()
        self.language_initial()

    def connect_signals(self):
        self.ui.radar_button.clicked.connect(self.radar_control_handle)
        self.ui.basic_control_button.clicked.connect(self.basic_control_handle)

        self.ui.save_map_button.clicked.connect(self.save_map)
        self.ui.open_build_map.clicked.connect(self.open_build_map)

        self.ui.navigation_3d_button.clicked.connect(self.navigation_3d)
        self.ui.navigation_button.clicked.connect(self.map_navigation)

        self.ui.log_clear.clicked.connect(self.clear_console_handle)

        self.ui.languageSelection.currentTextChanged.connect(self.onLanguageChange)

        self.ui.color_brightness_slider.setRange(0, 511)
        self.ui.color_brightness_slider.setValue(511)

        self.ui.start_detection_btn.clicked.connect(self.start_testing)

        self.ui.restore_btn.clicked.connect(self.servo_restore_handle)

        self.color_picker.currentColorChanged.connect(self.set_color_picker_handle)

    def on_console_output(self, message):
        self.ui.loggerLabel.append(message)
        if not self.ui.loggerLabel.underMouse():
            end_cursor = self.ui.loggerLabel.textCursor().End
            self.ui.loggerLabel.moveCursor(end_cursor)

    def on_functional_processed(self, parameters: T.Dict[str, T.Any]):
        test_name = parameters.get("test_name")
        if test_name == Translate.Functional.Motor:
            direction = parameters.get("direction")
            self.console.info(test_name, direction)
        elif test_name == Translate.Functional.Pump:
            behavior = parameters.get("behavior")
            self.console.info(test_name, behavior)
        elif test_name == Translate.Functional.Led:
            name = parameters.get("name")
            color = parameters.get("color")
            self.console.info(test_name, name, str(color))

    def on_functional_finished(self, test_name, is_stop=False):
        if is_stop is True:
            self.console.info(Translate.State.Stop, test_name, Translate.Other.Testing)
        elif isinstance(self.functional_testing, AGVCameraWidget) and not self.functional_testing.opened():
            self.console.info(Translate.State.Fail, Translate.Other.CameraOpenFailed)
        else:
            self.console.info(Translate.State.Finish, test_name, Translate.Other.Testing)

        testing_status = self.ui.start_detection_btn.isEnabled()

        self.functional_testing = None
        self.ui.start_detection_btn.setChecked(not testing_status)
        self.ui.start_detection_btn.setText(_translate("myAGV", "Start Detection"))
        self.ui.start_detection_btn.setStyleSheet(ButtonStyleEnum.BLUE)
        self.ui.functional_items.setDisabled(False)
        self.button_status_switch(True)
        self.in_function_testing = False

        ComponentsSet.testing_open_close(self.ui, True)

    def set_color_picker_handle(self, color: T.Optional[QColor] = None):
        if color is None:
            color = self.color_picker.selected_color

        if self.check_radar_running(running=True):  # open radar
            return

        if self.check_function_testing():  # in functional testing
            return

        if self.agv_handler is None:  # not connect
            return

        red = color.red()
        green = color.green()
        blue = color.blue()

        color_hex = color.name()
        self.ui.lineEdit_HEX.setText(color_hex)
        self.ui.lineEdit_RGB.setText(f"({red}, {green}, {blue})")
        self.agv_handler.set_led(1, red, green, blue)

    def servo_restore_handle(self):
        self.console.info(_translate("myAGV", "Motor Restore"))

        if self.check_radar_running(running=True) is False:
            self.ui.restore_btn.setStyleSheet(ButtonStyleEnum.DEEP_GREEN)
            self.agv_handler.restore()

        self.ui.restore_btn.setStyleSheet(ButtonStyleEnum.GREEN)

    def button_status_switch(self, status):
        button_style = ButtonStyleEnum.BLUE if status else ButtonStyleEnum.GRAY
        buttons = [
            self.ui.basic_control_button,
            self.ui.save_map_button,
            self.ui.open_build_map,
            self.ui.navigation_button,
            self.ui.navigation_3d_button
        ]
        for button in buttons:
            button.setStyleSheet(button_style)
            button.setCheckable(status)
            button.setEnabled(status)

    def clear_console_handle(self):
        self.ui.loggerLabel.clear()

    def radar_control_handle(self):
        if self.is_radar_running is False:
            self.update_radar_status(True)
            self.console.info(_translate("myAGV", "Radar open..."))
            threading.Thread(target=Functional.radar_open, daemon=True).start()

        elif self.flag_all:  # other functions are running...
            self.ui.radar_button.setChecked(True)
            self.prompt.warning(
                _translate("myAGV", "Warning"),
                _translate("myAGV", "Other functions are running.")
            )
        else:
            self.console.info(_translate("myAGV", "close radar"))
            threading.Thread(target=Functional.radar_close, daemon=True).start()
            self.update_radar_status(False)

    def basic_control_handle(self):

        control_item_basic = self.ui.basic_control_selection.currentText()

        if self.ui.basic_control_button.isChecked():

            if self.check_radar_running(running=True) is False:
                self.ui.basic_control_button.setChecked(False)
                return

            self.ui.basic_control_button.setStyleSheet(ButtonStyleEnum.RED)
            self.ui.basic_control_button.setText(_translate("myAGV", "OFF"))

            self.ui.basic_control_selection.setEnabled(False)  # 设置下拉框不可选区

            if control_item_basic == "Keyboard Control" or control_item_basic == "键盘控制":
                self.keyboard_flag = True
                try:
                    self.console.info(_translate("myAGV", "Keyboard open..."))
                    threading.Thread(target=self.keyboard_open, daemon=True).start()
                except Exception as e:
                    self.console.exception(e)

            elif control_item_basic == "Joystick-Alphabet" or control_item_basic == "手柄控制(字母)":
                self.joystick_flag = True
                try:
                    self.console.info(_translate("myAGV", "Open joystick control..."))
                    joystick_open = threading.Thread(target=self.joystick_open, daemon=True)
                    joystick_open.start()

                except Exception as e:
                    self.console.exception(e)

            elif control_item_basic == "Joystick-Number" or control_item_basic == "手柄控制(数字)":
                self.joystick_flag = True
                try:
                    self.console.info(_translate("myAGV", "Open joystick control"))
                    joystick_open = threading.Thread(target=self.joystick_open_number, daemon=True)
                    joystick_open.start()
                except Exception as e:
                    self.console.exception(e)

        else:
            self.ui.basic_control_button.setStyleSheet(ButtonStyleEnum.GREEN)
            self.ui.basic_control_button.setText(_translate("myAGV", "ON"))

            self.ui.basic_control_selection.setEnabled(True)

            if control_item_basic == "Keyboard Control" or control_item_basic == "键盘控制":
                try:
                    self.console.info(_translate("myAGV", "Close keyboard control"))
                    keyboard_run_launch = "myagv_teleop.launch"
                    keyboard_close = threading.Thread(target=self.keyboard_close, args=(keyboard_run_launch,),
                                                      daemon=True)
                    keyboard_close.start()
                    self.keyboard_flag = False
                except Exception as e:
                    self.console.exception(e)

            elif control_item_basic == "Joystick-Alphabet" or control_item_basic == "手柄控制(字母)":
                self.joystick_flag = False

                try:
                    self.console.info(_translate("myAGV", "close joystick control"))
                    joystick_run_launch = "myagv_ps2.launch"
                    joystick_close = threading.Thread(
                        target=self.joystick_close, args=(joystick_run_launch,), daemon=True)
                    joystick_close.start()

                except Exception as e:
                    self.console.exception(e)

            elif control_item_basic == "Joystick-Number" or control_item_basic == "手柄控制(数字)":

                try:
                    self.console.info(_translate("myAGV", "close joystick control"))
                    joystick_run_launch = "myagv_ps2_number.launch"
                    joystick_close = threading.Thread(
                        target=self.joystick_close_number, args=(joystick_run_launch,), daemon=True)
                    joystick_close.start()

                except Exception as e:
                    self.console.exception(e)

    def save_map(self):
        if not self.is_radar_running:
            QMessageBox.warning(
                self,
                _translate("myAGV", "Warning"),
                _translate("myAGV", "Radar not open!"),
                QMessageBox.Ok
            )
            self.ui.save_map_button.setChecked(False)
            return
        else:
            save_map = threading.Thread(target=self.save_map_file, daemon=True)
            save_map.start()

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

            if not self.is_radar_running:  # 检测雷达
                QMessageBox.warning(
                    self,
                    _translate("myAGV", "Warning"),
                    _translate("myAGV", "Radar not open!"),
                    QMessageBox.Ok
                )
                self.ui.open_build_map.setChecked(False)
                return

            if not self.keyboard_flag:  # 检测键盘控制
                self.prompt.warning(
                    _translate("myAGV", "Warning"),
                    _translate("myAGV", "Please turn on keyboard control before mapping.")
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

                self.ui.open_build_map.setText(_translate("myAGV", "Close Build Map"))
                self.ui.open_build_map.setStyleSheet(ButtonStyleEnum.RED)

                if build_map_method == "Gmapping":
                    self.console.info(_translate("myAGV", "Open Gmapping..."))
                    gmapping_build()

                if build_map_method == "Cartographer":
                    self.console.info(_translate("myAGV", "Open Cartographer..."))
                    cartographer_build()

        else:
            self.ui.open_build_map.setStyleSheet(ButtonStyleEnum.BLUE)
            self.ui.open_build_map.setText(_translate("myAGV", "Open Build Map"))

            if build_map_method == "Gmapping":
                self.console.info(_translate("myAGV", "Close Gmapping"))
                gmapping_close()

            if build_map_method == "Cartographer":
                self.console.info(_translate("myAGV", "Close Cartographer"))
                cartographer_close()

            # 关闭建图打开导航按钮

            self.ui.build_map_selection.setEnabled(True)
            self.ui.navigation_3d_button.setEnabled(True)  # 建图关闭后导航可用
            self.ui.navigation_3d_button.setStyleSheet(ButtonStyleEnum.BLUE)
            self.ui.navigation_button.setEnabled(True)
            self.ui.navigation_button.setStyleSheet(ButtonStyleEnum.BLUE)
            self.flag_build = True

    def navigation_3d(self):
        if self.ui.navigation_3d_button.isChecked():
            if not self.is_radar_running:
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

                self.console.info(_translate("myAGV", "Open 3D navigation"))

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

            self.console.info(_translate("myAGV", "Close 3D navigation"))
            close_launch = "navigation_active.launch"
            close_navigation = threading.Thread(target=self.navigation_close, args=(close_launch,), daemon=True)
            close_navigation.start()

    def map_navigation(self):
        if self.ui.navigation_button.isChecked():

            if not self.is_radar_running:
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

                self.console.info(_translate("myAGV", "Open navigation"))

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
            self.console.info(_translate("myAGV", "Close navigation"))
            close_launch = "navigation_active.launch"
            close_navigation = threading.Thread(target=self.navigation_close, args=(close_launch,), daemon=True)
            close_navigation.start()

    @classmethod
    def keyboard_open(cls):
        source_ros = "source /opt/ros/noetic/setup.bash"
        source_workspace = "source /home/er/myagv_ros/devel/setup.bash"
        launch_command = "roslaunch myagv_teleop myagv_teleop.launch"
        # subprocess.run(['gnome-terminal', '-e', f"bash -c '{launch_command}; exec $SHELL'"])
        os.system(f"gnome-terminal -e 'bash -c \"{source_ros} && {source_workspace} && {launch_command}; exec bash\"'")

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
        subprocess.run(['gnome-terminal', '-e', f"bash -c '{source_ros} && {source_workspace} && {launch_command}; exec $SHELL'"])

    @classmethod
    def navigation_close(cls, run_launch):
        os.system("ps -ef | grep -E rviz" + " | grep -v 'grep' | awk '{print $2}' | xargs kill -2")
        os.system("ps -ef | grep -E " + run_launch + " | grep -v 'grep' | awk '{print $2}' | xargs kill -2")
    
    def start_testing(self):
        current_testing_item = self.ui.functional_items.currentText()
        if self.ui.start_detection_btn.isChecked():
            if self.check_radar_running(running=True):
                return

            self.in_function_testing = True
            self.ui.start_detection_btn.setText(_translate("myAGV", "Stop Detection"))
            self.ui.start_detection_btn.setStyleSheet(ButtonStyleEnum.RED)
            self.ui.functional_items.setDisabled(True)

            self.console.info(Translate.State.Start, current_testing_item, Translate.Other.Testing)

            AGVFunctionalTester = self.functional_testing_mapping[current_testing_item]
            if current_testing_item == Translate.Functional.Camera2D:
                self.functional_testing = AGVFunctionalTester(test_name=current_testing_item)
                self.functional_testing.finished.connect(self.on_functional_finished)
                self.functional_testing.startup()
            else:
                self.functional_testing = AGVFunctionalTester(test_name=current_testing_item, agv=self.agv_handler)
                self.functional_testing.finished.connect(self.on_functional_finished)
                # self.functional_testing.processed.connect(self.on_functional_processed)
                self.functional_testing.start()
            self.button_status_switch(False)
            ComponentsSet.testing_open_close(self.ui, False)
        else:
            if current_testing_item == Translate.Functional.Camera2D:
                if isinstance(self.functional_testing, AGVCameraWidget) and self.functional_testing.isVisible():
                    self.functional_testing.shutdown()
                return

            if self.functional_testing is not None and self.functional_testing.isRunning():
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

        self.agv_status_detector = MyAGVStatusDetector(self.agv_handler)
        self.agv_status_detector.voltages.connect(voltage_set)
        self.agv_status_detector.battery.connect(battery_set)
        self.agv_status_detector.powers.connect(powers_set)
        self.agv_status_detector.motors.connect(motors_set)
        self.agv_status_detector.start()

    def closeEvent(self, event):
        GpioHandler.cleanup()
        if self.agv_status_detector is not None:
            self.agv_status_detector.stop_detector()
        event.accept()


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
