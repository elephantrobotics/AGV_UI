#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import time
import traceback
import typing as T
import serial.serialutil
from PyQt5.QtCore import pyqtSignal, QThread, QObject
from PyQt5.QtWidgets import QApplication

from api.handler import AgvHandler, Motor, BatteryGroup, Battery
from core import utils


def wait_for_timeout(timeout: T.Union[float, int]):
    base_time = 0.1
    loop_counter = int(timeout / base_time)
    for i in range(loop_counter):
        QApplication.processEvents()
        time.sleep(base_time)


class MyAGVStatusDetector(QThread):
    battery_stated = pyqtSignal(BatteryGroup)
    motor_stated = pyqtSignal(list)
    versioned = pyqtSignal(str)
    ip_stated = pyqtSignal(str)
    camera_changed = pyqtSignal(bool)

    def __init__(self, agv_handler: AgvHandler, interval: float = 10, parent: QObject = None):
        super().__init__(parent=parent)
        self.__agv_handler = agv_handler
        self.__detector = True
        self.__interval = interval
        self.__firmware_version = "0.0.0"
        self.__localhost = "127.0.0.1"
        self.__3d_camera_state = False

    def stop_detector(self):
        self.__detector = False
        self.set_auto_report_state(0)
        self.motor_stated.emit([Motor(id=i, current=0.0, stall_state=False, encoder_state=False) for i in range(1, 5)])
        self.battery_stated.emit(BatteryGroup(state=True, adapter_access=False, charging_pile_access=False, batteries=[
            Battery(id=1, voltage=0.0, plugged=False, LED=False)
        ]))

    def get_status_info(self):
        report_message = self.__agv_handler.get_auto_report_message()
        if not report_message:
            return

        # 电机电流
        self.motor_stated.emit(report_message.motors)
        self.battery_stated.emit(report_message.battery_groups)

    def set_auto_report_state(self, state: int):
        for i in range(10):
            auto_state = self.__agv_handler.get_auto_report_state()
            print(f" # Set auto report state {state, auto_state}")
            if auto_state == state:
                break
            self.__agv_handler.set_auto_report_state(state)
            wait_for_timeout(1)

    def get_firmware_version(self):
        version = self.__agv_handler.get_firmware_version()
        if version and version != self.__firmware_version:
            self.__firmware_version = version
            self.versioned.emit(str(version))

    def get_localhost_address(self):
        localhost_address = utils.get_localhost()
        if localhost_address and localhost_address != self.__localhost:
            self.__localhost = localhost_address
            self.ip_stated.emit(localhost_address)

    def check_3d_camera_state(self):
        state = utils.get_3d_camera_status()
        if self.__3d_camera_state != state:
            self.__3d_camera_state = state
            self.camera_changed.emit(state)

    def run(self):
        self.set_auto_report_state(1)
        while self.__detector is True:
            try:
                self.get_status_info()
                self.get_firmware_version()
                self.get_localhost_address()
                self.check_3d_camera_state()

            except serial.serialutil.SerialException:
                pass

            except Exception as e:
                print(f"@MyAGVStatusDetector::run exception: {e}")
                traceback.print_exc()

            finally:
                time.sleep(self.__interval)
        self.set_auto_report_state(0)
