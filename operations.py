#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import logging
import sys
import json
import traceback
import typing as T
from PyQt5.QtCore import QCoreApplication, QTranslator
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication, QSizePolicy, QDesktopWidget, QWidget

from functions import Functional
from functions.detector import MyAGVStatusDetector, Motor, BatteryGroup
from functions.functional import FunctionalBaseTesting, AGVMotorTesting, AGVLEDTesting, AGVPUMPTesting
from functions.ros_subscribe import MoveBaseStatusSubscriber, GoalStatus
from functions.aging import AgvMotorPersistentAging, AgingDirectionFlag, AgingState, AgingStateFlag

from core import GlobalVar, GpioHandler, Command, System
from api.handler import AgvHandler
from core.stylesheet import Stylesheet
from core.resource import FileResource
from core.console import QConsoleHandler
from core.translate import Translate

from config import LoggingConfiger, __version__

from components.operation_ui import Ui_Operation as OperationUI
from components.color_picker import ColorPickerWidget
from components.button import SwitchButton
from components.camera import AGVCameraWidget
from components.prompt import QPrompt

GpioHandler.setmode(GpioHandler.BCM)
GpioHandler.setup(GlobalVar.radar_control_pin, GpioHandler.OUT)

_translate = QCoreApplication.translate


class MyAGVMainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.ui = OperationUI()
        self.color_picker: T.Optional[ColorPickerWidget] = None
        self.led_mode_toggle_btn: T.Optional[SwitchButton] = None
        self.agv_handler: T.Optional[AgvHandler] = None
        self.functional_testing: T.Optional[FunctionalBaseTesting, AGVCameraWidget] = None
        self.agv_status_detector: T.Optional[MyAGVStatusDetector] = None
        self.move_base_status_subscriber: T.Optional[MoveBaseStatusSubscriber] = None
        self.agv_motor_persistent_aging: T.Optional[AgvMotorPersistentAging] = None

        # flag
        self.is_diy_mode = False        # LED 自定义模式
        self.is_motor_stalled = False   # 电机堵转
        self.is_motor_encoder_abnormal = False  # 电机编码器异常

        self._3d_camera_status = False
        self.camera_3d_flag = False
        self.in_function_testing = False  # 功能检测运行中

        self.basic_control_flag = False  # 记录当雷达关闭时， 是否还存在运行的ros节点
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
        self.led_default = (255, 255, 255)
        self._app = QApplication.instance()
        self.translator = QTranslator(self)
        self.file_resource = FileResource('resources')
        self.console = logging.getLogger("console")
        self.prompt = QPrompt()

        # language
        self.current_language = Translate.Language.English

    def format_language(self, *message):
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
        self.console.addHandler(console_handle)

        self.navigation_change_handle()
        self.setup_color_picker()
        self.setup_color_button()
        self.setup_system_configer()

    def setup_color_button(self):
        switch_button = SwitchButton(on_color="rgb(39, 174, 96)", off_color="#dadada")
        self.ui.led_color_picker_panel.setEnabled(False)
        self.ui.led_control_header.layout().addWidget(switch_button)
        self.color_picker.setValue(0.5)
        self.color_picker.setEnabled(True)
        self.led_mode_toggle_btn = switch_button

    def on_brightness_slider_changed(self, value: int):
        if self.agv_motor_persistent_aging is not None:
            return self.prompt.warning(
                _translate("myAGV", "Warning"),
                # 老化正在运行，不允许修改亮度
                _translate("myAGV", "Aging is running, brightness modification is not allowed!")
            )
        print(f" # brightness slider changed: {value}")
        self.color_picker.setValue(value / 510)

    def on_color_button_state_changed(self, switch_state: bool):
        if not self.agv_handler.is_opened:
            print(f" # agv handler not opened, switch button state: {switch_state}")
            return

        if self.agv_motor_persistent_aging is not None:
            print(f" # aaaaaa led mode toggle button state: {switch_state} {self.led_mode_toggle_btn.isChecked()}")
            if self.led_mode_toggle_btn.isChecked():
                return

            self.led_mode_toggle_btn.switch_state(True, False)
            self.prompt.warning(
                _translate("myAGV", "Warning"),
                # 老化正在运行，不允许关闭
                _translate("myAGV", "Aging is running and cannot be shutdown!")
            )
            return

        print(f" # switch button state changed: {switch_state}")
        led_mode = int(switch_state)
        print(f" # toggle led mode: {led_mode}")
        self.agv_handler.set_led_mode(led_mode)
        self.ui.led_color_picker_panel.setEnabled(switch_state)

        if switch_state is False:
            print(f" # close diy mode")
            self.color_picker.setValue(value=0.5, notify=False)
        else:
            print(f" # open diy mode")
            value = self.ui.color_brightness_slider.value()
            self.color_picker.setValue(value=value / 510, notify=True)

            if self.check_radar_running(running=True):
                return

    def setup_color_picker(self):
        label_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        label_policy.setHeightForWidth(True)

        color_picker = ColorPickerWidget(parent=self, color=self.led_default)
        color_picker.setMaximumWidth(200)
        color_picker.setMaximumHeight(150)
        color_picker.setMinimumWidth(200)
        color_picker.setMinimumHeight(150)
        color_picker.setSizePolicy(label_policy)

        self.color_picker = color_picker
        self.ui.horizontalLayout_palette.insertWidget(0, color_picker)
        self.ui.horizontalLayout_palette.setStretch(0, 2)
        self.ui.horizontalLayout_palette.setStretch(1, 0)
        self.ui.color_brightness_slider.setRange(0, 510)
        self.ui.color_brightness_slider.setValue(510)

        color = self.color_picker.getColor()
        self.ui.lineEdit_HEX.setText(color.name())
        self.ui.lineEdit_RGB.setText(f"({color.red()}, {color.green()}, {color.blue()})")

    def setup_system_configer(self):
        if not System.RASPBERRYPI.equal(GlobalVar.system_device_model):
            return

        self.ui.camera_3d_panel.setHidden(True)

        for counter in range(self.ui.camera_3d_layout.count()):
            item = self.ui.camera_3d_layout.itemAt(counter)
            if item.widget():
                item.widget().setHidden(True)

        self.ui.build_map_selection.clear()
        self.ui.build_map_selection.addItem("GMapping")
        self.ui.navigation_3d_button.setHidden(True)

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
            self.ui.radar_control_button.setText(_translate("myAGV", "OFF"))
        else:
            self.ui.radar_control_button.setText(_translate("myAGV", "ON"))

        if self.agv_motor_persistent_aging is not None:
            self.ui.start_aging_btn.setText(_translate("myAGV", "Stop Aging"))
        else:
            self.ui.start_aging_btn.setText(_translate("myAGV", "Start Aging"))

        self.setup_system_configer()

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
        self.setWindowTitle(f"AGV_UI v{__version__}")

    def onLanguageChange(self, language: str):
        language_filepath = self.file_resource.get('translation', 'language.json')
        with open(language_filepath, "w") as f:
            json.dump({"language": language}, f, indent=4)
        self.language_initial(language)
        self.current_language = language

    def update_radar_status(self, is_running: T.Optional[bool] = None):
        if is_running is not None:
            self.is_radar_running = is_running
        else:
            is_running = self.is_radar_running

        if is_running is True:
            self.ui.radar_status.setEnabled(True)
            self.ui.restore_btn.setEnabled(False)
            self.ui.start_aging_btn.setEnabled(False)
            self.ui.start_detection_btn.setEnabled(False)
            self.ui.radar_control_button.setText(_translate("myAGV", "OFF"))
            self.ui.radar_control_button.setStyleSheet(Stylesheet.RedButtonStyle)

            self.led_mode_toggle_btn.switch_state(False, False)
            self.on_color_button_state_changed(False)

            if self.agv_status_detector is not None:
                self.agv_status_detector.emit_empty_data()

            if self.agv_handler is not None:
                self.agv_handler.close()

        else:
            self.ui.radar_status.setEnabled(False)
            self.ui.restore_btn.setEnabled(True)
            self.ui.start_aging_btn.setEnabled(True)
            self.ui.start_detection_btn.setEnabled(True)
            self.led_mode_toggle_btn.setEnabled(True)
            self.ui.radar_control_button.setText(_translate("myAGV", "ON"))
            self.ui.radar_control_button.setStyleSheet(Stylesheet.GreenButtonStyle)
            self.connect_agv_handler()
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
            self.agv_handler.stop()
        else:
            print(f" # open agv serial port {self.agv_handler.is_opened}")
            self.agv_handler.open()
            print(f" # open agv serial port {self.agv_handler.is_opened}")

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
            self.ui.radar_status.setEnabled(True)

    def connect_signals(self):
        self.ui.radar_control_button.clicked.connect(self.radar_control_handle)
        self.ui.basic_control_button.clicked.connect(self.basic_control_handle)
        self.ui.save_mapping_button.clicked.connect(self.save_gmapping_handle)
        self.ui.open_build_map.clicked.connect(self.open_build_mapping_handle)
        self.ui.navigation_3d_button.clicked.connect(self.navigation_3D_handle)
        self.ui.navigation_2d_button.clicked.connect(self.navigation_2D_handle)
        self.ui.log_clear.clicked.connect(self.clear_console_handle)
        self.ui.language_selection.currentTextChanged.connect(self.onLanguageChange)
        self.ui.start_detection_btn.clicked.connect(self.start_testing)
        self.ui.restore_btn.clicked.connect(self.servo_restore_handle)
        self.ui.build_map_selection.currentTextChanged.connect(self.build_map_change_handle)
        self.ui.navigation_selection.currentTextChanged.connect(self.navigation_change_handle)
        self.ui.camera_3d_button.clicked.connect(self.camera_3D_handle)
        self.ui.start_aging_btn.clicked.connect(self.start_motor_persistent_aging)
        self.color_picker.currentColorChanged.connect(self.set_color_picker_handle)
        self.led_mode_toggle_btn.switched.connect(self.on_color_button_state_changed)
        self.ui.color_brightness_slider.valueChanged.connect(self.on_brightness_slider_changed)

    def on_console_output(self, message):
        self.ui.loggerLabel.append(message)

        if not self.ui.loggerLabel.underMouse():
            end_cursor = self.ui.loggerLabel.textCursor().End
            self.ui.loggerLabel.moveCursor(end_cursor)

    def on_functional_processed(self, parameters: T.Dict[str, T.Any]):
        test_name = parameters.get("test_name")
        if test_name == Translate.Functional.Motor:
            direction = parameters.get("direction")
            self.console.info(f"{test_name} {direction}")
        elif test_name == Translate.Functional.Pump:
            behavior = parameters.get("behavior")
            self.console.info(f"{test_name} {behavior}")
        elif test_name == Translate.Functional.Led:
            name = parameters.get("name")
            color = parameters.get("color")
            self.console.info(f"{test_name} {name} {color}")

    def build_map_change_handle(self, current_text: str):
        # GMapping 需要手动保存,  rtabmap 不需要
        if current_text == "GMapping":
            self.ui.save_mapping_button.setEnabled(True)
        else:
            self.ui.save_mapping_button.setEnabled(False)

    def navigation_change_handle(self, current_text: str = None):
        if current_text is None:
            current_text = self.ui.navigation_selection.currentText()

        if current_text in ("Single-point Navigation", "单点导航"):
            self.ui.navigation_3d_button.setEnabled(False)
        else:
            self.ui.navigation_3d_button.setEnabled(True)

    def set_color_picker_handle(self, color: T.Optional[QColor] = None):
        print(f" # set led color")
        if color is None:
            color = self.color_picker.selected_color

        if self.check_radar_running(running=True):  # open radar
            return

        if self.check_function_testing():  # in functional testing
            return

        if not self.led_mode_toggle_btn.isChecked():
            return

        if self.agv_motor_persistent_aging is not None:
            # 老化正在运行，不允许设置颜色
            title = _translate("myAGV", "Warning")
            message = _translate("myAGV", "Aging is running, setting color is not allowed!")
            self.prompt.warning(title, message)
            self.console.warning(message)
            return

        red = color.red()
        green = color.green()
        blue = color.blue()

        color_hex = color.name()
        self.ui.lineEdit_HEX.setText(color_hex)
        self.ui.lineEdit_RGB.setText(f"({red}, {green}, {blue})")
        self.agv_handler.set_led(1, red, green, blue)
        print(f" # {color_hex} ({red}, {green}, {blue})")

    def servo_restore_handle(self):
        self.console.info(_translate("myAGV", "Motor Restore"))

        if not self.check_radar_running(running=True):
            self.ui.restore_btn.setEnabled(False)
            self.agv_handler.restore()
            self.ui.restore_btn.setEnabled(True)

    def button_status_switch(self, status):
        for button in [
            self.ui.basic_control_button,
            self.ui.save_mapping_button,
            self.ui.navigation_2d_button,
            self.ui.navigation_3d_button,
            self.ui.radar_control_button,
            self.ui.open_build_map,
            self.ui.camera_3d_button
        ]:
            button.setEnabled(status)

    def clear_console_handle(self):
        self.ui.loggerLabel.clear()

    def radar_control_handle(self):
        if self.agv_motor_persistent_aging is not None:
            self.prompt.warning(_translate("myAGV", "Warning"), _translate("myAGV", "Aging is running."))
            return

        if self.is_radar_running is False:
            self.update_radar_status(True)
            self.console.info(_translate("myAGV", "Radar open..."))
            Functional.radar_open()
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
            Functional.radar_close()
            self.update_radar_status(False)

    def basic_control_handle(self):
        if self.basic_control_flag is False:
            if self.check_radar_running(running=False):
                return

            self.ui.basic_control_button.setStyleSheet(Stylesheet.RedButtonStyle)
            self.ui.basic_control_button.setText(_translate("myAGV", "OFF"))
            self.ui.basic_control_selection.setEnabled(False)  # 设置下拉框不可选区
        else:
            self.ui.basic_control_button.setStyleSheet(Stylesheet.GreenButtonStyle)
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
            self.ui.open_build_map.setStyleSheet(Stylesheet.RedButtonStyle)

            self.ui.build_map_selection.setEnabled(False)  # 建图方式不可选取
            self.ui.navigation_selection.setEnabled(False)  # 导航方式不可选取

            self.ui.navigation_3d_button.setEnabled(False)  # 建图打开后导航均不可用

            self.ui.navigation_2d_button.setEnabled(False)

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
            self.ui.open_build_map.setStyleSheet(Stylesheet.GreenButtonStyle)

            self.ui.build_map_selection.setEnabled(True)
            self.ui.navigation_selection.setEnabled(True)  # 导航方式不可选取

            navigation_model = self.ui.navigation_selection.currentText()
            navigation_enabled = navigation_model in ("Single-point Navigation", "单点导航")
            self.ui.navigation_3d_button.setEnabled(not navigation_enabled)  # 建图关闭后导航可用

            self.ui.navigation_2d_button.setEnabled(True)

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

            if self.build_mapping_flag is True:
                return self.prompt.warning(
                    _translate("myAGV", "Warning"),
                    _translate("myAGV", "Build map not close!")
                )

            if self.camera_3d_flag is False:
                return self.prompt.warning(
                    _translate("myAGV", "Warning"),
                    _translate("myAGV", "Please open 3D camera first!")
                )

            self.ui.navigation_selection.setEnabled(False)  # 导航选项不可选
            self.ui.build_map_selection.setEnabled(False)  # 建图下拉框不可选
            self.ui.open_build_map.setEnabled(False)  # 打开建图不可选
            self.ui.navigation_2d_button.setEnabled(False)  # 导航不可选

            self.ui.navigation_3d_button.setText(_translate("myAGV", "Close 3D Navigation"))
            self.ui.navigation_3d_button.setStyleSheet(Stylesheet.RedButtonStyle)

            self.console.info(_translate("myAGV", "Open 3D navigation"))
            Functional.open_3d_navigation()
            self.move_base_status_subscriber = MoveBaseStatusSubscriber(parent=self)
            self.move_base_status_subscriber.goal_status_changed.connect(self.on_navigation_goal_status_changed)
            self.move_base_status_subscriber.start()

            self.navigation_3d_flag = True

        else:
            self.ui.navigation_selection.setEnabled(True)  # 导航选项不可选
            self.ui.build_map_selection.setEnabled(True)
            self.ui.open_build_map.setEnabled(True)
            self.ui.navigation_2d_button.setEnabled(True)

            self.ui.navigation_3d_button.setText(_translate("myAGV", "3D Navigation"))
            self.ui.navigation_3d_button.setStyleSheet(Stylesheet.BlueButtonStyle)

            self.console.info(_translate("myAGV", "Close 3D navigation"))
            Functional.close_3d_navigation()
            self.navigation_3d_flag = False

    def camera_3D_handle(self):
        if self.camera_3d_flag is False:
            if self._3d_camera_status is False:
                return self.prompt.warning(
                    _translate("myAGV", "Warning"),
                    _translate("myAGV", "3D camera not connected")
                )

            self.console.info(_translate("myAGV", "Open 3D camera"))
            self.ui.camera_3d_button.setText(_translate("myAGV", "OFF"))
            self.ui.camera_3d_button.setStyleSheet(Stylesheet.RedButtonStyle)
            Functional.open_3d_camera()
            self.camera_3d_flag = True
        else:
            self.console.info(_translate("myAGV", "Close 3D camera"))
            self.ui.camera_3d_button.setText(_translate("myAGV", "ON"))
            self.ui.camera_3d_button.setStyleSheet(Stylesheet.BlueButtonStyle)
            Functional.close_3d_camera()
            self.camera_3d_flag = False

    def navigation_2D_handle(self):
        navigation_2d_method = self.ui.navigation_selection.currentText()
        if self.navigation_2d_flag is False:
            if self.check_radar_running(running=False):
                return

            if self.build_mapping_flag is True:
                return self.prompt.warning(
                    _translate("myAGV", "Warning"),
                    _translate("myAGV", "Build map not close!")
                )

            self.ui.navigation_selection.setEnabled(False)  # 导航选项不可选
            self.ui.build_map_selection.setEnabled(False)
            self.ui.open_build_map.setEnabled(False)
            self.ui.navigation_3d_button.setEnabled(False)
            self.ui.save_mapping_button.setEnabled(False)

            self.ui.navigation_2d_button.setText(_translate("myAGV", "Close Navigation"))
            self.ui.navigation_2d_button.setStyleSheet(Stylesheet.RedButtonStyle)

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
            self.ui.navigation_selection.setEnabled(True)
            self.ui.build_map_selection.setEnabled(True)
            self.ui.open_build_map.setEnabled(True)
            self.ui.navigation_3d_button.setEnabled(True)
            self.ui.save_mapping_button.setEnabled(True)

            self.ui.navigation_2d_button.setText(_translate("myAGV", "2D Navigation"))
            self.ui.navigation_2d_button.setStyleSheet(Stylesheet.BlueButtonStyle)
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
                status_message = _translate("myAGV", "navigation success")
                self.console.info(f"{navi_point} {point}, {status_message}")
            elif status.status == GoalStatus.PREEMPTED:
                status_message = _translate("myAGV", "navigation is preempted")
                self.console.error(f"{navi_point} {point}, {status_message}")
            elif status.status == GoalStatus.ABORTED:
                status_message = _translate("myAGV", "navigation failed")
                self.console.error(f"{navi_point} {point}, {status_message}")
            elif status.status == GoalStatus.REJECTED:
                status_message = _translate("myAGV", "navigation is denied")
                self.console.error(f"{navi_point} {point}, {status_message}")
            elif status.status == GoalStatus.ACTIVE:
                status_message = _translate("myAGV", "navigation is being performed")
                self.console.info(f"{navi_point} {point}, {status_message}")
            elif status.status == GoalStatus.PENDING:
                status_message = _translate("myAGV", "navigation awaits execution")
                self.console.info(f"{navi_point} {point}, {status_message}")
            else:
                status_message = _translate("myAGV", f"unknown navigation status")
                self.console.error(f"{navi_point} {point}, {status_message}")

        except Exception as e:
            print(f"Error in on_navigation_goal_status_changed: {e}")
            print(traceback.format_exc())

    def start_testing(self):
        if self.agv_motor_persistent_aging is not None:
            self.prompt.warning(_translate("myAGV", "Warning"), _translate("myAGV", "Aging is running."))
            return

        current_testing_item = self.ui.functional_selection.currentText()
        if self.in_function_testing is False:
            if self.check_radar_running(running=True):
                return

            self.in_function_testing = True
            self.ui.start_detection_btn.setText(_translate("myAGV", "Stop Detection"))
            self.ui.start_detection_btn.setStyleSheet(Stylesheet.RedButtonStyle)

            self.ui.functional_selection.setEnabled(False)
            self.ui.navigation_selection.setEnabled(False)
            self.ui.build_map_selection.setEnabled(False)
            self.ui.basic_control_selection.setEnabled(False)
            self.ui.led_control_panel.setEnabled(False)
            self.led_mode_toggle_btn.setChecked(False)
            self.ui.motor_aging_panel.setEnabled(False)

            self.console.info(self.format_language(
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
                self.functional_testing.processed.connect(self.on_functional_processed)
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
            self.console.info(self.format_language(Translate.State.Stop, test_name, Translate.Other.Testing))

        elif isinstance(self.functional_testing, AGVCameraWidget) and self.functional_testing.opened():
            self.console.info(self.format_language(Translate.Other.CameraOpenFailed))
        else:
            self.console.info(self.format_language(Translate.State.Finish, test_name, Translate.Other.Testing))

        self.functional_testing = None
        self.ui.start_detection_btn.setText(_translate("myAGV", "Start Detection"))
        self.ui.start_detection_btn.setStyleSheet(Stylesheet.BlueButtonStyle)

        self.ui.functional_selection.setEnabled(True)
        self.ui.navigation_selection.setEnabled(True)
        self.ui.build_map_selection.setEnabled(True)
        self.ui.basic_control_selection.setEnabled(True)
        self.ui.led_control_panel.setEnabled(True)
        self.ui.motor_aging_panel.setEnabled(True)

        self.button_status_switch(True)
        self.in_function_testing = False

    def on_motor_status_updated(self, motors: T.List[Motor]):
        ui_motors = [
            self.ui.electricity_motor1,
            self.ui.electricity_motor2,
            self.ui.electricity_motor3,
            self.ui.electricity_motor4
        ]
        currents = [motor.current for motor in motors]
        self.ui.motor_status.setEnabled(any(map(lambda x: x > 0, currents)))
        for current, ui in zip(currents, ui_motors):
            ui.setText(f'{current:.2f}')

        self.is_motor_stalled = any(motor.stall_state for motor in motors)
        for motor in filter(lambda m: m.stall_state is True, motors):
            if motor.id == 1:
                self.console.error(_translate("MyAGV", "The upper left motor is blocked"))
            elif motor.id == 2:
                self.console.error(_translate("MyAGV", "The upper right motor is blocked"))
            elif motor.id == 3:
                self.console.error(_translate("MyAGV", "The lower left motor is blocked"))
            elif motor.id == 4:
                self.console.error(_translate("MyAGV", "The lower right motor is blocked"))
            else:
                self.console.error(_translate("MyAGV", "The motor is blocked"))

        if self.is_motor_stalled:
            # 请尝试恢复!
            self.console.error(_translate("MyAGV", "Please try to recover!"))

            # 请检查电机编码器是否异常！
            self.console.error(_translate("MyAGV", "Please check whether the motor encoder is abnormal!"))

        self.is_motor_encoder_abnormal = any(motor.encoder_state for motor in motors)
        for motor in filter(lambda m: m.encoder_state is True, motors):
            if motor.id == 1:
                # 左上角电机编码器异常
                self.console.error(_translate("MyAGV", "The encoder of the upper left motor is abnormal"))
                # 请检查左上角的电机通讯线是否连接正常！
                self.console.error(_translate("MyAGV", "Please check whether the motor communication cable in the upper left corner is connected normally!"))
            elif motor.id == 2:
                # 右上角电机编码器异常
                self.console.error(_translate("MyAGV", "The encoder of the upper right motor is abnormal"))
                # 请检查右上角的电机通讯线是否连接正常！
                self.console.error(_translate("MyAGV", "Please check whether the motor communication cable in the upper right corner is connected normally!"))
            elif motor.id == 3:
                # 左下角电机编码器异常
                self.console.error(_translate("MyAGV", "The encoder of the lower left motor is abnormal"))
                # 请检查左下角的电机通讯线是否连接正常！
                self.console.error(_translate("MyAGV", "Please check whether the motor communication cable in the lower left corner is connected normally!"))
            elif motor.id == 4:
                # 右下角电机编码器异常
                self.console.error(_translate("MyAGV", "The encoder of the lower right motor is abnormal"))
                # 请检查右下角的电机通讯线是否连接正常！
                self.console.error(_translate("MyAGV", "Please check whether the motor communication cable in the lower right corner is connected normally!"))

        if self.agv_motor_persistent_aging is not None and (
                self.is_motor_stalled is True or self.is_motor_encoder_abnormal is True
        ):
            title = _translate("MyAGV", "Warning")
            # AGV 电机持续老化测试停止
            message = _translate("MyAGV", "AGV motor persistent aging test is stopped")
            self.console.error(message)
            self.agv_motor_persistent_aging.stopped()
            self.prompt.warning(title, message)

    def on_battery_status_updated(self, battery_group: BatteryGroup):

        for battery in battery_group.batteries:
            if battery.id == 1:
                self.ui.main_battery_state.setEnabled(battery.plugged)
                self.ui.main_battery_voltage.setText(f"{battery.voltage:.2f}")
                self.ui.main_battery_power.setText(f"{battery.percentage:.2f}%")

            elif battery.id == 2:
                self.ui.backup_battery_state.setEnabled(battery.plugged)
                self.ui.backup_battery_voltage.setText(f"{battery.voltage:.2f}")
                self.ui.backup_battery_power.setText(f"{battery.percentage:.2f}%")

    def on_version_updated(self, version: str):
        self.ui.firmware_version_edit.setText(version)

    def status_detecting(self):
        self.agv_status_detector = MyAGVStatusDetector(agv_handler=self.agv_handler, interval=1, parent=self)
        self.agv_status_detector.motor_stated.connect(self.on_motor_status_updated)
        self.agv_status_detector.battery_stated.connect(self.on_battery_status_updated)
        self.agv_status_detector.versioned.connect(self.on_version_updated)
        self.agv_status_detector.ip_stated.connect(self.on_localhost_changer)
        self.agv_status_detector.camera_changed.connect(self.on_3d_camera_state_changer)
        self.agv_status_detector.start()

    def on_localhost_changer(self, ipaddress: str):
        self.ui.ip_address_edit.setText(ipaddress)

    def on_3d_camera_state_changer(self, plug: bool):
        if self.ui.camera_3d_layout.count() == 0:
            return

        self.ui.camera_3d_status.setEnabled(plug)
        self._3d_camera_status = plug

    def start_motor_persistent_aging(self):
        self.ui.start_aging_btn.setEnabled(False)

        if self.agv_motor_persistent_aging is not None:
            is_stopping = self.prompt.question(
                title="MyAGV",
                # 电机持续老化正在运行，您要停止吗？
                message=_translate("MyAGV", "Motor persistent aging is running, do you want to stop it?")
            )
            if is_stopping is True:
                self.ui.start_aging_btn.setEnabled(False)
                self.agv_motor_persistent_aging.stopped()
                # 确认停止电机持续老化
                self.console.info(_translate("MyAGV", "Confirm that the stop motor continues to deteriorate"))
            else:
                # 提示已取消停止老化
                # 取消停止电机持续老化
                self.console.info(_translate("MyAGV", "Cancel the stop and the motor continues to age"))
                self.ui.start_aging_btn.setEnabled(True)
            return

        if self.check_radar_running(running=True):
            self.ui.start_aging_btn.setEnabled(True)
            return

        if self.is_motor_stalled is True:
            # 电机存在堵转, 请检查电机编码器是否正常
            message = _translate(
                "MyAGV",
                "There is stalled rotor in the motor, please check whether the motor encoder is normal"
            )
            self.console.error(message)
            self.prompt.warning(_translate("myAGV", "Warning"), message)
            self.ui.start_aging_btn.setEnabled(True)
            return False

        # 提示开始进行老化
        self.ui.color_brightness_slider.setValue(510)
        self.ui.color_brightness_slider.setEnabled(False)
        self.led_mode_toggle_btn.setEnabled(False)
        self.changer_picker(255, 255, 0)
        self.console.info(_translate("MyAGV", "Start Motor Persistent Aging"))
        self.agv_motor_persistent_aging = AgvMotorPersistentAging(parent=self)
        self.agv_motor_persistent_aging.noticed.connect(self.on_motor_persistent_aging_noticed)
        self.agv_motor_persistent_aging.finished.connect(self.on_motor_persistent_aging_finished)
        self.agv_motor_persistent_aging.start()

        self.ui.start_aging_btn.setEnabled(True)
        self.ui.start_aging_btn.setText(_translate("MyAGV", "Stop Aging"))
        self.ui.start_aging_btn.setStyleSheet(Stylesheet.RedButtonStyle)

    def changer_picker(self, r, g, b):
        self.led_mode_toggle_btn.switch_state(state=True, notify=False)
        for i in range(3):
            self.color_picker.setColor(QColor(r, g, b))

    @classmethod
    def get_aging_prompt_message(cls, direction_flag: AgingDirectionFlag, state_flag: AgingStateFlag):
        aging_prompt_message_table = {
            AgingDirectionFlag.FORWARD: {
                # AGV开始向前移动
                AgingStateFlag.STARTUP: _translate("MyAGV", "The AGV starts to move forward"),
                # AGV停止向前移动
                AgingStateFlag.STOPPED: _translate("MyAGV", "The AGV stops moving forward"),
                # AGV完成向前移动
                AgingStateFlag.FINISHED: _translate("MyAGV", "The AGV completes its forward movement"),
            },
            AgingDirectionFlag.BACKWARD: {
                # AGV开始向后移动
                AgingStateFlag.STARTUP: _translate("MyAGV", "The AGV starts to move backward"),
                # AGV停止向后移动
                AgingStateFlag.STOPPED: _translate("MyAGV", "The AGV stops moving backward"),
                # AGV完成向后移动
                AgingStateFlag.FINISHED: _translate("MyAGV", "The AGV completes its backward movement"),
            },
            AgingDirectionFlag.PAN_LEFT: {
                # AGV开始向左移动
                AgingStateFlag.STARTUP: _translate("MyAGV", "The AGV starts to move left"),
                # AGV停止向左移动
                AgingStateFlag.STOPPED: _translate("MyAGV", "The AGV stops moving left"),
                # AGV完成向左移动
                AgingStateFlag.FINISHED: _translate("MyAGV", "The AGV completes its movement to the left"),
            },
            AgingDirectionFlag.PAN_RIGHT: {
                # AGV开始向右移动
                AgingStateFlag.STARTUP: _translate("MyAGV", "The AGV starts to move right"),
                # AGV停止向右移动
                AgingStateFlag.STOPPED: _translate("MyAGV", "The AGV stops moving right"),
                # AGV完成向右移动
                AgingStateFlag.FINISHED: _translate("MyAGV", "The AGV completes its movement to the right"),
            },
            AgingDirectionFlag.CLOCKWISE_ROTATION: {
                # AGV开始顺时针旋转
                AgingStateFlag.STARTUP: _translate("MyAGV", "The AGV starts to clockwise rotation"),
                # AGV停止顺时针旋转
                AgingStateFlag.STOPPED: _translate("MyAGV", "The AGV stops moving clockwise rotation"),
                # AGV完成顺时针旋转
                AgingStateFlag.FINISHED: _translate("MyAGV", "The AGV completes the clockwise rotation"),
            },
            AgingDirectionFlag.COUNTERCLOCKWISE_ROTATION: {
                # AGV开始逆时针旋转
                AgingStateFlag.STARTUP: _translate("MyAGV", "The AGV starts to counterclockwise rotation"),
                # AGV停止逆时针旋转
                AgingStateFlag.STOPPED: _translate("MyAGV", "The AGV has stopped counterclockwise rotation"),
                # AGV完成逆时针旋转
                AgingStateFlag.FINISHED: _translate("MyAGV", "The AGV completes the counterclockwise rotation"),
            }
        }

        direction_message_table = aging_prompt_message_table.get(direction_flag, None)
        if direction_message_table is None:
            return _translate("MyAGV", "Unknown direction")

        return direction_message_table.get(state_flag, _translate("MyAGV", "Unknown state"))

    def on_motor_persistent_aging_noticed(self, aging_state: AgingState):
        if aging_state.state_flag == AgingStateFlag.RUNNING:
            aging_duration_text = _translate('MyAGV', 'Aging duration: ')
            aging_progress_text = _translate('MyAGV', 'Aging progress: ')
            aging_speed_text = _translate('MyAGV', 'Aging speed: ')

            self.console.info(f"{aging_progress_text}{aging_state.progress:.2f}%")
            self.console.info(f"{aging_duration_text}{aging_state.duration:.2f}s")
            self.console.info(f"{aging_speed_text}{aging_state.speed:.2f}m/s")
            return

        message = self.get_aging_prompt_message(aging_state.direction_flag, aging_state.state_flag)
        self.console.info(message)
        return

    def on_motor_persistent_aging_finished(self, aging_state: bool):
        self.ui.color_brightness_slider.setEnabled(True)    # 无法提前知道当前状态改变, 以及不能拒绝状态改变，所以直接禁用
        self.led_mode_toggle_btn.setEnabled(True)
        self.agv_motor_persistent_aging = None
        self.agv_handler.stop()

        if aging_state is True:
            if self.is_motor_stalled is False and self.is_motor_encoder_abnormal is False:
                self.changer_picker(0, 255, 0)

            self.console.info(_translate("MyAGV", "Motor Persistent Aging Finished"))
        else:
            self.console.info(_translate("MyAGV", "Motor Persistent Aging Stopped"))

            if any((self.is_motor_stalled, self.is_motor_encoder_abnormal)):
                self.changer_picker(255, 0, 0)
            else:
                self.changer_picker(0, 0, 255)

        if not self.ui.start_aging_btn.isEnabled():
            self.ui.start_aging_btn.setEnabled(True)

        self.ui.start_aging_btn.setText(_translate("MyAGV", "Start Aging"))
        self.ui.start_aging_btn.setStyleSheet(Stylesheet.GreenButtonStyle)

    def closeEvent(self, event):
        GpioHandler.cleanup()
        if System.RASPBERRYPI.equal(GlobalVar.system_device_model):
            GpioHandler.setmode(GpioHandler.BCM)
            GpioHandler.setup(GlobalVar.radar_control_pin, GpioHandler.OUT)
            GpioHandler.output(GlobalVar.radar_control_pin, GpioHandler.HIGH)

        if self.agv_status_detector is not None:
            print(f" # stop detector")
            self.agv_status_detector.stop_detector()

        if self.agv_motor_persistent_aging is not None:
            print(f" # stop aging")
            self.agv_motor_persistent_aging.terminate()
            self.agv_handler.stop()

        if self.agv_handler.is_opened:
            print(f" # close auto report state")
            self.agv_handler.set_auto_report_state(0)

        print(" # exit")
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
