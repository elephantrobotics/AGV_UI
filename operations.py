#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import logging
import sys
import threading
import json
import traceback
import typing as T
from datetime import datetime

from PyQt5.QtCore import QCoreApplication, QTranslator, QTimer
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication, QSizePolicy, QMainWindow, QDesktopWidget

from functions import Functional
from functions.detector import MyAGVStatusDetector, AGVMotor, AGVBattery
from functions.functional import FunctionalBaseTesting, AGVMotorTesting, AGVLEDTesting, AGVPUMPTesting
from functions.ros_subscribe import MoveBaseStatusSubscriber, GoalStatus

from core import GlobalVar, GpioHandler, Command, utils
from core.handler import AgvHandler
from core.style import ButtonStyleEnum
from core.resource import FileResource
from core.console import QConsoleHandler
from core.translate import Translate

from config import LoggingConfiger

from widgets.operation_ui import Ui_Operation as OperationUI
from widgets.color_picker import ColorPickerWidget
from widgets.camera import AGVCameraWidget
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
        self.move_base_status_subscriber: T.Optional[MoveBaseStatusSubscriber] = None

        # flag
        self._3d_camera_status = False
        self.in_function_testing = False  # 功能检测运行中

        self.basic_control_flag = False     # 记录当雷达关闭时， 是否还存在运行的ros节点
        self.build_mapping_flag = False
        self.navigation_2d_flag = False
        self.navigation_3d_flag = False

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
        self.console = logging.getLogger("console")
        self.prompt = QPrompt()
        self.timer = QTimer(self)

    def format_log_by_different_languages(self, *message):
        current_language = self.ui.language_selection.currentText()
        if Translate.Language.English == current_language:
            separator = " "
            return separator.join(message[::-1]).lower().title()
        else:
            separator = ""
        return separator.join(message)

    def setup_ui(self):
        self.ui.setupUi(self)

        # Displayed in the middle of the screen
        size = self.geometry()
        screen = QDesktopWidget().screenGeometry()
        self.move((screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2)

        self.ui.functional_selection.clear()
        self.ui.functional_selection.addItems([
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
        self.ui.navigation_3d_button.setEnabled(False)
        self.ui.navigation_3d_button.setStyleSheet(ButtonStyleEnum.GRAY)
        self.console.addHandler(console_handle)
        self.setup_color_picker()

    def setup_color_picker(self):
        label_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        label_policy.setHeightForWidth(True)

        color = ColorPickerWidget(parent=self, color=self.led_default)
        color.setSizePolicy(label_policy)
        color.setMaximumWidth(200)
        color.setMaximumHeight(150)
        color.setMinimumWidth(200)
        color.setMinimumHeight(150)

        self.color_picker = color
        self.ui.horizontalLayout_palette.insertWidget(0, color)
        self.ui.horizontalLayout_palette.setStretch(0, 2)
        self.ui.horizontalLayout_palette.setStretch(1, 0)
        self.ui.color_brightness_slider.setRange(0, 511)
        self.ui.color_brightness_slider.setValue(511)
        self.ui.color_brightness_slider.valueChanged.connect((lambda x: color.setValue(x / 511)))

    def retranslate_operation(self):
        Translate.reload()  # reload the translation file
        self.ui.functional_selection.clear()
        self.ui.functional_selection.addItems([
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

        self.ui.language_selection.currentTextChanged.disconnect(self.onLanguageChange)

        if language == Translate.Language.English or language in ("英文", "English"):
            self._app.removeTranslator(self.translator)
            self.retranslate_operation()
            self.ui.language_selection.setCurrentText("English")

        elif language == Translate.Language.Chinese or language in ("中文", 'Chinese'):
            language_filepath = self.file_resource.get('translation', 'operations_lang.qm')
            self.translator.load(language_filepath)
            self._app.installTranslator(self.translator)

            self.retranslate_operation()
            self.ui.language_selection.setCurrentText("中文")
        self.ui.language_selection.currentTextChanged.connect(self.onLanguageChange)

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

            self.ui.radar_status.setStyleSheet(ButtonStyleEnum.LightGreen)
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

            self.ui.radar_status.setStyleSheet(ButtonStyleEnum.LightGrey)
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
        else:
            self.agv_handler.open()
            
    def initialization(self):
        self.prompt.set_parent(self)

        is_high = GpioHandler.ishigh(GlobalVar.radar_control_pin)
        is_running = Command.alive("myagv_active.launch")
        self.is_radar_running = is_running and is_high
        self.update_radar_status()
        self.language_initial()

        if is_high is True:
            self.console.info(_translate("myAGV", "Radar is running."))
        else:
            self.console.warning(_translate("myAGV", "Radar is not running."))

        if is_running is True:
            self.console.info(_translate("myAGV", "The topic of radar has been published."))
        else:
            self.console.warning(_translate("myAGV", "The topic of radar has not been published."))

        if is_high and is_running is False:
            Functional.radar_close()

        if is_running and is_high:
            self.ui.radar_status.setStyleSheet(ButtonStyleEnum.GREEN)

    def connect_signals(self):
        self.ui.radar_button.clicked.connect(self.radar_control_handle)
        self.ui.basic_control_button.clicked.connect(self.basic_control_handle)

        self.ui.save_map_button.clicked.connect(self.save_gmapping_handle)
        self.ui.open_build_map.clicked.connect(self.open_build_mapping_handle)

        self.ui.navigation_3d_button.clicked.connect(self.navigation_3D_handle)
        self.ui.navigation_2d_button.clicked.connect(self.navigation_2D_handle)

        self.ui.log_clear.clicked.connect(self.clear_console_handle)

        self.ui.language_selection.currentTextChanged.connect(self.onLanguageChange)

        self.ui.start_detection_btn.clicked.connect(self.start_testing)

        self.ui.restore_btn.clicked.connect(self.servo_restore_handle)

        self.color_picker.currentColorChanged.connect(self.set_color_picker_handle)

        self.ui.build_map_selection.currentTextChanged.connect(self.build_map_change_handle)
        self.ui.navigation_selection.currentTextChanged.connect(self.navigation_change_handle)
        self.timer.timeout.connect(self.system_information_query)
        self.timer.start(2000)

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

    def build_map_change_handle(self, current_text: str):
        # GMapping 需要手动保存,  rtabmap 不需要
        if current_text == "GMapping":
            self.ui.save_map_button.setEnabled(True)
            self.ui.save_map_button.setStyleSheet(ButtonStyleEnum.GREEN)
        else:
            self.ui.save_map_button.setEnabled(False)
            self.ui.save_map_button.setStyleSheet(ButtonStyleEnum.GRAY)

    def navigation_change_handle(self, current_text: str):
        if current_text in ("Multi-point Navigation", "多点导航"):
            self.ui.navigation_3d_button.setEnabled(False)
            self.ui.navigation_3d_button.setStyleSheet(ButtonStyleEnum.GRAY)
        else:
            self.ui.navigation_3d_button.setEnabled(True)
            self.ui.navigation_3d_button.setStyleSheet(ButtonStyleEnum.GREEN)

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

        if not self.check_radar_running(running=True):
            self.ui.restore_btn.setStyleSheet(ButtonStyleEnum.DEEP_GREEN)
            self.agv_handler.restore()

        self.ui.restore_btn.setStyleSheet(ButtonStyleEnum.GREEN)

    def button_status_switch(self, status):
        buttons = [
            {"button": self.ui.basic_control_button, "style": ButtonStyleEnum.GREEN},
            {"button": self.ui.save_map_button, "style": ButtonStyleEnum.GREEN},
            {"button": self.ui.navigation_2d_button, "style": ButtonStyleEnum.BLUE},
            {"button": self.ui.radar_button, "style": ButtonStyleEnum.GREEN},
            {"button": self.ui.open_build_map, "style": ButtonStyleEnum.BLUE},
        ]
        navigation_model = self.ui.navigation_selection.currentText()
        if navigation_model in ("Single-point Navigation", "单点导航"):
            buttons.append(
                {"button": self.ui.navigation_3d_button, "style": ButtonStyleEnum.GREEN},
            )

        for button_item in buttons:
            button = button_item["button"]
            style = button_item["style"]
            if status is False:
                style = ButtonStyleEnum.GRAY
            button.setStyleSheet(style)
            button.setEnabled(status)

    def clear_console_handle(self):
        self.ui.loggerLabel.clear()

    def radar_control_handle(self):
        if self.is_radar_running is False:
            self.update_radar_status(True)
            self.console.info(_translate("myAGV", "Radar open..."))
            threading.Thread(target=Functional.radar_open, daemon=True).start()
            return

        if self.basic_control_flag is True:
            self.prompt.warning(_translate("myAGV", "Warning"), _translate("myAGV", "Basic control is running."))

        elif self.build_mapping_flag is True:
            self.prompt.warning(_translate("myAGV", "Warning"), _translate("myAGV", "Mapping is running."))

        elif self.navigation_2d_flag is True:
            self.prompt.warning(_translate("myAGV", "Warning"), _translate("myAGV", "2D Navigation is running."))

        elif self.navigation_3d_flag is True:
            self.prompt.warning(_translate("myAGV", "Warning"), _translate("myAGV", "3D Navigation is running."))

        else:
            self.console.info(_translate("myAGV", "close radar"))
            threading.Thread(target=Functional.radar_close, daemon=True).start()
            self.update_radar_status(False)

    def basic_control_handle(self):
        if self.basic_control_flag is False:
            if self.check_radar_running(running=False):
                return

            self.ui.basic_control_button.setStyleSheet(ButtonStyleEnum.RED)
            self.ui.basic_control_button.setText(_translate("myAGV", "OFF"))
            self.ui.basic_control_selection.setEnabled(False)  # 设置下拉框不可选区
        else:
            self.ui.basic_control_button.setStyleSheet(ButtonStyleEnum.GREEN)
            self.ui.basic_control_button.setText(_translate("myAGV", "ON"))
            self.ui.basic_control_selection.setEnabled(True)  # 设置下拉框可选区

        control_item_basic = self.ui.basic_control_selection.currentText()

        if control_item_basic in ("Keyboard Control", "键盘控制"):
            if self.basic_control_flag is False:
                self.console.info(_translate("myAGV", "Open keyboard control"))
                Functional.open_keyboard_control()
                self.basic_control_flag = True
            else:
                Functional.close_keyboard_control()
                self.console.info(_translate("myAGV", "Close keyboard control"))
                self.basic_control_flag = False

        elif control_item_basic in ("Joystick-Alphabet", "手柄控制(字母)"):
            if self.basic_control_flag is False:
                self.console.info(_translate("myAGV", "Open joystick-alphabet control"))
                Functional.open_joystick_alphabet_control()
                self.basic_control_flag = True
            else:
                Functional.close_joystick_alphabet_control()
                self.console.info(_translate("myAGV", "Close joystick-alphabet control"))
                self.basic_control_flag = False

        elif control_item_basic in ("Joystick-Number", "手柄控制(数字)"):
            if self.basic_control_flag is False:
                self.console.info(_translate("myAGV", "Open joystick-number control..."))
                Functional.open_joystick_number_control()
                self.basic_control_flag = True
            else:
                Functional.close_joystick_number_control()
                self.console.info(_translate("myAGV", "Close joystick number control"))
                self.basic_control_flag = False

    def save_gmapping_handle(self):
        if self.check_radar_running(running=False):
            return

        if self.build_mapping_flag is False:
            return self.prompt.warning(
                _translate("myAGV", "Warning"),
                # 请先打开 GMapping 构建地图
                _translate("myAGV", "Please open GMapping build map first")
            )

        self.console.info(_translate("myAGV", "Save map..."))
        Functional.save_gmapping_map()

    def open_build_mapping_handle(self):
        open_build_map_method = self.ui.build_map_selection.currentText()

        if self.build_mapping_flag is False:
            if self.check_radar_running(running=False):
                return

            if self.basic_control_flag is False:
                # 使用此功能先先打开基础控制
                self.prompt.warning(
                    _translate("myAGV", "Warning"),
                    _translate("myAGV", "Please open basic control first")
                )
                return

            self.ui.open_build_map.setText(_translate("myAGV", "Close Build Map"))
            self.ui.open_build_map.setStyleSheet(ButtonStyleEnum.RED)

            self.ui.build_map_selection.setEnabled(False)  # 建图方式不可选取
            self.ui.navigation_selection.setEnabled(False)  # 导航方式不可选取

            self.ui.navigation_3d_button.setEnabled(False)  # 建图打开后导航均不可用
            self.ui.navigation_3d_button.setStyleSheet(ButtonStyleEnum.GRAY)

            self.ui.navigation_2d_button.setEnabled(False)
            self.ui.navigation_2d_button.setStyleSheet(ButtonStyleEnum.GRAY)

            if open_build_map_method == "GMapping":
                self.console.info(_translate("myAGV", "Open Gmapping..."))
                Functional.open_gmapping_mapping()
                self.build_mapping_flag = True
            else:
                self.console.info(_translate("myAGV", "Open Rtabmap..."))
                Functional.open_rtabmap_mapping()
                self.build_mapping_flag = True

        else:
            self.ui.open_build_map.setText(_translate("myAGV", "Open Build Map"))
            self.ui.open_build_map.setStyleSheet(ButtonStyleEnum.GREEN)

            self.ui.build_map_selection.setEnabled(True)
            self.ui.navigation_selection.setEnabled(False)  # 导航方式不可选取

            self.ui.navigation_3d_button.setEnabled(True)  # 建图关闭后导航可用
            self.ui.navigation_3d_button.setStyleSheet(ButtonStyleEnum.BLUE)

            self.ui.navigation_2d_button.setEnabled(True)
            self.ui.navigation_2d_button.setStyleSheet(ButtonStyleEnum.BLUE)

            if open_build_map_method == "GMapping":
                Functional.close_gmapping_mapping()
                self.console.info(_translate("myAGV", "Close Gmapping"))
                self.build_mapping_flag = False
            else:
                Functional.close_rtabmap_mapping()
                self.console.info(_translate("myAGV", "Close Rtabmap"))
                self.build_mapping_flag = False

    def navigation_3D_handle(self):
        if self.navigation_3d_flag is False:
            if self.check_radar_running(running=False):
                return

            if self._3d_camera_status is False:
                return self.prompt.warning(
                    _translate("myAGV", "Warning"),
                    _translate("myAGV", "3D camera not connected")
                )

            self.ui.build_map_selection.setEnabled(False)  # 建图下拉框不可选

            self.ui.open_build_map.setEnabled(False)  # 打开建图不可选
            self.ui.open_build_map.setStyleSheet(ButtonStyleEnum.GRAY)

            self.ui.navigation_2d_button.setEnabled(False)  # 导航不可选
            self.ui.navigation_2d_button.setStyleSheet(ButtonStyleEnum.GRAY)

            self.ui.navigation_3d_button.setText(_translate("myAGV", "Close 3D Navigation"))
            self.ui.navigation_3d_button.setStyleSheet(ButtonStyleEnum.RED)

            self.console.info(_translate("myAGV", "Open 3D navigation"))

            Functional.open_3d_navigation()
            self.navigation_3d_flag = True

        else:
            self.ui.build_map_selection.setEnabled(True)

            self.ui.open_build_map.setEnabled(True)
            self.ui.open_build_map.setStyleSheet(ButtonStyleEnum.BLUE)

            self.ui.navigation_2d_button.setEnabled(True)
            self.ui.navigation_2d_button.setStyleSheet(ButtonStyleEnum.BLUE)

            self.ui.navigation_3d_button.setText(_translate("myAGV", "3D Navigation"))
            self.ui.navigation_3d_button.setStyleSheet(ButtonStyleEnum.BLUE)

            self.console.info(_translate("myAGV", "Close 3D navigation"))
            Functional.close_3d_navigation()
            self.navigation_3d_flag = False

    def navigation_2D_handle(self):
        navigation_2d_method = self.ui.navigation_selection.currentText()
        if self.navigation_2d_flag is False:
            if self.check_radar_running(running=False):
                return

            if self.basic_control_flag is False:
                return self.prompt.warning(
                    _translate("myAGV", "Warning"),
                    _translate("myAGV", "Keyboard Control not open!"),
                )

            if self.build_mapping_flag is True:
                return self.prompt.warning(
                    _translate("myAGV", "Warning"),
                    _translate("myAGV", "Build map not close!")
                )

            self.ui.build_map_selection.setEnabled(False)

            self.ui.open_build_map.setEnabled(False)
            self.ui.open_build_map.setStyleSheet(ButtonStyleEnum.GRAY)

            self.ui.save_map_button.setEnabled(False)
            self.ui.save_map_button.setStyleSheet(ButtonStyleEnum.GRAY)

            self.ui.navigation_2d_button.setText(_translate("myAGV", "Close Navigation"))
            self.ui.navigation_2d_button.setStyleSheet(ButtonStyleEnum.RED)

            self.console.info(_translate("myAGV", "Open 2D navigation"))

            if navigation_2d_method in ("Multi-point Navigation", "多点导航"):
                Functional.open_multipoint_navigation()
                self.move_base_status_subscriber = MoveBaseStatusSubscriber(parent=self)
                self.move_base_status_subscriber.goal_status_changed.connect(self.on_navigation_goal_status_changed)
                self.move_base_status_subscriber.start()
            else:
                Functional.open_singlepoint_navigation()
            self.navigation_2d_flag = True
        else:
            self.ui.build_map_selection.setEnabled(True)

            self.ui.open_build_map.setEnabled(True)
            self.ui.open_build_map.setStyleSheet(ButtonStyleEnum.BLUE)

            self.ui.save_map_button.setEnabled(True)
            self.ui.save_map_button.setStyleSheet(ButtonStyleEnum.GREEN)

            self.ui.navigation_2d_button.setText(_translate("myAGV", "2D Navigation"))
            self.ui.navigation_2d_button.setStyleSheet(ButtonStyleEnum.BLUE)
            self.console.info(_translate("myAGV", "Close 2D navigation"))
            if navigation_2d_method in ("Multi-point Navigation", "多点导航"):
                Functional.close_multipoint_navigation()
                if self.move_base_status_subscriber is not None:
                    self.move_base_status_subscriber.unregister()
            else:
                Functional.close_singlepoint_navigation()
            self.navigation_2d_flag = False

    def on_navigation_goal_status_changed(self, point: int, status: GoalStatus):
        try:
            navi_point = _translate("myAGV", "Target navigation point")
            if status.status == GoalStatus.SUCCEEDED:
                # status_message = _translate("myAGV", "导航成功")
                status_message = _translate("myAGV", "navigation success")
                self.console.info(f"{navi_point} {point}, {status_message}")
            elif status.status == GoalStatus.PREEMPTED:
                # status_message = _translate("myAGV", "导航被抢占")
                status_message = _translate("myAGV", "navigation is preempted")
                self.console.error(f"{navi_point} {point}, {status_message}")
            elif status.status == GoalStatus.ABORTED:
                # status_message = _translate("myAGV", "导航失败")
                status_message = _translate("myAGV", "navigation failed")
                self.console.error(f"{navi_point} {point}, {status_message}")
            elif status.status == GoalStatus.REJECTED:
                # status_message = _translate("myAGV", "导航被拒绝")
                status_message = _translate("myAGV", "navigation is denied")
                self.console.error(f"{navi_point} {point}, {status_message}")
            elif status.status == GoalStatus.ACTIVE:
                # status_message = _translate("myAGV", "导航正在执行")
                status_message = _translate("myAGV", "navigation is being performed")
                self.console.info(f"{navi_point} {point}, {status_message}")
            elif status.status == GoalStatus.PENDING:
                # status_message = _translate("myAGV", "导航等待执行")
                status_message = _translate("myAGV", "navigation awaits execution")
                self.console.info(f"{navi_point} {point}, {status_message}")
            else:
                # status_message = _translate("myAGV", "未知导航状态")
                status_message = _translate("myAGV", f"unknown navigation status")
                self.console.error(f"{navi_point} {point}, {status_message}")

        except Exception as e:
            print(f"Error in on_navigation_goal_status_changed: {e}")
            print(traceback.format_exc())

    def start_testing(self):
        current_testing_item = self.ui.functional_selection.currentText()
        if self.in_function_testing is False:
            if self.check_radar_running(running=True):
                return

            self.in_function_testing = True
            self.ui.start_detection_btn.setText(_translate("myAGV", "Stop Detection"))
            self.ui.start_detection_btn.setStyleSheet(ButtonStyleEnum.RED)

            self.ui.functional_selection.setEnabled(False)
            self.ui.navigation_selection.setEnabled(False)
            self.ui.build_map_selection.setEnabled(False)
            self.ui.basic_control_selection.setEnabled(False)

            self.console.info(self.format_log_by_different_languages(
                Translate.State.Start, current_testing_item, Translate.Other.Testing
            ))

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
        else:
            if current_testing_item == Translate.Functional.Camera2D:
                if isinstance(self.functional_testing, AGVCameraWidget) and self.functional_testing.isVisible():
                    self.functional_testing.shutdown()
                return

            if self.functional_testing is not None and self.functional_testing.isRunning():
                self.functional_testing.terminate()
                self.on_functional_finished(current_testing_item, True)  # 更新延迟

    def on_functional_finished(self, test_name, is_stop=False):
        if is_stop is True:
            self.console.info(self.format_log_by_different_languages(
                Translate.State.Stop, test_name, Translate.Other.Testing
            ))
        elif isinstance(self.functional_testing, AGVCameraWidget) and not self.functional_testing.opened():
            self.console.info(self.format_log_by_different_languages(
                Translate.State.Fail, Translate.Other.CameraOpenFailed
            ))
        else:
            self.console.info(self.format_log_by_different_languages(
                Translate.State.Finish, test_name, Translate.Other.Testing
            ))

        self.functional_testing = None
        self.ui.start_detection_btn.setText(_translate("myAGV", "Start Detection"))
        self.ui.start_detection_btn.setStyleSheet(ButtonStyleEnum.BLUE)

        self.ui.functional_selection.setEnabled(True)
        self.ui.navigation_selection.setEnabled(True)
        self.ui.build_map_selection.setEnabled(True)
        self.ui.basic_control_selection.setEnabled(True)

        self.button_status_switch(True)
        self.in_function_testing = False

    def on_motor_status_updated(self, motors_status: AGVMotor):
        ui_motors = [
            self.ui.electricity_motor1,
            self.ui.electricity_motor2,
            self.ui.electricity_motor3,
            self.ui.electricity_motor4
        ]
        motor_style_status = ButtonStyleEnum.LightGreen if motors_status.state else ButtonStyleEnum.LightGrey
        self.ui.motor_status.setStyleSheet(motor_style_status)
        for el, val in enumerate(zip(ui_motors, motors_status.currents)):
            val[0].setText(str(val[1]))

    def on_battery_status_updated(self, battery_status: AGVBattery):
        main_battery_style = ButtonStyleEnum.LightGreen if battery_status.status[0] else ButtonStyleEnum.LightGrey
        sub_battery_style = ButtonStyleEnum.LightGreen if battery_status.status[1] else ButtonStyleEnum.LightGrey
        self.ui.main_battery_state.setStyleSheet(main_battery_style)
        self.ui.backup_battery_state.setStyleSheet(sub_battery_style)

        self.ui.main_battery_voltage.setText(str(battery_status.voltages[0]))
        self.ui.backup_battery_voltage.setText(str(battery_status.voltages[1]))

        self.ui.main_battery_power.setText(str(battery_status.powers[0]))
        self.ui.backup_battery_power.setText(str(battery_status.powers[1]))

    def on_version_updated(self, version: str):
        self.ui.firmware_version_edit.setText(version)

    def status_detecting(self):
        self.agv_status_detector = MyAGVStatusDetector(agv_handler=self.agv_handler, interval=1, parent=self)
        self.agv_status_detector.motor_stated.connect(self.on_motor_status_updated)
        self.agv_status_detector.battery_stated.connect(self.on_battery_status_updated)
        self.agv_status_detector.versioned.connect(self.on_version_updated)
        self.agv_status_detector.start()

    def system_information_query(self):
        ipaddress = utils.get_localhost()
        camera_status = utils.get_3d_camera_status()
        self._3d_camera_status = camera_status
        self.ui.ip_address_edit.setText(ipaddress)
        self.ui.camera_3d_status.setStyleSheet(
            ButtonStyleEnum.LightGreen if camera_status else ButtonStyleEnum.LightGrey
        )

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
